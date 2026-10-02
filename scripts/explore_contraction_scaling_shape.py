#!/usr/bin/env python3
"""Stage-two post-hoc exploration of the shape and timescale of contraction."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def _weighted_lstsq(X: np.ndarray, y: np.ndarray, w: np.ndarray) -> np.ndarray:
    sw=np.sqrt(w)[:,None]
    beta, *_=np.linalg.lstsq(X*sw, y*np.sqrt(w), rcond=None)
    return beta


def _design(x: np.ndarray, model: str) -> np.ndarray:
    x=np.asarray(x,dtype=float)
    if model=="M1":
        return x[:,None]
    if model=="M2":
        return np.column_stack([x,x**2])
    hinges={
        "M3_50":math.log(2.0),
        "M3_25":math.log(4.0),
        "M3_10":math.log(10.0),
    }
    if model in hinges:
        h=hinges[model]
        return np.column_stack([x,np.maximum(0.0,x-h)])
    raise ValueError(model)


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    out=[]
    for pop,g in df.groupby("population",sort=False):
        g=g.sort_values("year").copy()
        n0=float(g.iloc[0]["breeding_pairs"])
        e0=float(g.iloc[0]["neff"])
        g["x"]=-np.log(g["breeding_pairs"].astype(float)/n0)
        g["y"]=-np.log(g["neff"].astype(float)/e0)
        g["row_weight"]=1.0/len(g)
        out.append(g)
    return pd.concat(out,ignore_index=True)


def _fit_model(train: pd.DataFrame, model: str) -> dict[str, object]:
    X=_design(train["x"].to_numpy(dtype=float),model)
    y=train["y"].to_numpy(dtype=float)
    w=train["row_weight"].to_numpy(dtype=float)
    beta=_weighted_lstsq(X,y,w)
    pred=X@beta
    rmse=float(np.sqrt(np.average((y-pred)**2,weights=w)))
    return {"beta":[float(v) for v in beta],"weighted_rmse":rmse}


def _loo(df: pd.DataFrame, model: str) -> dict[str, object]:
    per={}
    for pop in df["population"].drop_duplicates():
        train=df[df["population"]!=pop]
        test=df[df["population"]==pop]
        fit=_fit_model(train,model)
        pred=_design(test["x"].to_numpy(dtype=float),model)@np.asarray(fit["beta"])
        rmse=float(np.sqrt(np.mean((test["y"].to_numpy(dtype=float)-pred)**2)))
        per[str(pop)]={
            "rmse":rmse,
            "n_rows":int(len(test)),
            "fit_beta":fit["beta"],
        }
    vals=[v["rmse"] for v in per.values()]
    return {
        "equal_weight_mean_population_rmse":float(np.mean(vals)),
        "median_population_rmse":float(np.median(vals)),
        "per_population":per,
    }


def _detrended(df: pd.DataFrame) -> dict[str, object]:
    rows=[]
    per={}
    for pop,g in df.groupby("population",sort=False):
        g=g.sort_values("year")
        yr=g["year"].to_numpy(dtype=float)
        ln=np.log(g["breeding_pairs"].to_numpy(dtype=float))
        le=np.log(g["neff"].to_numpy(dtype=float))
        A=np.column_stack([np.ones(len(g)),yr])
        bn, *_=np.linalg.lstsq(A,ln,rcond=None)
        be, *_=np.linalg.lstsq(A,le,rcond=None)
        rn=ln-A@bn
        re=le-A@be
        denom=float(np.sum(rn**2))
        slope=float(np.sum(rn*re)/denom) if denom>0 else math.nan
        pred=slope*rn
        sst=float(np.sum(re**2))
        r2=float(1-np.sum((re-pred)**2)/sst) if sst>0 else math.nan
        per[str(pop)]={"slope":slope,"r2":r2}
        rows.append(pd.DataFrame({
            "population":str(pop),
            "rn":rn,
            "re":re,
            "row_weight":np.repeat(1.0/len(g),len(g)),
        }))
    z=pd.concat(rows,ignore_index=True)
    x=z["rn"].to_numpy(dtype=float)
    y=z["re"].to_numpy(dtype=float)
    w=z["row_weight"].to_numpy(dtype=float)
    denom=float(np.sum(w*x*x))
    slope=float(np.sum(w*x*y)/denom)
    pred=slope*x
    ym=float(np.average(y,weights=w))
    sst=float(np.sum(w*(y-ym)**2))
    r2=float(1-np.sum(w*(y-pred)**2)/sst) if sst>0 else math.nan
    return {"common_slope":slope,"common_r2":r2,"per_population":per}


def analyze(path: Path) -> dict[str, object]:
    raw=pd.read_csv(path)
    df=_prepare(raw)
    models=["M1","M2","M3_50","M3_25","M3_10"]
    fits={m:_fit_model(df,m) for m in models}
    loo={m:_loo(df,m) for m in models}

    ranked=sorted(models,key=lambda m:loo[m]["equal_weight_mean_population_rmse"])
    best=ranked[0]
    linear=loo["M1"]["equal_weight_mean_population_rmse"]
    best_rmse=loo[best]["equal_weight_mean_population_rmse"]
    improvement=float((linear-best_rmse)/linear) if linear>0 else math.nan

    accel={}
    b2=fits["M2"]["beta"]
    xmax=float(df["x"].max())
    accel["M2"]={
        "early_slope_at_x0":float(b2[0]),
        "quadratic_coefficient":float(b2[1]),
        "slope_at_max_observed_decline":float(b2[0]+2*b2[1]*xmax),
        "max_x":xmax,
    }
    for m,h in [("M3_50",math.log(2)),("M3_25",math.log(4)),("M3_10",math.log(10))]:
        b=fits[m]["beta"]
        accel[m]={
            "hinge_x":h,
            "early_slope":float(b[0]),
            "late_slope":float(b[0]+b[1]),
            "slope_change":float(b[1]),
        }

    candidate_acceleration=False
    if best=="M2":
        candidate_acceleration=accel["M2"]["slope_at_max_observed_decline"]>accel["M2"]["early_slope_at_x0"]
    elif best.startswith("M3_"):
        candidate_acceleration=accel[best]["late_slope"]>accel[best]["early_slope"]

    return {
        "schema_version":1,
        "analysis_id":"mina-contraction-scaling-shape-exploration-v1",
        "status":"stage2_posthoc_not_for_frozen_submission",
        "full_data_model_fits":fits,
        "leave_one_population_out":loo,
        "model_ranking_by_equal_weight_loo_rmse":ranked,
        "best_model":best,
        "best_vs_linear_relative_rmse_improvement":improvement,
        "acceleration_descriptors":accel,
        "candidate_acceleration_rule_supported_by_frozen_stage2_rule":bool(best!="M1" and candidate_acceleration),
        "detrended_abundance_neff_diagnostic":_detrended(df),
        "interpretation_boundary":[
            "All models are post-hoc exploratory and cannot alter the frozen Ecology Report.",
            "A nonlinear winner is a trajectory-shape candidate, not a causal tipping point.",
            "Detrended coupling is used only to assess whether the apparent scaling survives removal of linear time trends.",
            "Five population units are nested in two monitoring systems."
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
