import csv
import math

import numpy as np

from mina.island_common_census_error import (
    _simulate_cv,
    _transition_arrays,
    analyze,
)


ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _fixture(path):
    values={
        (island,code):300.0+30*code+15*k
        for k,island in enumerate(ISLANDS)
        for code in range(4)
    }
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            if year>1991:
                for k,island in enumerate(ISLANDS):
                    for code in range(4):
                        # deterministic colony-specific variation, deliberately
                        # no shared island-year biological shock
                        g=(
                            0.035*math.sin(0.61*year+0.83*code+0.37*k)
                            +0.018*math.cos(1.17*year+0.29*code+0.53*k)
                        )
                        values[(island,code)]=max(
                            1.0, values[(island,code)]*math.exp(g)
                        )
            for island in ISLANDS:
                for code in range(4):
                    w.writerow([
                        f"PAL{year}",
                        f"{year}-11-15T00:00:00Z",
                        island,
                        str(code+1),
                        round(values[(island,code)]),
                    ])


def test_shared_error_increases_pseudo_island_coherence(tmp_path):
    p=tmp_path/"census.csv"
    _fixture(p)
    data=_transition_arrays(p,ISLANDS)
    v0=_simulate_cv(
        data,0.0,400,np.random.SeedSequence([17,0])
    )
    v50=_simulate_cv(
        data,0.50,400,np.random.SeedSequence([17,1])
    )
    assert float(np.mean(v50)) > float(np.mean(v0)) + 0.03


def test_diagnostic_grid_is_fixed(tmp_path):
    p=tmp_path/"census.csv"
    _fixture(p)
    x=analyze(p,n_replicates=99,seed=19)
    assert list(x["five_island_primary"]["grid"]) == [
        "0.00","0.02","0.05","0.10","0.20","0.30","0.50"
    ]
    assert x["measurement_error"]["replicates_per_cv"] == 99
    assert x["decision"]["classification"] in {
        "strong_robustness",
        "moderate_robustness",
        "fragile_to_shared_error",
    }
