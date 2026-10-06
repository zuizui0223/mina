#!/usr/bin/env python3
"""Forecast exact-zero loss of penguin breeding components from local state."""
from __future__ import annotations
import argparse, json, math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss

from scripts.describe_concentration_dominance import (
    SIGNY_ADELIE_UNITS, SIGNY_CHINSTRAP_UNITS,
    canonical_adelie, load_palmer, signy_panel,
)
from scripts.audit_signy_replication_support import read_official_zip

PALMER_ISLANDS=("COR","HUM","LIT")
MODELS={
    "Msize":["z_local_size","z_relative_time"],
    "Mtrend":["z_local_size","z_relative_time","z_recent_growth"],
    "Mshare":["z_local_size","z_relative_time","z_local_share"],
    "Mstate":["z_local_size","z_relative_time","z_recent_growth","z_local_share"],
}

def palmer_panels(path):
    rows=load_palmer(path); out={}
    for island in PALMER_ISLANDS:
        by=defaultdict(dict)
        for r in rows:
            if r["island"]==island:
                by[int(r["year"])][str(r["unit"])]=float(r["count"])
        years=sorted(by)
        rosters=[set(by[y]) for y in years]
        if not rosters or any(r!=rosters[0] for r in rosters[1:]):
            raise ValueError(f"{island}: unstable roster")
        units=sorted(rosters[0])
        mat=np.asarray([[by[y][u] for y in years] for u in units],float)
        out[f"ADPE_PALMER_{island}"]=(units,np.asarray(years,int),mat)
    return out

def make_rows(pop,units,years,mat):
    total=mat.sum(axis=0)
    y0,y1=int(years[0]),int(years[-1])
    rows=[]
    for ti in range(1,len(years)-1):
        if int(years[ti])-int(years[ti-1])!=1 or int(years[ti+1])-int(years[ti])!=1:
            continue
        rel=(int(years[ti])-y0)/(y1-y0) if y1>y0 else 0.
        for ui,u in enumerate(units):
            prev=float(mat[ui,ti-1]); cur=float(mat[ui,ti]); nxt=float(mat[ui,ti+1])
            if cur<=0:
                continue
            rows.append({
                "population":pop,"unit":str(u),"year":int(years[ti]),
                "loss_next":int(nxt==0),
                "local_size":math.log1p(cur),
                "recent_growth":math.log1p(cur)-math.log1p(max(prev,0.0)),
                "local_share":float(cur/total[ti]) if total[ti]>0 else 0.0,
                "relative_time":float(rel),
            })
    return rows

def z_within(df,cols):
    x=df.copy()
    for c in cols:
        out=pd.Series(index=x.index,dtype=float)
        for pop,g in x.groupby("population",sort=False):
            v=g[c].astype(float); sd=float(v.std(ddof=0))
            out.loc[g.index]=0.0 if sd<=0 or not np.isfinite(sd) else (v-float(v.mean()))/sd
        x["z_"+c]=out
    return x

def fit(train,features):
    m=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",max_iter=2000)
    m.fit(train[features],train.loss_next.astype(int))
    return m

def ranking_metrics(pred_rows):
    d=pd.DataFrame(pred_rows)
    event_years=[]
    loss_percentiles=[]
    for (pop,year),g in d.groupby(["population","year"],sort=True):
        if int(g.loss_next.sum())<=0:
            continue
        gg=g.sort_values("pred",ascending=False).reset_index(drop=True)
        lost=np.where(gg.loss_next.to_numpy(int)==1)[0]
        n=len(gg)
        ranks=(lost+1).tolist()
        # 1.0 means highest predicted risk; 0 means lowest.
        percs=[1.0-(r-1)/max(n-1,1) for r in ranks]
        loss_percentiles.extend(percs)
        event_years.append({
            "population":pop,"year":int(year),"n_at_risk":int(n),
            "n_losses":int(len(lost)),
            "best_loss_rank":int(min(ranks)),
            "top1_hit":bool(min(ranks)<=1),
            "top2_hit":bool(min(ranks)<=2),
        })
    return {
        "event_years":int(len(event_years)),
        "top1_hit_fraction":float(np.mean([x["top1_hit"] for x in event_years])) if event_years else None,
        "top2_hit_fraction":float(np.mean([x["top2_hit"] for x in event_years])) if event_years else None,
        "median_loss_percentile":float(np.median(loss_percentiles)) if loss_percentiles else None,
        "event_details":event_years,
    }

