#!/usr/bin/env python3
"""Final bounded post-hoc search for contraction/rebound asymmetry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _prepare(path: Path) -> pd.DataFrame:
    raw=pd.read_csv(path)
    rows=[]
    for pop,g in raw.groupby("population",sort=False):
        g=g.sort_values("year")
        ln=np.log(g["breeding_pairs"].to_numpy(dtype=float))
        le=np.log(g["neff"].to_numpy(dtype=float))
        years=g["year"].to_numpy(dtype=int)
        dN=np.diff(ln)
        dE=np.diff(le)
        n=len(dN)
        for i,(x,y) in enumerate(zip(dN,dE)):
            rows.append({
                "population":str(pop),
                "system":str(g.iloc[0]["system"]),
                "from_year":int(years[i]),
                "to_year":int(years[i+1]),
                "dlogN":float(x),
                "dlogE":float(y),
                "direction":"decline" if x<0 else "rebound" if x>0 else "zero",
                "row_weight":1.0/n if n>0 else 0.0,
            })
    return pd.DataFrame(rows)


def _fit_symmetric(df: pd.DataFrame) -> dict[str,float]:
    z=df[df["direction"]!="zero"]
    x=z["dlogN"].to_numpy(dtype=float)
    y=z["dlogE"].to_numpy(dtype=float)
    w=z["row_weight"].to_numpy(dtype=float)
    den=float(np.sum(w*x*x))
    k=float(np.sum(w*x*y)/den)
    pred=k*x
    rmse=float(np.sqrt(np.average((y-pred)**2,weights=w)))
    return {"k":k,"weighted_rmse":rmse}


def _fit_asymmetric(df: pd.DataFrame) -> dict[str,float]:
    z=df[df["direction"]!="zero"]
    out={}
    preds=np.empty(len(z),dtype=float)
    y=z["dlogE"].to_numpy(dtype=float)
    w=z["row_weight"].to_numpy(dtype=float)
    for direction,key in (("decline","k_down"),("rebound","k_up")):
        mask=(z["direction"].to_numpy()==direction)
        x=z.loc[mask,"dlogN"].to_numpy(dtype=float)
        yy=z.loc[mask,"dlogE"].to_numpy(dtype=float)
        ww=z.loc[mask,"row_weight"].to_numpy(dtype=float)
        den=float(np.sum(ww*x*x))
        k=float(np.sum(ww*x*yy)/den) if den>0 else float("nan")
        out[key]=k
        preds[mask]=k*x
    out["weighted_rmse"]=float(np.sqrt(np.average((y-preds)**2,weights=w)))
    return out


def _predict(test: pd.DataFrame, fit: dict[str,float], model: str) -> np.ndarray:
    z=test[test["direction"]!="zero"]
    x=z["dlogN"].to_numpy(dtype=float)
    if model=="symmetric":
        return fit["k"]*x
    dirs=z["direction"].to_numpy()
    return np.where(dirs=="decline",fit["k_down"]*x,fit["k_up"]*x)


def _loo(df: pd.DataFrame, model: str) -> dict[str,object]:
    per={}
    for pop in df["population"].drop_duplicates():
        train=df[df["population"]!=pop]
        test=df[df["population"]==pop]
        fit=_fit_symmetric(train) if model=="symmetric" else _fit_asymmetric(train)
        z=test[test["direction"]!="zero"]
        pred=_predict(test,fit,model)
        y=z["dlogE"].to_numpy(dtype=float)
        rmse=float(np.sqrt(np.mean((y-pred)**2)))
        per[str(pop)]={"rmse":rmse,"n_transitions":int(len(z)),"fit":fit}
    vals=[v["rmse"] for v in per.values()]
    return {
        "equal_weight_mean_population_rmse":float(np.mean(vals)),
        "median_population_rmse":float(np.median(vals)),
        "per_population":per,
    }


def analyze(path: Path) -> dict[str,object]:
    df=_prepare(path)
    sym=_fit_symmetric(df)
    asym=_fit_asymmetric(df)
    loo_sym=_loo(df,"symmetric")
    loo_asym=_loo(df,"asymmetric")

    nonzero=df[df["direction"]!="zero"]
    decline=nonzero[nonzero["direction"]=="decline"]
    rebound=nonzero[nonzero["direction"]=="rebound"]

    by_pop={}
    for pop,g in df.groupby("population",sort=False):
        d=g[g["direction"]=="decline"]
        r=g[g["direction"]=="rebound"]
        by_pop[str(pop)]={
            "decline_transitions":int(len(d)),
            "rebound_transitions":int(len(r)),
            "zero_dN_transitions":int(np.sum(g["direction"]=="zero")),
            "decline_sign_concordance":None if len(d)==0 else float(np.mean(d["dlogE"]<0)),
            "rebound_sign_concordance":None if len(r)==0 else float(np.mean(r["dlogE"]>0)),
        }

    rule=(
        loo_asym["equal_weight_mean_population_rmse"] < loo_sym["equal_weight_mean_population_rmse"]
        and asym["k_down"] > 0
        and asym["k_up"] >= 0
        and asym["k_down"] > asym["k_up"]
    )

    return {
        "schema_version":1,
        "analysis_id":"mina-contraction-ratchet-exploration-v1",
        "status":"stage5_posthoc_final_rule_search_not_for_frozen_submission",
        "full_data_fits":{
            "symmetric":sym,
            "asymmetric":asym,
        },
        "leave_one_population_out":{
            "symmetric":loo_sym,
            "asymmetric":loo_asym,
        },
        "transition_summary":{
            "decline_count":int(len(decline)),
            "rebound_count":int(len(rebound)),
            "zero_dN_count":int(np.sum(df["direction"]=="zero")),
            "decline_sign_concordance":float(np.mean(decline["dlogE"]<0)) if len(decline) else None,
            "rebound_sign_concordance":float(np.mean(rebound["dlogE"]>0)) if len(rebound) else None,
            "by_population":by_pop,
        },
        "candidate_ratchet_rule_supported_descriptively":bool(rule),
        "interpretation_boundary":[
            "Final bounded post-hoc rule search; no further lags, thresholds or nonlinear transition models are opened.",
            "No p-values or significance claims.",
            "A supported asymmetry is a trajectory hypothesis, not evidence of irreversible colony loss or individual memory.",
            "Nothing here modifies the frozen Ecology Report."
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
