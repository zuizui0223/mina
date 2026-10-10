#!/usr/bin/env python3
"""Original NZ 2026 colony-location workbook provenance and name crosswalk.

Official DataStore CKAN location resource (source-known resource ID), with
strict MD5/hash and HTTPS checks. Geography is treated as provider metadata,
not interpreted colony movement or penguin natal origin. Runs from the same
39-site source-census snapshot, preserving blanks and explicit zeros.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from urllib.parse import urlencode
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_nz_2026_ross_39_colony_census_source_v13 as census

LOC_ID="f82c5e1d-f04d-446d-9338-e9d0603360f8"
SCHEMA_LABELS=("colony","site","location","latitude","longitude","lat","lon","island","area")
API="https://datastore.landcareresearch.co.nz/api/3/action/resource_show"

def resource_metadata(raw):
    z=json.loads(raw)
    if z.get("success") is not True or not isinstance(z.get("result"),dict):
        raise ValueError("CKAN location metadata unavailable")
    r=z["result"]
    if r.get("id")!=LOC_ID:
        raise ValueError("Not source publication colony locations resource ID")
    if str(r.get("format","")).upper()!="XLSX":
        raise ValueError("Location file must be official XLSX")
    u=str(r.get("url",""))
    if not census.approved(u):
        raise ValueError("File not on official HTTPS CKAN host")
    md5=str(r.get("hash","")).lower()
    if not re.fullmatch("[a-f0-9]{32}",md5):
        raise ValueError("No unambiguous original resource MD5; stop before parsing")
    return {"official_url":u,"md5":md5,"size":r.get("size"),"filename":r.get("name","")}

def clean_name(value):
    return re.sub(r"\s+"," ",str(value or "").lower().strip())

def summarize_original_table(raw):
    w=census.workbook_first_table(raw)
    rows=w["rows"]
    # Not necessarily a census sheet: source location metadata may contain
    # multiple prose rows then named site list. Report structure first.
    inferred=[]
    for i, row in enumerate(rows[:40]):
        parts=[(col,str(text).strip()) for col,text in sorted(row.items())]
        matches=[(col,text) for col,text in parts
                 if any(token==clean_name(text) or clean_name(text).startswith(token+" ")
                        for token in SCHEMA_LABELS)]
        if len(matches)>=2:
            inferred.append({"row_1_based":i+1,
                             "headers":[{"column_1_based":col+1,"name":text}
                                        for col,text in parts[:30]],
                             "matched_candidate_headers":[text for col,text in matches]})
    # Textual named rows and possible measurements only. Never claim the
    # generic source includes exact latitude/longitude until verified.
    return {
      "sheet_name":w["sheet_name"],
      "data_nonempty_rows":len(rows),
      "column_counts_first_ten_nonempty_rows":[len(r) for r in rows[:10]],
      "sample_first_ten_rows_as_source_layout":[
          [{"column":k+1,"value":str(v)[:130]} for k,v in sorted(row.items())[:12]]
          for row in rows[:10]],
      "candidate_column_header_rows":inferred[:8],
    }

def run():
    out={
      "status":"HOLD_OFFICIAL_NZ_LOCATION_SOURCE",
      "location_resource_id":LOC_ID,
      "total_census_site_roster_verified":False,
      "source_census_location_exact_identity_join_verified":False,
      "known_geographic_island_systems_count":None,
      "independent_island_events_validated":0,
      "recruitment_or_immigrant_biology_rows_read":0,
      "causal_ecology_effect_estimated":False,
      "frozen_Ecology_PR189_unchanged":True
    }
    try:
        meta=resource_metadata(census.fetch_bounded(API+"?"+urlencode({"id":LOC_ID}),census.MAX_SOURCE_METADATA))
        raw=census.fetch_bounded(meta["official_url"])
        h=hashlib.md5(raw).hexdigest()
        if h!=meta["md5"]:
            raise ValueError("Downloaded colony site location XLSX MD5 differs from published official checksum")
        out["official_location_md5_verified"]=h
        out["location_source_metadata"]={"filename":meta["filename"],"bytes":len(raw),"official_MD5":meta["md5"]}
        out["original_location_sheet_shape"]=summarize_original_table(raw)
        out["status"]="OFFICIAL_LOCATION_XLSX_AUTHENTICATED_LAYOUT_ONLY"
        src=census.run()
        if src.get("status")!="SOURCE_XLSX_VALIDATED_AND_STRUCTURAL_COVERAGE_REPORTED":
            out["source_census_status"]=src.get("status")
            return out
        names=src["colony_name_roster"]
        out["total_census_site_roster_verified"]=len(names)==39
        # Metadata layout independent; do not falsely join from substring,
        # row number or marine geographical proximity.
        out["census_2026_roster"] = names
        out["status"]="LOCATION_AND_CENSUS_BOTH_CHECKSUM_VERIFIED_BUT_NAME_CROSSWALK_NOT_YET_VALIDATED"
    except Exception as exc:
        out["status"]="HOLD_OFFICIAL_LOCATION_DOWNLOAD_OR_LAYOUT"
        out["reason_type"]=type(exc).__name__
        out["reason"]=str(exc)[:230]
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    z=run()
    args.out.write_text(json.dumps(z,indent=2)+"\n")
    print("LOCATION_SOURCE_GATE",z["status"])
    print("LOCATION_MD5",z.get("official_location_md5_verified","NONE"))
    print("ORIGINAL_LOCATION_SHEET_SHAPE",json.dumps(z.get("original_location_sheet_shape",{}),ensure_ascii=False)[:7000])
    print("CENSUS_ROSTER_N",len(z.get("census_2026_roster",[])))
    print("REASON_IF_HOLD",z.get("reason_type",""),z.get("reason",""))
    print("NEVER_CLAIM_INTER_ISLAND_MOVEMENT_FROM_METADATA")

if __name__=="__main__": main()
