#!/usr/bin/env python3
"""Pre/post summer Landsat scene INVENTORY for the 16 high-evidence AADC A->P reports.

Source-only reconnaissance. Original 2025 AADC geog IDs & hard-frozen original
high-evidence events; anonymous Earth Search Landsat Collection 2 Level 2 STAC.
STAC footprints/scene-cloud percentages DO NOT prove cloud-free pixels, bare
rock, ice retreat, or colonization. Do not infer habitat from missing scenes.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date
import hashlib
import io
import json
import math
from pathlib import Path
import time
from urllib.parse import urlparse
import requests
from openpyxl import load_workbook

from scripts.audit_aadc_2025_seabird_riskset_original_schema import SETS, download_original
from scripts.audit_aadc_2025_eight_species_original_riskset import ORIGINAL_SHA256, txt

EVENT_SOURCE_RUN=44530909415
EVENT_SOURCE_ARTIFACT_ID=14534131482
SOURCE_STAC="https://earth-search.aws.element84.com/v1/search"
SOURCE_COLLECTION="landsat-c2-l2"
EXPECTED_EVENTS=16
EXPECTED_SITES=14
MAX_STAC_ITEMS=100
MAX_RESPONSE=8_000_000
MAX_SITE_BOX_HALF_LAT=0.012
MAX_SITE_BOX_HALF_LON=0.022

def read_source_geo():
    spec=SETS["2025_geographic_sites"]
    with requests.Session() as session:
        blob,meta=download_original(session,spec)
    if meta["sha256"]!=ORIGINAL_SHA256["2025_geographic_sites"]:
        raise ValueError("Publisher geographic site SHA drift")
    wb=load_workbook(io.BytesIO(blob),read_only=True,data_only=True)
    try:
        ws=wb["2_geog_sites_all"]
        rows=ws.iter_rows(values_only=True)
        keys=[txt(v).lower() for v in next(rows)]
        need={"geog_site_id","geog_site_latitude","geog_site_longitude",
              "geog_site_feature","sub_group"}
        if not need.issubset(keys):
            raise ValueError(f"Unexpected geographic schema: {keys}")
        names={}
        for row in rows:
            record=dict(zip(keys,row))
            site=txt(record["geog_site_id"])
            if not site:continue
            if site in names:raise ValueError(f"duplicated original site ID {site}")
            names[site]=record
        if len(names)!=7785:
            raise ValueError("AADC geographic candidate site roster drift")
    finally:
        wb.close()
    return names,meta["sha256"]

def read_events(path:Path):
    raw=path.read_bytes()
    s=json.loads(raw)
    if s.get("status")!="AADC_EIGHT_SPECIES_VERIFIED_DETECTION_QUALITY_SOURCE_GATE":
        raise ValueError("Wrong original strict A/P receipt")
    g=s["strict_all_expert_Y_and_high_A_certainty_support"]
    events=g["AP_event_source_rows"]
    if len(events)!=EXPECTED_EVENTS or len({x["geog_site_id"] for x in events})!=EXPECTED_SITES:
        raise ValueError("Immutable 16 observed A/P, 14 original sites drift")
    for x in events:
        if x.get("true_new_settlement_confirmed") is not False:
            raise ValueError("Observed A/P unexpectedly labeled true colonization")
    return sorted(events,key=lambda x:(int(x["season_start"]),x["geog_site_id"],x["species_code"])),hashlib.sha256(raw).hexdigest()

def site_geometry(e,site):
    lat=float(site["geog_site_latitude"])
    lon=float(site["geog_site_longitude"])
    if not (-85<=lat<=-60 and 30<=lon<=150 and math.isfinite(lat) and math.isfinite(lon)):
        raise ValueError(f"Out-of-domain source coordinates {lat} {lon}")
    field=txt(site["geog_site_feature"]).lower()
    if field!=txt(e["geog_site_feature"]).lower():
        raise ValueError(f"Geographical site class drift {e['geog_site_id']}")
    return {"geog_site_id":e["geog_site_id"],
            "species_code":e["species_code"],
            "a_season_start":int(e["season_start"]),
            "p_season_start":int(e["season_next"]),
            "source_geog_feature":field,
            "original_subgroup":txt(site["sub_group"]),
            "lat":lat,"lon":lon,
            "source_location_is_nest_patch_polygon":False}

def season_bounds(start_year:int):
    # Source year (Austral season) y/y+1: November(y)-March(y+1).
    return f"{start_year:04d}-11-01T00:00:00Z/{start_year+1:04d}-03-31T23:59:59Z"

def stac_scene_inventory(session,lat:float,lon:float,year:int)->dict:
    if year < 1984:
        return {"source_status":"OUTSIDE_1984_PLUS_LANDSAT_SOURCE_ERA",
                "n_scene_items":0,"no_scene_is_no_icefree_evidence":True}
    bbox=[round(lon-MAX_SITE_BOX_HALF_LON,6),round(lat-MAX_SITE_BOX_HALF_LAT,6),
          round(lon+MAX_SITE_BOX_HALF_LON,6),round(lat+MAX_SITE_BOX_HALF_LAT,6)]
    body={"collections":[SOURCE_COLLECTION],
          "bbox":bbox,
          "datetime":season_bounds(year),
          "limit":MAX_STAC_ITEMS}
    if urlparse(SOURCE_STAC).hostname!="earth-search.aws.element84.com":
        raise ValueError("Untrusted Earth Search host")
    resp=session.post(SOURCE_STAC,json=body,timeout=(15,45),
                      headers={"User-Agent":"mina-ant-source-landsat-metadata-audit/1.0",
                               "Accept":"application/geo+json,application/json"})
    resp.raise_for_status()
    if len(resp.content)>MAX_RESPONSE:
        raise ValueError("STAC scene metadata response exceeded bounded 8MB")
    result=resp.json()
    if result.get("type")!="FeatureCollection" or not isinstance(result.get("features"),list):
        raise ValueError("STAC result not a FeatureCollection")
    feats=result["features"]
    if len(feats)>MAX_STAC_ITEMS:
        raise ValueError("STAC returned more items than requested")
    years=Counter()
    sensors=Counter()
    scenes=[]
    for feature in feats:
        props=feature.get("properties") or {}
        dt=str(props.get("datetime") or feature.get("datetime") or "")
        if not dt[:4].isdigit():
            raise ValueError("STAC scene missing real acquisition year")
        if not feature.get("id"):
            raise ValueError("STAC scene missing scene ID")
        platform=str(props.get("platform","<missing>"))
        asset_names=set(feature.get("assets") or {})
        # QA_PIXEL is required to determine actual local cloud/shadow/snow.
        # Global scene cloud percentage is not pixel- or patch-level QC.
        qa_present=bool({"qa_pixel","qa"}&asset_names)
        cloud=props.get("eo:cloud_cover")
        years[dt[:4]]+=1
        sensors[platform]+=1
        scenes.append({
          "stac_id":str(feature["id"]),
          "acquired":dt,
          "platform":platform,
          "global_scene_cloud_cover":cloud,
          "qa_pixel_asset_listed":qa_present,
        })
    return {
        "source_status":"SCENE_METADATA_PRESENT" if feats else "NO_SCENE_METADATA",
        "n_scene_items":len(feats),
        "possible_incomplete_first_page":len(feats)>=MAX_STAC_ITEMS or bool(
          [x for x in result.get("links",[]) if x.get("rel")=="next"]),
        "scene_year_histogram":dict(years),
        "platform_histogram":dict(sensors),
        "n_scenes_with_qa_pixel_metadata":sum(bool(x["qa_pixel_asset_listed"]) for x in scenes),
        "scene_first_twelve_by_datetime":sorted(scenes,key=lambda x:x["acquired"])[:12],
        "searched_bbox_lonlat":bbox,
        "searched_season_date_range":body["datetime"],
        "cloud_information_is_only_scene_level":True,
        "original_scene_imagery_downloaded":False,
        "new_bare_rock_verified":False
    }

def audit(event_json:Path,max_events:int):
    events,event_sha=read_events(event_json)
    if not 1<=max_events<=EXPECTED_EVENTS:raise ValueError("max-events out of source contract")
    places,publisher_sha=read_source_geo()
    # Chronologically stratified deterministic pilot: earliest, middle, latest; not based on scene success.
    indices=[round(i*(len(events)-1)/(max_events-1)) for i in range(max_events)] if max_events>1 else [0]
    selected=[events[i] for i in indices]
    itemrows=[]
    errs=Counter()
    with requests.Session() as s:
        for e in selected:
            loc=places.get(e["geog_site_id"])
            if not loc:raise ValueError("Unknown AADC original event geographic site")
            d=site_geometry(e,loc)
            for side,year in (("reported_A_season",d["a_season_start"]),
                              ("reported_P_season",d["p_season_start"])):
                try:
                    reply=stac_scene_inventory(s,d["lat"],d["lon"],year)
                except (requests.RequestException,ValueError,TypeError) as ex:
                    reply={"source_status":"HOLD_STAC_SCENE_ACCESS",
                           "error":f"{type(ex).__name__}: {str(ex)}"[:200]}
                    errs["source_query_error"]+=1
                itemrows.append({**d,"comparison_side":side,"imaging_season_start":year,**reply})
                time.sleep(0.15)
    valid=[x for x in itemrows if x["source_status"]=="SCENE_METADATA_PRESENT"
           and not x.get("possible_incomplete_first_page")]
    bykey={(x["geog_site_id"],x["species_code"],x["a_season_start"]):[]
           for x in itemrows}
    for x in itemrows:
        bykey[(x["geog_site_id"],x["species_code"],x["a_season_start"])].append(x)
    paired=sum(len(v)==2 and all(x in valid for x in v) for v in bykey.values())
    return {
      "status":"LANDSAT_STAC_PILOT_ORIGINAL_SCENE_METADATA_ONLY",
      "sources":{"aadc_original_publisher_geographic_sha256":publisher_sha,
                 "strict_AtoP_original_workflow_run":EVENT_SOURCE_RUN,
                 "strict_AtoP_original_workflow_artifact":EVENT_SOURCE_ARTIFACT_ID,
                 "strict_AtoP_receipt_sha256":event_sha,
                 "landsat_catalog_url":SOURCE_STAC,
                 "landsat_collection":SOURCE_COLLECTION},
      "original_eight_species_AtoP_events":EXPECTED_EVENTS,
      "original_eight_species_AtoP_site_ids":EXPECTED_SITES,
      "events_sampled":len(selected),
      "events_with_complete_scene_metadata_both_seasons":paired,
      "source_queries_run":len(itemrows),
      "source_query_error_counts":dict(errs),
      "source_site_scene_metadata":itemrows,
      "source_inference_boundaries":[
         "Event-driven scene inventory is selection on observed events, not an unoccupied whole habitat risk set.",
         "ASI/AADC source site points are geographic centroids, not mapped nest patch locations.",
         "STAC scene overlap and cloud percentage do not establish local pixel valid reflectance or rock/ice identity.",
         "Without dated DEM and source imagery labels, date-specific ice loss and bare-rock exposure are unverified.",
         "No effect, p-value, climate association, or first true colonization estimated.",
         "Scenes outside archive or absent scenes are missing data, never evidence of historical no land.",
         "AADC 8 species original A->P = 16 reports, not 16 independent colony establishment events.",
         "NASA NSIDC-0794 annual 240m coastal masks constrain many islands to constant area and are not usable for newly exposed island-rock trajectories."
      ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--strict-aadc-events-json",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--max-events",type=int,default=2)
    a=p.parse_args()
    try:
        report=audit(a.strict_aadc_events_json,a.max_events)
    except Exception as e:
        report={"status":"HOLD_EVENT_GEO_OR_STAC_SOURCE",
                "reason":f"{type(e).__name__}: {str(e)}"[:300],
                "ecological_effect_fitted":False}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({"status":report["status"],"events_sampled":report.get("events_sampled"),
                      "paired_scene_metadata":report.get("events_with_complete_scene_metadata_both_seasons"),
                      "query_errors":report.get("source_query_error_counts")},sort_keys=True))

if __name__=="__main__":
    main()
