import csv
import math

from mina.island_year_coherence_robustness import analyze

ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _fixture(path):
    values={(island,code):500.0+30*code for island in ISLANDS for code in range(4)}
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            if year>1991:
                region=0.02*math.sin(0.31*year)
                for k,island in enumerate(ISLANDS):
                    shock=0.11*math.sin(0.72*year+1.1*k)
                    for code in range(4):
                        noise=0.01*math.sin(1.3*year+0.5*code)
                        values[(island,code)]=max(
                            1.0,
                            values[(island,code)]
                            *math.exp(region+shock+noise),
                        )
            for island in ISLANDS:
                for code in range(4):
                    w.writerow([
                        f"PAL{year}",
                        f"{year}-11-20T00:00:00Z",
                        island,
                        str(code+1),
                        round(values[(island,code)]),
                    ])


def test_strict_robustness_audits_pass_on_shared_island_signal(tmp_path):
    p=tmp_path/"census.csv"
    _fixture(p)
    x=analyze(p,n_permutations=500,seed=21)
    assert x["decision"]["positive_to_positive_robust"] is True
    assert x["decision"]["not_single_island_driven"] is True
    assert x["decision"]["strong_robustness"] is True
