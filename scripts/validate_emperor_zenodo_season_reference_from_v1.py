#!/usr/bin/env python3
"""Build semantic V2 from the frozen V1 Zenodo feature table without redownloading the remote ZIP."""
from __future__ import annotations

import argparse, json, math
from pathlib import Path

import pandas as pd
from pyproj import Geod

GEOD=Geod(ellps="WGS84")

def geod_m(a,b):
    _,_,d=GEOD.inv(float(a[0]),float(a[1]),float(b[0]),float(b[1]))
    return float(abs(d))

def summarize(features:pd.DataFrame, contract:dict):
    required={"colony","season","date","point_lon","point_lat"}
    missing=required-set(features.columns)
    if missing:
        raise ValueError(f"missing frozen V1 fields: {sorted(missing)}")
    x=features.copy()
    x["date"]=pd.to_datetime(x["date"],errors="coerce",format="mixed")
    season_rows=[]
    tol=float(contract["semantic_test"]["within_colony_season_coordinate_tolerance_m"])
    for (colony,season),g in x.groupby(["colony","season"],sort=True):
        coords=g[["point_lon","point_lat"]].drop_duplicates().to_numpy(float)
        max_pair=0.0
        for i in range(len(coords)):
            for j in range(i+1,len(coords)):
                max_pair=max(max_pair,geod_m(coords[i],coords[j]))
        season_rows.append({
            "colony":str(colony),
            "season":str(season),
            "features":int(len(g)),
            "distinct_reference_coordinates":int(len(coords)),
            "max_within_season_reference_distance_m":float(max_pair),
            "reference_invariant":bool(max_pair<=tol),
            "date_parse_fraction":float(g["date"].notna().mean()),
            "reference_lon":float(coords[0,0]) if len(coords) else math.nan,
            "reference_lat":float(coords[0,1]) if len(coords) else math.nan,
            "earliest_route_date":g["date"].min().date().isoformat() if g["date"].notna().any() else None,
            "latest_route_date":g["date"].max().date().isoformat() if g["date"].notna().any() else None,
        })
    seasons=pd.DataFrame(season_rows)
    expected=set(contract["source"]["expected_colonies"])
    by_colony={}
    for colony,g in seasons.groupby("colony",sort=True):
        fx=x[x["colony"].eq(colony)]
        by_colony[str(colony)]={
            "seasons":int(len(g)),
            "invariant_seasons":int(g["reference_invariant"].sum()),
            "invariant_fraction":float(g["reference_invariant"].mean()),
            "date_parse_fraction":float(fx["date"].notna().mean()),
            "max_within_season_reference_distance_m":float(g["max_within_season_reference_distance_m"].max()),
        }
    inv_frac=float(seasons["reference_invariant"].mean()) if len(seasons) else 0.0
    date_frac=float(x["date"].notna().mean()) if len(x) else 0.0
    min_seasons=int(contract["semantic_test"]["minimum_seasons_per_colony"])
    passed=bool(
        set(by_colony)==expected
        and all(v["seasons"]>=min_seasons for v in by_colony.values())
        and inv_frac>=float(contract["semantic_test"]["required_seasons_with_invariant_reference_fraction"])
        and date_frac>=float(contract["semantic_test"]["required_date_parse_fraction"])
    )
    out={
        "schema_version":2,
        "result_id":"mina-paper3-zenodo-season-reference-semantic-v2",
        "contract_id":contract["contract_id"],
        "summary":{
            "features":int(len(x)),
            "colony_seasons":int(len(seasons)),
            "invariant_seasons":int(seasons["reference_invariant"].sum()),
            "invariant_fraction":inv_frac,
            "date_parse_fraction":date_frac,
            "by_colony":by_colony,
        },
        "decision":{
            "semantic_gate_passed":passed,
            "interannual_aliasing_authorized":passed,
            "movement_outcomes_opened":False,
        },
        "interpretation":contract["semantic_test"]["interpretation_if_passed"] if passed else None,
        "provenance":{"input":contract.get("source_frozen_artifact")},
        "boundary":[
            "V2 reuses the frozen V1 feature table and does not redownload or alter source coordinates.",
            "The semantic audit tests within-season invariance only.",
            "No interannual displacement or radius-specific turnover is computed.",
            "The failed V1 endpoint-origin semantic result remains in the audit trail."
        ]
    }
    return seasons,out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--features-csv",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-seasons-csv",required=True,type=Path)
    a=p.parse_args()
    c=json.loads(a.contract.read_text())
    seasons,out=summarize(pd.read_csv(a.features_csv),c)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    seasons.to_csv(a.out_seasons_csv,index=False)
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
