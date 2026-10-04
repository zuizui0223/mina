#!/usr/bin/env python3
"""Interannual fixed-node aliasing from semantically validated Zenodo annual anchors."""
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
    req={"colony","season","point_lon","point_lat","earliest_route_date"}
    missing=req-set(df.columns)
    if missing:
        raise ValueError(f"missing annual-anchor fields: {sorted(missing)}")
    x=df.copy()
    x["point_lon"]=pd.to_numeric(x["point_lon"],errors="raise")
    x["point_lat"]=pd.to_numeric(x["point_lat"],errors="raise")
    x["earliest_route_date"]=pd.to_datetime(x["earliest_route_date"],errors="raise")
    rows=[]
    for _,r in x.iterrows():
        xx,yy=TR.transform(float(r["point_lon"]),float(r["point_lat"]))
        rows.append({
          "colony_id":str(r["colony"]),
          "season":str(r["season"]),
          "season_start":season_start(r["season"]),
          "anchor_date":r["earliest_route_date"].date().isoformat(),
          "x3031":float(xx),"y3031":float(yy)
        })
    out=pd.DataFrame(rows).sort_values(["colony_id","season_start"]).reset_index(drop=True)
    if out.duplicated(["colony_id","season"]).any():
        raise ValueError("annual-anchor input contains duplicate colony-season rows")
    return out

def transitions(anchors:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for colony,g in anchors.groupby("colony_id"):
        vals=list(g.sort_values("season_start").to_dict("records"))
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
    if len(t)==0:
        raise ValueError("no consecutive interannual transitions")
    curve={}
    for r in radii:
        mask=t["displacement_km"]>float(r)
        curve[str(r)]={"false_turnover_n":int(mask.sum()),"transition_n":int(len(t)),
                       "false_turnover_fraction":float(mask.mean())}
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
    return curve,by,qs,t.loc[imax].to_dict()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--semantic-json",required=True,type=Path)
    p.add_argument("--annual-anchors-csv",required=True,type=Path)
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-anchors-csv",required=True,type=Path)
    p.add_argument("--out-transitions-csv",required=True,type=Path)
    a=p.parse_args()
    sem=json.loads(a.semantic_json.read_text())
    if not sem.get("decision",{}).get("annual_anchor_semantic_gate_passed"):
        raise SystemExit("annual-anchor semantic gate not passed")
    c=json.loads(a.contract.read_text())
    anchors=build_anchors(pd.read_csv(a.annual_anchors_csv))
    expected=int(c["input_rule"]["expected_seasons_per_colony"])
    support=anchors.groupby("colony_id")["season"].nunique().to_dict()
    if set(support)!={"Astrid","Mertz","SANAE"} or any(int(v)!=expected for v in support.values()):
        raise SystemExit(f"anchor support drift: {support}")
    t=transitions(anchors)
    curve,by,qs,maxrow=summarize(t,c["radii_km"])
    out={
      "schema_version":1,"analysis_id":"mina-paper3-zenodo-interannual-aliasing-v1",
      "support":{"annual_anchors":int(len(anchors)),"transitions":int(len(t)),
                 "seasons_by_colony":{k:int(v) for k,v in support.items()}},
      "aliasing_curve":curve,"by_colony":by,"identity_preserving_radii_km":qs,
      "maximum_transition":maxrow,
      "semantic_provenance":{
        "annual_anchor_contract":"mina-paper3-zenodo-annual-anchor-semantic-v1",
        "failed_route_endpoint_origin_match_used_for_selection":False
      },
      "boundary":c["boundaries"]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    anchors.to_csv(a.out_anchors_csv,index=False); t.to_csv(a.out_transitions_csv,index=False)
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
