import csv
import math

from mina.island_year_timing_audit import analyze

ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _fixture(path):
    values={
        (island,code):500.0+30*code
        for island in ISLANDS
        for code in range(4)
    }
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            if year>1991:
                regional=0.02*math.sin(0.3*year)
                for k,island in enumerate(ISLANDS):
                    island_shock=0.11*math.sin(0.71*year+0.9*k)
                    for code in range(4):
                        noise=0.01*math.sin(1.2*year+0.4*code)
                        values[(island,code)]=max(
                            1.0,
                            values[(island,code)]*math.exp(
                                regional+island_shock+noise
                            ),
                        )
            # Two census schedules used across every island, so timing itself
            # cannot identify island membership.
            for island in ISLANDS:
                for code in range(4):
                    day=18 if code<2 else 20
                    w.writerow([
                        f"PAL{year}",
                        f"{year}-11-{day:02d}T00:00:00Z",
                        island,
                        str(code+1),
                        round(values[(island,code)]),
                    ])


def test_exact_schedule_audit_detects_island_signal_beyond_timing(tmp_path):
    p=tmp_path/"census.csv"
    _fixture(p)
    x=analyze(p,n_permutations=500,seed=3)
    assert x["five_island"]["observed_same_island_fixed_effect"]>0
    assert x["five_island"]["null"]["two_sided_p"]<=0.05
    assert x["four_island_no_litchfield"]["null"]["two_sided_p"]<=0.05
    assert x["decision"]["strong_timing_robustness"] is True
