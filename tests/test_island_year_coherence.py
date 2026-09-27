import csv
import math

from mina.island_year_coherence import analyze


ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _write_fixture(path):
    values={
        (island,code):500.0+40*code
        for island in ISLANDS
        for code in range(4)
    }
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            if year>1991:
                regional=0.03*math.sin(0.4*year)
                for k,island in enumerate(ISLANDS):
                    island_shock=0.12*math.sin(0.77*year+1.2*k)
                    for code in range(4):
                        noise=0.01*math.sin(1.31*year+0.4*code)
                        values[(island,code)]=max(
                            1.0,
                            values[(island,code)]
                            *math.exp(regional+island_shock+noise),
                        )
            for island in ISLANDS:
                for code in range(4):
                    # One structured missing census to verify unbalanced handling.
                    if island=="CHR" and code==0 and year==2006:
                        continue
                    w.writerow([
                        f"PAL{year}",
                        f"{year}-11-15T00:00:00Z",
                        island,
                        str(code+1),
                        round(values[(island,code)]),
                    ])


def test_unbalanced_island_year_coherence_detects_shared_island_shocks(tmp_path):
    p=tmp_path/"census.csv"
    _write_fixture(p)
    x=analyze(p,n_permutations=500,seed=11)
    assert x["five_island_all_period"]["observed"]["island_year_covariance_contrast"]>0
    assert x["five_island_all_period"]["null"]["two_sided_p"]<=0.05
    assert x["four_island_no_litchfield"]["null"]["two_sided_p"]<=0.05
    assert x["decision"]["strong_confirmation"] is True


def test_zero_to_zero_transitions_do_not_create_information(tmp_path):
    p=tmp_path/"census.csv"
    _write_fixture(p)
    # Append a colony that is always zero; it should never become eligible.
    with p.open("a",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        for year in range(1991,2018):
            w.writerow([
                f"PAL{year}",
                f"{year}-11-15T00:00:00Z",
                "CHR",
                "99",
                0,
            ])
    x=analyze(p,n_permutations=99,seed=12)
    records=x["five_island_all_period"]["eligibility"]["colony_records"]
    assert not any(r["island"]=="CHR" and r["colony_code"]=="99" for r in records)
