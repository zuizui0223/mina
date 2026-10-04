#!/usr/bin/env python3
"""Interannual fixed-node aliasing for the Zenodo emperor-penguin route-origin series."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer

TR=Transformer.from_crs(4326,3031,always_xy=True)

def season_start(s:str)->int:
    return int(str(s).split("-")[0])

def build_anchors(df:pd.DataFrame)->pd.DataFrame:
    x=df.copy()
    x=x[x["origin_match"].astype(str).str.lower().isin(["true","1"])].copy()
    x=x[x["date"].notna()].copy()
    x["date"]=pd.to_datetime(x["date"])
    xx=[]; yy=[]
    for lon,lat in zip(x["point_lon"],x["point_lat"]):
        a,b=TR.transform(float(lon),float(lat)); xx.append(a); yy.append(b)
    x["x3031"]=xx; x["y3031"]=yy
    rows=[]
    for (colony,season),g in x.groupby(["colony","season"]):
        d0=g["date"].min()
        h=g[g["date"].eq(d0)]
        rows.append({
          "colony_id":str(colony),"season":str(season),"season_start":season_start(season),
          "anchor_date":d0.date().isoformat(),"n_points_anchor_date":int(len(h)),
          "x3031":float(h["x3031"].mean()),"y3031":float(h["y3031"].mean())
        })
    return pd.DataFrame(rows).sort_values(["colony_id","season_start"]).reset_index(drop=True)

def transitions(anchors:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for colony,g in anchors.groupby("colony_id"):
        g=g.sort_values("season_start")
        vals=list(g.to_dict("records"))
        for a,b in zip(vals[:-1],vals[1:]):
            if int(b["season_start"])-int(a["season_start"])!=1:
                continue
            d=float(np.hypot(b["x3031"]-a["x3031"],b["y3031"]-a["y3031"]))/1000.0
            rows.append({
              "colony_id":colony,"from_season":a["season"],"to_season":b["season"],
              "from_date":a["anchor_date"],"to_date":b["anchor_date"],
              "displacement_km":d
            })
    return pd.DataFrame(rows)

def summarize(t:pd.DataFrame,radii):
    curve={}
    for r in radii:
        mask=t["displacement_km"]>float(r)
        curve[str(r)]={"false_turnover_n":int(mask.sum()),"transition_n":int(len(t)),
                       "false_turnover_fraction":float(mask.mean()) if len(t) else None}
    by=[]
    for colony,g in t.groupby("colony_id"):
        item={"colony_id":colony,"transitions":int(len(g)),
              "q50_km":float(g["displacement_km"].quantile(.5)),
              "q90_km":float(g["displacement_km"].quantile(.9)),
              "q95_km":float(g["displacement_km"].quantile(.95)),
              "max_km":float(g["displacement_km"].max())}
        for r in radii:
            item[f"false_turnover_fraction_{r}km"]=float((g["displacement_km"]>float(r)).mean())
        by.append(item)
    qs={f"q{int(q*100)}":float(t["displacement_km"].quantile(q)) for q in (.5,.9,.95)}
    imax=t["displacement_km"].idxmax()
    maxrow=t.loc[imax].to_dict() if len(t) else None
    return curve,by,qs,maxrow

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--semantic-json",required=True,type=Path)
    p.add_argument("--points-csv",required=True,type=Path)
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-anchors-csv",required=True,type=Path)
    p.add_argument("--out-transitions-csv",required=True,type=Path)
    a=p.parse_args()
    sem=json.loads(a.semantic_json.read_text())
    if not sem.get("decision",{}).get("annual_anchor_semantic_gate_passed"):
        raise SystemExit("annual-anchor semantic gate not passed")
    c=json.loads(a.contract.read_text())
    pts=pd.read_csv(a.points_csv)
    anchors=build_anchors(pts)
    expected=int(c["input_rule"]["expected_seasons_per_colony"])
    support=anchors.groupby("colony_id")["season"].nunique().to_dict()
    if set(support)!={"Astrid","Mertz","SANAE"} or any(int(v)<expected for v in support.values()):
        raise SystemExit(f"anchor support drift: {support}")
    t=transitions(anchors)
    curve,by,qs,maxrow=summarize(t,c["radii_km"])
    out={
      "schema_version":1,"analysis_id":"mina-paper3-zenodo-interannual-aliasing-v1",
      "support":{"annual_anchors":int(len(anchors)),"transitions":int(len(t)),
                 "seasons_by_colony":{k:int(v) for k,v in support.items()}},
      "aliasing_curve":curve,"by_colony":by,"identity_preserving_radii_km":qs,
      "maximum_transition":maxrow,
      "boundary":c["boundaries"]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    anchors.to_csv(a.out_anchors_csv,index=False); t.to_csv(a.out_transitions_csv,index=False)
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
