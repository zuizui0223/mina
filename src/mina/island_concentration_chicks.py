"""Island-level chick output versus within-island breeding concentration."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .colony_extinction_hazard import ISLANDS, load_rows
from .preextinction_chick import load_chicks

N_SIMULATIONS = 100_000
SEED = 20260930
BATCH = 1000


def build_panel(adult_census: str | Path, chick_path: str | Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    adults=load_rows(adult_census)
    chick_lookup,chick_inventory=load_chicks(chick_path)

    chick_totals: dict[tuple[str,int], float]=defaultdict(float)
    chick_codes: dict[tuple[str,int], int]=defaultdict(int)
    for (island,code,season),value in chick_lookup.items():
        chick_totals[(island,season)]+=float(value)
        chick_codes[(island,season)]+=1

    grouped: dict[tuple[str,int], list[float]]=defaultdict(list)
    for row in adults:
        grouped[(str(row["island"]),int(row["year"]))].append(float(row["count"]))

    panel=[]
    zero_adult_years=[]
    for (island,year),counts in sorted(grouped.items()):
        if (island,year) not in chick_totals:
            continue
        total=float(sum(counts))
        positive=np.asarray([x for x in counts if x>0],dtype=float)
        if total<=0 or positive.size==0:
            zero_adult_years.append({"island":island,"year":year,"adult_pairs":total})
            continue
        shares=positive/total
        hhi=float(np.sum(shares**2))
        neff=1.0/hhi
        largest=float(np.max(shares))
        panel.append({
            "island":island,
            "year":year,
            "adult_pairs":total,
            "total_chicks":float(chick_totals[(island,year)]),
            "chick_codes":int(chick_codes[(island,year)]),
            "effective_colony_number":neff,
            "largest_colony_share":largest,
            "concentration":-math.log(neff),
            "chick_rate":float(chick_totals[(island,year)])/total,
        })
    inventory={
        **chick_inventory,
        "eligible_panel_rows":len(panel),
        "zero_adult_island_years_excluded":len(zero_adult_years),
        "zero_adult_details":zero_adult_years,
        "panel_by_island":{island:sum(r["island"]==island for r in panel) for island in ISLANDS},
        "panel_year_range":[min(r["year"] for r in panel),max(r["year"] for r in panel)],
    }
    return panel,inventory


def _base_design(rows: list[dict[str, object]]) -> tuple[np.ndarray,np.ndarray,list[str]]:
    islands=sorted({str(r["island"]) for r in rows})
    years=sorted({int(r["year"]) for r in rows})
    cols=[np.ones(len(rows),dtype=float)]
    names=["intercept"]
    for island in islands[1:]:
        cols.append(np.asarray([1.0 if r["island"]==island else 0.0 for r in rows]))
        names.append(f"island_{island}")
    for year in years[1:]:
        cols.append(np.asarray([1.0 if int(r["year"])==year else 0.0 for r in rows]))
        names.append(f"year_{year}")
    logn=np.log1p(np.asarray([float(r["adult_pairs"]) for r in rows]))
    cols.append(logn);names.append("log1p_adult_pairs")
    x=np.column_stack(cols)
    y=np.log1p(np.asarray([float(r["total_chicks"]) for r in rows]))
    if np.linalg.matrix_rank(x)!=x.shape[1]:
        raise ValueError("rank-deficient base design")
    return x,y,names


def _raw_predictor(rows: list[dict[str, object]], kind: str) -> np.ndarray:
    if kind=="concentration":
        return np.asarray([float(r["concentration"]) for r in rows])
    if kind=="largest_share":
        p=np.asarray([float(r["largest_colony_share"]) for r in rows])
        p=np.clip(p,1e-6,1-1e-6)
        return np.log(p/(1-p))
    raise ValueError(kind)


def _fit_observed(rows: list[dict[str, object]],kind: str) -> dict[str, object]:
    x0,y,names=_base_design(rows)
    c=_raw_predictor(rows,kind)
    sd=float(np.std(c,ddof=1))
    if sd<=0: raise ValueError("zero predictor variance")
    z=(c-float(np.mean(c)))/sd
    x=np.column_stack([x0,z])
    beta,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
    if rank!=x.shape[1]: raise ValueError("rank-deficient full design")
    fitted=x@beta;resid=y-fitted
    sse=float(resid@resid);tss=float(np.sum((y-y.mean())**2))
    return {
        "beta":float(beta[-1]),
        "r2":1-sse/tss if tss>0 else None,
        "n_rows":len(rows),
        "predictor_mean":float(np.mean(c)),
        "predictor_sd":sd,
        "chick_rate_median":float(np.median([r["chick_rate"] for r in rows])),
        "chick_rate_mean":float(np.mean([r["chick_rate"] for r in rows])),
    }


def _shift_null(rows: list[dict[str, object]],kind: str,simulations: int,seed: int) -> dict[str, object]:
    x0,y,_=_base_design(rows)
    c=_raw_predictor(rows,kind)
    c=(c-float(np.mean(c)))/float(np.std(c,ddof=1))
    # Frisch-Waugh residualization with reduced QR basis.
    q,_=np.linalg.qr(x0,mode="reduced")
    yres=y-q@(q.T@y)
    cres=c-q@(q.T@c)
    observed=float((cres@yres)/(cres@cres))

    island_indices={}
    for island in sorted({str(r["island"]) for r in rows}):
        idx=np.asarray([i for i,r in enumerate(rows) if r["island"]==island],dtype=int)
        idx=idx[np.argsort([int(rows[i]["year"]) for i in idx])]
        if len(idx)<2: raise ValueError("island has fewer than two eligible years")
        island_indices[island]=idx

    rng=np.random.default_rng(seed)
    null=np.empty(simulations,dtype=float)
    done=0
    while done<simulations:
        b=min(BATCH,simulations-done)
        mat=np.repeat(c[:,None],b,axis=1)
        for idx in island_indices.values():
            n=len(idx)
            lags=rng.integers(1,n,size=b)
            base=c[idx]
            # Each column gets its own non-zero circular lag.
            pos=(np.arange(n)[:,None]-lags[None,:])%n
            mat[idx,:]=base[pos]
        # Global z scale is invariant to within-island permutation.
        res=mat-q@(q.T@mat)
        num=yres@res
        den=np.sum(res*res,axis=0)
        null[done:done+b]=num/den
        done+=b

    lower=(1+int(np.sum(null<=observed)))/(simulations+1)
    upper=(1+int(np.sum(null>=observed)))/(simulations+1)
    return {
        "observed_beta":observed,
        "simulations":simulations,
        "seed":seed,
        "null_mean":float(np.mean(null)),
        "null_sd":float(np.std(null,ddof=1)),
        "null_q025":float(np.quantile(null,.025)),
        "null_q50":float(np.quantile(null,.5)),
        "null_q975":float(np.quantile(null,.975)),
        "lower_tail_p":float(lower),
        "upper_tail_p":float(upper),
        "two_sided_p":float(min(1.0,2*min(lower,upper))),
    }


def fit_and_test(rows,kind,simulations,seed):
    return {
        "fit":_fit_observed(rows,kind),
        "circular_shift_inference":_shift_null(rows,kind,simulations,seed),
    }


def _period_fit(rows,start,end):
    local=[r for r in rows if start<=int(r["year"])<=end]
    try:
        return _fit_observed(local,"concentration")
    except ValueError as exc:
        return {"estimable":False,"reason":str(exc),"n_rows":len(local)}


def analyze(adult_census,chick_path,simulations=N_SIMULATIONS,seed=SEED):
    rows,inventory=build_panel(adult_census,chick_path)
    primary=fit_and_test(rows,"concentration",simulations,seed)
    largest=fit_and_test(rows,"largest_share",simulations,seed+1)
    no_lit=[r for r in rows if r["island"]!="LIT"]
    exclude_lit=fit_and_test(no_lit,"concentration",simulations,seed+2)

    loo={}
    for k,island in enumerate(ISLANDS):
        local=[r for r in rows if r["island"]!=island]
        loo[island]=_fit_observed(local,"concentration")

    inf=primary["circular_shift_inference"]
    beta=float(inf["observed_beta"])
    if beta>0 and inf["upper_tail_p"]<=.05:
        decision="quality_sorting_signal"
    elif beta<0 and inf["lower_tail_p"]<=.05:
        decision="degradation_signal"
    elif inf["two_sided_p"]>.05:
        decision="decoupled"
    else:
        decision="directionally_ambiguous"

    largest_beta=float(largest["circular_shift_inference"]["observed_beta"])
    loo_same=all(np.sign(float(v["beta"]))==np.sign(beta) for v in loo.values())
    strong=bool(
        decision in {"quality_sorting_signal","degradation_signal"}
        and np.sign(largest_beta)==np.sign(beta)
        and loo_same
    )
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-island-concentration-chick-output-v1",
        "contracts":[
            "mina-palmer-island-concentration-chick-output-v1",
            "mina-palmer-island-concentration-chick-output-execution-v1"
        ],
        "source":{
            "adult_census_sha256":hashlib.sha256(Path(adult_census).read_bytes()).hexdigest(),
            "chick_snapshot_sha256":hashlib.sha256(Path(chick_path).read_bytes()).hexdigest()
        },
        "inventory":inventory,
        "primary_concentration":primary,
        "sensitivities":{
            "largest_share":largest,
            "exclude_litchfield":exclude_lit,
            "leave_one_island_out":loo,
            "early_1991_2003":_period_fit(rows,1991,2003),
            "late_2004_2017":_period_fit(rows,2004,2017)
        },
        "decision":{
            "classification":decision,
            "strong_cross_metric_leave_one_island_stability":strong
        },
        "descriptive_chick_rates":{
            island:{
                "median":float(np.median([r["chick_rate"] for r in rows if r["island"]==island])),
                "mean":float(np.mean([r["chick_rate"] for r in rows if r["island"]==island])),
                "n":sum(r["island"]==island for r in rows)
            } for island in ISLANDS
        },
        "interpretation_boundary":{
            "not_specific_to_snow_predation_or_food":True,
            "not_an_allee_effect_test":True,
            "colony_level_chick_extinction_link_not_used":True
        }
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--adult-census",required=True,type=Path)
    p.add_argument("--chicks",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--simulations",type=int,default=N_SIMULATIONS)
    p.add_argument("--seed",type=int,default=SEED)
    a=p.parse_args()
    x=analyze(a.adult_census,a.chicks,a.simulations,a.seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
