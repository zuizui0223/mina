#!/usr/bin/env python3
"""Survey-history SOURCE gate for three-source, 1km rock/GLIMS colony candidates.

Counts are used only to identify the presence and year of recorded nest surveys.
An absent survey row (or a numeric zero without verified survey protocol) is
NOT a biological absence. No A->P transitions or effect coefficients fitted.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
import pyreadr

PINNED = "88c73a507e0921b2541c218c71eaf16721bc6502"
ROCK_RESULT_RUN = 44508816915
ROCK_RESULT_ARTIFACT = 14520279224
EXPECTED_SITES = 25
SPECIES = {"ADPE","CHPE","GEPE"}

def original_rda(path,name):
    obj=pyreadr.read_r(str(path))
    if name in obj: return obj[name]
    if len(obj)==1:return next(iter(obj.values()))
    raise ValueError("original MAPPPD RDA object not uniquely identifiable")

def run(source_site_csv:Path,mapppdr:Path):
    src=pd.read_csv(source_site_csv)
    required={"site_id","near_1km_source_only","rock_source_year",
              "glims_late_year","land_source_feature_id","bbox_region"}
    if not required.issubset(src):
        raise ValueError("source rocktime crosswalk required columns missing")
    selected=src.loc[src["near_1km_source_only"].eq(True)].copy()
    if len(selected)!=EXPECTED_SITES or selected["site_id"].nunique()!=EXPECTED_SITES:
        raise ValueError("source-rock 1km original roster drift")
    if selected["rock_source_year"].isna().any() or selected["glims_late_year"].isna().any():
        raise ValueError("rock / GLIMS source acquisition year missing")
    obs=original_rda(mapppdr/"data/penguin_obs.rda","penguin_obs")
    must={"site_id","species_id","type","count","season"}
    if not must.issubset(obs):
        raise ValueError("source MAPPPD observation schema drift")
    nest=obs.loc[
        obs["site_id"].astype(str).isin(set(selected["site_id"].astype(str)))
        &obs["species_id"].astype(str).isin(SPECIES)
        &obs["type"].astype(str).eq("nests")
        &obs["count"].notna()
    ].copy()
    nest["season"]=pd.to_numeric(nest["season"],errors="coerce")
    nest["count"]=pd.to_numeric(nest["count"],errors="coerce")
    nest=nest.loc[nest["season"].notna()&nest["count"].notna()].copy()
    nest=nest.loc[nest["count"].ge(0)].copy()
    nest["season"]=nest["season"].astype(int)
    # Multiple records in one site/species/season do not create new years.
    records=(nest.groupby(["site_id","species_id","season"],as_index=False)
             .agg(raw_rows=("count","size"),
                  any_positive=("count",lambda x:bool((x>0).any())),
                  any_numeric_zero=("count",lambda x:bool((x==0).any()))))
    pairs=[]
    for r in selected.itertuples(index=False):
        local=records.loc[records["site_id"].astype(str).eq(str(r.site_id))]
        rock_year=int(r.rock_source_year)
        late=int(r.glims_late_year)
        for species in sorted(SPECIES):
            ss=local.loc[local["species_id"].eq(species)].copy()
            if ss.empty:continue
            years=sorted(ss["season"].unique().tolist())
            strictly_after=ss["season"].gt(rock_year)
            before_glims=ss["season"].lt(late)
            pairs.append({
                "site_id":str(r.site_id),"species_id":species,
                "bbox_region":str(r.bbox_region),
                "land_source_feature_id":str(r.land_source_feature_id),
                "source_glims_late_year":late,
                "source_rock_acquisition_year":rock_year,
                "raw_nest_count_records":int(ss["raw_rows"].sum()),
                "distinct_recorded_nest_seasons":len(years),
                "earliest_recorded_season":years[0],
                "latest_recorded_season":years[-1],
                "nest_seasons_strictly_after_rock_image_year":int(strictly_after.sum()),
                "nest_seasons_strictly_before_latest_glims_outline":int(before_glims.sum()),
                "seasons_with_numeric_zero_count":int(ss["any_numeric_zero"].sum()),
                "seasons_with_positive_nest_count":int(ss["any_positive"].sum()),
                "seasons_with_both_positive_and_zero":int(
                     (ss["any_numeric_zero"]&ss["any_positive"]).sum()),
                "numeric_zero_is_verified_surveyed_absence":False,
                "earliest_positive_is_colonization":False,
            })
    tbl=pd.DataFrame(pairs)
    site_with_record=set(tbl["site_id"].astype(str)) if not tbl.empty else set()
    site_post=set(tbl.loc[tbl["nest_seasons_strictly_after_rock_image_year"].gt(0),"site_id"].astype(str)) if not tbl.empty else set()
    zero_sites=set(tbl.loc[tbl["seasons_with_numeric_zero_count"].gt(0),"site_id"].astype(str)) if not tbl.empty else set()
    report={
        "status":"ORIGINAL_MAPPPD_SURVEY_COVERAGE_QA_ONLY",
        "original_source_commit":PINNED,
        "input_source_rocktime_run":ROCK_RESULT_RUN,
        "input_source_rocktime_artifact":ROCK_RESULT_ARTIFACT,
        "candidate_site_ids":EXPECTED_SITES,
        "site_ids_with_any_nest_count_record":len(site_with_record),
        "site_ids_with_strictly_post_rock_source_year_nest_records":len(site_post),
        "site_ids_with_any_numeric_zero_count_record":len(zero_sites),
        "n_site_species_with_nest_records":len(tbl),
        "n_site_species_with_post_rock_source_year_records":int(
            tbl["nest_seasons_strictly_after_rock_image_year"].gt(0).sum()) if not tbl.empty else 0,
        "n_site_species_with_numeric_zero":int(
            tbl["seasons_with_numeric_zero_count"].gt(0).sum()) if not tbl.empty else 0,
        "n_site_species_with_both_positive_and_zero_same_season":int(
            tbl["seasons_with_both_positive_and_zero"].gt(0).sum()) if not tbl.empty else 0,
        "n_independent_verified_survey_absence_events":None,
        "n_verified_A_to_P_events":None,
        "fitted_biological_effect":False,
        "source_limitations":[
            "MAPPPD is primarily a database of known colonies, not a comprehensive survey-visited non-occupied risk set.",
            "No row means not recorded, never A.",
            "A reported numeric zero is NOT an independently verified whole-patch survey absence.",
            "Earliest positive nest record is first detected in the database, not first colonization.",
            "Season matching rock source-year without verified exact acquisition date cannot imply observation after rock exposure.",
            "The 25 sites are not 25 independent physical landmasses, and source land feature IDs are not biological island identifiers.",
            "Post-source nesting can occur at an already-established colony and does not prove settlement on formerly glaciated rock."
        ],
    }
    return report,tbl

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-site-csv",type=Path,required=True)
    p.add_argument("--mapppdr-dir",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    p.add_argument("--out-csv",type=Path,required=True)
    a=p.parse_args()
    try:
        result,rows=run(a.source_site_csv,a.mapppdr_dir)
    except Exception as ex:
        result={"status":"HOLD_SOURCE_CROSSWALK_OR_SURVEY_SCHEMA",
                "reason":f"{type(ex).__name__}: {str(ex)}"[:400],
                "biological_effect_fitted":False}
        rows=pd.DataFrame()
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if not rows.empty:
        a.out_csv.parent.mkdir(parents=True,exist_ok=True)
        rows.to_csv(a.out_csv,index=False)
    print(json.dumps({k:result.get(k) for k in (
        "status","reason","candidate_site_ids","site_ids_with_any_nest_count_record",
        "site_ids_with_strictly_post_rock_source_year_nest_records",
        "site_ids_with_any_numeric_zero_count_record")},sort_keys=True))

if __name__=="__main__":
    main()
