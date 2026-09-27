import csv

from mina.census_timing_audit import audit

ISLANDS=("CHR","COR","HUM","LIT","TOR")


def test_timing_audit_allows_split_island_censuses(tmp_path):
    p=tmp_path/"c.csv"
    with p.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        for year in range(1991,1995):
            for i,island in enumerate(ISLANDS):
                w.writerow(["x",f"{year}-11-{15+i:02d}T00:00:00Z",island,1,10])
                day=16+i if island=="TOR" else 15+i
                w.writerow(["x",f"{year}-11-{day:02d}T00:00:00Z",island,2,10])
    x=audit(p)
    assert x["n_complete_years"]==4
    assert x["within_island_year_timing"]["n_multi_date_cells"]==4
    assert x["within_island_year_timing"]["max_span_days"]==1
    assert x["cross_island_median_timing"]["max_five_island_span_days"]>0
