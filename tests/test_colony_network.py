import csv
from mina.colony_network import analyze

ISLANDS=("CHR","COR","HUM","LIT","TOR")

def test_colony_network_predicts_synthetic_decline(tmp_path):
    p=tmp_path/"census.csv"
    with p.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        totals={i:1200+100*k for k,i in enumerate(ISLANDS)}
        effective_state={i:4 for i in ISLANDS}
        for year in range(1991,2010):
            for k,island in enumerate(ISLANDS):
                # fewer active colonies in year t causes worse next-year growth
                active=max(1,effective_state[island])
                share=[1/active]*active
                for j,s in enumerate(share):
                    w.writerow([f"PAL{year}",f"{year}-11-15T00:00:00Z",island,str(j+1),round(totals[island]*s)])
                if year<2009:
                    growth=-0.03+0.03*(active-2)+0.002*k
                    totals[island]=max(1,totals[island]*__import__("math").exp(growth))
                    if (year+k)%4==0:
                        effective_state[island]=max(1,effective_state[island]-1)
    x=analyze(p)
    assert x["primary"]["full_data_coefficient"]>0
    assert x["primary"]["loyo"]["mse_gain_C0_minus_C1"]>0
