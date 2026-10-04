#!/usr/bin/env python3
"""Interannual fixed-node aliasing from validated Zenodo season-reference coordinates."""
from __future__ import annotations

import argparse, json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer

TR=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)

def season_start(s:str)->int:
    return int(str(s).split("-")[0])

def build_anchors(df:pd.DataFrame)->pd.DataFrame:
    required={"colony","season","reference_lon","reference_lat","reference_invariant"}
    missing=required-set(df.columns)
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    x=df.copy()
    x=x[x["reference_invariant"].astype(str).str.lower().isin(["true","1"])].copy()
    x["season_start"]=x["season"].astype(str).map(season_start)
    x["reference_lon"]=pd.to_numeric(x["reference_lon"],errors="raise").astype(float)
    x["reference_lat"]=pd.to_numeric(x["reference_lat"],errors="raise").astype(float)
    xx,yy=TR.transform(x["reference_lon"].to_numpy(),x["reference_lat"].to_numpy())
    x["x3031"]=np.asarray(xx,float); x["y3031"]=np.asarray(yy,float)
    out=x.rename(columns={"colony":"colony_id"})[
        ["colony_id","season","season_start","reference_lon","reference_lat","x3031","y3031"]
    ].sort_values(["colony_id","season_start"]).reset_index(drop=True)
    if out.duplicated(["colony_id","season"]).any():
        raise ValueError("duplicate colony-season anchors")
    return out

def transitions(anchors:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for colony,g in anchors.groupby("colony_id",sort=True):
        g=g.sort_values("season_start").reset_index(drop=True)
        for i in range(1,len(g)):
            a=g.iloc[i-1]; b=g.iloc[i]
            gap=int(b.season_start)-int(a.season_start)
            d=float(np.hypot(float(b.x3031)-float(a.x3031),float(b.y3031)-float(a.y3031))/1000.0)
            rows.append({
                "colony_id":str(colony),
                "from_season":str(a.season),
                "to_season":str(b.season),
                "season_gap":gap,
                "consecutive":bool(gap==1),
                "displacement_km":d
            })
    return pd.DataFrame(rows)

def quantiles(values):
    v=np.asarray(list(values),float)
    v=v[np.isfinite(v)]
    if len(v)==0:
        return {"q50":None,"q90":None,"q95":None}
    return {f"q{int(q*100)}":float(np.quantile(v,q)) for q in (0.5,0.9,0.95)}

def summarize(anchors:pd.DataFrame,trans:pd.DataFrame,radii):
    consec=trans[trans["consecutive"]].copy()
    curve={}
    for r in radii:
        m=consec["displacement_km"]>float(r)
        key=str(r).rstrip("0").rstrip(".")
        curve[key]={
            "false_turnover_n":int(m.sum()),
            "transition_n":int(len(consec)),
            "false_turnover_fraction":float(m.mean()) if len(consec) else None
        }
    by=[]
    for colony,g in consec.groupby("colony_id",sort=True):
        item={
            "colony_id":str(colony),
            "transitions":int(len(g)),
            **{f"displacement_{k}_km":v for k,v in quantiles(g["displacement_km"]).items()},
            "max_displacement_km":float(g["displacement_km"].max())
        }
        for r in radii:
            key=str(r).rstrip("0").rstrip(".")
            item[f"false_turnover_fraction_{key}km"]=float((g["displacement_km"]>float(r)).mean())
        by.append(item)
    maxrow=None
    if len(consec):
        row=consec.loc[consec["displacement_km"].idxmax()]
        maxrow={
            "colony_id":str(row.colony_id),
            "from_season":str(row.from_season),
            "to_season":str(row.to_season),
            "displacement_km":float(row.displacement_km)
        }
    return {
        "support":{
            "colonies":int(anchors["colony_id"].nunique()),
            "annual_anchors":int(len(anchors)),
            "consecutive_transitions":int(len(consec)),
            "seasons_by_colony":{
                str(k):int(v) for k,v in anchors.groupby("colony_id")["season"].nunique().to_dict().items()
            }
        },
        "aliasing_curve":curve,
        "identity_preserving_radii_km":quantiles(consec["displacement_km"]),
        "by_colony":by,
        "maximum_transition":maxrow
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--semantic-json",required=True,type=Path)
    p.add_argument("--seasons-csv",required=True,type=Path)
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-anchors-csv",required=True,type=Path)
    p.add_argument("--out-transitions-csv",required=True,type=Path)
    a=p.parse_args()
    sem=json.loads(a.semantic_json.read_text())
    if not sem.get("decision",{}).get("semantic_gate_passed"):
        raise SystemExit("semantic V2 gate not passed")
    c=json.loads(a.contract.read_text())
    anchors=build_anchors(pd.read_csv(a.seasons_csv))
    expected=set(c["input_rule"]["expected_colonies"])
    support=anchors.groupby("colony_id")["season"].nunique().to_dict()
    if set(support)!=expected:
        raise SystemExit(f"colony support drift: {support}")
    if any(int(v)<int(c["support_gate"]["minimum_seasons_per_colony"]) for v in support.values()):
        raise SystemExit(f"season support drift: {support}")
    trans=transitions(anchors)
    result=summarize(anchors,trans,c["radii_km"])
    if result["support"]["consecutive_transitions"]<int(c["support_gate"]["minimum_consecutive_transitions_total"]):
        raise SystemExit(f"transition support drift: {result['support']}")
    out={
        "schema_version":2,
        "analysis_id":"mina-paper3-zenodo-interannual-aliasing-v2",
        **result,
        "boundary":c["boundaries"]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    anchors.to_csv(a.out_anchors_csv,index=False)
    trans.to_csv(a.out_transitions_csv,index=False)
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
