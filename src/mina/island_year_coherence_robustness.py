"""Post-positive robustness audits for island-year demographic coherence."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows
from .island_year_coherence import (
    MIN_INFORMATIVE_TRANSITIONS,
    N_PERMUTATIONS,
    SEED,
    _contrast_from_labels,
    _p_two_sided,
    _pair_aggregates,
    _permute_labels,
    _rank_strata,
    _regional_residuals,
    _run as base_run,
)


def _positive_colonies(
    path: str | Path,
    islands: tuple[str,...],
) -> list[dict[str,object]]:
    rows=load_colony_rows(path)
    counts: dict[tuple[str,str,int],float]=defaultdict(float)
    codes:set[tuple[str,str]]=set()
    for row in rows:
        island=str(row["island"])
        if island not in islands:
            continue
        code=str(row["colony_code"]); year=int(row["year"])
        counts[(island,code,year)]+=float(row["breeding_pairs"])
        codes.add((island,code))

    colonies=[]
    for island,code in sorted(codes):
        years=sorted(
            year for ii,cc,year in counts
            if ii==island and cc==code
        )
        growth=[]
        for end_year in years:
            start_year=end_year-1
            if (island,code,start_year) not in counts:
                continue
            start=float(counts[(island,code,start_year)])
            end=float(counts[(island,code,end_year)])
            if start<=0 or end<=0:
                continue
            growth.append(
                (end_year,math.log1p(end)-math.log1p(start))
            )
        if len(growth)<MIN_INFORMATIVE_TRANSITIONS:
            continue
        values=np.asarray([value for _,value in growth],dtype=float)
        sd=float(np.std(values,ddof=1))
        if sd<=0:
            continue
        mean=float(np.mean(values))
        reported=np.asarray(
            [counts[(island,code,year)] for year in years],dtype=float
        )
        colonies.append({
            "island":island,
            "colony_code":code,
            "n_informative_transitions":len(growth),
            "mean_log1p_abundance":float(np.mean(np.log1p(reported))),
            "z_growth":[
                (year,(value-mean)/sd) for year,value in growth
            ],
        })
    return colonies


def _run_positive(
    path: str | Path,
    islands: tuple[str,...],
    n_permutations: int,
    seed: int,
) -> dict[str,object]:
    colonies=_positive_colonies(path,islands)
    labels=np.asarray([str(c["island"]) for c in colonies],dtype=object)
    strata=_rank_strata(colonies)
    residuals=_regional_residuals(colonies)
    pairs=_pair_aggregates(colonies,residuals)
    observed=_contrast_from_labels(labels,pairs)

    rng=np.random.default_rng(seed)
    null=np.empty(n_permutations,dtype=float)
    for index in range(n_permutations):
        perm=_permute_labels(labels,strata,rng)
        null[index]=float(
            _contrast_from_labels(
                perm,pairs
            )["island_year_covariance_contrast"]
        )
    p=_p_two_sided(
        null,float(observed["island_year_covariance_contrast"])
    )
    return {
        "islands":list(islands),
        "n_eligible_colonies":len(colonies),
        "observed":observed,
        "null":{
            "n_permutations":n_permutations,
            "seed":seed,
            "mean":float(np.mean(null)),
            "q025":float(np.quantile(null,0.025)),
            "q975":float(np.quantile(null,0.975)),
            "two_sided_p":p,
        },
        "supported":bool(
            observed["island_year_covariance_contrast"]>0 and p<=0.05
        ),
    }


def analyze(
    path: str | Path,
    n_permutations: int=N_PERMUTATIONS,
    seed: int=SEED,
) -> dict[str,object]:
    if n_permutations<99:
        raise ValueError("at least 99 permutations are required")

    extant=tuple(island for island in ISLANDS if island!="LIT")
    positive_five=_run_positive(path,ISLANDS,n_permutations,seed)
    positive_four=_run_positive(path,extant,n_permutations,seed+1)

    loo={}
    for index,dropped in enumerate(ISLANDS):
        subset=tuple(island for island in ISLANDS if island!=dropped)
        loo[dropped]=base_run(
            path,subset,n_permutations,seed+10+index
        )

    positive_pass=bool(
        positive_five["supported"] and positive_four["supported"]
    )
    loo_pass=bool(all(bool(value["supported"]) for value in loo.values()))
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-island-year-coherence-robustness-v1",
        "positive_to_positive_only":{
            "five_island":positive_five,
            "four_island_no_litchfield":positive_four,
            "audit_pass":positive_pass,
        },
        "leave_one_island_out":loo,
        "decision":{
            "positive_to_positive_robust":positive_pass,
            "not_single_island_driven":loo_pass,
            "strong_robustness":bool(positive_pass and loo_pass),
        },
        "interpretation_boundary":{
            "post_positive_audit":True,
            "no_additional_subsets_or_thresholds":True,
        },
    }


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--census",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--permutations",type=int,default=N_PERMUTATIONS)
    parser.add_argument("--seed",type=int,default=SEED)
    args=parser.parse_args()
    result=analyze(args.census,args.permutations,args.seed)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
