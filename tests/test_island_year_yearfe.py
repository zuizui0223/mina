import csv
import math

from mina.island_year_yearfe import analyze

ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _fixture(path):
    values={(i,c):600.0+30*c for i in ISLANDS for c in range(4)}
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            if year>1991:
                year_effect=0.04*math.sin(0.33*year)
                for k,island in enumerate(ISLANDS):
                    island_effect=0.12*math.sin(0.71*year+1.1*k)
                    for c in range(4):
                        noise=0.01*math.sin(1.4*year+0.4*c)
                        values[(island,c)]=max(
                            1.0,
                            values[(island,c)]*math.exp(year_effect+island_effect+noise),
                        )
            for island in ISLANDS:
                for c in range(4):
                    if island=="CHR" and c==0 and year in {2005,2006,2007}:
                        continue
                    w.writerow([f"PAL{year}",f"{year}-11-20T00:00:00Z",island,str(c+1),round(values[(island,c)])])


def test_year_fixed_effect_audit_recovers_island_signal(tmp_path):
    p=tmp_path/"c.csv"
    _fixture(p)
    x=analyze(p,n_permutations=500,seed=17)
    assert x["five_island"]["observed_same_island_year_fixed_effect"]>0
    assert x["five_island"]["null"]["two_sided_p"]<=0.05
    assert x["four_island_no_litchfield"]["null"]["two_sided_p"]<=0.05
    assert x["decision"]["strong_year_robustness"] is True
