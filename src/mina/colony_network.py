"""Fresh test of within-island breeding-colony network erosion."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows


def colony_states(path: str | Path) -> list[dict[str, object]]:
    rows=load_colony_rows(path)
    groups: dict[tuple[int,str],list[dict[str,object]]]=defaultdict(list)
    for row in rows:
        groups[(int(row["year"]),str(row["island"]))].append(row)

    out=[]
    for (year,island),local in sorted(groups.items()):
        positive=[float(r["breeding_pairs"]) for r in local if float(r["breeding_pairs"])>0]
        total=float(sum(float(r["breeding_pairs"]) for r in local))
        active=len(positive)
        if total>0:
            shares=np.asarray(positive,dtype=float)/total
            hhi=float(np.sum(shares**2))
            effective=1.0/hhi
            max_share=float(np.max(shares))
        else:
            effective=None
            max_share=None
        out.append({
            "year":year,
            "island":island,
            "total":total,
            "reported_colony_rows":len(local),
            "active_positive_colonies":active,
            "effective_colony_number":effective,
            "largest_colony_share":max_share,
        })
    return out


def transition_rows(path: str | Path) -> list[dict[str, object]]:
    states=colony_states(path)
    lookup={(int(r["year"]),str(r["island"])):r for r in states}
    years=sorted({int(r["year"]) for r in states})
    out=[]
    for year in years[:-1]:
        if year+1 not in years:
            continue
        for island in ISLANDS:
            now=lookup.get((year,island)); nxt=lookup.get((year+1,island))
            if now is None or nxt is None or float(now["total"])<=0:
                continue
            prev=lookup.get((year-1,island))
            prev_growth=None
            if prev is not None and float(prev["total"])>0:
                prev_growth=math.log1p(float(now["total"]))-math.log1p(float(prev["total"]))
            out.append({
                "start_year":year,
                "end_year":year+1,
                "island":island,
                "current_total":float(now["total"]),
                "next_total":float(nxt["total"]),
                "next_growth":math.log1p(float(nxt["total"]))-math.log1p(float(now["total"])),
                "effective_colony_number":float(now["effective_colony_number"]),
                "active_positive_colonies":int(now["active_positive_colonies"]),
                "reported_colony_rows":int(now["reported_colony_rows"]),
                "largest_colony_share":float(now["largest_colony_share"]),
                "previous_growth":prev_growth,
            })
    return out


def _z(train_values: np.ndarray,test_values: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
    mean=float(np.mean(train_values)); sd=float(np.std(train_values,ddof=1))
    if sd<=0: raise ValueError("zero predictor variance")
    return (train_values-mean)/sd,(test_values-mean)/sd


def _levels(rows: list[dict[str,object]]) -> tuple[str,...]:
    present={str(r["island"]) for r in rows}
    return tuple(i for i in ISLANDS if i in present)


def _island_matrix(islands: list[str],levels: tuple[str,...]) -> np.ndarray:
    lookup={v:i for i,v in enumerate(levels)}
    x=np.zeros((len(islands),len(levels)),dtype=float)
    for r,island in enumerate(islands):
        x[r,lookup[island]]=1.0
    return x


def _ols(x: np.ndarray,y: np.ndarray) -> np.ndarray:
    beta,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
    if rank!=x.shape[1]: raise ValueError("rank deficient colony-network model")
    return beta


def _predictor(row: dict[str,object],kind: str) -> float:
    if kind=="effective":
        return math.log1p(float(row["effective_colony_number"]))
    if kind=="active":
        return math.log1p(float(row["active_positive_colonies"]))
    raise ValueError(kind)


def _design(train: list[dict[str,object]],test: list[dict[str,object]],
            topology: bool,kind: str,include_prev: bool=False):
    levels=_levels(train)
    if any(str(r["island"]) not in levels for r in test):
        raise ValueError("test island absent from training")
    itr=[str(r["island"]) for r in train]; ite=[str(r["island"]) for r in test]
    xtr=_island_matrix(itr,levels); xte=_island_matrix(ite,levels)

    abundance_tr=np.asarray([math.log1p(float(r["current_total"])) for r in train])
    abundance_te=np.asarray([math.log1p(float(r["current_total"])) for r in test])
    atr,ate=_z(abundance_tr,abundance_te)
    year_tr=np.asarray([float(r["start_year"]) for r in train])
    year_te=np.asarray([float(r["start_year"]) for r in test])
    ytrz,ytez=_z(year_tr,year_te)
    xtr=np.column_stack([xtr,atr,ytrz]); xte=np.column_stack([xte,ate,ytez])

    if topology:
        p_tr=np.asarray([_predictor(r,kind) for r in train])
        p_te=np.asarray([_predictor(r,kind) for r in test])
        ptr,pte=_z(p_tr,p_te)
        xtr=np.column_stack([xtr,ptr]); xte=np.column_stack([xte,pte])

    if include_prev:
        prev_tr=np.asarray([float(r["previous_growth"]) for r in train])
        prev_te=np.asarray([float(r["previous_growth"]) for r in test])
        prtr,prte=_z(prev_tr,prev_te)
        xtr=np.column_stack([xtr,prtr]); xte=np.column_stack([xte,prte])

    return xtr,xte,levels


def loyo(rows: list[dict[str,object]],kind: str="effective",
         allowed_islands: tuple[str,...]=ISLANDS,include_prev: bool=False) -> dict[str,object]:
    local=[r for r in rows if str(r["island"]) in allowed_islands]
    if include_prev:
        local=[r for r in local if r["previous_growth"] is not None]
    years=sorted({int(r["end_year"]) for r in local})
    errors={"C0":[],"C1":[]}; folds=[]
    for held in years:
        train=[r for r in local if int(r["end_year"])!=held]
        test=[r for r in local if int(r["end_year"])==held]
        rec={"end_year":held,"n_test":len(test)}
        for model,topology in (("C0",False),("C1",True)):
            xtr,xte,_=_design(train,test,topology,kind,include_prev)
            ytr=np.asarray([float(r["next_growth"]) for r in train])
            yte=np.asarray([float(r["next_growth"]) for r in test])
            beta=_ols(xtr,ytr)
            err=yte-xte@beta
            errors[model].extend((err**2).tolist())
            rec[f"{model}_mse"]=float(np.mean(err**2))
        folds.append(rec)
    mse={k:float(np.mean(v)) for k,v in errors.items()}
    return {
        "n_rows":len(local),"n_years":len(years),"mse":mse,
        "mse_gain_C0_minus_C1":mse["C0"]-mse["C1"],"folds":folds
    }


def full_coefficient(rows: list[dict[str,object]],kind: str="effective",
                     allowed_islands: tuple[str,...]=ISLANDS,
                     include_prev: bool=False) -> float:
    local=[r for r in rows if str(r["island"]) in allowed_islands]
    if include_prev: local=[r for r in local if r["previous_growth"] is not None]
    x,_,_=_design(local,local,True,kind,include_prev)
    y=np.asarray([float(r["next_growth"]) for r in local])
    beta=_ols(x,y)
    # topology is last unless previous growth is included
    return float(beta[-2] if include_prev else beta[-1])


def analyze(path: str|Path) -> dict[str,object]:
    states=colony_states(path)
    rows=transition_rows(path)
    primary=loyo(rows,"effective")
    beta=full_coefficient(rows,"effective")
    active=loyo(rows,"active")
    active_beta=full_coefficient(rows,"active")
    prev=loyo(rows,"effective",include_prev=True)
    prev_beta=full_coefficient(rows,"effective",include_prev=True)
    four=loyo(rows,"effective",allowed_islands=("CHR","COR","HUM","TOR"))
    four_beta=full_coefficient(rows,"effective",allowed_islands=("CHR","COR","HUM","TOR"))
    supported=bool(primary["mse_gain_C0_minus_C1"]>0 and beta>0)
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-colony-network-erosion-v1",
        "states":states,
        "transition_rows":rows,
        "primary":{
            "predictor":"log1p effective colony number",
            "loyo":primary,
            "full_data_coefficient":beta,
            "decision":"supported" if supported else "not_supported"
        },
        "sensitivities":{
            "active_colony_count":{"loyo":active,"coefficient":active_beta},
            "add_previous_growth":{"loyo":prev,"coefficient":prev_beta},
            "four_persistently_extant_islands":{"loyo":four,"coefficient":four_beta}
        },
        "code_diagnostics":{
            island:{
                "min_reported_colony_rows":min(int(r["reported_colony_rows"]) for r in states if r["island"]==island),
                "max_reported_colony_rows":max(int(r["reported_colony_rows"]) for r in states if r["island"]==island),
                "unique_reported_colony_row_counts":sorted({int(r["reported_colony_rows"]) for r in states if r["island"]==island})
            } for island in ISLANDS
        },
        "interpretation_boundary":{
            "internal_demographic_state_not_external_habitat_measure":True,
            "predictive_not_causal":True,
            "no_post_hoc_topology_search":True
        }
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=analyze(args.census)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
