#!/usr/bin/env python3
"""Source-level feasibility test for arrival -> own first egg.

NOAA focal camera data are selected only after two adults at an empty nest,
and terminal maxn codes 4/5 do NOT mean adult attendance counts. Zenodo
tracks already known nonbreeders AT SEA without following their own eggs.
This script tests the empirical source-level joint-ID observational key.
No biological records opened, no downloads of individual tracking files.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError,HTTPError

ZENODO_RECORD="https://zenodo.org/api/records/5036339"
PUBLISHED_MD5="d4ca95fd92096e58ffbffff84250d669"
ATTENDANCE_CODES={"0":"NO_ADULT_VISIBLE_AT_SELECTED_NEST",
                  "1":"ONE_ADULT_AT_SELECTED_NEST",
                  "2":"TWO_ADULTS_AT_SELECTED_NEST",
                  "4":"CRECHE_TERMINAL_EVENT_NOT_ADULT_COUNT",
                  "5":"CONFIRMED_NEST_FAILURE_TERMINAL_EVENT_NOT_ADULT_COUNT"}

def classify_attendance_maxn(value):
    s=str(value or "").strip()
    if s in ATTENDANCE_CODES:return ATTENDANCE_CODES[s]
    if not s:return "UNKNOWN_OR_MISSING_ATTENDANCE"
    return "HOLD_UNDOCUMENTED_CODE"

def validate_zenodo_record(z):
    if str(z.get("id"))!="5036339":
        raise ValueError("Wrong independent Zenodo dataset record")
    files=z.get("files")
    if not isinstance(files,list) or not files:
        raise ValueError("No official Zenodo file list")
    records=[]
    for f in files:
        name=str(f.get("key",f.get("filename","")))
        checksum=str(f.get("checksum",""))
        md5=checksum.split(":",1)[-1] if checksum.startswith("md5:") else checksum
        records.append({"name":name,"size":f.get("size"),"official_record_checksum":checksum,
                        "MD5_matches_published_data_csv":name=="data.csv" and md5==PUBLISHED_MD5})
    if not any(f["MD5_matches_published_data_csv"] for f in records):
        raise ValueError("Zenodo nonbreeder file MD5 no longer as in published archive")
    return records

def evaluate(metadata=None):
    statuses={
        "NOAA_camera_focal_selected_after_two_adults":True,
        "NOAA_focal_attendance_unknown_day_is_not_unseen_immigrant":True,
        "NOAA_numeric_4_5_are_terminal_outcome_not_four_or_five_adults":True,
        "NOAA_clutch_initiation_estimator_already_published_Hinke2018":True,
        "Zenodo_nonbreeders_not_followed_to_individual_first_egg":True,
        "Zenodo_2016_17_2_stations_both_King_George_Island":True,
        "NOAA_2015_17_multi_site_camera_individual_entrants_ID_absent":True,
        "joining_aggregate_rookery_year_without_matched_bird_ID_does_not_identify_conditional_breeding":True,
        "observed_all_arrivals_denominator":False,
        "matched_individual_visit_to_own_egg":False,
        "matched_visitors_with_actual_chick_outcomes":False,
        "new_causal_source_supply_or_reproductive_constraint_test":False
    }
    report={
        "status":"HOLD_NO_POPULATION_AT_RISK_ENTRANT_TO_OWN_EGG_JOIN",
        "2018_noaa_camera_doi":"10.7289/V5Z036F7",
        "NOAA_original_focal_attendance_fields":["year","rookery","colony","camera","spp","nest","date","maxn"],
        "NOAA_codebook":ATTENDANCE_CODES,
        "source_z_nonbreeder_doi":"10.5281/zenodo.5036339",
        "source_z_expected_nonbreeder_tagged_adults":30,
        "source_z_two_stations_geographical_independence":"SAME_ISLAND_KING_GEORGE",
        "identifiability_flags":statuses,
        "NOAA_cam_source_bird_records_loaded":0,
        "Zenodo_tracking_source_bird_records_loaded":0,
        "observed_penguin_eggs_matched_across_sources":0,
        "proposed_visitor_to_breeding_probability_numerator_available":False,
        "proposed_visitor_to_breeding_probability_denominator_available":False,
        "source_access_Zenodo_metadata":"NOT_QUERIED",
        "Ecology_PR189_scientific_freeze_preserved":True,
        "official_USAP_PR142_not_unlocked":True
    }
    if metadata is not None:
        report["Zenodo_official_file_manifest"]=validate_zenodo_record(metadata)
        report["source_access_Zenodo_metadata"]="VERIFIED_OFFICIAL_MANIFEST_CHECKSUM_ONLY"
    return report

def remote_probe():
    result=evaluate()
    try:
        with urlopen(Request(ZENODO_RECORD,headers={
            "Accept":"application/json","User-Agent":"Antarctic-research-origin-audit/1.0"}),
            timeout=16) as response:
            if response.geturl()!=ZENODO_RECORD:
                raise ValueError("Official Zenodo metadata redirected unexpectedly")
            b=response.read(150_001)
            if len(b)>150_000:
                raise ValueError("Oversized Zenodo metadata; cannot validate source")
        result=evaluate(json.loads(b.decode("utf-8")))
    except (URLError,HTTPError,ValueError,UnicodeDecodeError,TimeoutError) as e:
        result["source_access_Zenodo_metadata"]="HOLD_OFFICIAL_METADATA_ACCESS_OR_CHECKSUM"
        result["metadata_access_error_type"]=type(e).__name__
        result["metadata_access_error_message"]=str(e)[:160]
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    z=remote_probe()
    a.out.write_text(json.dumps(z,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("OFFICIAL_ZENODO_METADATA",z["source_access_Zenodo_metadata"])
    print("ZENODO_ORIGINAL_FILE_MANIFEST",z.get("Zenodo_official_file_manifest",[]))
    print("NOAA_ATTENDANCE_CODES_4_AND_5",
        classify_attendance_maxn("4"),classify_attendance_maxn("5"))
    print("ARRIVAL_TO_OWN_FIRST_EGG_ID_JOIN",False)
    print("NO_NEW_PENGUIN_CAUSAL_RESULT")
if __name__=="__main__": main()
