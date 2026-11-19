#!/usr/bin/env python3
"""Audit actual local Landsat QA for all 8 source scene-paired AADC transitions.

Frozen all-16 AADC original A->P event roster, no outcome subset choice.
Use earliest 12 returned STAC scenes per season, choose min scene-global cloud
with QA band; read actual center-local QA via anonymous Planetary Computer SAS.
This is evidence/measurement feasibility, not a new land ice-to-rock effect.
"""
from __future__ import annotations
import argparse
from collections import defaultdict,Counter
from datetime import datetime,timezone
import json
from pathlib import Path
from shapely.geometry import Point,shape
from scripts.audit_aadc_landsat_qa_via_planetary_computer import (
    get_item, sign_validated_asset, read_qa_chip
)

SOURCE_EVENT_COUNT=16
SOURCE_PAIRED_META_COUNT=8
STAC_SOURCE_RUN=44538120002

def selected_scene(r):
    scenes=[s for s in r.get("scene_first_twelve_by_datetime",[])
            if s.get("qa_pixel_asset_listed") and isinstance(
               s.get("global_scene_cloud_cover"),(int,float))]
    if not scenes:return None
    return min(scenes,key=lambda s:(s["global_scene_cloud_cover"],
                                   s["acquired"],s["stac_id"]))

def index_events(receipt):
    if receipt.get("events_sampled")!=SOURCE_EVENT_COUNT:
        raise ValueError("Immutable all-16 source roster changed")
    result=defaultdict(dict)
    for r in receipt.get("source_site_scene_metadata",[]):
        key=(r["geog_site_id"],r["species_code"],int(r["a_season_start"]))
        label=r["comparison_side"]
        if label in result[key]:raise ValueError("Duplicate original event scene slot")
        result[key][label]=r
    if len(result)!=SOURCE_EVENT_COUNT or any(set(v)!={"reported_A_season","reported_P_season"}
                                               for v in result.values()):
        raise ValueError("Original Landsat source event/season pair metadata incomplete")
    return result

def eligible_source_pairs(events):
    return [(k,v) for k,v in sorted(events.items())
            if all(v[q]["source_status"]=="SCENE_METADATA_PRESENT" and
                   v[q].get("n_scene_items",0)>0
                   for q in ("reported_A_season","reported_P_season"))]

