import csv, math
from mina.large_groups import analyze
ISLANDS=("CHR","COR","HUM","LIT","TOR")
def test_large_groups(tmp_path):
    p=tmp_path/"c.csv"
    with p.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h); w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"]); w.writerow(["","UTC","","","1"])
        totals={i:1000+100*k for k,i in enumerate(ISLANDS)}
        ng={i:5 for i in ISLANDS}
        for y in range(1991,2010):
            for k,i in enumerate(ISLANDS):
                g=ng[i]; each=totals[i]/g
                for j in range(g): w.writerow([f"P{y}",f"{y}-11-15T00:00:00Z",i,str(j),round(each)])
                if y<2009:
                    growth=-0.12+0.035*g+0.002*k
                    totals[i]*=math.exp(growth)
                    if (y+k)%5==0: ng[i]=max(1,ng[i]-1)
    x=analyze(p)
    assert x["primary"]["coefficient"]>0
    assert x["primary"]["loyo"]["gain_G0_minus_G1"]>0
