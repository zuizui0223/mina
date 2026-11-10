using Circuitscape, DelimitedFiles
const cache = abspath("work/circuit_share")
const stress = "--stress" in ARGS
const triple = "--triple" in ARGS
const out = abspath("outputs/circuit_share_forecast", stress ? "stress_native.csv" : triple ? "tri_native.csv" : "native_resistances.csv")
jobs = readdlm(joinpath(cache,stress ? "stress_jobs.csv" : triple ? "tri_jobs.csv" : "jobs.csv"), ',', Any, '\n';header=true)[1]
open(out,"w") do f
    println(f,"case,key,year,beta,R_A,R_B,max_abs_solver_difference")
    for row in eachrow(jobs)
        case,key,yr,beta,path,nodes,va,vb=row
        cfg=Circuitscape.init_config()
        cfg["data_type"]="network"
        cfg["scenario"]="pairwise"
        cfg["habitat_map_is_resistances"]="False"
        cfg["habitat_file"]=string(path)
        cfg["point_file"]=string(nodes)
        cfg["output_file"]=joinpath(cache,string(case))
        cfg["solver"]="cholmod"
        cfg["write_cur_maps"]="False"
        cfg["write_volt_maps"]="False"
        Circuitscape.compute(cfg)
        tab=readdlm(joinpath(cache,string(case)*"_resistances_3columns.out"))
        function getR(node)
            only(tab[(tab[:,1].==node).&(tab[:,2].==3),3])
        end
        a,b=getR(1),getR(2)
        err=max(abs(a-va),abs(b-vb))
        @assert err<1e-6 (case,err)
        println(f,join((case,key,Int(yr),Int(beta),a,b,err),","))
        flush(f)
    end
end
