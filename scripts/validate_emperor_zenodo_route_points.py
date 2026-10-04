#!/usr/bin/env python3
"""Validate route-origin semantics in the published Zenodo emperor dataset."""
from __future__ import annotations

import argparse, io, json, math, re, tempfile
from pathlib import Path

import pandas as pd
import shapefile
from pyproj import Geod
from remotezip import RemoteZip


GEOD = Geod(ellps="WGS84")
COLONY_HINTS={"astrid":"Astrid","mertz":"Mertz","sanae":"SANAE"}
SEASON_RE=re.compile(r"(?i)(\d{2})[_-](\d{2}).*distance")


def colony_from_path(path: str):
    low=path.lower()
    for token,name in COLONY_HINTS.items():
        if token in low:
            return name
    return None


def season_from_path(path: str):
    m=SEASON_RE.search(Path(path).stem)
    if not m:
        return None
    a=int(m.group(1)); b=int(m.group(2))
    y0=2000+a if a<80 else 1900+a
    y1=2000+b if b<80 else 1900+b
    if y1 != y0+1:
        return f"{y0}-{y1}"
    return f"{y0}-{y1}"


def geod_m(lon1,lat1,lon2,lat2):
    _,_,d=GEOD.inv(float(lon1),float(lat1),float(lon2),float(lat2))
    return float(abs(d))


def parse_date(v):
    d=pd.to_datetime(v,errors="coerce")
    if pd.isna(d):
        return None
    return d.date().isoformat()


def inspect(url: str, tolerance_m: float) -> tuple[pd.DataFrame, dict]:
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
                for fi in range(len(rd)):
                    rows.append({
                        "archive_path":shp_name,"colony":colony_from_path(shp_name),
                        "season":season_from_path(shp_name),"feature_index":fi,
                        "semantic_error":"missing required fields","date":None,
                        "origin_match":False
                    })
                continue
            for fi,(shape,rec) in enumerate(zip(rd.shapes(),rd.records())):
                try:
                    lon=float(rec[idx["pointLon"]]); lat=float(rec[idx["pointLat"]])
                    date=parse_date(rec[idx["Date"]])
                    pts=shape.points
                    if not pts:
                        raise ValueError("empty polyline")
                    first_lon,first_lat=pts[0]
                    last_lon,last_lat=pts[-1]
                    d_first=geod_m(lon,lat,first_lon,first_lat)
                    d_last=geod_m(lon,lat,last_lon,last_lat)
                    origin_match=bool(d_first <= tolerance_m and d_first <= d_last)
                    err=None
                except Exception as exc:
                    lon=lat=first_lon=first_lat=last_lon=last_lat=math.nan
                    d_first=d_last=math.nan; date=None; origin_match=False
                    err=f"{type(exc).__name__}: {exc}"
                rows.append({
                    "archive_path":shp_name,
                    "colony":colony_from_path(shp_name),
                    "season":season_from_path(shp_name),
                    "feature_index":int(fi),
                    "date":date,
                    "point_lon":lon,
                    "point_lat":lat,
                    "route_first_lon":first_lon,
                    "route_first_lat":first_lat,
                    "route_last_lon":last_lon,
                    "route_last_lat":last_lat,
                    "distance_attr_to_first_m":d_first,
                    "distance_attr_to_last_m":d_last,
                    "origin_match":origin_match,
                    "semantic_error":err,
                })
    rz.close()
    df=pd.DataFrame(rows)
    valid_dates=int(df["date"].notna().sum())
    origin=int(df["origin_match"].fillna(False).sum())
    n=len(df)
    by_colony={}
    for colony,g in df.groupby("colony"):
        by_colony[str(colony)]={
            "features":int(len(g)),
            "seasons":int(g["season"].nunique()),
            "origin_match_fraction":float(g["origin_match"].mean()),
            "date_parse_fraction":float(g["date"].notna().mean()),
            "earliest_date":min(g["date"].dropna()) if g["date"].notna().any() else None,
            "latest_date":max(g["date"].dropna()) if g["date"].notna().any() else None,
        }
    return df,{
        "features":n,
        "origin_matches":origin,
        "origin_match_fraction":float(origin/n) if n else 0.0,
        "date_parsed":valid_dates,
        "date_parse_fraction":float(valid_dates/n) if n else 0.0,
        "by_colony":by_colony
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()
    c=json.loads(a.contract.read_text())
    test=c["semantic_test"]
    df,s=inspect(c["source"]["route_zip"],float(test["primary_origin_tolerance_m"]))
    expected=set(c["source"]["expected_colonies"])
    colonies=set(df["colony"].dropna())
    season_ok=all(df[df["colony"].eq(col)]["season"].nunique()>=int(c["support_after_semantic_pass"]["minimum_seasons_per_colony"]) for col in expected)
    passed=bool(
        colonies==expected and
        s["origin_match_fraction"]>=float(test["required_origin_match_fraction"]) and
        s["date_parse_fraction"]>=float(test["required_date_parse_fraction"]) and
        season_ok
    )
    out={
        "schema_version":1,
        "result_id":"mina-paper3-zenodo-route-point-semantic-v1",
        "contract_id":c["contract_id"],
        "summary":s,
        "decision":{
            "semantic_gate_passed":passed,
            "interannual_aliasing_authorized":passed,
            "within_season_primary_authorized":False,
            "movement_outcomes_opened":False
        },
        "boundary":[
            "Distances in this audit only compare each published point attribute to its own route endpoints; they are not colony movement outcomes.",
            "No inter-date or interannual colony displacement is computed.",
            "No abundance, breeding success or environmental covariates are used."
        ]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(a.out_csv,index=False)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
