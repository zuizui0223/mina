#!/usr/bin/env python3
"""Validate source-supplied season-reference coordinates in the Zenodo emperor route archive."""
from __future__ import annotations

import argparse, io, json, math, re, tempfile
from pathlib import Path

import pandas as pd
import shapefile
from pyproj import Geod
from remotezip import RemoteZip

GEOD=Geod(ellps="WGS84")
COLONY_HINTS={"astrid":"Astrid","mertz":"Mertz","sanae":"SANAE"}
SEASON_RE=re.compile(r"(?i)(\d{2})[_-](\d{2}).*distance")

def colony_from_path(path:str):
    low=path.lower()
    for token,name in COLONY_HINTS.items():
        if token in low:
            return name
    return None

def season_from_path(path:str):
    m=SEASON_RE.search(Path(path).stem)
    if not m:
        return None
    a=int(m.group(1)); b=int(m.group(2))
    y0=2000+a if a<80 else 1900+a
    y1=2000+b if b<80 else 1900+b
    return f"{y0}-{y1}"

def parse_date(v):
    d=pd.to_datetime(v,errors="coerce",format="mixed")
    if pd.isna(d):
        return None
    return d.date().isoformat()

def geod_m(a,b):
    _,_,d=GEOD.inv(float(a[0]),float(a[1]),float(b[0]),float(b[1]))
    return float(abs(d))

def inspect(url:str,tolerance_m:float):
    rz=RemoteZip(url)
    names=rz.namelist()
    shps=sorted(n for n in names if n.lower().endswith(".shp") and not n.startswith("__MACOSX"))
    rows=[]
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        for si,shp_name in enumerate(shps):
            base=shp_name[:-4]
            blobs={}
            for ext in (".shp",".dbf",".shx",".prj",".cpg"):
                member=base+ext
                if member in names:
                    blobs[ext]=rz.read(member)
            if not all(k in blobs for k in (".shp",".dbf",".shx")):
                continue
            local=root/f"s{si}"
            for ext,blob in blobs.items():
                local.with_suffix(ext).write_bytes(blob)
            rd=shapefile.Reader(str(local.with_suffix(".shp")))
            fields=[str(f[0]) for f in rd.fields[1:]]
            idx={name:i for i,name in enumerate(fields)}
            required={"pointLon","pointLat","Date"}
            if not required.issubset(idx):
                raise ValueError(f"missing required fields in {shp_name}: {sorted(required-set(idx))}")
            colony=colony_from_path(shp_name); season=season_from_path(shp_name)
            if colony is None or season is None:
                continue
            for fi,rec in enumerate(rd.records()):
                rows.append({
                    "archive_path":shp_name,
                    "colony":colony,
                    "season":season,
                    "feature_index":int(fi),
                    "date":parse_date(rec[idx["Date"]]),
                    "point_lon":float(rec[idx["pointLon"]]),
                    "point_lat":float(rec[idx["pointLat"]]),
                })
    rz.close()
    df=pd.DataFrame(rows)
    season_rows=[]
    for (colony,season),g in df.groupby(["colony","season"],sort=True):
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
            "reference_invariant":bool(max_pair<=tolerance_m),
            "date_parse_fraction":float(g["date"].notna().mean()),
            "reference_lon":float(coords[0,0]) if len(coords) else math.nan,
            "reference_lat":float(coords[0,1]) if len(coords) else math.nan,
            "earliest_route_date":min(g["date"].dropna()) if g["date"].notna().any() else None,
            "latest_route_date":max(g["date"].dropna()) if g["date"].notna().any() else None,
        })
    return df,pd.DataFrame(season_rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-features-csv",required=True,type=Path)
    p.add_argument("--out-seasons-csv",required=True,type=Path)
    a=p.parse_args()
    c=json.loads(a.contract.read_text())
    test=c["semantic_test"]
    features,seasons=inspect(c["source"]["route_zip"],float(test["within_colony_season_coordinate_tolerance_m"]))
    expected=set(c["source"]["expected_colonies"])
    by_colony={}
    for colony,g in seasons.groupby("colony",sort=True):
        by_colony[str(colony)]={
            "seasons":int(len(g)),
            "invariant_seasons":int(g["reference_invariant"].sum()),
            "invariant_fraction":float(g["reference_invariant"].mean()),
            "date_parse_fraction":float(features[features["colony"].eq(colony)]["date"].notna().mean()),
            "max_within_season_reference_distance_m":float(g["max_within_season_reference_distance_m"].max()),
        }
    colonies=set(by_colony)
    n_seasons=int(len(seasons))
    invariant_fraction=float(seasons["reference_invariant"].mean()) if n_seasons else 0.0
    date_fraction=float(features["date"].notna().mean()) if len(features) else 0.0
    min_seasons=int(test["minimum_seasons_per_colony"])
    passed=bool(
        colonies==expected
        and all(v["seasons"]>=min_seasons for v in by_colony.values())
        and invariant_fraction>=float(test["required_seasons_with_invariant_reference_fraction"])
        and date_fraction>=float(test["required_date_parse_fraction"])
    )
    out={
        "schema_version":2,
        "result_id":"mina-paper3-zenodo-season-reference-semantic-v2",
        "contract_id":c["contract_id"],
        "summary":{
            "features":int(len(features)),
            "colony_seasons":n_seasons,
            "invariant_seasons":int(seasons["reference_invariant"].sum()),
            "invariant_fraction":invariant_fraction,
            "date_parse_fraction":date_fraction,
            "by_colony":by_colony,
        },
        "decision":{
            "semantic_gate_passed":passed,
            "interannual_aliasing_authorized":passed,
            "movement_outcomes_opened":False,
        },
        "interpretation":c["semantic_test"]["interpretation_if_passed"] if passed else None,
        "boundary":[
            "This semantic audit tests within-season invariance of the source point fields only.",
            "No interannual displacement, radius-specific turnover, abundance, breeding success or environmental outcome is computed.",
            "The failed V1 route-endpoint semantic test remains part of the audit trail."
        ]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    features.to_csv(a.out_features_csv,index=False)
    seasons.to_csv(a.out_seasons_csv,index=False)
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
