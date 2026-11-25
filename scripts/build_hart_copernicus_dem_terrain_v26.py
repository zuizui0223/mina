#!/usr/bin/env python3
"""V26 independently sampled public Copernicus DEM 30m at original BAS nests.

Original V20 10-file, 122139-point South Sandwich source is fixed.
Geography/terrain source-only stage; no new species–terrain effect fitting.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Geod,Transformer
from rasterio.transform import rowcol
import requests

from validate_bas_hart_original_multiisland_nest_points_v20 import LOCALITIES

COPDEM_BUCKET="https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com"
COPDEM_LIST_URL=COPDEM_BUCKET+"/tileList.txt"
COPDEM_PUBLIC_COLLECTION="Copernicus DEM GLO-30 Public 2021"
EXPECTED_TILE={
    "Ashen_Hills":"Copernicus_DSM_COG_10_S58_00_W027_00_DEM",
    "Bellingshausen":"Copernicus_DSM_COG_10_S60_00_W028_00_DEM",
    "Beach_Point":"Copernicus_DSM_COG_10_S60_00_W028_00_DEM",
    "Hewison_Point":"Copernicus_DSM_COG_10_S60_00_W028_00_DEM",
}
MAX_TILE_BYTES=200_000_000
MAX_TILE_INDEX_BYTES=8_000_000
WGS84=Geod(ellps="WGS84")
UTM_TO_LONLAT=Transformer.from_crs(32726,4326,always_xy=True)


def quantile_finite(x):
    a=np.asarray(x,dtype=float)
    a=a[np.isfinite(a)]
    return {
        "n":int(len(a)),
        "median":float(np.median(a)) if len(a) else None,
        "p10":float(np.percentile(a,10)) if len(a) else None,
        "p90":float(np.percentile(a,90)) if len(a) else None,
        "minimum":float(a.min()) if len(a) else None,
        "maximum":float(a.max()) if len(a) else None,
    }


def validate_original_tile_index(text:str):
    # The S3 original tileList is either a list of original directory names
    # or the COG .tif object keys. Do not invent missing tiles.
    available=set()
    for tile in set(EXPECTED_TILE.values()):
        if tile in text:
            available.add(tile)
    if len(available)!=len(set(EXPECTED_TILE.values())):
        raise ValueError("SOURCE_TILE_HOLD original CopDEM public tile index lacks "+
                         repr(sorted(set(EXPECTED_TILE.values())-available)))
    return sorted(available)


def get_source_bytes(url,size_cap:int):
    with requests.Session() as session:
        with session.get(url,timeout=(20,140),stream=True,headers={
            "User-Agent":"mina-antarctic-island-cop30-publisher-geographic-v26/1.0"}) as response:
            response.raise_for_status()
            if not response.url.startswith(COPDEM_BUCKET+"/"):
                raise ValueError("SOURCE_STOP COG source redirected outside publisher bucket")
            data=bytearray()
            for part in response.iter_content(1<<20):
                data.extend(part)
                if len(data)>size_cap:
                    raise ValueError("SOURCE_STOP COG original source exceeds bounded size")
    return bytes(data)


def fetch_dem_original_tiles(directory:Path):
    tilelist=get_source_bytes(COPDEM_LIST_URL,MAX_TILE_INDEX_BYTES)
    tilelist_sha=hashlib.sha256(tilelist).hexdigest()
    names=validate_original_tile_index(tilelist.decode("utf-8-sig"))
    locations={}
    for tile in names:
        url=COPDEM_BUCKET+"/"+tile+"/"+tile+".tif"
        blob=get_source_bytes(url,MAX_TILE_BYTES)
        if not (blob.startswith(b"II*") or blob.startswith(b"MM\x00*")
                or blob.startswith(b"II+\x00") or blob.startswith(b"MM\x00+")):
            raise ValueError("SOURCE_STOP original remote tile not a TIFF/BigTIFF")
        p=directory/(tile+".tif")
        p.write_bytes(blob)
        locations[tile]={
            "source_publisher_tile":tile,
            "source_publisher_HTTPS_object_URL":url,
            "source_original_COG_SHA256":hashlib.sha256(blob).hexdigest(),
            "source_original_COG_bytes":len(blob),
            "local_source_file":str(p),
        }
    return locations,{"original_GLO30_publisher_index_SHA256":tilelist_sha,
                      "original_publisher_1degree_tile_names":names,
                      "original_GLO30_tile_receipts":locations}


def sample_locality_dem(src, nest_xy):
    if not src.crs or src.crs.to_epsg()!=4326 or src.count!=1:
        raise ValueError("SOURCE_CRS_STOP original CopDEM COG not single-band WGS84")
    arr=src.read(1,masked=True)
    affine=src.transform
    if affine.b!=0 or affine.d!=0 or affine.a<=0 or affine.e>=0:
        raise ValueError("SOURCE_CRS_STOP original global geographic DEM affine orientation unexpected")
    lon,lat=UTM_TO_LONLAT.transform(nest_xy[:,0],nest_xy[:,1])
    lon=np.asarray(lon,dtype=float)
    lat=np.asarray(lat,dtype=float)
    if not np.isfinite(lon).all() or not np.isfinite(lat).all():
        raise ValueError("GEOMETRY_STOP original projected nest inverse transformation nonfinite")
    rr,cc=rowcol(affine,lon,lat)
    r=np.asarray(rr,dtype=np.int64)
    c=np.asarray(cc,dtype=np.int64)
    inside=(r>=1)&(r<src.height-1)&(c>=1)&(c<src.width-1)
    e=np.full(len(lon),np.nan,dtype=np.float64)
    slope=np.full(len(lon),np.nan,dtype=np.float64)
    if np.any(inside):
        idx=np.flatnonzero(inside)
        row=r[idx]
        col=c[idx]
        center=arr[row,col]
        east=arr[row,col+1]
        west=arr[row,col-1]
        north=arr[row-1,col]
        south=arr[row+1,col]
        valid=(~np.ma.getmaskarray(center)) & (~np.ma.getmaskarray(east)) & (
               ~np.ma.getmaskarray(west)) & (~np.ma.getmaskarray(north)) & (
               ~np.ma.getmaskarray(south))
        values=np.column_stack((np.ma.filled(center,np.nan),
                                np.ma.filled(east,np.nan),np.ma.filled(west,np.nan),
                                np.ma.filled(north,np.nan),np.ma.filled(south,np.nan)))
        valid &= np.isfinite(values).all(axis=1)
        if np.any(valid):
            h=idx[valid]
            latp=lat[h]
            lonp=lon[h]
            lat_dx=abs(affine.a)
            lat_dy=abs(affine.e)
            _a,_b,dx=WGS84.inv(lonp-lat_dx/2,latp,
                               lonp+lat_dx/2,latp)
            _a,_b,dy=WGS84.inv(lonp,latp-lat_dy/2,
                               lonp,latp+lat_dy/2)
            dx=np.asarray(dx,dtype=float)
            dy=np.asarray(dy,dtype=float)
            if np.any(dx<1) or np.any(dy<1):
                raise ValueError("SOURCE_STOP CopDEM degree spacing unexpected in metres")
            these=values[valid]
            slope[h]=np.degrees(np.arctan(np.hypot(
                (these[:,1]-these[:,2])/(2*dx),
                (these[:,3]-these[:,4])/(2*dy))))
            e[h]=these[:,0]
    coverage=np.isfinite(e)
    return e,slope,{
        "source_original_point_n":len(nest_xy),
        "source_point_cell_outside_original_DEM_tile_or_edge":int(np.sum(~inside)),
        "source_points_with_valid_COG_elevation_and_3x3_slope":int(np.sum(coverage)),
        "source_dem_complete_neighborhood_fraction":float(np.mean(coverage)),
        "source_DEM_sampled_elevation_m":quantile_finite(e),
        "source_DEM_sampled_slope_degrees_3x3":quantile_finite(slope),
        "source_dem_sampled_exact_elevation_0m_n":int(np.sum((e==0)&coverage)),
        "source_dem_elevation_0m_is_independent_verified_nesting_substrate":False,
        "terrain_habitat_selection_effect_fitted":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v20",type=Path,required=True)
    ap.add_argument("--source-points",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--point-terrain",type=Path,required=True)
    args=ap.parse_args()
    report={"status":"HOLD_COPDEM_ORIGINAL_SOURCE_V26",
            "species_terrain_ecological_association_fitted":False}
    try:
        source=json.loads(args.v20.read_text(encoding="utf-8"))
        if source.get("status")!="BAS_HART_ORIGINAL_10_SPECIES_NEST_CSV_SOURCE_V20":
            raise ValueError("SOURCE_STOP original nest source V20 identity missing")
        digest=hashlib.sha256(args.source_points.read_bytes()).hexdigest()
        if digest!=source["derived_source_geography_NPZ_SHA256"]:
            raise ValueError("SOURCE_STOP original nest point bytes differ from published V20 artifact")
        with np.load(args.source_points,allow_pickle=False) as data:
            orig={k:data[k] for k in data.files}
        if sorted(orig)!=sorted(source["derived_nest_points_NPZ_array_keys"]):
            raise ValueError("SOURCE_STOP original frozen nest coordinate file array keys changed")
        with tempfile.TemporaryDirectory(prefix="cop30-original-public-dem-") as tmp:
            tiles,receipts=fetch_dem_original_tiles(Path(tmp))
            by_site={}
            output={k:v for k,v in orig.items()}
            for locality in LOCALITIES:
                expected_tile=EXPECTED_TILE[locality]
                with rasterio.open(tiles[expected_tile]["local_source_file"]) as src:
                    source_xy=orig[f"{locality}_xy"]
                    elev,slope,qa=sample_locality_dem(src,source_xy)
                output[f"{locality}_DEM_elevation_m"]=elev.astype(np.float32)
                output[f"{locality}_DEM_slope_degrees"]=slope.astype(np.float32)
                by_site[locality]={**qa,"publisher_COG_tile_id":expected_tile}
            report={
                "status":"ORIGINAL_COPERNICUS_DEM30_TERRAIN_AT_HART_NEST_SITES_V26",
                "independent_environmental_source":COPDEM_PUBLIC_COLLECTION,
                "source_DOI":"10.5270/ESA-c5d3d65",
                "source_original_dem_tiles":receipts,
                "source_original_nest_point_Utm_NPZ_SHA256":digest,
                "source_original_colony_gps_points_all_sites_n":source["source_nest_point_sum"],
                "original_source_locality_sample_by_DEM_coverage":by_site,
                "source_static_DSM_is_historical_2019_2020_nest_substrate":False,
                "original_nest_locations_are_random_background_habitat_samples":False,
                "source_is_sub_Antarctic":True,
                "old_100m_spatial_species_label_null_recomputed":False,
                "new_species_terrain_ecological_association_fitted":False,
                "original_bird_counts_imputed_from_DEM":False,
            }
            args.point_terrain.parent.mkdir(parents=True,exist_ok=True)
            np.savez_compressed(args.point_terrain,**output)
        report["derived_independent_environment_tied_to_original_nest_points_NPZ_SHA256"]=hashlib.sha256(
            args.point_terrain.read_bytes()).hexdigest()
        report["derived_environment_nest_point_array_keys"]=sorted(output)
    except Exception as exc:
        report["error_type"]=type(exc).__name__
        report["error"]=str(exc)[:1600]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
