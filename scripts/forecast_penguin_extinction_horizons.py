#!/usr/bin/env python3
"""Forecast exact-zero component loss over 1-, 3-, and 5-year horizons."""
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
HORIZONS=(1,3,5)

def palmer_panels(path:Path):
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

def rows_for_horizon(pop,units,years,mat,h):
    year_to_idx={int(y):i for i,y in enumerate(years)}
    y0,y1=int(years[0]),int(years[-1])
    rows=[]
    for ti,y in enumerate(years):
        y=int(y)
        future=[y+k for k in range(1,h+1)]
        if any(f not in year_to_idx for f in future):
            continue
        rel=(y-y0)/(y1-y0) if y1>y0 else 0.0
        prev_ok=(y-1 in year_to_idx)
        for ui,u in enumerate(units):
            cur=float(mat[ui,ti])
            if cur<=0: continue
            fut=np.asarray([mat[ui,year_to_idx[f]] for f in future],float)
            row={
                "population":pop,"unit":str(u),"year":y,
                "loss":int(np.any(fut==0)),
                "local_size":math.log1p(cur),
                "relative_time":float(rel),
                "recent_growth":None,
                "trend_eligible":bool(prev_ok),
            }
            if prev_ok:
                prev=float(mat[ui,year_to_idx[y-1]])
                row["recent_growth"]=math.log1p(cur)-math.log1p(max(prev,0.0))
            rows.append(row)
    return rows

def z_within(df,cols):
    x=df.copy()
    for c in cols:
        z=pd.Series(index=x.index,dtype=float)
        for pop,g in x.groupby("population",sort=False):
            v=g[c].astype(float)
            sd=float(v.std(ddof=0))
            z.loc[g.index]=0.0 if sd<=0 or not np.isfinite(sd) else (v-float(v.mean()))/sd
        x["z_"+c]=z
    return x

def fit(train,features):
    m=LogisticRegression(penalty="l2",C=1.0,solver="lbfgs",max_iter=2000)
    m.fit(train[features],train.loss.astype(int))
    return m

def ranking(pred_rows):
    d=pd.DataFrame(pred_rows)
    years=[]; percs=[]
    if d.empty:
        return {"event_years":0,"top1_hit_fraction":None,"top2_hit_fraction":None,"median_loss_percentile":None}
    for (pop,y),g in d.groupby(["population","year"],sort=True):
        if int(g.loss.sum())<=0: continue
        gg=g.sort_values("pred",ascending=False).reset_index(drop=True)
        lost=np.where(gg.loss.to_numpy(int)==1)[0]
        n=len(gg)
        ranks=(lost+1)
        ps=[1.0-(int(r)-1)/max(n-1,1) for r in ranks]
        percs.extend(ps)
        years.append({
            "population":str(pop),"year":int(y),"n_at_risk":int(n),
            "future_losses":int(len(lost)),
            "best_loss_rank":int(ranks.min()),
            "top1":bool(ranks.min()<=1),
            "top2":bool(ranks.min()<=2),
        })
    return {
        "event_years":len(years),
        "top1_hit_fraction":float(np.mean([r["top1"] for r in years])) if years else None,
        "top2_hit_fraction":float(np.mean([r["top2"] for r in years])) if years else None,
        "median_loss_percentile":float(np.median(percs)) if percs else None,
        "event_details":years,
    }

def evaluate(df,features):
    if df.loss.nunique()<2 or int(df.loss.sum())<2:
        return {"estimable":False,"n":int(len(df)),"losses":int(df.loss.sum())}
    pooled=fit(df,features)
    pops=sorted(df.population.unique())
    yy=[]; pp=[]; pred_rows=[]; folds=[]
    for hold in pops:
        tr=df[df.population!=hold]; te=df[df.population==hold]
        if len(te)==0 or tr.loss.nunique()<2: continue
        m=fit(tr,features)
        pred=m.predict_proba(te[features])[:,1]
        yy.extend(te.loss.astype(int).tolist()); pp.extend(pred.tolist())
        folds.append({
            "held_population":str(hold),"n":int(len(te)),"losses":int(te.loss.sum()),
            "log_loss":float(log_loss(te.loss,pred,labels=[0,1])),
            "brier":float(brier_score_loss(te.loss,pred)),
        })
        for (_,r),p0 in zip(te.iterrows(),pred):
            pred_rows.append({
                "population":str(r.population),"unit":str(r.unit),"year":int(r.year),
                "loss":int(r.loss),"pred":float(p0)
            })
    return {
        "estimable":True,
        "n":int(len(df)),"losses":int(df.loss.sum()),
        "pooled_coefficients":{f:float(v) for f,v in zip(features,pooled.coef_[0])},
        "held_population_log_loss":float(log_loss(yy,pp,labels=[0,1])),
        "held_population_brier":float(brier_score_loss(yy,pp)),
        "ranking":ranking(pred_rows),
        "folds":folds,
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

    results={}
    for h in HORIZONS:
        rows=[]
        for pop,(units,years,mat) in panels.items():
            rows.extend(rows_for_horizon(pop,units,years,mat,h))
        full=pd.DataFrame(rows)
        size=z_within(full,["local_size","relative_time"])
        size_res=evaluate(size,["z_local_size","z_relative_time"])

        trend=full[full.trend_eligible & full.recent_growth.notna()].copy()
        trend=z_within(trend,["local_size","relative_time","recent_growth"])
        # Fair comparison on the same trend-eligible rows.
        size_same=evaluate(trend,["z_local_size","z_relative_time"])
        trend_res=evaluate(trend,["z_local_size","z_relative_time","z_recent_growth"])
        if size_same.get("estimable") and trend_res.get("estimable"):
            trend_res["log_loss_improvement_vs_same_rows_Msize"]=float(
                size_same["held_population_log_loss"]-trend_res["held_population_log_loss"]
            )
            trend_res["brier_improvement_vs_same_rows_Msize"]=float(
                size_same["held_population_brier"]-trend_res["held_population_brier"]
            )
        results[str(h)]={
            "horizon_years":h,
            "Msize_all_eligible":size_res,
            "Msize_trend_eligible_rows":size_same,
            "Mtrend":trend_res,
        }

    out={
        "schema_version":1,
        "analysis_id":"mina-penguin-extinction-horizon-v1",
        "status":"exploratory_already_exposed_no_p_values",
        "results":results,
        "boundary":[
            "Multi-year outcomes overlap and are forecasting records, not independent inferential replicates.",
            "Exact census-unit zero is not necessarily physical habitat extinction.",
            "No low-count threshold, interaction, spline or alternate lag is searched."
        ]
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
