#!/usr/bin/env python3
"""V14 original AADC colony boundary DBF SCHEMA ONLY (no count observations).

Uses frozen V10 per-source DBF field-name metadata for 13 original sites
across 28 years. Area/polygon features were previously analyzed; source
field names only do not establish nest count availability or validity.
"""
from __future__ import annotations
import argparse,ast,csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path

EXPECTED_ORIGINAL_CSV_SHA="0d4a86944dc6e0cb6c4157384762c9f35acc346edaf191e7071fa45ab91dc1cf"
STRONG_COUNT_FIELDS={
  "occupied_nests","n_occupied_nests","number_occupied_nests",
  "num_occupied_nests","nest_count","nests_count",
  "nest_counts","n_nests","number_nests","number_of_nests",
  "breeding_pairs","breeding_pair_count","n_breeding_pairs",
  "number_breeding_pairs","pair_count","total_nests",
}
WEAK_COUNT_TOKENS=("nest","count","pair","breed","number","num","occup")
def normalized(field):
    return re.sub(r"[^a-z0-9]+","_",str(field).strip().lower()).strip("_")


def load_source_fields(csvpath:Path):
    original=csvpath.read_bytes()
    if hashlib.sha256(original).hexdigest()!=EXPECTED_ORIGINAL_CSV_SHA:
        raise ValueError("SOURCE_STOP original V10 site-year source field CSV SHA drift")
    with csvpath.open(newline="",encoding="utf-8") as f:
        records=list(csv.DictReader(f))
    if len(records)!=28 or len({r["site_id"] for r in records})!=13:
        raise ValueError("SAMPLE_STOP source V10 repeat site/year corpus changed")
    fields=[]
    for row in records:
        try:
            items=ast.literal_eval(row["original_DBf_fields"])
        except (SyntaxError,ValueError,KeyError) as e:
            raise ValueError("SCHEMA_STOP original source DBF fields unreadable") from e
        if not isinstance(items,list) or not items or not all(isinstance(x,str) for x in items):
            raise ValueError("SCHEMA_STOP original source DBF schema not distinct string fields")
        names=[normalized(x) for x in items]
        if len(set(names))!=len(names):
            raise ValueError("SCHEMA_STOP duplicate source original normalized field names")
        strong=sorted(set(x for x in names if x in STRONG_COUNT_FIELDS))
        potential=sorted(set(x for x in names if any(t in x for t in WEAK_COUNT_TOKENS)))
        fields.append({
            "site_id":str(row["site_id"]),
            "source_group":str(row["source_group"]),
            "season_start_year":int(row["season_start_year"]),
            "original_DBf_field_names":items,
            "definite_semantic_count_candidate_columns":strong,
            "vague_count_like_columns_not_assumed_nest_counts":potential,
            "any_strong_semantic_field_name":bool(strong),
        })
    if len({(r["site_id"],r["season_start_year"]) for r in fields})!=28:
        raise ValueError("SOURCE_STOP duplicate original GIS source site-year")
    return fields


def summarize_source_fields(fields):
    bysite=defaultdict(list)
    allfields=Counter()
    strong=Counter()
    vague=Counter()
    for row in fields:
        bysite[row["site_id"]].append(row)
        for k in row["original_DBf_field_names"]:allfields[k]+=1
        for k in row["definite_semantic_count_candidate_columns"]:strong[k]+=1
        for k in row["vague_count_like_columns_not_assumed_nest_counts"]:vague[k]+=1
    paired=0
    strong_pair=0
    site_pairs=[]
    for site,rows in sorted(bysite.items()):
        for left,right in zip(sorted(rows,key=lambda z:z["season_start_year"])[:-1],
                              sorted(rows,key=lambda z:z["season_start_year"])[1:]):
            paired+=1
            shared=sorted(set(left["definite_semantic_count_candidate_columns"]) &
                          set(right["definite_semantic_count_candidate_columns"]))
            strong_pair+=bool(shared)
            site_pairs.append({
                "site_id":site,
                "first_year":left["season_start_year"],
                "last_year":right["season_start_year"],
                "same_strong_count_source_field_names":shared,
                "count_values_are_known":False,
                "biological_count_stage_verified":False,
            })
    if paired!=15:
        raise ValueError("SOURCE_STOP source V10 observed pair cohort drift")
    return {
      "status":"AADC_REPEATED_ORIGINAL_COLONY_GIS_DBF_FIELDS_V14_NO_ANIMAL_VALUES",
      "original_source_repeat_polygon_layers":len(fields),
      "original_source_repeat_site_IDs":len(bysite),
      "original_original_source_15_observed_pair_count":paired,
      "original_DBF_fields_by_source_literal_name":dict(sorted(allfields.items())),
      "strong_candidate_breeding_count_fields_by_yearfile":dict(sorted(strong.items())),
      "weaker_count_like_field_names_not_trusted_as_nest_count":dict(sorted(vague.items())),
      "original_source_yearfiles_with_strong_named_count_field":sum(
          r["any_strong_semantic_field_name"] for r in fields),
      "successive_source_site_pair_with_same_strong_count_field":strong_pair,
      "original_source_site_pair_count_schema":site_pairs,
      "original_count_values_read":0,
      "actual_breeding_pair_count_data_available_verified":False,
      "V10_original_polygon_area_ratio_is_breeding_pair_count_change":False,
      "V12_V13_cross_programme_landmass_identity_still_unresolved":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v10-source-siteyears",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    fields=load_source_fields(a.v10_source_siteyears)
    summary=summarize_source_fields(fields)
    summary["original_V10_siteyr_metadata_CSV_SHA256"]=EXPECTED_ORIGINAL_CSV_SHA
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))


if __name__=="__main__":
    main()
