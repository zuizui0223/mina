import csv
from pathlib import Path

from mina.paper_data import build

ISLANDS=("CHR","COR","HUM","LIT","TOR")


def test_paper_data_builds_expected_surfaces(tmp_path):
    census=tmp_path/"census.csv"
    with census.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in (2000,2001,2002):
            for k,island in enumerate(ISLANDS):
                w.writerow([f"P{year}",f"{year}-11-15T00:00:00Z",island,"1",1000-50*(year-2000)+10*k])
                w.writerow([f"P{year}",f"{year}-11-15T00:00:00Z",island,"2",500-20*(year-2000)+5*k])
    results=Path(__file__).resolve().parents[1]/"results"
    out=tmp_path/"paper"
    manifest=build(results,census,out)
    assert len(manifest["files"])==5
    for name in manifest["files"]:
        assert (out/name).exists()
    with (out/"figure3_prospective_mechanism_tests.csv").open(newline="",encoding="utf-8") as h:
        rows=list(csv.DictReader(h))
    assert len(rows)==6
    supported=[row["test_id"] for row in rows if row["supported"]=="True"]
    assert supported==["effective_colony_number"]
