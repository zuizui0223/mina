#!/usr/bin/env python3
"""Recover ONLY 3 AADC source QA pairs previously blocked by 429; 1 PC dataset token.

No repeat image selection or ecological outcome search. Uses the same six
exact scene IDs already selected with pre-locked metadata rule, and publisher
PC collection-scoped SAS, not separate per-scene signing calls.
Never persist credential, signed URL, local nest inference, or effect statistic.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import requests
from urllib.parse import urlparse
from scripts.audit_aadc_landsat_qa_via_planetary_computer import (
    get_item,read_qa_chip
)

TOKEN_URL="https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2"
EXPECTED_BLOCKED_SITES={"IS_70731","IS_70749","R_223"}
SOURCE_ALL8_RUN=44540867647
SOURCE_ALL16_RUN=44538120002

def read_sources(previous:Path,all16:Path):
    old=json.loads(previous.read_text())
    full=json.loads(all16.read_text())
    if old["summary"]["event_pairs_with_actual_QA_both_seasons"]!=5 or old["summary"]["unique_source_site_ids"]!=8:
        raise ValueError("Original 5/8 QA source results drift")
    if full.get("events_sampled")!=16:
        raise ValueError("Wrong original full source event roster")
    old_sites={x["site_id"]:x for x in old["event_results"]
               if not x["actual_both_seasons_QA_available"]}
    if set(old_sites)!=EXPECTED_BLOCKED_SITES:
        raise ValueError(f"Expected exactly 3 old provider-limited cases, got {sorted(old_sites)}")
    for row in old_sites.values():
        if any(v["status"]!="HOLD_LOCAL_QA_READ" or "429" not in v.get("error","")
               for v in row["two_seasons"].values()):
            raise ValueError("Original QA failure is not provider per-scene sign rate-limiting")
    geo={}
    for r in full["source_site_scene_metadata"]:
        if r["geog_site_id"] in EXPECTED_BLOCKED_SITES:
            key=(r["geog_site_id"],r["species_code"],r["a_season_start"],r["comparison_side"])
            if key in geo:raise ValueError("Duplicate fixed AADC site/season identity")
            geo[key]=(float(r["lat"]),float(r["lon"]))
    return old_sites,geo

def get_collection_sas_token():
    r=requests.get(TOKEN_URL,timeout=(15,40),
                   headers={"User-Agent":"mina-anonymous-PC-collection-token/1.0"})
    r.raise_for_status()
    obj=r.json()
    token=obj.get("token","")
    if not token or not all(s in token for s in ("se=","sig=")):
        raise ValueError("PC collection token not supplied in expected form")
    return token  # only in local process memory

def attach_original_container_sas(href:str,token:str):
    u=urlparse(href)
    if (u.scheme!="https" or u.hostname!="landsateuwest.blob.core.windows.net"
        or not u.path.startswith("/landsat-c2/") or u.query):
        raise ValueError("PC original asset is not expected Landsat Azure collection path")
    if not token.startswith("se="):
        raise ValueError("Missing PC authorization expiry")
    return href+"?"+token

def error_class(exc):
    # NEVER return a SAS query string or internal URL to artifacts/logs.
    code=re.search(r"\b(400|401|403|404|408|429|500|502|503)\b",str(exc))
    return {"type":type(exc).__name__,
            "http_code":int(code.group(1)) if code else None}

def audit(previous:Path,full:Path):
    blocked,geo=read_sources(previous,full)
    result={"status":"ONE_COLLECTION_TOKEN_SOURCE_ONLY_429_RECOVERY",
            "source_previous_all8_run":SOURCE_ALL8_RUN,
            "source_original_all16_run":SOURCE_ALL16_RUN,
            "expected_old_429_site_ids":sorted(EXPECTED_BLOCKED_SITES),
            "collection_token_requested_once":True,
            "collection_token_or_signed_assets_exported":False,
            "original_five_good_cases_unmodified":True,
            "new_rock_or_true_colonization_claim":False,
            "recoveries":[]}
    try: token=get_collection_sas_token()
    except Exception as e:
        result["status"]="HOLD_ANONYMOUS_PC_COLLECTION_TOKEN"
        result["token_request_error"]=error_class(e)
        return result
    for site in sorted(blocked):
        event=blocked[site]
        q={"site_id":site,"species":event["species_code"],
           "a_season_start":event["a_season_start"],"two_seasons":{}}
        for label in ("reported_A_season","reported_P_season"):
            original=event["two_seasons"][label]
            sceneid=original["stac_item_id"]
            out={"original_scene_id":sceneid,"original_image_date":original["acquired"],
                 "selected_scene_changed":False}
            try:
                key=(site,event["species_code"],event["a_season_start"],label)
                lat,lon=geo[key]
                item=get_item(sceneid)
                qa=(item.get("assets") or {}).get("qa_pixel")
                if not qa or not qa.get("href"):
                    raise ValueError("Exact original item lacks QA asset")
                signed=attach_original_container_sas(qa["href"],token)
                out.update(read_qa_chip(signed,lat,lon))
                out["status"]="ACTUAL_QA_PIXELS_RECOVERED"
            except Exception as e:
                out["status"]="HOLD_QA_AFTER_COLLECTION_TOKEN"
                out["error"]=error_class(e)
            q["two_seasons"][label]=out
        q["both_seasons_actual"]=all(v["status"]=="ACTUAL_QA_PIXELS_RECOVERED"
                                      for v in q["two_seasons"].values())
        result["recoveries"].append(q)
    result["newly_recovered_event_pairs"]=sum(x["both_seasons_actual"] for x in result["recoveries"])
    result["final_source_event_pairs_with_actual_qa"]=5+result["newly_recovered_event_pairs"]
    result["caveats"]=[
      "An original Landsat scene or QA flag does not imply icefree rock, new land or new penguin occupation.",
      "ASI site centroid is not the exact nest patch; no temporal exposure boundary polygon.",
      "Collection-scoped SAS is used once to avoid repeatedly requesting signing tokens after a provider 429.",
      "No previous five valid QA source cases are overwritten, no changed scene selection, and no model or p-value fitted."
    ]
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--all8-qa-json",required=True,type=Path)
    p.add_argument("--all16-scene-json",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    try:r=audit(a.all8_qa_json,a.all16_scene_json)
    except Exception as e:
        r={"status":"HOLD_PREVIOUS_SOURCE_QA_PROVENANCE","error":error_class(e),
           "biological_effect_fitted":False}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":r["status"],
                      "n_newly_recovered":r.get("newly_recovered_event_pairs"),
                      "final_source_event_pairs_with_actual_qa":r.get("final_source_event_pairs_with_actual_qa"),
                      "token_request_error":r.get("token_request_error")},sort_keys=True))
if __name__=="__main__":main()
