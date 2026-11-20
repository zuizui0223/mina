#!/usr/bin/env python3
"""Independent VHR INEX area years 2013/2017/2018 × matched L8 native QA source gate.
Reads only true USGS QA_PIXEL/QA_RADSAT at original, old-guano geolocation; no
new guano truth, spectral reflectance, optical isotope or polynya regression.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import pandas as pd
from pilot_original88_fixed_guano_L8_QA_ONLY_2018_20261120 import one,source_bytes
from pilot_original88_fixed_guano_L8_QA_ONLY_2018_20261120 import SOURCE_OLD_GUANO_GEOGRAPHY_SHA256,OLD_COORD_CSV
CROSSWALK_SHA="e439ae605988981b807954b763e145bdd9083f7beeb5f4d18ab22ec61e65c688"
CROSSWALK_CSV="INEX_three_independent_VHR_dates_L8_original_scene_source_only.csv"

def load_crosswalk(p):
    b=Path(p).read_bytes()
    if hashlib.sha256(b).hexdigest()!=CROSSWALK_SHA:raise ValueError("Verified INEX crosswalk SHA drift")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip():raise ValueError("Crosswalk ZIP CRC failed")
        n=[n for n in z.namelist() if n==CROSSWALK_CSV or n.endswith("/"+CROSSWALK_CSV)]
        if len(n)!=1:raise ValueError("Source crosswalk member missing")
        d=pd.read_csv(io.BytesIO(z.read(n[0])))
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(6,1,1):
        raise ValueError("Only three INEX years two pre-fixed scene rules allowed")
    if set(d.season)!={2013,2017,2018} or set(d.site_id)!={"INEX"}:
        raise ValueError("Strict source site-year set changed")
    if set(d.fixed_scene_rule)!={"nearest_date","lowest_cloud_within_8_days"}:
        raise ValueError("Prohibited scene selection beyond two frozen date/calendar rules")
    return d

def main(a):
    records=load_crosswalk(a.crosswalk_zip)
    old=pd.read_csv(io.BytesIO(source_bytes(a.old_roi_zip,SOURCE_OLD_GUANO_GEOGRAPHY_SHA256,OLD_COORD_CSV)))
    if (len(old),old.site_id.nunique())!=(15347,88):
        raise ValueError("Original 15,347 old reference points/88 site source changed")
    n=int(old.site_id.astype(str).eq("INEX").sum())
    if n<4:raise ValueError("Inexpressible Island original source ROI too small")
    output=[];failures=[];cache={}
    for row in records.itertuples(index=False):
        item={"site_id":"INEX","region":"Victoria Land",
              "season":int(row.season),"scene_id":str(row.source_L8_scene_id),
              "selection_rule":str(row.fixed_scene_rule),
              "scene_cloud_percent":float(row.original_scene_overall_cloud_pct),
              "scene_datetime":str(row.source_L8_scene_date)+"T00:00:00Z",
              "original_fixed_guano_point_count":n,
              "independent_VHR_observation_date":str(row.VHR_observation_date),
              "independent_VHR_guano_area_m2":float(row.true_VHR_guano_area_m2),
              "real_days_signed_from_independent_VHR":int(row.day_offset)}
        scene=item["scene_id"]
        if scene in cache:
            val={**item,**{k:v for k,v in cache[scene].items() if k not in item}}
            output.append(val)
            continue
        try:
            val=one(item,old)
            cache[scene]=val
            output.append(val)
            print(json.dumps({"season":item["season"],"original_scene":scene,
                "old_ROI_points_native_QA_valid":val["valid_original_2018_L8_QA_selected_source_points"],
                "original_old_ROI":n,"day_gap":item["real_days_signed_from_independent_VHR"]}),flush=True)
        except Exception as e:
            failures.append({**item,"source_error":f"{type(e).__name__}: {str(e)[:700]}"})
    a.out.mkdir(parents=True,exist_ok=True)
    if output:
        pd.DataFrame(output).drop(columns=["native_raster_source"],errors="ignore").to_csv(
          a.out/"INEX_external_VHR_three_years_L8_same_day_QA_pixels_only.csv",index=False)
    if failures:pd.DataFrame(failures).to_csv(a.out/"INEX_VHR_L8_source_QA_failures.csv",index=False)
    receipt={"status":"SOURCE_INEX_2013_2017_2018_VHR_L8_MATCHED_QA_ONLY" if not failures
       else "SOURCE_NATIVE_QA_UNVERIFIED",
       "true_original_source_site":"INEX","true_regions":1,
       "new_2013_2021_independent_reference_VHR_seasons":[2013,2017,2018],
       "frozen_date_match_rules":["nearest_date","lowest_cloud_within_8_days"],
       "distinct_USGS_L8_scenes_read":len(cache),
       "source_reference_scene_QA_rows":len(output),
       "source_results":output,
       "source_failures":failures,
       "all_2013_2021_optical_delta15N_not_estimated":True,
       "no_polynya_ecological_model_fitted":True,
       "original_past_guano_points_not_automatically_current_guano":True,
       "external_VHR_area_not_guano_pixel_mask":True,
       "one_source_region_not_replicated_pan_Antarctic_validation":True}
    (a.out/"INEX_VHR_3YEARS_L8_NATIVE_QA_ONLY_GATE.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps({"status":receipt["status"],"n_USGS_original_scenes":len(cache),
        "scene_quality":[{"season":v["season"],"scene_id":v["scene_id"],
            "native_QA_good_old_ROI":v["valid_original_2018_L8_QA_selected_source_points"],
            "original_ROI_count":v["original_fixed_guano_point_count"]} for v in output],
        "errors":failures},indent=2),flush=True)
    if failures:raise RuntimeError("Source native QA failures at external independent VHR matched dates")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--crosswalk-zip",type=Path,required=True)
    p.add_argument("--old-roi-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
