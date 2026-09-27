import csv

from mina.census_timing_audit import audit

ISLANDS=("CHR","COR","HUM","LIT","TOR")


def test_timing_audit(tmp_path):
    p=tmp_path/"c.csv"
    with p.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        for year in range(1991,1995):
            for i,island in enumerate(ISLANDS):
                for colony in (1,2):
                    w.writerow(["x",f"{year}-11-{15+i:02d}T00:00:00Z",island,colony,10])
    x=audit(p)
    assert x["n_complete_years"]==4
    assert x["five_island_span_days"]["max"]==4
    assert x["all_pairwise_day_difference"]["max"]==4
