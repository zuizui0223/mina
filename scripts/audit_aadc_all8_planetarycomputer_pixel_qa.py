#!/usr/bin/env python3
"""Read-only expansion of fixed AADC Landsat QA_PIXEL site-buffer source gate.

Evaluate ALL 8 original source-verified A->P observed events for which both
adjacent austral seasons have public Landsat scene metadata, 2 lowest-global-
cloud signed Planetary Computer QA_PIXEL 5x5 windows per event-season.
The 8-event roster is fixed from original 16-event source before inspecting
any pixel QA; no biology outcomes or new habitat effect tests are fitted.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
from scripts.audit_aadc_planetarycomputer_pixel_qa import select_scenes, STAC

EXPECTED={
 ("IS_70749","SK",2008),("R_223","SK",2008),
 ("IS_70714","SK",2010),("IS_70731","SK",2011),
 ("IS_70715","ADP",2014),("IS_70729","SK",2014),
 ("IS_121","ADP",2016),("IS_105","ADP",2017)
}
SOURCE_RUN=44850629480
EXPECTED_SOURCE_SHA="988a66154633202af46495b2f6b46cc02e51363451ebc5754a6435a0825f6950"

def source_roster(path:Path):
    import hashlib
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SOURCE_SHA:
        raise ValueError("Frozen original 16-event Landsat source SHA changed")
    j=json.loads(raw)
    if j.get("events_sampled")!=16 or j.get("source_queries_run")!=32:
        raise ValueError("Original source event-season count drift")
    rows=j["source_site_scene_metadata"]
    grouped={}
    for row in rows:
        key=(str(row["geog_site_id"]),str(row["species_code"]),int(row["a_season_start"]))
        grouped.setdefault(key,[]).append(row)
    if len(grouped)!=16 or any(len(x)!=2 for x in grouped.values()):
        raise ValueError("Original site event-season duplications changed")
    selected={}
    for key,rr in grouped.items():
        sides={r["comparison_side"] for r in rr}
        if sides!={"reported_A_season","reported_P_season"}:
            raise ValueError("Original expected A/P source observations missing")
        if all(int(r.get("n_scene_items",0))>0 for r in rr):
            selected[key]={"lat":float(rr[0]["lat"]),"lon":float(rr[0]["lon"]),
                           "sub_group":rr[0]["original_subgroup"]}
    if set(selected)!=EXPECTED:
        raise ValueError(f"Original fixed 8-event imagery roster changed {sorted(selected)}")
    return selected

def audit(path:Path):
    from pystac_client import Client
    selected=source_roster(path)
    client=Client.open(STAC)
    source=[]
    for (site,sp,y),pos in sorted(selected.items()):
        out={"source_site":site,"source_species":sp,"A_year":y,
             "P_year":y+1,"sub_group":pos["sub_group"],
             "site_center_is_nest_patch_polygon":False,"source_seasons":[]}
        for year,label in ((y,"A_reported"),(y+1,"P_reported")):
            try:
                scenes,meta=select_scenes(client,pos["lat"],pos["lon"],year)
                out["source_seasons"].append({
                   "season":year,"state_label":label,
                   "stac_query":meta,"source_scenes":scenes})
            except Exception as e:
                out["source_seasons"].append({
                   "season":year,"state_label":label,
                   "source_status":"HOLD_STAC_OR_ASSET",
                   "source_error_type":type(e).__name__})
        source.append(out)
    counts=Counter()
    any_site=set()
    unique_scenes=set()
    both=0
    for e in source:
        positive=[]
        for q in e["source_seasons"]:
            scenes=q.get("source_scenes",[])
            valid=[s for s in scenes if s["local_qa"].get("status")=="SOURCE_PIXEL_QA_READ"]
            possible=[s for s in valid if s["local_qa"]["visible_non_snow_non_water_candidate"]>0]
            counts["QA_scene_attempts"]+=len(scenes)
            counts["QA_scene_success"]+=len(valid)
            counts["QA_scene_any_visible_land_not_snow_water"]+=len(possible)
            counts["source_season_windows"]+=1
            counts["season_with_readable_QA"]+=int(bool(valid))
            counts["season_with_any_candidate_visible_nonsnow_nonwater"]+=int(bool(possible))
            positive.append(bool(possible))
            unique_scenes.update(s["source_stac_item_id"] for s in scenes)
        if len(positive)==2 and all(positive):
            both+=1
            any_site.add(e["source_site"])
        if any(positive):any_site.add(e["source_site"])
    return {
       "status":"ALL_EIGHT_2SEASON_PIXEL_QA_SOURCE_GATE_COMPLETE",
       "original_source_run":SOURCE_RUN,
       "original_source_sha256":EXPECTED_SOURCE_SHA,
       "PC_source":STAC,
       "input_events":16,
       "fixed_usable_scene_metadata_events":8,
       "fixed_original_event_roster":[list(x) for x in sorted(EXPECTED)],
       "source_scene_checks":source,
       "summary":{
           **dict(counts),
           "distinct_stac_scene_ids_in_source_checks":len(unique_scenes),
           "events_with_candidate_visible_nonsnow_nonwater_in_both_seasons":both,
           "sites_with_any_candidate_visible_nonsnow_nonwater":sorted(any_site),
       },
       "ecological_effect_fitted":False,
       "true_new_rock_exposure_identified":False,
       "actual_nest_patch_identified":False,
       "limitations":[
           "AADC geographic point is not the true nest polygon and source landmass is not confirmed physical island.",
           "QA_PIXEL bit5=0 does NOT prove bare rock and bit5=1 does not mean permanently glaciated land.",
           "Pairwise source scene checks use 2 lowest global cloud rank per season, and shared scenes are not independent replicates.",
           "Earlier 16 A->P are observations not ecological colonization; no new ice area or population effect calculated.",
           "No actual raw multispectral reflectance classification or image label QA has been undertaken."
       ],
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--stac-all16",type=Path,required=True)
    a.add_argument("--out-json",type=Path,required=True)
    args=a.parse_args()
    try:out=audit(args.stac_all16)
    except Exception as e:
        out={"status":"HOLD_ALL_EIGHT_PIXEL_QA_OR_SOURCE",
             "error_type":type(e).__name__,
             "ecological_effect_fitted":False}
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"summary":out.get("summary"),
                      "error_type":out.get("error_type")},sort_keys=True))
if __name__=="__main__":main()
