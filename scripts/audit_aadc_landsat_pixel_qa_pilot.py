#!/usr/bin/env python3
"""Small predeclared read-only pixel QA pilot at two original Antarctic AADC site points.

Inputs: original-source-pinned 16-event STAC metadata receipt (GitHub Actions).
The catalog lookup intentionally selects two different AADC regions/periods:
DUM 2008->2009 SK IS_70749, LUT 2017->2018 ADP IS_105.
For each summer, query original Landsat C2L2 catalog and inspect the two
least-globally-cloudy first-page QA_PIXEL COG assets, up to 8 scenes total.

Crucial: geographic point is not a verified nest patch; QA flag is not
land/rock exposure, and a 2008->2009 A/P transition is not true colonization.
Do not infer bare rock from bit 5 snow=0 (spectral/geom validation needed).
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
from urllib.parse import urlparse
import requests
import numpy as np
from pyproj import Transformer

SRC="https://earth-search.aws.element84.com/v1/search"
COLLECTION="landsat-c2-l2"
SOURCE_WORKFLOW_RUN=44850629480
PILOTS=(("IS_70749","SK",2008),("IS_105","ADP",2017))
MAX_SCENES_PER_SIDE=2
WINDOW_SIZE=5
BAD_FLAGS=(0,1,3,4)
QA_COG_DOMAINS=("landsatlook.usgs.gov", "usgs-landsat.s3.us-west-2.amazonaws.com",
                 "usgs-landsat.s3.amazonaws.com", "s3.us-west-2.amazonaws.com",
                 "storage.googleapis.com")

def classify_pixel_qa(value:int)->dict:
    v=int(value)
    return {
       "fill": bool(v&1),
       "dilated_cloud":bool(v&(1<<1)),
       "cloud":bool(v&(1<<3)),
       "cloud_shadow":bool(v&(1<<4)),
       "snow_or_ice_flag":bool(v&(1<<5)),
       "water_flag":bool(v&(1<<7)),
       "not_fill_cloud_or_shadow": not any(v&(1<<i) for i in BAD_FLAGS),
       "candidate_visible_non_snow_non_water": not any(
            v&(1<<i) for i in (*BAD_FLAGS,5,7)),
    }

def validate_source_receipt(path:Path):
    d=json.loads(path.read_text(encoding="utf-8"))
    if (d.get("status")!="LANDSAT_STAC_PILOT_ORIGINAL_SCENE_METADATA_ONLY"
        or d.get("events_sampled")!=16
        or d.get("source_queries_run")!=32
        or d.get("events_with_any_scene_metadata_in_both_seasons")!=8):
        raise ValueError("Not the original verified all-16 AADC STAC source receipt")
    rows=d["source_site_scene_metadata"]
    if len(rows)!=32:
        raise ValueError("Original source event-season rows drift")
    source={}
    for site,sp,y in PILOTS:
        found=[r for r in rows if r["geog_site_id"]==site
            and r["species_code"]==sp and int(r["a_season_start"])==y]
        if len(found)!=2 or {r["comparison_side"] for r in found}!={
             "reported_A_season","reported_P_season"}:
             raise ValueError(f"Selected source event-season missing: {site}")
        if any(r.get("n_scene_items",0)<=0 for r in found):
            raise ValueError(f"Two-source-season candidate imagery unexpectedly absent: {site}")
        source[(site,sp,y)]={
            "lat":float(found[0]["lat"]),"lon":float(found[0]["lon"]),
            "a_year":y,"p_year":y+1,
            "publisher_subgroup":found[0]["original_subgroup"],
        }
    return source

def source_scenes(session,lat:float,lon:float,y:int):
    bbox=[round(lon-0.022,6),round(lat-0.012,6),
          round(lon+0.022,6),round(lat+0.012,6)]
    body={"collections":[COLLECTION],"bbox":bbox,
          "datetime":f"{y}-11-01T00:00:00Z/{y+1}-03-31T23:59:59Z",
          "limit":100}
    resp=session.post(SRC,json=body,timeout=(15,55))
    resp.raise_for_status()
    if len(resp.content)>8_000_000:
        raise ValueError("Oversized STAC first-page JSON")
    data=resp.json()
    if data.get("type")!="FeatureCollection" or not isinstance(data.get("features"),list):
        raise ValueError("Original Landsat STAC query format not FeatureCollection")
    items=[]
    for feat in data["features"]:
        cloud=feat.get("properties",{}).get("eo:cloud_cover")
        cloud=float(cloud) if cloud is not None else math.inf
        assets=feat.get("assets") or {}
        qa=assets.get("qa_pixel") or assets.get("qa")
        if not isinstance(qa,dict) or not qa.get("href"):
            continue
        items.append({
            "id":feat["id"],"date":str(feat.get("properties",{}).get("datetime","")),
            "cloud_global_percent":cloud,
            "qa_href":qa["href"],
            "platform":str(feat.get("properties",{}).get("platform","")),
        })
    items.sort(key=lambda q:(q["cloud_global_percent"],q["date"],q["id"]))
    return items[:MAX_SCENES_PER_SIDE],{
        "first_page_item_count":len(data["features"]),
        "first_page_has_next_link":any(z.get("rel")=="next" for z in data.get("links",[])),
        "scenes_with_qa_asset_on_first_page":len(items),
    }

def permitted_asset(href:str)->bool:
    url=urlparse(href)
    if url.scheme=="s3":
        return url.netloc in ("usgs-landsat","usgs-landsat-collection-2")
    return url.scheme=="https" and (
        url.hostname in QA_COG_DOMAINS
        or bool(url.hostname and url.hostname.endswith(".landsatlook.usgs.gov"))
    )

def read_source_qa_window(href:str,lat:float,lon:float):
    """Read 5x5 local QA_PIXEL COG window, not complete imagery or rock labels."""
    if not permitted_asset(href):
        return {"status":"HOLD_ASSET_HOST_UNVERIFIED",
                "asset_hostname":urlparse(href).hostname}
    # Lazy import allows synthetic pixel decoder tests even without Rasterio.
    import rasterio
    from rasterio.windows import Window
    from rasterio.errors import RasterioIOError
    env=dict(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
             GDAL_HTTP_MAX_RETRY="1",
             GDAL_HTTP_RETRY_DELAY="1",
             CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF,.tif",
             AWS_NO_SIGN_REQUEST="YES")
    try:
        with rasterio.Env(**env):
            with rasterio.open(href) as ds:
                if ds.crs is None:
                    return {"status":"HOLD_IMAGE_CRS_UNKNOWN"}
                transformer=Transformer.from_crs("EPSG:4326",ds.crs,always_xy=True)
                px,py=transformer.transform(lon,lat)
                r,c=ds.index(px,py)
                n=WINDOW_SIZE
                if r-n//2<0 or c-n//2<0 or r+n//2>=ds.height or c+n//2>=ds.width:
                    return {"status":"HOLD_SITE_OUTSIDE_QA_RASTER_FOOTPRINT"}
                vals=ds.read(1,window=Window(c-n//2,r-n//2,n,n))
                if vals.shape!=(n,n):
                    return {"status":"HOLD_LOCAL_QA_CROP_INCOMPLETE"}
                flat=[classify_pixel_qa(v) for v in vals.ravel()]
                return {
                    "status":"PIXEL_QA_READ_SUCCESS_NO_ROCK_CLASSIFICATION",
                    "site_center_qa_pixel":int(vals[n//2,n//2]),
                    "qa_window_side_pixels":n,
                    "qa_total_pixels":n*n,
                    "qa_non_fill_cloud_shadow_count":sum(x["not_fill_cloud_or_shadow"] for x in flat),
                    "qa_possible_visible_non_snow_non_water_count":sum(
                         x["candidate_visible_non_snow_non_water"] for x in flat),
                    "qa_snow_or_ice_flag_count":sum(x["snow_or_ice_flag"] for x in flat),
                    "qa_water_flag_count":sum(x["water_flag"] for x in flat),
                    "qa_fill_flag_count":sum(x["fill"] for x in flat),
                    "qa_cloud_flag_count":sum(x["cloud"] for x in flat),
                    "qa_dilated_cloud_flag_count":sum(x["dilated_cloud"] for x in flat),
                    "qa_shadow_flag_count":sum(x["cloud_shadow"] for x in flat),
                    "raster_pixel_size_units":[float(abs(ds.transform.a)),float(abs(ds.transform.e))],
                    "raster_crs":str(ds.crs),
                    "qa_is_not_bare_rock_ground_truth":True,
                }
    except (RasterioIOError, OSError, ValueError, RuntimeError) as e:
        return {"status":"HOLD_REMOTE_QA_ASSET_IO",
                "reason":f"{type(e).__name__}: {str(e)}"[:280]}

def run(source_path:Path):
    candidates=validate_source_receipt(source_path)
    out={"status":"TWO_SOURCE_CASES_QA_PIXEL_PILOT",
         "original_event_source_workflow":SOURCE_WORKFLOW_RUN,
         "selected_source_events":[list(x) for x in PILOTS],
         "scene_selection":"first STAC page, two lowest global cloud percentage per season, without inspecting pixel QA or outcomes",
         "qa_flags":"USGS C2 QA_PIXEL fill[0],dilated-cloud[1],cloud[3],shadow[4],snow/ice[5],water[7]; do NOT use Clear bit6",
         "uses_true_nest_patch_polygon":False,
         "source_rock_exposure_verified":False,
         "true_colonization_verified":False,
         "biological_effect_fitted":False,
         "event_sources":[]}
    with requests.Session() as session:
        for key,c in candidates.items():
            source_event={"geog_site_id":key[0],"species":key[1],
                          "a_year":key[2],"p_year":key[2]+1,
                          "region":c["publisher_subgroup"],
                          "lat":c["lat"],"lon":c["lon"],
                          "seasons":[]}
            for side,yr in (("reported_A",c["a_year"]),("reported_P",c["p_year"])):
                try:
                    scenes,catalog=source_scenes(session,c["lat"],c["lon"],yr)
                except (ValueError,requests.RequestException) as exc:
                    source_event["seasons"].append({
                        "side":side,"year":yr,"status":"HOLD_STAC_QUERY",
                        "reason":f"{type(exc).__name__}: {str(exc)}"[:220]})
                    continue
                selected=[]
                for scene in scenes:
                    local=read_source_qa_window(scene["qa_href"],c["lat"],c["lon"])
                    selected.append({
                        "stac_id":scene["id"],"acquisition_datetime":scene["date"],
                        "platform":scene["platform"],
                        "global_cloud_percent":(
                            scene["cloud_global_percent"]
                            if math.isfinite(scene["cloud_global_percent"]) else None),
                        "source_qa_asset_hostname":urlparse(scene["qa_href"]).hostname,
                        "local_pixel_QA":local,
                    })
                source_event["seasons"].append({
                    "side":side,"year":yr,"catalog_first_page":catalog,
                    "selected_original_scene_count":len(selected),
                    "original_scene_QA_checks":selected,
                })
            out["event_sources"].append(source_event)
    out["summary"]={
        "source_cases":len(out["event_sources"]),
        "scene_qa_checks_attempted":sum(
             len(s.get("original_scene_QA_checks",[]))
             for e in out["event_sources"] for s in e["seasons"]),
        "scene_local_QA_success":sum(
             q["local_pixel_QA"]["status"]=="PIXEL_QA_READ_SUCCESS_NO_ROCK_CLASSIFICATION"
             for e in out["event_sources"] for s in e["seasons"]
             for q in s.get("original_scene_QA_checks",[])),
        "cases_with_any_readable_QA_both_seasons":sum(
             all(any(q["local_pixel_QA"]["status"]=="PIXEL_QA_READ_SUCCESS_NO_ROCK_CLASSIFICATION"
                     for q in s.get("original_scene_QA_checks",[]))
                  for s in e["seasons"]) and len(e["seasons"])==2
             for e in out["event_sources"]),
    }
    out["limitations"]=[
       "The AADC original geog-site point can be ocean, hillside, large island centroid or offshore, not nest-patch boundary.",
       "USGS QA_PIXEL snow/ice/clear/water flags cannot independently prove new exposed rock.",
       "Low scene-wide cloud percentage can still have missing/cloud pixels at the AADC site.",
       "Landsat 7 has post-2003 scanline gaps; mask fill and cloud flags at original local pixels.",
       "Two selected source cases are a technical pilot only; not a random or inferential colony subset.",
       "No dynamic ice retreat, nest occupancy process, or independent unoccupied habitat survey has been fitted."
    ]
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stac-16-receipt",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    args=p.parse_args()
    try: result=run(args.stac_16_receipt)
    except Exception as exc:
        result={"status":"HOLD_ORIGINAL_SOURCE_OR_QA_PILOT",
                "reason":f"{type(exc).__name__}: {str(exc)}"[:360],
                "biological_effect_fitted":False}
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"summary":result.get("summary"),
                      "reason":result.get("reason")},sort_keys=True))

if __name__=="__main__":
    main()
