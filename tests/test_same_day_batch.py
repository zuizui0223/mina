import csv
import math

import numpy as np

from mina.same_day_batch import (
    analyze,
    build_pair_records,
    focal_beta,
    load_units,
    permuted_dates,
    update_date_predictors,
)

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
                    common=0.08*math.sin(0.5*year+ii)
                    for c in range(4):
                        # Pair 0/1 share a stronger extra fluctuation and the same dates;
                        # pair 2/3 use different dates and mostly idiosyncratic noise.
                        extra=(0.08*math.sin(0.9*year) if c<2 else
                               0.015*math.sin(1.1*year+c))
                        state[(island,c)]*=math.exp(common+extra)
            for ii,island in enumerate(ISLANDS):
                for c in range(4):
                    day=12 if c<2 else 15+c
                    w.writerow([
                        f"P{year}",f"{year}-11-{day:02d}T00:00:00Z",
                        island,c+1,round(state[(island,c)])
                    ])


def test_same_day_batch_positive_fixture(tmp_path):
    p=tmp_path/"c.csv"
    _fixture(p)
    x=analyze(p,n_permutations=199,seed=19)
    assert x["n_within_island_pairs"]>0
    assert x["observed"]["focal_beta_fisher_z_per_fraction"]>0


def test_perf_update_matches_full_recomputation(tmp_path):
    p=tmp_path/"c.csv"
    _fixture(p)
    units=load_units(p)
    base=build_pair_records(units)
    rng=np.random.default_rng(77)
    override=permuted_dates(units,rng)
    slow=build_pair_records(units,override)
    fast=update_date_predictors(base,units,override)
    assert len(slow)==len(fast)
    assert np.isclose(focal_beta(slow),focal_beta(fast),rtol=0,atol=1e-15)
    assert all(
        np.isclose(
            float(a["same_both_endpoint_fraction"]),
            float(b["same_both_endpoint_fraction"]),
            rtol=0,
            atol=0,
        )
        for a,b in zip(slow,fast)
    )
