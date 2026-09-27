import csv
import math

from mina.island_partition_date_separated import analyze

ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _fixture(path):
    state={(island,c):300.0+20*c for island in ISLANDS for c in range(4)}
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            if year>1991:
                for ii,island in enumerate(ISLANDS):
                    shock=0.10*math.sin(0.45*year+ii)
                    for c in range(4):
                        state[(island,c)]*=math.exp(shock+0.01*math.sin(year+c))
            for ii,island in enumerate(ISLANDS):
                for c in range(4):
                    # All subcolonies get distinct dates, so strict mode has data.
                    day=10 + ((ii*4+c+year)%15)
                    w.writerow([
                        f"P{year}",
                        f"{year}-11-{day:02d}T00:00:00Z",
                        island,
                        c+1,
                        round(state[(island,c)]),
                    ])


def test_strict_date_separated_partition(tmp_path):
    p=tmp_path/"c.csv"
    _fixture(p)
    x=analyze(p,n_permutations=300,seed=41)
    assert x["strict"]["validity_pass"] is True
    assert x["strict"]["n_informative_pairs"]>0
    assert x["strict"]["observed"]["partition_contrast_r"]>0
