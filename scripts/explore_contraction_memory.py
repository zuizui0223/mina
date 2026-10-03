#!/usr/bin/env python3
"""Stage-four post-hoc exploration of slow-variable / memory-like contraction rules."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


MODELS=("current","trailing3","running_min","calendar_time")


def _prepare(path: Path) -> pd.DataFrame:
    raw=pd.read_csv(path)
    out=[]
    for pop,g in raw.groupby("population",sort=False):
        g=g.sort_values("year").copy()
        n=g["breeding_pairs"].to_numpy(dtype=float)
        e=g["neff"].to_numpy(dtype=float)
        years=g["year"].to_numpy(dtype=float)
        if np.any(n<=0) or np.any(e<=0):
            raise ValueError(f"nonpositive value in {pop}")
        n0=float(n[0]); e0=float(e[0])
        current=-np.log(n/n0)
        running=-np.log(np.minimum.accumulate(n)/n0)
        trailing=[]
        for i in range(len(n)):
            lo=max(0,i-2)
            gm=float(np.exp(np.mean(np.log(n[lo:i+1]))))
            trailing.append(-math.log(gm/n0))
        span=float(years[-1]-years[0])
        time=(years-years[0])/span if span>0 else np.zeros_like(years)
        g["y"]=-np.log(e/e0)
        g["current"]=current
        g["trailing3"]=np.asarray(trailing)
        g["running_min"]=running
        g["calendar_time"]=time
        g["row_weight"]=1.0/len(g)
        out.append(g)
    return pd.concat(out,ignore_index=True)


def _fit(train: pd.DataFrame, model: str) -> dict[str,float]:
    x=train[model].to_numpy(dtype=float)
    y=train["y"].to_numpy(dtype=float)
    w=train["row_weight"].to_numpy(dtype=float)
    den=float(np.sum(w*x*x))
    if den<=0:
        raise ValueError(f"zero predictor variance for {model}")
    k=float(np.sum(w*x*y)/den)
    pred=k*x
    rmse=float(np.sqrt(np.average((y-pred)**2,weights=w)))
    return {"k":k,"weighted_rmse":rmse}


def _loo(df: pd.DataFrame, model: str) -> dict[str,object]:
    per={}
    for pop in df["population"].drop_duplicates():
        train=df[df["population"]!=pop]
        test=df[df["population"]==pop]
        fit=_fit(train,model)
        pred=fit["k"]*test[model].to_numpy(dtype=float)
        rmse=float(np.sqrt(np.mean((test["y"].to_numpy(dtype=float)-pred)**2)))
        per[str(pop)]={"rmse":rmse,"fit_k":fit["k"],"n_rows":int(len(test))}
    vals=[v["rmse"] for v in per.values()]
    return {
        "equal_weight_mean_population_rmse":float(np.mean(vals)),
        "median_population_rmse":float(np.median(vals)),
        "per_population":per,
    }


def analyze(path: Path) -> dict[str,object]:
    df=_prepare(path)
    fits={m:_fit(df,m) for m in MODELS}
    loo={m:_loo(df,m) for m in MODELS}
    ranking=sorted(MODELS,key=lambda m:loo[m]["equal_weight_mean_population_rmse"])
    memory=(
        loo["running_min"]["equal_weight_mean_population_rmse"]
        < loo["current"]["equal_weight_mean_population_rmse"]
        and loo["running_min"]["equal_weight_mean_population_rmse"]
        < loo["trailing3"]["equal_weight_mean_population_rmse"]
    )
    return {
        "schema_version":1,
        "analysis_id":"mina-contraction-memory-exploration-v1",
        "status":"stage4_posthoc_not_for_frozen_submission",
        "full_data_fits":fits,
        "leave_one_population_out":loo,
        "ranking_by_equal_weight_loo_rmse":ranking,
        "historical_bottleneck_memory_candidate_supported":bool(memory),
        "interpretation_boundary":[
            "Exploratory only; cannot alter the frozen Ecology Report.",
            "A running-minimum win suggests path dependence or structural persistence, not individual memory or causal hysteresis.",
            "No lag length beyond trailing3 is searched.",
            "Calendar time is a secular-trend benchmark.",
            "Five population units are nested within two monitoring systems."
        ]
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--trajectories",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=analyze(a.trajectories)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
