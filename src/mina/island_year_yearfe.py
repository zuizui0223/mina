"""End-year fixed-effect audit for Palmer island demographic coherence."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

from .lter import ISLANDS
from .island_year_coherence import (
    N_PERMUTATIONS,
    SEED,
    _build_colonies,
    _p_two_sided,
    _permute_labels,
    _rank_strata,
    _regional_residuals,
)


def _records(path: str | Path, islands: tuple[str,...]):
    colonies=_build_colonies(path,islands)
    labels=np.asarray([str(c["island"]) for c in colonies],dtype=object)
    strata=_rank_strata(colonies)
    residuals=_regional_residuals(colonies)

    by_colony: dict[int,dict[int,float]]=defaultdict(dict)
    for (idx,year),value in residuals.items():
        by_colony[idx][year]=value

    a=[]; b=[]; years=[]; response=[]
    for i,j in combinations(range(len(colonies)),2):
        for year in sorted(set(by_colony[i]) & set(by_colony[j])):
            a.append(i); b.append(j); years.append(year)
            response.append(by_colony[i][year]*by_colony[j][year])

    a=np.asarray(a,dtype=int); b=np.asarray(b,dtype=int)
    years=np.asarray(years,dtype=int); y=np.asarray(response,dtype=float)

    yres=np.empty_like(y)
    for year in sorted(set(years.tolist())):
        idx=years==year
        yres[idx]=y[idx]-float(np.mean(y[idx]))
    return colonies,labels,strata,a,b,years,y,yres


def _coef(labels,a,b,years,yres):
    same=(labels[a]==labels[b]).astype(float)
    xres=np.empty_like(same)
    variable_years=0
    for year in sorted(set(years.tolist())):
        idx=years==year
        x=same[idx]
        xres[idx]=x-float(np.mean(x))
        if bool(np.any(x)) and bool(np.any(~x)):
            variable_years+=1
    den=float(np.sum(xres*xres))
    if den<=0:
        raise ValueError("no within-year same-island variation")
    return float(np.sum(xres*yres)/den),variable_years


def _run(path,islands,n_permutations,seed):
    colonies,labels,strata,a,b,years,y,yres=_records(path,islands)
    observed,variable_years=_coef(labels,a,b,years,yres)
    same=labels[a]==labels[b]
    rng=np.random.default_rng(seed)
    null=np.empty(n_permutations,dtype=float)
    for k in range(n_permutations):
        perm=_permute_labels(labels,strata,rng)
        null[k]=_coef(perm,a,b,years,yres)[0]
    p=_p_two_sided(null,observed)
    return {
        "islands":list(islands),
        "n_eligible_colonies":len(colonies),
        "n_pairyear_records":int(y.size),
        "n_end_years":len(set(years.tolist())),
        "n_years_with_observed_within_between_variation":variable_years,
        "observed_same_island_year_fixed_effect":observed,
        "pooled_unconditioned":{
            "within_mean_pairyear_product":float(np.mean(y[same])),
            "between_mean_pairyear_product":float(np.mean(y[~same])),
        },
        "null":{
            "n_permutations":n_permutations,
            "seed":seed,
            "mean":float(np.mean(null)),
            "sd":float(np.std(null,ddof=1)),
            "q025":float(np.quantile(null,0.025)),
            "q975":float(np.quantile(null,0.975)),
            "two_sided_p":p,
        },
        "supported":bool(observed>0 and p<=0.05),
    }


def analyze(path: str|Path,n_permutations:int=N_PERMUTATIONS,seed:int=SEED):
    if n_permutations<99:
        raise ValueError("at least 99 permutations are required")
    five=_run(path,ISLANDS,n_permutations,seed)
    four=_run(path,tuple(i for i in ISLANDS if i!="LIT"),n_permutations,seed+1)
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-island-year-yearfe-v1",
        "five_island":five,
        "four_island_no_litchfield":four,
        "decision":{
            "primary_year_robust":bool(five["supported"]),
            "no_litchfield_year_robust":bool(four["supported"]),
            "strong_year_robustness":bool(five["supported"] and four["supported"]),
        },
        "interpretation_boundary":{
            "conditions_exactly_on_end_year":True,
            "post_positive_audit":True,
            "does_not_control_distance_or_all_observation_processes":True,
        },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--permutations",type=int,default=N_PERMUTATIONS)
    p.add_argument("--seed",type=int,default=SEED)
    a=p.parse_args()
    x=analyze(a.census,a.permutations,a.seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
