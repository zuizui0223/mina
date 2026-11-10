# Native Julia Circuitscape.jl pairwise effective-resistance solves on original OSI SAF pixels.
# This is a hypothetical physical conductance network, not a penguin migration model.
using Circuitscape
using DelimitedFiles
using Dates

const HERE = @__DIR__
const OUT = joinpath(HERE,"circuit_outputs")
const SOURCE = joinpath(OUT,"circuit_scenarios.tsv")
isfile(SOURCE) || error("Locked scenario manifest not found: $SOURCE")
rows = readlines(SOURCE)
length(rows) >= 2 || error("Empty circuit scenario list")
fieldnames = split(rows[1],'\t')
fieldnames == ["key","year","model","beta","neighbor_count","habitat_raster","focal_raster","write_current"] ||
    error("Locked fields changed: $fieldnames")

function mkconfig(values)
    key,year,model,beta,neighbors,habitat,focal,current = values
    neighbors in ["4","8"] || error("Unsupported neighbor scheme")
    beta in ["-2.0","0.0","2.0"] || error("Non-frozen beta")
    path = joinpath(OUT,"solves",key)
    mkpath(dirname(path))
    cfg = Circuitscape.init_config()
    cfg["data_type"] = "raster"
    cfg["scenario"] = "pairwise"
    cfg["habitat_file"] = joinpath(OUT,habitat)
    cfg["point_file"] = joinpath(OUT,focal)
    cfg["habitat_map_is_resistances"] = "True"
    cfg["connect_using_avg_resistances"] = "False"
    cfg["connect_four_neighbors_only"] = neighbors == "4" ? "True" : "False"
    cfg["solver"] = "cholmod"
    cfg["precision"] = "Double"
    cfg["output_file"] = path * ".out"
    cfg["write_cur_maps"] = current == "True" ? "True" : "False"
    cfg["write_cum_cur_map_only"] = current == "True" ? "True" : "False"
    cfg["write_volt_maps"] = "False"
    cfg["parallelize"] = "False"
    return cfg, path
end
println("ACTUAL_CIRCUITSCAPE_JULIA_VERSION=" * string(VERSION))
println("ACTUAL_CIRCUITSCAPE_STARTED=" * string(now()))
for (j,line) in enumerate(rows[2:end])
    values=split(strip(line),'\t')
    length(values)==length(fieldnames) || error("Bad scenario row $j")
    key=values[1]
    cfg,path=mkconfig(values)
    isfile(cfg["habitat_file"]) || error("Absent original raster")
    isfile(cfg["point_file"]) || error("Absent original points")
    println("CIRCUIT_START="*key)
    flush(stdout)
    matrix=Circuitscape.compute(cfg)
    size(matrix)==(7,7) || error("Expected a 7x7 six-focal resistance matrix, got $(size(matrix))")
    writedlm(path*"_matrix_from_actual_julia.csv",matrix,',')
    println("CIRCUIT_DONE="*key*" shape="*string(size(matrix))*" saved="*path)
    flush(stdout)
end
println("ACTUAL_CIRCUITSCAPE_ALL_SOLVES_COMPLETE count="*(string(length(rows)-1)))
