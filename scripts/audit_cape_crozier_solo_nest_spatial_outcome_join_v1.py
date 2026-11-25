#!/usr/bin/env python3
"""Source-faithful Cape Crozier solitary nest join and publication-date QA.

NO inferential ecology: Cox et al. 2024 already analyzed these 50 nests,
2021-22 brood/crèche results and next-year reoccupancy. We only quantify
matched raw nest identities and date-code integrity from the 2023 release.

Do NOT read the 25MB unrelated resight database or infer marked pioneers.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re

SHA = {
    "outcomes": "a21648a25b12f42759ca5d5bd011ec32c36d3dfc",
    "locations": "9e2dbe1426e47d6cf2dfc84110e8204c7ba92329",
    "followup": "f814feb8100eedeb635c9672e71889dfe0dc6d50"
}
FOLLOWUP_WINDOW_START = datetime(2022,10,1)
FOLLOWUP_WINDOW_END = datetime(2023,3,31,23,59,59)
ASSERT_SOURCE_FILE_RELEASE_BEFORE = datetime(2023,8,25)
UNCERTAIN_STATUS = {"", "MT", "MT?", "UNK", "INC?", "NBS", "FAIL?", "FBN?", "INC9"}
CLEAR_ACTIVITY = {"INC", "BR", "G"}


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def load_author_csv(path, expected_sha):
    b=Path(path).read_bytes()
    if git_blob_sha(b)!=expected_sha:
        raise ValueError(f"Frozen original author git blob mismatch at {path}")
    with open(path,encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def canonical_key(value):
    raw=str(value or "").strip().lower()
    raw=re.sub(r"^solo\s*", "", raw)
    return raw if re.fullmatch(r"\d{1,3}",raw) else None


def parse_original_date(value):
    s=str(value or "").strip()
    if not s: return None
    try:
        return datetime.strptime(s,"%m/%d/%Y")
    except ValueError:
        return None


def finite(value):
    try:
        n=float(value)
    except (ValueError,TypeError):
        return None
    return n if math.isfinite(n) else None


def raw_occupied(status):
    return str(status or "").strip().upper() not in UNCERTAIN_STATUS


def raw_active(row):
    s=str(row.get("status","")).strip().upper()
    if s not in CLEAR_ACTIVITY: return False
    # Follow published data code's egg/chick 9=unknown convention.
    return any(str(row.get(c,"")).strip() not in ("","NA","9")
               for c in ("egg_n","chick_n"))


def audit(outcomes,locations,followup,require_original_counts=True):
    o={}
    dropped_footer=0
    for z in outcomes:
        k=canonical_key(z.get("nestid"))
        if k is None:
            dropped_footer+=1
            continue
        if k in o: raise ValueError("Duplicate original breeding outcome nest ID")
        o[k]=z
    l={}
    for z in locations:
        k=canonical_key(z.get("nestid"))
        if k is None or k in l:
            raise ValueError("Invalid or duplicated original GPS nest ID")
        lat=finite(z.get("latitude"))
        lon=finite(z.get("longitude"))
        if lat is None or lon is None or not (-90<=lat<=90 and -180<=lon<=180):
            raise ValueError("Original solitary nest GPS invalid")
        l[k]=z
    if set(o)!=set(l):
        raise ValueError("Nest ID join mismatch (no forced joins or dropped records)")
    if require_original_counts and (len(o)!=50 or len(l)!=50 or dropped_footer!=3):
        raise ValueError("Not the frozen 50-nest source tables")
    if require_original_counts and set(o)!={str(i) for i in range(1,51)}:
        raise ValueError("The frozen 50 solitary source IDs changed")
    raw_breeder=[k for k,z in o.items() if z["breeder"].strip()=="1"]
    raw_cr=[k for k,z in o.items() if finite(z["cr_confirm"]) is not None
            and finite(z["cr_confirm"])>0]
    raw_join_keys={k:(float(l[k]["latitude"]),float(l[k]["longitude"])) for k in o}
    source_rows=Counter()
    unknown_dates=[]
    outside=[]
    bynest=defaultdict(list)
    for z in followup:
        key=canonical_key(z.get("nestid"))
        if key is None or key not in o:
            raise ValueError("Nonmatching 2022 followup nest identity")
        day=parse_original_date(z.get("date"))
        if day is None:
            source_rows["MISSING_OR_INVALID_DATE"]+=1
            unknown_dates.append(key)
        elif FOLLOWUP_WINDOW_START<=day<=FOLLOWUP_WINDOW_END:
            source_rows["IN_PLANNED_2022_23_SEASON"]+=1
        else:
            source_rows["OUTSIDE_2022_23_SEASON"]+=1
            outside.append({
                "id":key,"date":str(z.get("date","")).strip(),
                "status":str(z.get("status","")).strip()
            })
        if day and day>ASSERT_SOURCE_FILE_RELEASE_BEFORE:
            source_rows["SOURCE_ROW_DATE_AFTER_AUGUST_2023_RELEASE"]+=1
        bynest[key].append({"raw":z,"date":day})
    if require_original_counts and len(followup)!=136:
        raise ValueError("Original 2022-season followup source row count changed")
    if require_original_counts and len(bynest)!=50:
        raise ValueError("Not all 50 original nests represented in followup source")
    found_occ={}
    found_act={}
    for tag,valid in (("all_rows",lambda day: True),
                      ("season_window",lambda day:day is not None and FOLLOWUP_WINDOW_START<=day<=FOLLOWUP_WINDOW_END)):
        occ={key for key,records in bynest.items() if any(
            valid(v["date"]) and raw_occupied(v["raw"].get("status")) for v in records)}
        act={key for key,records in bynest.items() if any(
            valid(v["date"]) and raw_active(v["raw"]) for v in records)}
        found_occ[tag]=occ
        found_act[tag]=act
    return {
        "status":"PUBLIC_ORIGINAL_50_NEST_SPATIAL_OUTCOME_FOLLOWUP_CROSSWALK",
        "source_release_tag":"PolarBiol-submission",
        "source_release_commit":"04517cedac18950408abd4d0b510f4aae3447f05",
        "outcome_table_valid_nests":len(o),
        "outcome_table_footer_rows_excluded":dropped_footer,
        "location_table_valid_georeferenced_nests":len(l),
        "exact_outcome_location_nestid_matches":len(set(o)&set(l)),
        "raw_breeder_nests":len(raw_breeder),
        "raw_creche_confirmed_nests":len(raw_cr),
        "followup_source_rows":len(followup),
        "followup_unique_nest_ids":len(bynest),
        "followup_record_date_classes":dict(sorted(source_rows.items())),
        "followup_outside_original_season_months":dict(sorted(Counter(
            z["date"][:2].lstrip("0")+"/" + z["date"][-4:] for z in outside
            if len(z["date"])>=8).items())),
        "n_followup_nest_ids_with_ambiguous_or_missing_date":len(set(unknown_dates)),
        "source_date_after_public_release_rows":source_rows["SOURCE_ROW_DATE_AFTER_AUGUST_2023_RELEASE"],
        "source_date_after_release_example":next((z for z in outside if z["date"].endswith("/2023")),None),
        "raw_detected_occupied_nest_counts":{k:len(v) for k,v in found_occ.items()},
        "raw_detected_active_nest_counts":{k:len(v) for k,v in found_act.items()},
        "raw_occupied_ids_only_outside_window":sorted(found_occ["all_rows"]-found_occ["season_window"],key=int),
        "raw_active_ids_only_outside_window":sorted(found_act["all_rows"]-found_act["season_window"],key=int),
        "author_followup_occupancy_not_a_marked_individual":True,
        "out_of_season_2023_rows_may_be_date_typos_not_proven_separate_season":True,
        "actual_spatial_habitat_at_same_nest_confirmed_by_original_GPS":True,
        "independent_exogenous_ice_or_access_shift_at_nest":False,
        "published_claims_discovered_by_new_analysis":False,
        "new_causal_hypothesis_or_p_values_fitted":False,
        "frozen_ecology_pr189_unchanged":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outcomes",type=Path,required=True)
    p.add_argument("--locations",type=Path,required=True)
    p.add_argument("--followup",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    z=audit(load_author_csv(a.outcomes,SHA["outcomes"]),
            load_author_csv(a.locations,SHA["locations"]),
            load_author_csv(a.followup,SHA["followup"]))
    a.out.write_text(json.dumps(z,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("SOURCE_JOINS",z["exact_outcome_location_nestid_matches"],"/",z["outcome_table_valid_nests"])
    print("FOLLOWUP_DATE_CLASSES",json.dumps(z["followup_record_date_classes"],sort_keys=True))
    print("FOLLOWUP_RAW_OCCUPIED",json.dumps(z["raw_detected_occupied_nest_counts"],sort_keys=True))
    print("FOLLOWUP_RAW_ACTIVE",json.dumps(z["raw_detected_active_nest_counts"],sort_keys=True))
    print("DATES_ONLY_ACTIVE",z["raw_active_ids_only_outside_window"])
    print("BIOLOGICAL_CAUSAL_FIT",False)


if __name__=="__main__":
    main()
