#!/usr/bin/env python3
"""Compute the frozen Paper 2D marine open-water access-distance change."""
from __future__ import annotations

import argparse
import io
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer
from rasterio.io import MemoryFile
from scipy.spatial import cKDTree
import requests


BASE = "https://noaadata.apps.nsidc.org/NOAA/G02135/south/monthly/geotiff"
MONTHS = {1: "01_Jan", 11: "11_Nov", 12: "12_Dec"}
VERSION = "v4.0"


def file_url(year: int, month: int) -> str:
    return (
        f"{BASE}/{MONTHS[int(month)]}/"
        f"S_{int(year):04d}{int(month):02d}_concentration_{VERSION}.tif"
    )


def required_year_months(sites: pd.DataFrame) -> list[tuple[int,int]]:
    out=set()
    for row in sites.itertuples(index=False):
        for prefix in ("early","late"):
            start=int(getattr(row,f"{prefix}_window_start"))
            end=int(getattr(row,f"{prefix}_window_end"))
            for year in range(start,end+1):
                for month in MONTHS:
                    out.add((year,month))
    return sorted(out)


def site_epoch_months(row, prefix: str) -> list[tuple[int,int]]:
    start=int(getattr(row,f"{prefix}_window_start"))
    end=int(getattr(row,f"{prefix}_window_end"))
    return [(y,m) for y in range(start,end+1) for m in MONTHS]


def read_open_water_tree(content: bytes):
    with MemoryFile(content) as mem:
        with mem.open() as src:
            arr=src.read(1)
            valid=(arr>=0) & (arr<=1000)
            open_water=valid & (arr<150)
            rr,cc=np.where(open_water)
            if len(rr)==0:
                return None, src.crs
            xs,ys=rasterio.transform.xy(src.transform, rr, cc, offset="center")
            coords=np.column_stack([np.asarray(xs,dtype=float),np.asarray(ys,dtype=float)])
            return cKDTree(coords), src.crs


def download(session: requests.Session, url: str) -> bytes | None:
    last=None
    for attempt in range(5):
        try:
            r=session.get(url,timeout=90,headers={"User-Agent":"mina-paper2d-marine-distance/1.0"})
            if r.status_code==404:
                return None
            r.raise_for_status()
            return r.content
        except Exception as exc:
            last=exc
            if attempt==4:
                raise
            time.sleep(2**attempt)
    raise last


def transform_sites(sites: pd.DataFrame, dst_crs) -> np.ndarray:
    tr=Transformer.from_crs("EPSG:4326",dst_crs,always_xy=True)
    x,y=tr.transform(sites["longitude"].to_numpy(float),sites["latitude"].to_numpy(float))
    return np.column_stack([x,y])


def compute_monthly_distances(sites: pd.DataFrame, workers_sleep: float = 0.0):
    session=requests.Session()
    need=required_year_months(sites)
    distances={(str(s.site_id),y,m):math.nan for s in sites.itertuples(index=False) for y,m in need}
    file_rows=[]
    transformed_cache={}
    for i,(year,month) in enumerate(need, start=1):
        url=file_url(year,month)
        try:
            content=download(session,url)
            if content is None:
                file_rows.append({"year":year,"month":month,"url":url,"available":False,"open_water_cells":0,"error":None})
                continue
            tree,crs=read_open_water_tree(content)
            if crs is None:
                raise ValueError("GeoTIFF has no CRS")
            key=str(crs)
            if key not in transformed_cache:
                transformed_cache[key]=transform_sites(sites,crs)
            pts=transformed_cache[key]
            if tree is None:
                vals=np.full(len(sites),np.nan)
                n_open=0
            else:
                vals,_=tree.query(pts,k=1)
                vals=np.asarray(vals,float)/1000.0
                n_open=int(tree.n)
            for idx,site_id in enumerate(sites["site_id"].astype(str)):
                d=float(vals[idx]) if np.isfinite(vals[idx]) and vals[idx] <= 1000.0 else math.nan
                distances[(site_id,year,month)]=d
            file_rows.append({"year":year,"month":month,"url":url,"available":True,"open_water_cells":n_open,"error":None})
        except Exception as exc:
            file_rows.append({"year":year,"month":month,"url":url,"available":False,"open_water_cells":0,"error":f"{type(exc).__name__}: {exc}"})
        print(f"[{i}/{len(need)}] {year}-{month:02d}",flush=True)
        if workers_sleep:
            time.sleep(workers_sleep)
    return distances,pd.DataFrame(file_rows)


