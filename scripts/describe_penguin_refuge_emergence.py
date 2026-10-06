#!/usr/bin/env python3
"""Describe when the eventual dominant breeding component emerges during decline."""
from __future__ import annotations
import argparse,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

from scripts.describe_concentration_dominance import (
    SIGNY_ADELIE_UNITS,SIGNY_CHINSTRAP_UNITS,
    canonical_adelie,load_palmer,signy_panel,
)
from scripts.audit_signy_replication_support import read_official_zip

PALMER_ISLANDS=("COR","HUM","LIT")

def palmer_panels(path):
    rows=load_palmer(path); out={}
    for island in PALMER_ISLANDS:
        by=defaultdict(dict)
        for r in rows:
            if r["island"]==island:
                by[int(r["year"])][str(r["unit"])]=float(r["count"])
        years=sorted(by); rosters=[set(by[y]) for y in years]
        if not rosters or any(r!=rosters[0] for r in rosters[1:]): raise ValueError(island)
        units=sorted(rosters[0])
        mat=np.asarray([[by[y][u] for y in years] for u in units],float)
        # For chronology stop at last positive population year.
        positive=[i for i in range(len(years)) if mat[:,i].sum()>0]
        out[f"ADPE_PALMER_{island}"]=(units,np.asarray([years[i] for i in positive],int),mat[:,positive])
    return out

def slope(x,y):
    x=np.asarray(x,float);y=np.asarray(y,float); xc=x-x.mean()
    return float(np.sum(xc*(y-y.mean()))/np.sum(xc*xc)) if np.sum(xc*xc)>0 else 0.0

def ranks_desc(v):
    return pd.Series(-np.asarray(v,float)).rank(method="min").astype(int).to_numpy()

def summarize(pop,units,years,mat):
    totals=mat.sum(axis=0)
    shares=mat/totals
    final_dom=int(np.argmax(shares[:,-1]))
    dom_each=np.argmax(shares,axis=0)
    first_ever=np.where(dom_each==final_dom)[0]
    first_ever_i=int(first_ever[0]) if len(first_ever) else None

    # Earliest year from which eventual final dominant remains dominant through endpoint.
    permanent_i=None
    for i in range(len(years)):
        if all(int(x)==final_dom for x in dom_each[i:]):
            permanent_i=i;break

    switches=int(np.sum(dom_each[1:]!=dom_each[:-1]))
    first_rank=ranks_desc(shares[:,0])

    k=min(5,len(years))
    early_slopes=np.asarray([
        slope(years[:k],np.log1p(mat[i,:k])) for i in range(len(units))
    ])
    slope_rank=ranks_desc(early_slopes)
    early_rho=float(pd.Series(early_slopes).rank().corr(pd.Series(shares[:,-1]).rank()))

    # First season in which final dominant's share exceeds its initial share by 50%,
    # reported only as a descriptive fixed multiplier, not used for inference.
    target=float(shares[final_dom,0]*1.5)
    idx=np.where(shares[final_dom]>=target)[0]
    share150_i=int(idx[0]) if len(idx) else None

    chronology=[]
    for t,y in enumerate(years):
        chronology.append({
            "year":int(y),
            "dominant_unit":str(units[int(dom_each[t])]),
            "final_dominant_count":float(mat[final_dom,t]),
            "final_dominant_share":float(shares[final_dom,t]),
            "final_dominant_rank":int(ranks_desc(shares[:,t])[final_dom]),
            "total":float(totals[t]),
        })

    return {
        "population":pop,
        "first_year":int(years[0]),
        "last_year":int(years[-1]),
        "n_seasons":int(len(years)),
        "n_components":int(len(units)),
        "final_dominant_unit":str(units[final_dom]),
        "final_dominant_initial_rank":int(first_rank[final_dom]),
        "final_dominant_early5_slope_rank":int(slope_rank[final_dom]),
        "final_dominant_early5_log1p_slope":float(early_slopes[final_dom]),
        "early5_slope_vs_final_share_spearman":early_rho,
        "dominant_identity_switches":switches,
        "first_ever_dominant_year":int(years[first_ever_i]) if first_ever_i is not None else None,
        "years_before_end_first_ever_dominant":int(years[-1]-years[first_ever_i]) if first_ever_i is not None else None,
        "permanent_dominance_year":int(years[permanent_i]) if permanent_i is not None else None,
        "years_before_end_permanent_dominance":int(years[-1]-years[permanent_i]) if permanent_i is not None else None,
        "year_share_reaches_1p5x_initial":int(years[share150_i]) if share150_i is not None else None,
        "chronology":chronology,
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
    results=[summarize(pop,*vals) for pop,vals in panels.items()]
    out={
      "schema_version":1,
      "analysis_id":"mina-penguin-refuge-emergence-chronology-v1",
      "status":"post_outcome_descriptive_only",
      "populations":results,
      "boundary":[
        "Final dominant identity is defined using the exposed endpoint and is therefore descriptive.",
        "Early five-season slopes are not confirmatory predictors.",
        "Dominance means relative share, not absolute population growth or habitat quality."
      ]
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__":main()
