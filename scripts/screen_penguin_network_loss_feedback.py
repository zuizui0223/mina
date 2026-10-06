#!/usr/bin/env python3
"""Exploratory loss-feedback screen in component-resolved penguin breeding networks."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss

from scripts.describe_concentration_dominance import (
    SIGNY_ADELIE_UNITS,
    SIGNY_CHINSTRAP_UNITS,
    SIGNY_YEARS,
    canonical_adelie,
    load_palmer,
    signy_panel,
)
from scripts.audit_signy_replication_support import read_official_zip

PALMER_ISLANDS=("COR","HUM","LIT")
FEATURES={
    "M0":["z_local_size","z_relative_time"],
    "Mmass":["z_local_size","z_relative_time","z_surrounding_mass"],
    "Mintegrity":["z_local_size","z_relative_time","z_network_integrity"],
    "Mboth":["z_local_size","z_relative_time","z_surrounding_mass","z_network_integrity"],
}


def palmer_panels(path:Path):
    rows=load_palmer(path)
    out={}
    for island in PALMER_ISLANDS:
        local=[r for r in rows if r["island"]==island]
        by_year=defaultdict(dict)
        for r in local:
            by_year[int(r["year"])][str(r["unit"])]=float(r["count"])
        years=sorted(by_year)
        rosters=[set(by_year[y]) for y in years]
        if not rosters or any(r!=rosters[0] for r in rosters[1:]):
            raise ValueError(f"{island}: unstable roster")
        units=sorted(rosters[0])
        mat=np.asarray([[by_year[y][u] for y in years] for u in units],float)
        out[f"ADPE_PALMER_{island}"]=(units,np.asarray(years,int),mat)
    return out


def rows_from_panel(pop,units,years,mat):
    total=mat.sum(axis=0)
    out=[]
    n_units=len(units)
    tmin,tmax=int(years[0]),int(years[-1])
    for ti in range(len(years)-1):
        if int(years[ti+1])-int(years[ti])!=1:
            continue
        rel=(int(years[ti])-tmin)/(tmax-tmin) if tmax>tmin else 0.0
        occupied=(mat[:,ti]>0)
        for ui,u in enumerate(units):
            x=float(mat[ui,ti]); nxt=float(mat[ui,ti+1])
            if x<=0:
                continue
            other_total=float(total[ti]-x)
            other_occ=int(np.sum(occupied)-1)
            out.append({
                "population":pop,
                "unit":str(u),
                "year":int(years[ti]),
                "loss_next":int(nxt==0),
                "local_size":math.log1p(x),
                "surrounding_mass":math.log1p(max(other_total,0.0)),
                "network_integrity":(
                    other_occ/(n_units-1) if n_units>1 else 0.0
                ),
                "relative_time":float(rel),
            })
    return out


def z_within_population(df,cols):
    x=df.copy()
    for c in cols:
        vals=[]
        for pop,g in x.groupby("population",sort=False):
            v=g[c].astype(float)
            sd=float(v.std(ddof=0))
            if not np.isfinite(sd) or sd<=0:
                z=np.zeros(len(g),float)
            else:
                z=(v-float(v.mean()))/sd
            vals.extend(zip(g.index,z))
        zser=pd.Series(index=x.index,dtype=float)
        for idx,val in vals:
            zser.loc[idx]=val
        x[f"z_{c}"]=zser
    return x


def fit_model(train,features):
    model=LogisticRegression(
        penalty="l2",C=1.0,solver="lbfgs",max_iter=2000,
        fit_intercept=True,class_weight=None,
    )
    model.fit(train[features],train["loss_next"].astype(int))
    return model


def eval_scope(df,label):
    if df["loss_next"].sum()<2 or df["loss_next"].nunique()<2:
        return {"scope":label,"estimable":False,"reason":"too_few_loss_events"}
    coefs={}
    pooled={}
    for name,features in FEATURES.items():
        model=fit_model(df,features)
        pooled[name]={
            "intercept":float(model.intercept_[0]),
            "coefficients":{
                f:float(v) for f,v in zip(features,model.coef_[0])
            }
        }

    pops=sorted(df["population"].unique())
    cv={}
    for name,features in FEATURES.items():
        ys=[]; ps=[]
        fold_rows=[]
        for hold in pops:
            train=df[df.population!=hold]
            test=df[df.population==hold]
            if train["loss_next"].nunique()<2 or len(test)==0:
                continue
            model=fit_model(train,features)
            pred=model.predict_proba(test[features])[:,1]
            ys.extend(test["loss_next"].astype(int).tolist())
            ps.extend(pred.tolist())
            fold_rows.append({
                "held_population":hold,
                "n":int(len(test)),
                "losses":int(test["loss_next"].sum()),
                "log_loss":float(log_loss(test["loss_next"],pred,labels=[0,1])),
                "brier":float(brier_score_loss(test["loss_next"],pred)),
            })
        if not ys:
            cv[name]={"estimable":False}
        else:
            cv[name]={
                "estimable":True,
                "n":int(len(ys)),
                "losses":int(sum(ys)),
                "mean_log_loss":float(log_loss(ys,ps,labels=[0,1])),
                "mean_brier":float(brier_score_loss(ys,ps)),
                "folds":fold_rows,
            }

    base=cv["M0"].get("mean_log_loss")
    for name in cv:
        if cv[name].get("estimable") and base is not None:
            cv[name]["log_loss_improvement_vs_M0"]=float(base-cv[name]["mean_log_loss"])
            cv[name]["brier_improvement_vs_M0"]=float(
                cv["M0"]["mean_brier"]-cv[name]["mean_brier"]
            )

    keycoef=pooled["Mintegrity"]["coefficients"]["z_network_integrity"]
    ll_imp=cv["Mintegrity"].get("log_loss_improvement_vs_M0")
    return {
        "scope":label,
        "estimable":True,
        "n_transitions":int(len(df)),
        "loss_events":int(df["loss_next"].sum()),
        "populations":pops,
        "pooled_models":pooled,
        "leave_one_population_out":cv,
        "generated_prediction":{
            "network_integrity_coefficient_negative":bool(keycoef<0),
            "integrity_improves_log_loss":bool(ll_imp is not None and ll_imp>0),
            "supported":bool(keycoef<0 and ll_imp is not None and ll_imp>0),
        }
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--palmer-census",required=True,type=Path)
    p.add_argument("--signy-adelie-zip",required=True,type=Path)
    p.add_argument("--signy-chinstrap-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()

    panels=palmer_panels(a.palmer_census)
    ad,_=read_official_zip(a.signy_adelie_zip)
    panels["ADPE_SIGNY"]=signy_panel(
        ad,units=SIGNY_ADELIE_UNITS,canonicalize=canonical_adelie
    )
    ch,_=read_official_zip(a.signy_chinstrap_zip)
    panels["CHPE_SIGNY"]=signy_panel(
        ch,units=SIGNY_CHINSTRAP_UNITS,canonicalize=None
    )

    rows=[]
    for pop,(units,years,mat) in panels.items():
        rows.extend(rows_from_panel(pop,units,years,mat))
    df=pd.DataFrame(rows)
    df=z_within_population(
        df,["local_size","surrounding_mass","network_integrity","relative_time"]
    )

    all_result=eval_scope(df,"all_five")
    palmer=df[df.population.str.contains("PALMER")].copy()
    palmer_result=eval_scope(palmer,"palmer_only")

    out={
        "schema_version":1,
        "analysis_id":"mina-penguin-network-loss-feedback-v1",
        "status":"exploratory_already_exposed_no_inferential_p_values",
        "transition_summary":{
            "n":int(len(df)),
            "loss_events":int(df.loss_next.sum()),
            "by_population":{
                pop:{
                    "n":int(len(g)),
                    "loss_events":int(g.loss_next.sum())
                }
                for pop,g in df.groupby("population",sort=True)
            }
        },
        "results":[all_result,palmer_result],
        "boundary":[
            "No low-count pseudo-absence threshold is used.",
            "No inferential p-values are reported.",
            "Network integrity is an observational state and does not identify causal rescue or social attraction.",
            "Exact-zero loss may reflect breeding absence, not necessarily mortality or permanent site abandonment."
        ]
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
