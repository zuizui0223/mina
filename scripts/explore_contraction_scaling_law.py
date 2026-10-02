#!/usr/bin/env python3
"""Post-hoc exploratory search for simple contraction scaling laws.

This script consumes the already source-checked trajectory table produced by
build_replicated_concentration_figure_data.py. It does not alter the frozen
Ecology Report or any confirmatory decision.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def _ols(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    x=np.asarray(x,dtype=float)
    y=np.asarray(y,dtype=float)
    xc=x-float(np.mean(x))
    yc=y-float(np.mean(y))
    denom=float(np.sum(xc**2))
    if denom<=0:
        return {"slope": math.nan, "intercept": math.nan, "r2": math.nan}
    slope=float(np.sum(xc*yc)/denom)
    intercept=float(np.mean(y)-slope*np.mean(x))
    fitted=intercept+slope*x
    sse=float(np.sum((y-fitted)**2))
    sst=float(np.sum((y-np.mean(y))**2))
    r2=float(1-sse/sst) if sst>0 else math.nan
    return {"slope":slope,"intercept":intercept,"r2":r2}


def _fixed_effect_slope(frame: pd.DataFrame) -> dict[str, float]:
    parts=[]
    for _,g in frame.groupby("population",sort=False):
        x=np.log(g["breeding_pairs"].to_numpy(dtype=float))
        y=np.log(g["neff"].to_numpy(dtype=float))
        parts.append(pd.DataFrame({
            "x":x-np.mean(x),
            "y":y-np.mean(y),
        }))
    z=pd.concat(parts,ignore_index=True)
    x=z["x"].to_numpy()
    y=z["y"].to_numpy()
    denom=float(np.sum(x**2))
    slope=float(np.sum(x*y)/denom)
    resid=y-slope*x
    sst=float(np.sum(y**2))
    return {
        "slope":slope,
        "r2_within":float(1-np.sum(resid**2)/sst) if sst>0 else math.nan,
        "n_rows":int(len(z)),
        "n_populations":int(frame["population"].nunique()),
    }


def _first_crossing(g: pd.DataFrame, col: str, threshold: float) -> dict[str, float | int] | None:
    hit=g[g[col] <= threshold]
    if hit.empty:
        return None
    row=hit.iloc[0]
    return {
        "year":int(row["year"]),
        "abundance_retained":float(row["abundance_retained"]),
        "neff_retained":float(row["neff_retained"]),
    }


def analyze(path: Path) -> dict[str, object]:
    df=pd.read_csv(path)
    required={"system","species","population","year","breeding_pairs","neff"}
    missing=required-set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if (df["breeding_pairs"]<=0).any() or (df["neff"]<=0).any():
        raise ValueError("all analyzed trajectory values must be positive")

    populations=[]
    for pop,g in df.groupby("population",sort=False):
        g=g.sort_values("year").copy()
        n=g["breeding_pairs"].to_numpy(dtype=float)
        e=g["neff"].to_numpy(dtype=float)
        years=g["year"].to_numpy(dtype=int)
        annual=_ols(np.log(n),np.log(e))
        endpoint=float(np.log(e[-1]/e[0])/np.log(n[-1]/n[0])) if n[-1]!=n[0] else math.nan
        nr=pd.Series(n).rank(method="average").to_numpy(dtype=float)\n        er=pd.Series(e).rank(method="average").to_numpy(dtype=float)\n        rho=float(np.corrcoef(nr,er)[0,1])

        dn=np.diff(np.log(n))
        de=np.diff(np.log(e))
        fd=_ols(dn,de) if len(dn)>=2 else {"slope":math.nan,"intercept":math.nan,"r2":math.nan}

        g["abundance_retained"]=g["breeding_pairs"]/float(n[0])
        g["neff_retained"]=g["neff"]/float(e[0])

        abundance_thresholds={
            str(int(100*t)): _first_crossing(g,"abundance_retained",t)
            for t in (0.50,0.25,0.10)
        }
        neff_thresholds={
            str(int(100*t)): _first_crossing(g,"neff_retained",t)
            for t in (0.75,0.50)
        }

        populations.append({
            "system":str(g.iloc[0]["system"]),
            "species":str(g.iloc[0]["species"]),
            "population":str(pop),
            "n_seasons":int(len(g)),
            "first_year":int(years[0]),
            "last_year":int(years[-1]),
            "first_total":float(n[0]),
            "last_total":float(n[-1]),
            "abundance_change_fraction":float(n[-1]/n[0]-1),
            "first_neff":float(e[0]),
            "last_neff":float(e[-1]),
            "neff_change_fraction":float(e[-1]/e[0]-1),
            "annual_loglog_elasticity":annual["slope"],
            "annual_loglog_r2":annual["r2"],
            "endpoint_elasticity":endpoint,
            "spearman_abundance_neff":rho,
            "first_difference_elasticity":fd["slope"],
            "first_difference_r2":fd["r2"],
            "abundance_threshold_crossings":abundance_thresholds,
            "neff_threshold_crossings":neff_thresholds,
        })

    all_fe=_fixed_effect_slope(df)
    by_system={
        system:_fixed_effect_slope(g)
        for system,g in df.groupby("system",sort=False)
    }

    loo={}
    pops=list(df["population"].drop_duplicates())
    for pop in pops:
        loo[pop]=_fixed_effect_slope(df[df["population"]!=pop])

    slopes=[float(p["annual_loglog_elasticity"]) for p in populations]
    universal_sublinear=all(0<s<1 for s in slopes)

    fd_parts=[]
    for _,g in df.groupby("population",sort=False):
        g=g.sort_values("year")
        fd_parts.append(pd.DataFrame({
            "population":g["population"].iloc[0],
            "dlog_n":np.diff(np.log(g["breeding_pairs"].to_numpy(dtype=float))),
            "dlog_e":np.diff(np.log(g["neff"].to_numpy(dtype=float))),
        }))
    fd_all=pd.concat(fd_parts,ignore_index=True)
    fd_fe_parts=[]
    for _,g in fd_all.groupby("population",sort=False):
        x=g["dlog_n"].to_numpy(dtype=float)
        y=g["dlog_e"].to_numpy(dtype=float)
        fd_fe_parts.append(pd.DataFrame({"x":x-np.mean(x),"y":y-np.mean(y)}))
    z=pd.concat(fd_fe_parts,ignore_index=True)
    fd_common=float(np.sum(z["x"]*z["y"])/np.sum(z["x"]**2))
    fd_r2=float(1-np.sum((z["y"]-fd_common*z["x"])**2)/np.sum(z["y"]**2))

    return {
        "schema_version":1,
        "analysis_id":"mina-contraction-scaling-law-exploration-v1",
        "status":"posthoc_exploratory_not_for_frozen_ecology_submission",
        "population_results":populations,
        "common_fixed_effect_elasticity":all_fe,
        "system_fixed_effect_elasticities":by_system,
        "leave_one_population_out_common_elasticity":loo,
        "first_difference_common_elasticity":{
            "slope":fd_common,
            "r2_within":fd_r2,
            "n_transitions":int(len(z)),
        },
        "bounded_rule_checks":{
            "all_five_annual_loglog_slopes_between_zero_and_one":bool(universal_sublinear),
            "min_population_elasticity":float(min(slopes)),
            "max_population_elasticity":float(max(slopes)),
        },
        "interpretation_boundary":[
            "This is a post-hoc exploratory analysis of the same five trajectories and cannot modify the frozen Ecology Report.",
            "Annual log-log elasticity is a trajectory scaling descriptor, not a causal response coefficient.",
            "The first-difference diagnostic distinguishes long-term co-trending from short-term co-movement.",
            "Palmer-versus-Signy slope differences are descriptive because there are only two monitoring systems.",
            "Threshold crossings are descriptive and do not establish a tipping point."
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
