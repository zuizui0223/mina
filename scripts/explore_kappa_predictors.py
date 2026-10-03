#!/usr/bin/env python3
"""Stage-three post-hoc exploration of predictors of contraction elasticity."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from mina.hierarchical_variability import colony_roster_audit
from mina.lter import load_colony_rows


PALMER_MAP = {
    "Cormorant": "COR",
    "Humble": "HUM",
    "Litchfield": "LIT",
}


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    xr=pd.Series(x).rank(method="average").to_numpy(dtype=float)
    yr=pd.Series(y).rank(method="average").to_numpy(dtype=float)
    return float(np.corrcoef(xr,yr)[0,1])


def _fit_predict(train_x,train_y,test_x):
    X=np.column_stack([np.ones(len(train_x)),np.asarray(train_x,dtype=float)])
    y=np.asarray(train_y,dtype=float)
    beta,*_=np.linalg.lstsq(X,y,rcond=None)
    return float(beta[0]+beta[1]*float(test_x)), [float(v) for v in beta]


def analyze(stage1_path: Path,palmer_census: Path,ad_path: Path,ch_path: Path):
    stage1=_read(stage1_path)
    ad=_read(ad_path)
    ch=_read(ch_path)

    audit=colony_roster_audit(load_colony_rows(palmer_census))
    component_counts={
        "Cormorant":int(audit["COR"]["intersection_code_count"]),
        "Humble":int(audit["HUM"]["intersection_code_count"]),
        "Litchfield":int(audit["LIT"]["intersection_code_count"]),
        "Signy Adelie":len(ad["primary_roster"]),
        "Signy chinstrap":len(ch["primary_roster"]),
    }

    rows=[]
    for rec in stage1["population_results"]:
        pop=rec["population"]
        e0=float(rec["first_neff"])
        n0=float(rec["first_total"])
        n1=float(rec["last_total"])
        j=component_counts[pop]
        rows.append({
            "population":pop,
            "system":rec["system"],
            "kappa":float(rec["annual_loglog_elasticity"]),
            "initial_neff":e0,
            "component_count":j,
            "initial_evenness":e0/j,
            "decline_depth":float(-math.log(n1/n0)),
        })
    df=pd.DataFrame(rows)

    predictors=["initial_neff","component_count","initial_evenness","decline_depth"]
    kappas=df["kappa"].to_numpy(dtype=float)

    baseline_errors=[]
    for i in range(len(df)):
        train=np.delete(kappas,i)
        pred=float(np.mean(train))
        baseline_errors.append((kappas[i]-pred)**2)
    baseline_rmse=float(np.sqrt(np.mean(baseline_errors)))

    results={}
    for p in predictors:
        x=df[p].to_numpy(dtype=float)
        errors=[]
        predictions=[]
        betas=[]
        for i in range(len(df)):
            mask=np.arange(len(df))!=i
            pred,beta=_fit_predict(x[mask],kappas[mask],x[i])
            errors.append((kappas[i]-pred)**2)
            predictions.append({
                "held_out_population":str(df.iloc[i]["population"]),
                "observed_kappa":float(kappas[i]),
                "predicted_kappa":pred,
            })
            betas.append(beta)
        rmse=float(np.sqrt(np.mean(errors)))
        results[p]={
            "spearman_rho":_spearman(x,kappas),
            "loo_rmse":rmse,
            "relative_rmse_vs_intercept_only":float(rmse/baseline_rmse),
            "improves_over_intercept_only":bool(rmse<baseline_rmse),
            "loo_predictions":predictions,
        }

    ranking=sorted(predictors,key=lambda p:results[p]["loo_rmse"])

    return {
        "schema_version":1,
        "analysis_id":"mina-kappa-predictor-exploration-v1",
        "status":"stage3_posthoc_not_for_frozen_submission",
        "population_table":rows,
        "intercept_only_loo_rmse":baseline_rmse,
        "predictor_results":results,
        "ranking_by_loo_rmse":ranking,
        "promising_predictors":[p for p in ranking if results[p]["improves_over_intercept_only"]],
        "interpretation_boundary":[
            "There are only five population units nested within two monitoring systems.",
            "No p-values or significance claims are made.",
            "Any predictor that improves LOO RMSE is only a hypothesis for independent testing.",
            "These results cannot modify the frozen Ecology Report."
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage1",required=True,type=Path)
    p.add_argument("--palmer-census",required=True,type=Path)
    p.add_argument("--signy-adelie-receipt",required=True,type=Path)
    p.add_argument("--signy-chinstrap-receipt",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=analyze(a.stage1,a.palmer_census,a.signy_adelie_receipt,a.signy_chinstrap_receipt)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
