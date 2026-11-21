#!/usr/bin/env python3
"""Read-only public PC Landsat QA_PIXEL at two frozen AADC site centroids.

Uses signed COG links from Microsoft Planetary Computer STAC, not USGS
anonymous S3 Requester Pays. No actual nest patch or new rock is identified.
Temporary signed URLs are never saved in results.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from urllib.parse import urlparse
from scripts.audit_aadc_landsat_pixel_qa_pilot import PILOTS, classify_pixel_qa, validate_source_receipt

STAC="https://planetarycomputer.microsoft.com/api/stac/v1"

def check_asset(href):
    x=urlparse(href)
    return x.scheme=="https" and bool(x.hostname) and x.hostname.endswith(".blob.core.windows.net") and "sig=" in x.query

def inspect_signed_qa(href,lat,lon):
    if not check_asset(href):
        return {"status":"HOLD_NOT_SIGNED_PUBLISHER_ASSET"}
    try:
        import rasterio
        from rasterio.windows import Window
        from pyproj import Transformer
        env={"GDAL_DISABLE_READDIR_ON_OPEN":"EMPTY_DIR","GDAL_HTTP_MAX_RETRY":"1",
             "CPL_VSIL_CURL_ALLOWED_EXTENSIONS":".tif,.TIF"}
        with rasterio.Env(**env):
            with rasterio.open(href) as ds:
                if ds.crs is None:return {"status":"HOLD_MISSING_CRS"}
                x,y=Transformer.from_crs("EPSG:4326",ds.crs,always_xy=True).transform(lon,lat)
                row,col=ds.index(x,y)
                if row<2 or col<2 or row>=ds.height-2 or col>=ds.width-2:
                    return {"status":"HOLD_CENTROID_OUTSIDE_SCENE"}
                arr=ds.read(1,window=Window(col-2,row-2,5,5))
                if arr.shape!=(5,5):return {"status":"HOLD_INCOMPLETE_5X5"}
                flags=[classify_pixel_qa(int(v)) for v in arr.flat]
                return {
                    "status":"SOURCE_PIXEL_QA_READ",
                    "number_pixels":25,
                    "non_fill_cloud_shadow":sum(a["not_fill_cloud_or_shadow"] for a in flags),
                    "visible_non_snow_non_water_candidate":sum(a["candidate_visible_non_snow_non_water"] for a in flags),
                    "snow_ice_qa_pixels":sum(a["snow_or_ice_flag"] for a in flags),
                    "water_qa_pixels":sum(a["water_flag"] for a in flags),
                    "fill_qa_pixels":sum(a["fill"] for a in flags),
                    "center_qa_value":int(arr[2,2]),
                    "pixel_size":[abs(ds.transform.a),abs(ds.transform.e)],
                    "scene_crs":str(ds.crs),
                    "proves_new_bare_rock":False,
                }
    except Exception as e:
        return {"status":"HOLD_SIGNED_COG_IO","error_class":type(e).__name__,"signed_url_saved":False}

def select_scenes(client,lat,lon,yr):
    import planetary_computer
    search=client.search(collections=["landsat-c2-l2"],
        bbox=[lon-.022,lat-.012,lon+.022,lat+.012],
        datetime=f"{yr}-11-01T00:00:00Z/{yr+1}-03-31T23:59:59Z",
        max_items=100,limit=100)
    items=list(search.items())
    candidates=[]
    for item in items:
        qa=item.assets.get("qa_pixel")
        if qa is None:continue
        cloud=item.properties.get("eo:cloud_cover")
        cloud=float(cloud) if cloud is not None else 999
        candidates.append((cloud,item))
    candidates.sort(key=lambda z:(z[0],z[1].id))
    result=[]
    for cloud,item in candidates[:2]:
        signed=planetary_computer.sign(item)
        qa=signed.assets.get("qa_pixel")
        href=qa.href if qa else ""
        result.append({
            "source_stac_item_id":item.id,
            "source_platform":item.properties.get("platform"),
            "global_scene_cloud_percent":cloud if cloud!=999 else None,
            "qa_asset_host":urlparse(href).hostname,
            "local_qa":inspect_signed_qa(href,lat,lon),
        })
    return result,{"stac_first_100_items":len(items),"with_QA_asset":len(candidates),
                   "pagination_possible":len(items)>=100}

def run(source_path):
    from pystac_client import Client
    points=validate_source_receipt(source_path)
    client=Client.open(STAC)
    cases=[]
    for code,sp,start in PILOTS:
        d=points[(code,sp,start)]
        value={"site":code,"species":sp,"reported_A_year":start,
               "reported_P_year":start+1,"original_region":d["publisher_subgroup"],
               "is_verified_nest_patch":False,"years":[]}
        for label,year in (("A",start),("P",start+1)):
            try:
                rows,meta=select_scenes(client,d["lat"],d["lon"],year)
                value["years"].append({"state_label":label,"year":year,
                                       "stac_source":meta,"qa":rows})
            except Exception as err:
                value["years"].append({"state_label":label,"year":year,
                                       "status":"HOLD_PC_SEARCH_OR_SIGN",
                                       "error_class":type(err).__name__})
        cases.append(value)
    n=sum(x["local_qa"].get("status")=="SOURCE_PIXEL_QA_READ"
          for case in cases for y in case["years"] for x in y.get("qa",[]))
    complete=sum(all(any(x["local_qa"].get("status")=="SOURCE_PIXEL_QA_READ"
                         for x in y.get("qa",[])) for y in case["years"]) and
                 len(case["years"])==2 for case in cases)
    return {
        "status":"PC_PUBLIC_SIGNED_QA_SITE_SOURCE_GATE",
        "original_16_event_scan_run_id":44850629480,
        "source_stac":STAC,"source_collection":"landsat-c2-l2",
        "source_regions":2,"source_cases":cases,
        "qa_pixel_scene_successes":n,
        "cases_with_qa_read_in_both_years":complete,
        "signed_urls_saved":False,
        "ice_to_new_bare_rock_verified":False,
        "true_colonization_inferred":False,
        "ecological_effect_fitted":False,
        "limits":["AADC geog-site coordinates are NOT exact nest patch polygons.",
                  "QA_PIXEL not fill/cloud/shadow/snow/water is NOT proven bare rock.",
                  "Only two preselected source cases; not an inferential sample.",
                  "Before/after scene selection does not verify change at actual nests."],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stac-16-json",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    try:out=run(a.stac_16_json)
    except Exception as e:
        out={"status":"HOLD_PC_SOURCE","error_class":type(e).__name__,
             "ecological_effect_fitted":False}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":out["status"],"qa_success":out.get("qa_pixel_scene_successes"),
                      "paired_cases":out.get("cases_with_qa_read_in_both_years")},sort_keys=True))

if __name__=="__main__":main()