def evaluate(df,label):
    if df.loss_next.sum()<2 or df.loss_next.nunique()<2:
        return {"scope":label,"estimable":False}
    pooled={}
    for name,features in MODELS.items():
        m=fit(df,features)
        pooled[name]={
            "intercept":float(m.intercept_[0]),
            "coefficients":{f:float(v) for f,v in zip(features,m.coef_[0])}
        }

    pops=sorted(df.population.unique())
    cv={}
    for name,features in MODELS.items():
        all_y=[]; all_p=[]; pred_rows=[]
        folds=[]
        for hold in pops:
            tr=df[df.population!=hold]; te=df[df.population==hold]
            if tr.loss_next.nunique()<2 or len(te)==0: continue
            m=fit(tr,features); pred=m.predict_proba(te[features])[:,1]
            all_y.extend(te.loss_next.astype(int)); all_p.extend(pred)
            for (_,r),pr in zip(te.iterrows(),pred):
                pred_rows.append({
                    "population":r.population,"unit":r.unit,"year":int(r.year),
                    "loss_next":int(r.loss_next),"pred":float(pr)
                })
            folds.append({
                "held_population":hold,"n":int(len(te)),"losses":int(te.loss_next.sum()),
                "log_loss":float(log_loss(te.loss_next,pred,labels=[0,1])),
                "brier":float(brier_score_loss(te.loss_next,pred))
            })
        cv[name]={
            "n":int(len(all_y)),"losses":int(sum(all_y)),
            "log_loss":float(log_loss(all_y,all_p,labels=[0,1])),
            "brier":float(brier_score_loss(all_y,all_p)),
            "ranking":ranking_metrics(pred_rows),
            "folds":folds,
        }
    base=cv["Msize"]
    for name in cv:
        cv[name]["log_loss_improvement_vs_Msize"]=float(base["log_loss"]-cv[name]["log_loss"])
        cv[name]["brier_improvement_vs_Msize"]=float(base["brier"]-cv[name]["brier"])

    beta=pooled["Mtrend"]["coefficients"]["z_recent_growth"]
    supported=bool(
        beta<0
        and cv["Mtrend"]["log_loss_improvement_vs_Msize"]>0
        and cv["Mtrend"]["ranking"]["top1_hit_fraction"]>=cv["Msize"]["ranking"]["top1_hit_fraction"]
    )
    return {
        "scope":label,"estimable":True,
        "n":int(len(df)),"losses":int(df.loss_next.sum()),
        "pooled_models":pooled,
        "leave_one_population_out":cv,
        "generated_prediction":{
            "recent_growth_coefficient_negative":bool(beta<0),
            "Mtrend_improves_log_loss":bool(cv["Mtrend"]["log_loss_improvement_vs_Msize"]>0),
            "Mtrend_top1_not_worse":bool(cv["Mtrend"]["ranking"]["top1_hit_fraction"]>=cv["Msize"]["ranking"]["top1_hit_fraction"]),
            "supported":supported,
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
    panels["ADPE_SIGNY"]=signy_panel(ad,units=SIGNY_ADELIE_UNITS,canonicalize=canonical_adelie)
    ch,_=read_official_zip(a.signy_chinstrap_zip)
    panels["CHPE_SIGNY"]=signy_panel(ch,units=SIGNY_CHINSTRAP_UNITS,canonicalize=None)

    rows=[]
    for pop,(units,years,mat) in panels.items():
        rows.extend(make_rows(pop,units,years,mat))
    df=z_within(pd.DataFrame(rows),["local_size","recent_growth","local_share","relative_time"])

    out={
        "schema_version":1,
        "analysis_id":"mina-penguin-patch-extinction-forecast-v1",
        "status":"exploratory_already_exposed_no_inferential_p_values",
        "transition_summary":{
            "n":int(len(df)),"losses":int(df.loss_next.sum()),
            "by_population":{
                pop:{"n":int(len(g)),"losses":int(g.loss_next.sum())}
                for pop,g in df.groupby("population",sort=True)
            }
        },
        "results":[
            evaluate(df,"all_five"),
            evaluate(df[df.population.str.contains("PALMER")].copy(),"palmer_only"),
        ],
        "boundary":[
            "No low-count pseudo-absence threshold is used.",
            "No inferential p-values are reported.",
            "Operational census-component loss is not equivalent to physical habitat destruction.",
            "Recent decline can arise from movement, survival, recruitment or breeding participation."
        ]
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