def audit(path):
    receipt=json.loads(path.read_text(encoding="utf-8"))
    idx=index_events(receipt)
    selected=eligible_source_pairs(idx)
    if len(selected)!=SOURCE_PAIRED_META_COUNT:
        raise ValueError("Original 8 two-sided STAC source event pairs drift")
    report={
      "status":"ALL_8_AADC_EVENT_PAIRED_SCENES_LOCAL_QA_SOURCE_ONLY",
      "date_utc":datetime.now(timezone.utc).isoformat(),
      "frozen_original_STAC_source_run":STAC_SOURCE_RUN,
      "original_A_to_P_events":SOURCE_EVENT_COUNT,
      "source_eligible_both_season_scene_pairs":SOURCE_PAIRED_META_COUNT,
      "event_results":[],
      "no_original_science_outcome_effect_fitted":True,
    }
    scene_read_cache={}  # preserve original item provenance, but QA pixel varies by site
    for key,slots in selected:
        row={"site_id":key[0],"species_code":key[1],
             "a_season_start":key[2],"p_season_start":key[2]+1,
             "site_geographic_feature":slots["reported_A_season"]["source_geog_feature"],
             "source_location_is_nest_footprint":False,
             "two_seasons":{}}
        for label in ("reported_A_season","reported_P_season"):
            r=slots[label]
            s=selected_scene(r)
            attempt={"stac_item_id":s.get("stac_id") if s else None,
                     "acquired":s.get("acquired") if s else None,
                     "global_scene_cloud":s.get("global_scene_cloud_cover") if s else None,
                     "first12_only":True}
            if not s:
                attempt["status"]="HOLD_NO_QA_SOURCE_SCENE"
            else:
                try:
                    sceneid=s["stac_id"]
                    item=scene_read_cache.get(sceneid)
                    if item is None:
                        item=get_item(sceneid)
                        scene_read_cache[sceneid]=item
                    lon,lat=float(r["lon"]),float(r["lat"])
                    if not shape(item["geometry"]).covers(Point(lon,lat)):
                        raise ValueError("Original exact scene does not cover source centroid")
                    qa=(item.get("assets") or {}).get("qa_pixel")
                    if not qa or not qa.get("href"):
                        raise ValueError("Original exact PC scene QA asset unavailable")
                    signed,host=sign_validated_asset(qa["href"])
                    attempt["source_asset_public_host"]=host
                    # Signed link is NEVER written into audit JSON or logs.
                    attempt.update(read_qa_chip(signed,lat,lon))
                    attempt["status"]="ACTUAL_LOCAL_QA_READ"
                except Exception as e:
                    attempt["status"]="HOLD_LOCAL_QA_READ"
                    attempt["error"]=f"{type(e).__name__}: {e}"[:190]
            row["two_seasons"][label]=attempt
        actual=all(x["status"]=="ACTUAL_LOCAL_QA_READ"
                   for x in row["two_seasons"].values())
        row["actual_both_seasons_QA_available"]=actual
        if actual:
            fracs=[]
            snow_fractions=[]
            for label in ("reported_A_season","reported_P_season"):
                counts=row["two_seasons"][label]["QA_21x21_counts"]
                usable=counts["usable_qa_pixels"]
                fracs.append(usable/counts["pixel_count"])
                snow_fractions.append(
                    counts["snow_flagged_valid_pixels"]/usable if usable else None)
            row["both_seasons_local_QA_valid_frac"]=fracs
            row["both_seasons_QA_snow_fraction_of_usable"]=snow_fractions
            row["both_seasons_usable_pixel_ratio_ge_80pct"]=all(v>=0.8 for v in fracs)
            row["both_seasons_any_usable_not_snow_flagged"]=all(
                 x is not None and x<1 for x in snow_fractions)
        report["event_results"].append(row)
    counts=Counter(r["site_geographic_feature"] for r in report["event_results"])
    report["summary"]={
      "event_pairs_with_actual_QA_both_seasons":sum(
          r["actual_both_seasons_QA_available"] for r in report["event_results"]),
      "event_pairs_with_both_seasons_80pct_qa_valid":sum(
          r.get("both_seasons_usable_pixel_ratio_ge_80pct",False)
          for r in report["event_results"]),
      "event_pairs_both_seasons_with_any_qa_snow_free_pixels":sum(
          r.get("both_seasons_any_usable_not_snow_flagged",False)
          for r in report["event_results"]),
      "events_by_source_land_category":dict(counts),
      "unique_source_site_ids":len({r["site_id"] for r in report["event_results"]}),
    }
    report["critical_limits"]=[
      "Data source is known AADC reported transitions; no surveyed unoccupied patch risk set was constructed.",
      "Each 21x21 chip is centered on geographical source landmass centroid, NOT exact occupied nest positions.",
      "One min-global-cloud scene from first12 per season; not a complete date/pixel search and not a randomly selected scene.",
      "QA snow may be seasonal; even repeated snow-free satellite pixels at coarse scale cannot prove perennial ice retreat without dated before/after imagery.",
      "STAC scene-global cloud is not patch-local cloud; QA_PIXEL bit values are source sensor quality only.",
      "Original year A->P can be imperfect detection; no 8 independent island colonizations are established.",
      "Original p-values, frozen Paper1/Paper2, and previous stop contracts are unchanged.",
    ]
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--full-stac-source-json",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    try:r=audit(a.full_stac_source_json)
    except Exception as ex:
        r={"status":"HOLD_ALL_8_ACTUAL_PIXEL_SOURCE",
           "error":f"{type(ex).__name__}: {ex}"[:300],
           "biological_effect_fitted":False}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(r,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print(json.dumps({"status":r["status"],"summary":r.get("summary"),
                      "error":r.get("error")},sort_keys=True))

if __name__=="__main__":main()
