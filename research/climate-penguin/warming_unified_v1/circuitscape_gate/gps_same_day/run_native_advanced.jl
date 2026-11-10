# Actual same-day source–peripheral-ground Circuitscape.jl advanced solves.
# All focal source, grounds and resistance grids are generated without GPS visited pixels.
using Circuitscape
using DelimitedFiles
using Dates

const HERE=@__DIR__
const OUT=joinpath(HERE,"daily_outputs")
const SOURCE=joinpath(OUT,"fixed_270_circuit_scenario_manifest.csv")
const TARGET=joinpath(OUT,"currents")
mkpath(TARGET)
isfile(SOURCE)||error("Original GPS/OSI case list not prepared")
lines=readlines(SOURCE)
length(lines)>1||error("No original GPS source-supported day models")
heads=split(lines[1],',')
expected=["case_id","year","other_island","date","site","scenario","beta","resistance_raster",
          "source_raster","ground_raster","distance_raster","n_original_matched_GPS_pixels",
          "n_source_valid_GPS_pixels_in_fixed_distance_bins"]
heads==expected||error("Original source-only scenario columns drift: "*string(heads))
println("ACTUAL_GPS_DAY_CIRCUITSCAPE_JULIA_VERSION="*string(VERSION))
println("ACTUAL_GPS_DAY_CIRCUITSCAPE_STARTED="*string(now()))
receipts=Vector{Vector{String}}()
for (i,line) in enumerate(lines[2:end])
    fields=split(strip(line),',')
    length(fields)==length(heads)||error("Malformed case "*string(i))
    key,year,other,date,site,model,beta,habitat,source,ground,dist,nGPS,nEligible=fields
    model in ("uniform","ice_penalty","ice_favor")||error("Non-frozen model")
    beta in ("0.0","2.0","-2.0")||error("Non-frozen coefficient")
    name=key*"_"*model
    prefix=joinpath(TARGET,name)
    cfg=Circuitscape.init_config()
    cfg["data_type"]="raster"
    cfg["scenario"]="advanced"
    cfg["habitat_file"]=joinpath(OUT,habitat)
    cfg["source_file"]=joinpath(OUT,source)
    cfg["ground_file"]=joinpath(OUT,ground)
    cfg["habitat_map_is_resistances"]="True"
    cfg["connect_using_avg_resistances"]="False"
    cfg["connect_four_neighbors_only"]="False"
    cfg["solver"]="cholmod"
    cfg["precision"]="Double"
    cfg["output_file"]=prefix
    cfg["write_cur_maps"]="True"
    cfg["write_volt_maps"]="False"
    cfg["use_unit_currents"]="False"
    cfg["use_direct_grounds"]="True"
    cfg["ground_file_is_resistances"]="True"
    for key0 in ("habitat_file","source_file","ground_file")
        isfile(cfg[key0])||error("Missing original pixel current input: "*cfg[key0])
    end
    Circuitscape.compute(cfg)
    # 6.0.0: Advanced mode current map is prefix_curmap.asc.
    actual=prefix*"_curmap.asc"
    isfile(actual)||error("Circuitscape did not emit its advanced current map: "*actual)
    if filesize(actual)<1000
        error("Circuitscape current source-grid output implausibly small: "*actual)
    end
    push!(receipts,[name,key,model,beta,year,date,site,joinpath("currents",basename(actual)),
                    string(filesize(actual))])
    if i%15==0 || i==length(lines)-1
        println("ACTUAL_SAME_DAY_CIRCUITSCAPE_SOLVED="*string(i)*"/"*string(length(lines)-1))
        flush(stdout)
    end
end
open(joinpath(OUT,"julia_curmap_receipts.tsv"),"w") do f
    println(f,"solve_id\tcase_id\tmodel\tbeta\tseason_start\tdate\tisland\tcurrent_raster\tbytes")
    for row in receipts
        println(f,join(row,"\t"))
    end
end
println("ACTUAL_GPS_DAY_CIRCUITSCAPE_ALL_SOLVED="*string(length(receipts)))
