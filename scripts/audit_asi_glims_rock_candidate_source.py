#!/usr/bin/env python3
"""Source-pinned ASI penguin detection/non-detection support × GLIMS/SCAR 25 sites.

Raw Antarctic Site Inventory visit states: 0 not detected, 1 present,
2 breeding; NA missing. This is NOT confirmed nest-patch absence, and
site-level 0 -> 2 is NOT independent proof of colonization.
No ecological effect fitted, and no historical glacier exposure inferred.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import pandas as pd
from pyproj import Geod

ASI_REPO="lynch-lab/Schrimpf_etal_PolarBiology_Occupancy"
ASI_COMMIT="f34545a163ee22eb557ac2cd8c01e219271787aa"
ASI_GIT_BLOBS={"Raw_ASI_Data.csv":"b26be882f7a56e77287dbebd897e8762efafe7a3",
               "ESM_5.csv":"44dfb41e696ed84cba54af356204e39f87561533"}
SOURCE_GIS_RUN=44508816915
SOURCE_GIS_ARTIFACT=14520279224
SPECIES=("ADPE","CHPE","GEPE")
VALID_STATES={"0","1","2","NA"}
GEOD=Geod(ellps="WGS84")

def parse_asi(raw:Path,metadata:Path):
    x=pd.read_csv(raw,dtype=str,keep_default_na=False)
    meta=pd.read_csv(metadata,dtype=str,keep_default_na=False)
    if len(x)!=1565 or len(meta)!=196:
        raise ValueError(f"Publisher original ASI source drift: {len(x)} visits/{len(meta)} site metadata")
    if x["Code"].nunique()!=196 or meta["Code"].nunique()!=196:
        raise ValueError("Original ASI site code duplicate/missing")
    if not set(x["Code"]).issubset(set(meta["Code"])):
        raise ValueError("Original ASI visit codes not in site metadata")
    needed={"Code","Season","Date",*SPECIES}
    if not needed.issubset(x) or not {"Code","Name","Lat","Lon"}.issubset(meta):
        raise ValueError("Publisher ASI columns missing")
    for sp in SPECIES:
        seen=set(x[sp].unique())
        if not seen.issubset(VALID_STATES):
            raise ValueError(f"Unrecognized original {sp} state codes: {seen-VALID_STATES}")
    x["season_start"]=pd.to_numeric(x["Season"].str.slice(0,4),errors="raise")
    if x["season_start"].min()!=1995 or x["season_start"].max()!=2016:
        raise ValueError("ASI original season coverage drift")
    return x,meta

def season_state(values):
    """Conservative observed site-season detection state, never true absence."""
    v=list(values)
    if "2" in v:return "BREEDING_OBSERVED"
    if "1" in v:return "PRESENCE_ONLY_OBSERVED"
    if v and all(x=="0" for x in v):return "ALL_VISITS_NONDETECTION"
    return "INCOMPLETE_OR_MISSING"

def annual_panel(visits):
    records=[]
    for (site,year),r in visits.groupby(["Code","season_start"],sort=True):
        item={"Code":str(site),"season_start":int(year),
              "visit_count":len(r)}
        for sp in SPECIES:
            v=r[sp].tolist()
            item[sp]=season_state(v)
            item[f"{sp}_within_season_0_and_positive"]=("0" in v and
                                            any(t in v for t in ("1","2")))
        records.append(item)
    return pd.DataFrame(records)

def transition_support(panel):
    all_rows=[]
    for sp in SPECIES:
        count=Counter()
        events=[]
        for site,r in panel.groupby("Code",sort=True):
            r=r.sort_values("season_start")
            byyear={int(row.season_start):getattr(row,sp)
                    for row in r.itertuples(index=False)}
            for year,a in sorted(byyear.items()):
                b=byyear.get(year+1)
                if b is None or "MISSING" in a or "MISSING" in b:
                    continue
                count["consecutive_seasons_with_states"]+=1
                count[f"{a}__TO__{b}"]+=1
                if a=="ALL_VISITS_NONDETECTION" and b=="BREEDING_OBSERVED":
                    events.append({"Code":site,"species_id":sp,
                                   "from_season_start":year,
                                   "to_season_start":year+1,
                                   "transition_type":"0_ONLY_TO_BREEDING_OBSERVED",
                                   "true_colonization_confirmed":False})
        all_rows.append({"species_id":sp,
                        "source_observed_transition_counts":dict(count),
                        "candidate_0_to_breeding_events":events})
    return all_rows

def crosswalk_25(asi_visits,asi_meta,source_rock):
    required={"site_id","site_name","latitude","longitude",
              "near_1km_source_only","glims_late_year","rock_source_year",
              "land_source_feature_id"}
    if not required.issubset(source_rock):
        raise ValueError("Original source GLIMS/SCAR cohort columns missing")
    selected=source_rock[source_rock["near_1km_source_only"].astype(str).str.lower().eq("true")]
    if selected["site_id"].nunique()!=25 or len(selected)!=25:
        raise ValueError(f"25 GIS candidate roster drift: {len(selected)}")
    meta=asi_meta.set_index("Code",drop=False)
    result=[]
    for row in selected.itertuples(index=False):
        site=str(row.site_id)
        m=meta.loc[site] if site in meta.index else None
        if m is None:
            result.append({"site_id":site,"matched_code":False,
                           "matched_exact_source_location":False,
                           "site_name":str(row.site_name)})
            continue
        distance=float(GEOD.inv(float(row.longitude),float(row.latitude),
                               float(m["Lon"]),float(m["Lat"]))[2])
        if not pd.notna(distance):
            raise ValueError("ASI coordinate non-finite")
        n=int((asi_visits["Code"]==site).sum())
        seasons=int(asi_visits.loc[asi_visits["Code"]==site,"season_start"].nunique())
        result.append({
            "site_id":site,"site_name":str(row.site_name),
            "asi_name":str(m["Name"]),
            "matched_code":True,"name_exact":str(row.site_name)==str(m["Name"]),
            "lat_asi":float(m["Lat"]),"lon_asi":float(m["Lon"]),
            "site_geodesic_distance_m":round(distance,3),
            "matched_exact_source_location":bool(distance<10),
            "asi_original_visits":n,"asi_original_seasons":seasons,
            "glims_late_year":int(float(row.glims_late_year)),
            "source_rock_year":int(float(row.rock_source_year)),
            "source_rock_year_strictly_after_ASI_end":int(float(row.rock_source_year))>2017,
            "has_historical_any_visit":bool(n>0),
            "source_locates_exact_nest_patch":False,
            "verified_prior_absence_of_breeding_at_the_rock_patch":False,
        })
    return pd.DataFrame(result)

def run(raw_path,meta_path,site_path):
    raw,meta=parse_asi(raw_path,meta_path)
    frame=annual_panel(raw)
    pairs=transition_support(frame)
    sites=pd.read_csv(site_path,dtype={"site_id":str},keep_default_na=False)
    cross=crosswalk_25(raw,meta,sites)
    exact=cross[(cross["matched_code"])&(cross["matched_exact_source_location"])]
    if len(exact)!=5 or sorted(exact["site_id"].tolist())!=["JOUG","PYPT","RENI","SART","TRUA"]:
        raise ValueError("Code+geodesic five-site original ASI crosswalk drift")
    matched=set(exact["site_id"])
    matched_panel=frame[frame["Code"].isin(matched)].copy()
    matched_transitions=transition_support(matched_panel)
    return {
        "status":"ASI_ORIGINAL_VISIT_NONDETECTION_SOURCE_VERIFIED_NO_SETTLEMENT_INFERENCE",
        "source_repositories":{"asi":ASI_REPO,"asi_commit":ASI_COMMIT,
                               "asi_original_git_blob_sha1":ASI_GIT_BLOBS,
                               "GIS_original_artifact_run":SOURCE_GIS_RUN,
                               "GIS_original_artifact_id":SOURCE_GIS_ARTIFACT},
        "original_ASI_n_visits":int(len(raw)),
        "original_ASI_distinct_site_codes":int(raw["Code"].nunique()),
        "original_ASI_site_season_units":int(len(frame)),
        "original_ASI_seasons":int(raw["season_start"].nunique()),
        "candidate_GIS_25":25,
        "source_match_exact_code_and_under_10m":int(len(exact)),
        "matched_5_original_visits":int(exact["asi_original_visits"].sum()),
        "matched_5_original_site_seasons":int(exact["asi_original_seasons"].sum()),
        "match_codes":sorted(matched),
        "species_visit_state_counts":{sp:{
            "0_not_detected":int((raw[sp]=="0").sum()),
            "1_detected_not_breeding":int((raw[sp]=="1").sum()),
            "2_breeding_detected":int((raw[sp]=="2").sum()),
            "NA_not_scored":int((raw[sp]=="NA").sum())
        } for sp in SPECIES},
        "species_site_season_mixed_0_and_positive":{
            sp:int(frame[f"{sp}_within_season_0_and_positive"].sum()) for sp in SPECIES},
        "observed_original_ASI_transition_support":pairs,
        "observed_five_exact_matched_site_transition_support":matched_transitions,
        "newly_ice_exposed_nest_patch_identified":False,
        "all_site_codes_are_physical_islands":False,
        "verified_surveyed_pre_exposure_A_to_postexposure_P_events":None,
        "fitted_biological_effect":False,
        "limits":[
            "Original ASI 0=not detected during that visit, NOT verified species absence.",
            "An observed all-zero season followed by breeding can reflect imperfect detection, seasonal observation, or settlement; the process cannot be identified from 0/2 alone.",
            "Original ASI surveys 1995/96–2016/17 and candidate SCAR rock image year 2024 do not provide post-rock survey risk sets.",
            "Matched site centroids are not exact nest-patch outlines; glacial old-minus-new polygons may include cartographic error and oceanic ice loss.",
            "ASI raw counts/presence are same broad Antarctic Site Inventory source family as part of APBP/MAPPPD; not a fully independent biological sample.",
            "No GLIMS date covariate, climate, demographic effect or colonization regression is fitted.",
        ]
    },cross,frame

def main():
    p=argparse.ArgumentParser()
    for s in ("raw-asi-csv","asi-site-csv","source-rock-site-csv","out-json","out-crosswalk-csv","out-panel-csv"):
        p.add_argument("--"+s,required=True,type=Path)
    a=p.parse_args()
    report,cross,panel=run(a.raw_asi_csv,a.asi_site_csv,a.source_rock_site_csv)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    cross.to_csv(a.out_crosswalk_csv,index=False)
    panel.to_csv(a.out_panel_csv,index=False)
    print(json.dumps({"status":report["status"],
                      "candidate":25,"exact_site_matches":report["source_match_exact_code_and_under_10m"],
                      "raw_visits":report["original_ASI_n_visits"],
                      "all_site_seasons":report["original_ASI_site_season_units"],
                      "matched_visits":report["matched_5_original_visits"]},sort_keys=True))

if __name__=="__main__":
    main()