def epoch_summary(row, prefix: str, distances: dict) -> dict:
    months=site_epoch_months(row,prefix)
    vals=[]
    by_year={}
    for y,m in months:
        v=distances.get((str(row.site_id),y,m),math.nan)
        if np.isfinite(v):
            vals.append(float(v))
            by_year.setdefault(y,set()).add(m)
    frac=len(vals)/len(months) if months else 0.0
    complete_years=sum(len(v)==3 for v in by_year.values())
    passed=frac>=0.90 and complete_years>=3
    return {
        f"{prefix}_required_months":len(months),
        f"{prefix}_available_months":len(vals),
        f"{prefix}_available_fraction":frac,
        f"{prefix}_complete_years":complete_years,
        f"{prefix}_median_open_water_distance_km":float(np.median(vals)) if vals else math.nan,
        f"{prefix}_marine_epoch_pass":bool(passed),
    }


def audit(sites: pd.DataFrame):
    if len(sites)!=77:
        raise ValueError(f"frozen summer-exposure site roster drift: {len(sites)} != 77")
    forbidden={"count","abundance","trend","beta","holm_p","kappa","n_eff"}
    present=forbidden.intersection({str(c).lower() for c in sites.columns})
    if present:
        raise ValueError(f"forbidden outcome fields present: {sorted(present)}")

    distances,files=compute_monthly_distances(sites)
    rows=[]
    for row in sites.itertuples(index=False):
        rec=row._asdict()
        rec.update(epoch_summary(row,"early",distances))
        rec.update(epoch_summary(row,"late",distances))
        rec["marine_metric_pass"]=bool(rec["early_marine_epoch_pass"] and rec["late_marine_epoch_pass"])
        e=rec["early_median_open_water_distance_km"]
        l=rec["late_median_open_water_distance_km"]
        rec["marine_distance_change_late_minus_early_km"]=float(l-e) if np.isfinite(e) and np.isfinite(l) else math.nan
        rec["marine_favorable_change_km"]=float(e-l) if np.isfinite(e) and np.isfinite(l) else math.nan
        rows.append(rec)
    out=pd.DataFrame(rows).sort_values("site_id").reset_index(drop=True)
    passed=out[out["marine_metric_pass"]]
    result={
        "schema_version":1,
        "result_id":"mina-paper2d-marine-distance-measurement-v1",
        "sites":{"candidate":int(len(out)),"passing":int(len(passed)),"passing_fraction":float(len(passed)/len(out))},
        "regions":{"represented":int(passed["region"].nunique()),"by_region":{str(k):int(v) for k,v in passed.groupby("region").size().items()}},
        "metric":{
            "median_early_distance_km":float(passed["early_median_open_water_distance_km"].median()) if len(passed) else None,
            "median_late_distance_km":float(passed["late_median_open_water_distance_km"].median()) if len(passed) else None,
            "median_favorable_change_km":float(passed["marine_favorable_change_km"].median()) if len(passed) else None
        },
        "archive":{
            "files_required":int(len(files)),
            "files_available":int(files["available"].sum()),
            "files_missing_or_failed":files.loc[~files["available"],["year","month","error"]].to_dict("records")
        },
        "decision":{
            "measurement_gate_passed":bool(len(passed)/len(out)>=0.80 and passed["region"].nunique()>=2),
            "H2_recovery_authorized":bool(len(passed)/len(out)>=0.80 and passed["region"].nunique()>=2),
            "demographic_outcome_used":False
        },
        "boundary":[
            "Distance is to the nearest 25-km Sea Ice Index grid-cell center classified below 15% concentration.",
            "This metric measures broad marine access, not prey availability or route-level cracks/leads.",
            "No alternate threshold, month set or epoch summary was selected from H1 or demographic outcomes."
        ]
    }
    return result,out,files


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--sites-csv",required=True,type=Path)
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-sites-csv",required=True,type=Path)
    p.add_argument("--out-files-csv",required=True,type=Path)
    a=p.parse_args()
    c=json.loads(a.contract.read_text(encoding="utf-8"))
    if c.get("status")!="frozen_after_H1_before_H2_values":
        raise SystemExit("marine measurement contract is not frozen")
    sites=pd.read_csv(a.sites_csv)
    result,site_table,file_table=audit(sites)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    site_table.to_csv(a.out_sites_csv,index=False)
    file_table.to_csv(a.out_files_csv,index=False)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
