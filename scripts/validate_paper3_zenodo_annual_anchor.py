#!/usr/bin/env python3
"""Validate season-level annual-anchor semantics without computing movement."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

def validate(df:pd.DataFrame, contract:dict)->dict:
    req={"colony","season","date","point_lon","point_lat"}
    missing=req-set(df.columns)
    if missing: raise ValueError(f"missing fields: {sorted(missing)}")
    x=df.copy()
    d=pd.to_datetime(x["date"],errors="coerce")
    finite=np.isfinite(pd.to_numeric(x["point_lon"],errors="coerce")) & np.isfinite(pd.to_numeric(x["point_lat"],errors="coerce"))
    x["lon8"]=pd.to_numeric(x["point_lon"],errors="coerce").round(8)
    x["lat8"]=pd.to_numeric(x["point_lat"],errors="coerce").round(8)
    groups=[]
    for (colony,season),g in x.groupby(["colony","season"]):
        pairs=set(zip(g["lon8"],g["lat8"]))
        groups.append({"colony":str(colony),"season":str(season),"rows":int(len(g)),"unique_anchor_pairs":int(len(pairs))})
    gd=pd.DataFrame(groups)
    expected=set(contract["validation"]["required_colonies"])
    seasons=gd.groupby("colony")["season"].nunique().to_dict()
    constancy=float((gd["unique_anchor_pairs"]==1).mean()) if len(gd) else 0.0
    date_frac=float(d.notna().mean()) if len(x) else 0.0
    finite_frac=float(finite.mean()) if len(x) else 0.0
    passed=bool(
      set(seasons)==expected and
      len(gd)==int(contract["validation"]["required_total_colony_seasons"]) and
      all(int(seasons.get(c,0))>=int(contract["validation"]["required_seasons_per_colony"]) for c in expected) and
      constancy>=float(contract["validation"]["required_constancy_fraction"]) and
      date_frac>=float(contract["validation"]["date_parse_required"]) and
      finite_frac>=float(contract["validation"]["finite_coordinate_required"])
    )
    anchors=x.groupby(["colony","season"],as_index=False).agg(
      point_lon=("point_lon","first"),point_lat=("point_lat","first"),
      earliest_route_date=("date","min"),route_features=("date","size")
    )
    return {
      "schema_version":1,
      "result_id":"mina-paper3-zenodo-annual-anchor-semantic-v1",
      "contract_id":contract["contract_id"],
      "support":{"rows":int(len(x)),"colony_seasons":int(len(gd)),
                 "seasons_by_colony":{k:int(v) for k,v in seasons.items()},
                 "coordinate_constancy_fraction":constancy,
                 "date_parse_fraction":date_frac,
                 "finite_coordinate_fraction":finite_frac},
      "decision":{"annual_anchor_semantic_gate_passed":passed,
                  "interannual_aliasing_authorized":passed,
                  "movement_outcomes_opened":False},
      "group_checks":groups,
      "anchors":anchors
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--points-csv",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-anchors-csv",required=True,type=Path)
    a=p.parse_args()
    c=json.loads(a.contract.read_text())
    r=validate(pd.read_csv(a.points_csv),c)
    anchors=r.pop("anchors")
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    anchors.to_csv(a.out_anchors_csv,index=False)
    print(json.dumps(r,indent=2,sort_keys=True))
if __name__=="__main__": main()
