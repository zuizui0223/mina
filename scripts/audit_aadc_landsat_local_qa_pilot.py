#!/usr/bin/env python3
"""Read local QA_PIXEL, not ecology, at fixed AADC IS_105 2017->2018 Landsat scenes."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from urllib.parse import quote,urlparse
import numpy as np
import rasterio
import requests
from pyproj import Transformer
from shapely.geometry import Point,shape

SITE="IS_105"; SPECIES="ADP"; START=2017
ROOT="https://earth-search.aws.element84.com/v1"
COLLECTION="landsat-c2-l2"

def qa_flags(x):
    x=np.asarray(x,dtype=np.uint16)
    bit=lambda k:(x & np.uint16(1<<k))!=0
    unusable=bit(0)|bit(1)|bit(2)|bit(3)|bit(4)
    valid=~unusable
    return {"pixel_count":int(x.size),"usable_qa_pixels":int(valid.sum()),
            "cloud_fill_shadow_pixels":int(unusable.sum()),
            "snow_flagged_valid_pixels":int((bit(5)&valid).sum()),
            "water_flagged_valid_pixels":int((bit(7)&valid).sum()),
            "QA_snow_is_permanent_ice":False,
            "clear_QA_proves_bare_rock":False}

def get_scene(scene_id):
    url=f"{ROOT}/collections/{COLLECTION}/items/{quote(scene_id,safe='')}"
    r=requests.get(url,timeout=(20,45),headers={"User-Agent":"mina-landcover-pilot/1.0"})
    r.raise_for_status()
    if len(r.content)>5_000_000:raise ValueError("STAC item metadata too large")
    x=r.json()
    if x.get("id")!=scene_id or x.get("collection")!=COLLECTION:
        raise ValueError("STAC item ID mismatch")
    return x

def qa_from_cog(href,lat,lon):
    u=urlparse(href)
    host=(u.hostname or "").lower()
    if u.scheme!="https" or not (
        host=="landsatlook.usgs.gov" or host=="usgs-landsat.s3.amazonaws.com"
        or host.endswith(".s3.amazonaws.com")
        or host.endswith(".s3.us-west-2.amazonaws.com")
    ):raise ValueError("Unverified QA COG host "+host)
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="YES",GDAL_HTTP_TIMEOUT="25",
                      GDAL_HTTP_MAX_RETRY="1"):
      with rasterio.open(href) as ds:
        if not ds.crs:raise ValueError("QA source raster lacks CRS")
        x,y=Transformer.from_crs(4326,ds.crs,always_xy=True).transform(lon,lat)
        row,col=ds.index(x,y)
        if min(row,col)<10 or row+10>=ds.height or col+10>=ds.width:
            raise ValueError("Original AADC centroid outside scene image edge")
        a=ds.read(1,window=rasterio.windows.Window(col-10,row-10,21,21))
        if a.shape!=(21,21):raise ValueError("Invalid QA chip size")
        return {"source_qa_host":host,"source_crs":str(ds.crs),
                "pixel_resolution":[abs(ds.res[0]),abs(ds.res[1])],
                "center_QA_integer":int(a[10,10]),"local_QA_21x21":qa_flags(a)}

def audit(p):
    x=json.loads(p.read_text())
    if x.get("events_sampled")!=16 or x.get("status")!="LANDSAT_STAC_PILOT_ORIGINAL_SCENE_METADATA_ONLY":
        raise ValueError("Expected original complete 16-event STAC receipt")
    target=[r for r in x["source_site_scene_metadata"]
            if r["geog_site_id"]==SITE and r["species_code"]==SPECIES
            and r["a_season_start"]==START]
    if len(target)!=2:raise ValueError("Expected exact 2 seasons")
    result={"status":"LOCAL_LANDSAT_QA_PIXEL_SOURCE_ONLY",
            "source_site_id":SITE,"original_A_to_P":[START,START+1],
            "source_is_exact_nest_footprint":False,
            "date_utc":datetime.now(timezone.utc).isoformat(),
            "source_seasons":{},
            "biological_effect_fitted":False}
    for r in target:
        label=r["comparison_side"]
        scenes=[s for s in r.get("scene_first_twelve_by_datetime",[])
                if s.get("qa_pixel_asset_listed")
                and isinstance(s.get("global_scene_cloud_cover"),(float,int))]
        scenes.sort(key=lambda s:(s["global_scene_cloud_cover"],s["acquired"],s["stac_id"]))
        entry={"scene_selection_rule":"first 12 returned scenes only; minimum scene-global cloud, then date and ID"}
        if not scenes:
            entry["status"]="HOLD_NO_QA_SCENE_IN_FIRST_TWELVE"
        else:
            s=scenes[0]
            entry.update({"scene_id":s["stac_id"],"acquired":s["acquired"],
                          "scene_global_cloud":s["global_scene_cloud_cover"]})
            try:
                item=get_scene(s["stac_id"])
                if not shape(item["geometry"]).covers(Point(r["lon"],r["lat"])):
                    raise ValueError("STAC footprint does not contain centroid")
                assets=item.get("assets") or {}
                qa=assets.get("qa_pixel") or assets.get("qa")
                if not qa or not qa.get("href"):raise ValueError("QA_PIXEL asset absent")
                entry["asset_host"]=urlparse(qa["href"]).hostname
                entry.update(qa_from_cog(qa["href"],r["lat"],r["lon"]))
                entry["status"]="ACTUAL_QA_21X21_READ"
            except Exception as e:
                entry["status"]="HOLD_QA_SOURCE_PIXELS"
                entry["error"]=f"{type(e).__name__}: {e}"[:250]
        result["source_seasons"][label]=entry
    result["n_actual_qa_seasons"]=sum(v["status"]=="ACTUAL_QA_21X21_READ"
                                      for v in result["source_seasons"].values())
    result["limits"]=[
      "Technical pilot of one observed A-to-P site, not a representative land-response sample.",
      "QA snow means possibly seasonal snow, not glacial ice; QA clear does not mean bare rock.",
      "One scene per season cannot resolve ice retreat from summer snow changes.",
      "Original AADC site point is a geographic centroid, not the actual nest patch.",
      "No establishment rate, causal island effect, oceanic forcing, or p-value estimated."]
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--original-stac-json",type=Path,required=True)
    a.add_argument("--out-json",type=Path,required=True)
    x=a.parse_args()
    try:r=audit(x.original_stac_json)
    except Exception as e:r={"status":"HOLD_QA_PILOT_SOURCE","reason":f"{type(e).__name__}: {e}"[:250]}
    x.out_json.parent.mkdir(parents=True,exist_ok=True)
    x.out_json.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":r["status"],"n_actual_qa_seasons":r.get("n_actual_qa_seasons"),
                      "seasons":{k:{"status":v["status"],"error":v.get("error")}
                                 for k,v in r.get("source_seasons",{}).items()}},sort_keys=True))
if __name__=="__main__":main()
