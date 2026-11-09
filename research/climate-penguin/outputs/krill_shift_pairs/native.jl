using Circuitscape, DelimitedFiles
folder=abspath("work/krill_shift_pairs")
nodes=joinpath(folder,"nodes.txt")
write(nodes,"1\n2\n3\n")
jobs=readdlm(joinpath(folder,"jobs.csv"),',',Any,'\n';header=true)[1]
open("outputs/krill_shift_pairs/native_check.csv","w") do result
    println(result,"network,R_A_native,R_B_native,max_abs_error")
    for (id,row) in enumerate(eachrow(jobs))
        file,a,b=row
        prefix=joinpath(folder,"native_"*string(id))
        cfg=Circuitscape.init_config()
        for (key,value) in [("data_type","network"),("scenario","pairwise"),("habitat_map_is_resistances","False"),("habitat_file",string(file)),("point_file",nodes),("output_file",prefix),("solver","cholmod"),("write_cur_maps","False"),("write_volt_maps","False")]
            cfg[key]=value
        end
        Circuitscape.compute(cfg)
        tab=readdlm(prefix*"_resistances_3columns.out")
        value(i)=only(tab[(tab[:,1].==i).&(tab[:,2].==3),3])
        va,vb=value(1),value(2)
        diff=max(abs(va-a),abs(vb-b))
        @assert diff<1e-7
        println(result,join((basename(file),va,vb,diff),","))
    end
end
