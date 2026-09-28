#!/usr/bin/env python3
"""Outcome-blind REMA terrain extraction for Antarctic Pygoscelis candidate sites."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr
import rasterio
from pyproj import Transformer
from rasterio.windows import from_bounds

MAPPPDR_COMMIT="88c73a507e0921b2541c218c71eaf16721bc6502"
PRIMARY_SPECIES=("ADPE","CHPE","GEPE")
RADII_M=(1000,2000,5000)
PRIMARY_RADIUS_M=2000


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        frame=x[expected]
    elif len(x)==1:
        frame=next(iter(x.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(x)}")
    if not isinstance(frame,pd.DataFrame):
        raise TypeError(expected)
    return frame


def candidate_sites(root:Path)->pd.DataFrame:
    sites=load_rda(root/"data"/"sites.rda","sites")
    obs=load_rda(root/"data"/"penguin_obs.rda","penguin_obs")
    nest=obs[
        obs["species_id"].isin(PRIMARY_SPECIES)
        & (obs["type"]=="nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest=nest.dropna(subset=["year"])

    units=[]
    for (site_id,species_id),local in nest.groupby(["site_id","species_id"]):
        years=sorted(set(int(y) for y in local["year"]))
        if len(years)>=5 and max(years)-min(years)>=10:
            units.append((str(site_id),str(species_id)))
    if len(units)!=152:
        raise ValueError(f"candidate unit drift: {len(units)} != 152")
    ids=sorted({site_id for site_id,_ in units})
    out=sites[sites["site_id"].isin(ids)].copy()
    if len(out)!=122:
        raise ValueError(f"candidate site drift: {len(out)} != 122")
    return out[["site_id","site_name","region","ccamlr_id","latitude","longitude"]]


def read_circle(src,x:float,y:float,radius:float)->np.ndarray:
    window=from_bounds(
        x-radius,y-radius,x+radius,y+radius,transform=src.transform
    ).round_offsets().round_lengths()
    arr=src.read(1,window=window,masked=True,boundless=True)
    transform=src.window_transform(window)
    rows,cols=np.indices(arr.shape)
    xs=transform.c+(cols+0.5)*transform.a+(rows+0.5)*transform.b
    ys=transform.f+(cols+0.5)*transform.d+(rows+0.5)*transform.e
    inside=(xs-x)**2+(ys-y)**2<=radius**2
    valid=inside & (~np.ma.getmaskarray(arr))
    vals=np.asarray(arr.data[valid],dtype=float)
    vals=vals[np.isfinite(vals)]
    return vals


def summary(vals:np.ndarray)->dict:
    if vals.size==0:
        return {
            "valid_dem_pixel_count":0,
            "elevation_median_m":None,
            "elevation_mean_m":None,
            "elevation_sd_m":None,
            "elevation_p10_m":None,
            "elevation_p90_m":None,
            "elevation_relief_p90_p10_m":None,
        }
    p10=float(np.quantile(vals,0.10))
    p90=float(np.quantile(vals,0.90))
    return {
        "valid_dem_pixel_count":int(vals.size),
        "elevation_median_m":float(np.median(vals)),
        "elevation_mean_m":float(np.mean(vals)),
        "elevation_sd_m":float(np.std(vals,ddof=0)),
        "elevation_p10_m":p10,
        "elevation_p90_m":p90,
        "elevation_relief_p90_p10_m":p90-p10,
    }


def point_elevation(src,x:float,y:float)->float|None:
    sample=next(src.sample([(x,y)],masked=True))
    if np.ma.is_masked(sample[0]):
        return None
    value=float(sample[0])
    return value if np.isfinite(value) else None


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--rema-tif",required=True,type=Path)
    p.add_argument("--source-archive",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()

    sites=candidate_sites(a.mapppdr_dir)
    archive_sha=sha256(a.source_archive)
    tif_sha=sha256(a.rema_tif)
    records=[]

    with rasterio.open(a.rema_tif) as src:
        if src.crs is None:
            raise ValueError("REMA has no CRS")
        transformer=Transformer.from_crs(4326,src.crs,always_xy=True)

        for row in sites.to_dict(orient="records"):
            x,y=transformer.transform(float(row["longitude"]),float(row["latitude"]))
            rec={
                "site_id":str(row["site_id"]),
                "site_name":str(row["site_name"]),
                "region":str(row["region"]),
                "ccamlr_id":None if pd.isna(row["ccamlr_id"]) else str(row["ccamlr_id"]),
                "latitude":float(row["latitude"]),
                "longitude":float(row["longitude"]),
                "x_rema_crs":float(x),
                "y_rema_crs":float(y),
                "site_elevation_m":point_elevation(src,x,y),
            }
            for radius in RADII_M:
                stats=summary(read_circle(src,x,y,radius))
                for key,value in stats.items():
                    rec[f"{key}_{radius}m"]=value
            records.append(rec)

        meta={
            "crs":str(src.crs),
            "width":int(src.width),
            "height":int(src.height),
            "count":int(src.count),
            "dtype":str(src.dtypes[0]),
            "nodata":None if src.nodata is None else float(src.nodata),
            "resolution":[float(abs(src.transform.a)),float(abs(src.transform.e))],
            "bounds":[
                float(src.bounds.left),float(src.bounds.bottom),
                float(src.bounds.right),float(src.bounds.top)
            ],
        }

    frame=pd.DataFrame(records)
    a.out_csv.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(a.out_csv,index=False)

    coverage={}
    for radius in RADII_M:
        col=f"valid_dem_pixel_count_{radius}m"
        n=int((frame[col]>0).sum())
        coverage[str(radius)]={
            "radius_m":radius,
            "sites_with_valid_dem":n,
            "coverage_fraction":n/len(frame),
            "missing_site_ids":frame.loc[frame[col]<=0,"site_id"].tolist(),
        }

    primary=coverage[str(PRIMARY_RADIUS_M)]["coverage_fraction"]
    result={
        "schema_version":1,
        "result_id":"mina-antarctic-terrain-atlas-gate1d-a-result-v1",
        "mapppdr_commit":MAPPPDR_COMMIT,
        "candidate_site_species_units":152,
        "distinct_candidate_sites":len(frame),
        "rema":{
            "version":"2.0",
            "resolution_m":500,
            "archive_file":a.source_archive.name,
            "archive_sha256":archive_sha,
            "dem_file":a.rema_tif.name,
            "dem_sha256":tif_sha,
            "raster_metadata":meta,
        },
        "radii_m":list(RADII_M),
        "primary_radius_m":PRIMARY_RADIUS_M,
        "coverage_by_radius":coverage,
        "primary_radius_coverage_fraction":float(primary),
        "gate_passed":bool(primary>=0.90),
        "derived_csv":a.out_csv.name,
        "boundary":[
            "REMA terrain is local topographic context rather than occupied nesting habitat.",
            "No demographic outcome is used in this extraction."
        ],
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result["gate_passed"]:
        raise SystemExit("Terrain Gate 1D-A failed frozen >=90% 2 km coverage rule")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
