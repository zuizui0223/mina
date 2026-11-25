#!/usr/bin/env python3
"""2022 neighboring nests versus 2021 focal-site re-occupancy, separate units.

Post-publication *source audit*, not an independent test of colonization:
Cox et al. 2024 already reported local prospective subcolonies. A known
2021 focal site may stay empty even when field notes show nearby nesters;
the origin, success and individual identity of neighbor breeders are unknown.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import datetime
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_cape_crozier_solo_nest_spatial_outcome_join_v1 as source

WIN_START=datetime(2022,10,1)
WIN_END=datetime(2023,3,31,23,59,59)
UNKNOWN_STATUSES={"","MT","MT?","UNK","INC?","NBS","FAIL?","FBN?","INC9"}

def analyze(outcomes,sites,followup,strict=True):
    original={}
    for r in outcomes:
        id=source.canonical_key(r.get("nestid"))
        if id is None:continue
        if id in original:raise ValueError("Duplicate focal nest")
        state=str(r.get("breeder","")).strip()
        if state not in ("0","1"):raise ValueError("Unknown 2021 breeder state")
        original[id]=state
    if strict and (set(original)!={str(i) for i in range(1,51)} or len(followup)!=136):
        raise ValueError("Original 50 sites/136 follow-up records changed")
    names=set()
    for r in sites:
        id=source.canonical_key(r.get("nestid"))
        if id is None or id in names: raise ValueError("Invalid original GPS site IDs")
        names.add(id)
    if names!=set(original):raise ValueError("GPS and original focal nest identity mismatch")
    by=defaultdict(list)
    outside=Counter()
    for r in followup:
        id=source.canonical_key(r.get("nestid"))
        if id not in original:raise ValueError("Follow-up site ID absent from source roster")
        day=source.parse_original_date(r.get("date"))
        if day is None:
            outside["UNKNOWN_DATE"]+=1
            continue
        if day<WIN_START or day>WIN_END:
            outside["DATE_OUTSIDE_2022_2023_SEASON"]+=1
            continue
        raw=str(r.get("n_neighbors","")).strip()
        try: number=float(raw)
        except ValueError: number=None
        if number is not None and (number<0 or number!=number):
            raise ValueError("Invalid adjacent nest count")
        status=str(r.get("status","")).strip().upper()
        by[id].append({
            "date":day.date().isoformat(),
            "focal_raw_status":status,
            "n_neighbors":number,
            "has_neighbor":number is not None and number>0,
            "focal_strict_occupied":status not in UNKNOWN_STATUSES,
            "original_source_note":str(r.get("notes","") or "")[:200]
        })
    groups={
        "original_2021_nonbreeders":[i for i,v in original.items() if v=="0"],
        "original_2021_breeders":[i for i,v in original.items() if v=="1"]
    }
    summary={}
    details=[]
    for group,ids in groups.items():
        supported=[i for i in ids if by[i]]
        near=[i for i in ids if any(r["has_neighbor"] for r in by[i])]
        focal=[i for i in ids if any(r["focal_strict_occupied"] for r in by[i])]
        near_without_focal=[i for i in near if i not in focal]
        summary[group]={
            "n_original_sites":len(ids),
            "n_sites_with_date_valid_followup":len(supported),
            "n_sites_with_positive_nearby_nest_count":len(near),
            "n_sites_with_strict_focal_occupancy":len(focal),
            "n_neighbor_positive_without_strict_focal_occupancy":len(near_without_focal),
            "n_stated_empty_focal_site_near_neighbor":sum(
                any(z["has_neighbor"] and z["focal_raw_status"]=="MT" for z in by[i])
                for i in ids)
        }
        for id in near_without_focal:
            candidates=[r for r in by[id] if r["has_neighbor"]]
            details.append({
                "nest_id":"solo"+id,
                "source_2021_breeder_code":original[id],
                "2022_nearby_nester_detected_at_original_mark":True,
                "2022_original_focal_site_occupancy_confirmed":False,
                "neighbor_observations":candidates,
                "inference":"NEIGHBOR_NOT_IDENTIFIED_AS_ORIGINAL_PARENT_OR_SUCCESSFUL_BREEDER"
            })
    if strict and (len(groups["original_2021_nonbreeders"])!=13 or
                   len(groups["original_2021_breeders"])!=37):
        raise ValueError("2021 original breeding/nonbreeding roster changed")
    return {
        "status":"SOURCE_FOCAL_SITE_VS_NEIGHBORHOOD_UNIT_DIFFERENCE",
        "study":"Cox et al 2024 original source, already published subcolony formation",
        "original_nest_sites":len(original),
        "retained_followup_site_visit_rows":sum(map(len,by.values())),
        "out_of_window_or_unparseable_records":dict(outside),
        "groups":summary,
        "positive_nearby_nesting_where_original_focal_not_confirmed":details,
        "new_colony_founder_origin_identified":False,
        "adjacent_nest_success_or_marked_breeder_identified":False,
        "original_focal_2022_absence_proven_in_ambiguous_INC_question_sites":False,
        "existing_Cox_2024_finding_of_four_nascent_subcolonies_prior_art":True,
        "no_causal_site_legacy_or_social_inhibition_fitted":True,
        "no_new_confirmatory_test":True,
        "PR189_frozen":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outcomes",type=Path,required=True)
    p.add_argument("--sites",type=Path,required=True)
    p.add_argument("--followup",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    res=analyze(
      source.load_author_csv(a.outcomes,source.SHA["outcomes"]),
      source.load_author_csv(a.sites,source.SHA["locations"]),
      source.load_author_csv(a.followup,source.SHA["followup"]))
    a.out.write_text(json.dumps(res,indent=2)+"\n",encoding="utf8")
    print("ORIGINAL_50_FOCAL_SITES",res["original_nest_sites"])
    for name,r in res["groups"].items():print("ORIGINAL_GROUP",name,r)
    print("NEIGHBOR_NEAR_NOT_FOCAL",
          [d["nest_id"] for d in res["positive_nearby_nesting_where_original_focal_not_confirmed"]])
    print("NO_TRUE_ORIGIN_COLONIZATION_OR_FITNESS_RESULT")
if __name__=="__main__":main()
