"""Exact census-schedule audit for island-year demographic coherence."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
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


def _date_map(path: str | Path, islands: tuple[str, ...]) -> dict[tuple[str,str,int], str]:
    out: dict[tuple[str,str,int],str] = {}
    with Path(path).open("r",encoding="utf-8-sig",newline="") as handle:
        for row in csv.DictReader(handle):
            island=str(row.get("island_name","")).strip()
            if island not in islands:
                continue
            value=str(row.get("num_breeding_pairs","")).strip()
            if value in {"","NA","NaN","nan"}:
                continue
            raw=str(row.get("time","")).strip()
            try:
                date=datetime.fromisoformat(raw.replace("Z","+00:00")).date()
            except ValueError:
                continue
            code=str(row.get("colony_code","")).strip()
            key=(island,code,date.year)
            if key in out and out[key]!=date.isoformat():
                raise ValueError(f"multiple census dates for {key}")
            out[key]=date.isoformat()
    return out


def _records(
    path: str | Path,
    islands: tuple[str,...],
) -> tuple[list[dict[str,object]], np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int]:
    colonies=_build_colonies(path,islands)
    labels=np.asarray([str(c["island"]) for c in colonies],dtype=object)
    strata=_rank_strata(colonies)
    residuals=_regional_residuals(colonies)
    dates=_date_map(path,islands)

    a_list=[]; b_list=[]; y_list=[]; block_keys=[]
    for a,b in combinations(range(len(colonies)),2):
        ca=colonies[a]; cb=colonies[b]
        ya={int(y) for y,_ in ca["z_growth"]}
        yb={int(y) for y,_ in cb["z_growth"]}
        for end_year in sorted(ya & yb):
            keys=(
                (str(ca["island"]),str(ca["colony_code"]),end_year-1),
                (str(cb["island"]),str(cb["colony_code"]),end_year-1),
                (str(ca["island"]),str(ca["colony_code"]),end_year),
                (str(cb["island"]),str(cb["colony_code"]),end_year),
            )
            if not all(key in dates for key in keys):
                continue
            start_a,start_b,end_a,end_b=(dates[key] for key in keys)
            if start_a!=start_b or end_a!=end_b:
                continue
            a_list.append(a); b_list.append(b)
            y_list.append(float(residuals[(a,end_year)]*residuals[(b,end_year)]))
            block_keys.append((end_year,start_a,end_a))

    unique={key:index for index,key in enumerate(sorted(set(block_keys)))}
    blocks=np.asarray([unique[key] for key in block_keys],dtype=int)
    a=np.asarray(a_list,dtype=int); b=np.asarray(b_list,dtype=int)
    response=np.asarray(y_list,dtype=float)

    yres=np.empty_like(response)
    for block in range(len(unique)):
        idx=blocks==block
        yres[idx]=response[idx]-float(np.mean(response[idx]))

    same=labels[a]==labels[b]
    variable_blocks=0
    for block in range(len(unique)):
        idx=blocks==block
        x=same[idx]
        if bool(np.any(x)) and bool(np.any(~x)):
            variable_blocks+=1
    return colonies,labels,strata,a,b,blocks,response,yres,len(unique),variable_blocks


def _coef(
    labels: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    blocks: np.ndarray,
    yres: np.ndarray,
) -> float:
    x=(labels[a]==labels[b]).astype(float)
    xres=np.empty_like(x)
    for block in sorted(set(blocks.tolist())):
        idx=blocks==block
        xres[idx]=x[idx]-float(np.mean(x[idx]))
    den=float(np.sum(xres*xres))
    if den<=0:
        raise ValueError("no within-block same-island variation")
    return float(np.sum(xres*yres)/den)


def _run(
    path: str | Path,
    islands: tuple[str,...],
    n_permutations: int,
    seed: int,
) -> dict[str,object]:
    (
        colonies,labels,strata,a,b,blocks,response,yres,n_blocks,variable_blocks
    )=_records(path,islands)
    observed=_coef(labels,a,b,blocks,yres)
    same=labels[a]==labels[b]

    rng=np.random.default_rng(seed)
    null=np.empty(n_permutations,dtype=float)
    for index in range(n_permutations):
        perm=_permute_labels(labels,strata,rng)
        null[index]=_coef(perm,a,b,blocks,yres)

    p=_p_two_sided(null,observed)
    return {
        "islands":list(islands),
        "n_eligible_colonies":len(colonies),
        "n_matched_pairyear_records":int(response.size),
        "n_schedule_blocks":n_blocks,
        "n_blocks_with_observed_within_between_variation":variable_blocks,
        "observed_same_island_fixed_effect":observed,
        "pooled_matched_schedule":{
            "within_mean_pairyear_product":float(np.mean(response[same])),
            "between_mean_pairyear_product":float(np.mean(response[~same])),
            "within_records":int(np.sum(same)),
            "between_records":int(np.sum(~same)),
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


def analyze(
    path: str | Path,
    n_permutations: int=N_PERMUTATIONS,
    seed: int=SEED,
) -> dict[str,object]:
    if n_permutations<99:
        raise ValueError("at least 99 permutations are required")
    five=_run(path,ISLANDS,n_permutations,seed)
    four=_run(
        path,
        tuple(island for island in ISLANDS if island!="LIT"),
        n_permutations,
        seed+1,
    )
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-island-year-timing-audit-v1",
        "five_island":five,
        "four_island_no_litchfield":four,
        "decision":{
            "primary_timing_robust":bool(five["supported"]),
            "no_litchfield_timing_robust":bool(four["supported"]),
            "strong_timing_robustness":bool(five["supported"] and four["supported"]),
        },
        "interpretation_boundary":{
            "conditions_on_exact_start_and_end_census_dates":True,
            "does_not_rule_out_all_observation_processes":True,
            "post_result_audit":True,
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
