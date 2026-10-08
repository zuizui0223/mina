#!/usr/bin/env python3
"""Post-publication exploratory ONLY: early neighbors vs confirmed creche.
Source: Cox et al 2024, pointblue/solo_nests 2023 release pinned SHA.
Observational nearest-neighbor count is NOT an independently assigned
treatment, and 0 cr_confirm means "not directly confirmed" not chick death.
No p-values and no new causal result are authorized.
"""
from __future__ import annotations
import argparse
from collections import defaultdict,Counter
import csv
from io import StringIO
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path

SHA={
    "checks":"019915d95f61ce2f4071959777ab92990a9021f4",
    "outcomes":"a21648a25b12f42759ca5d5bd011ec32c36d3dfc",
    "locations":"9e2dbe1426e47d6cf2dfc84110e8204c7ba92329",
}
CUTOFFS=("2021-11-24","2021-12-01","2021-12-15","2021-12-22")
CR_SUCCESS_LABEL="DIRECTLY_CONFIRMED_CRECHE_NOT_POPULATION_FLEDGING"


def csv_author(path, expected_blob):
    b=Path(path).read_bytes()
    digest=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if digest != expected_blob:
        raise ValueError(f"Original source blob mismatch: {path}")
    # The author's 2021 observation comments contain literal Windows-1252
    # bytes (e.g. 0x85 for ellipsis). Do not silently corrupt them with
    # replacement characters; preserve the original byte SHA first.
    try:
        text=b.decode("utf-8-sig")
    except UnicodeDecodeError:
        text=b.decode("cp1252")
    return list(csv.DictReader(StringIO(text,newline="")))


def num(value):
    try: v=float(value)
    except (TypeError,ValueError):return None
    return v if math.isfinite(v) else None


def source_check_date(value):
    try:return datetime.strptime(str(value or "").strip(),"%m/%d/%Y").date()
    except ValueError:return None


def score(checks,outcomes,locations,require_original=True):
    all_o={}
    for r in outcomes:
        nid=str(r.get("nestid","")).strip()
        if not nid.startswith("solo") or not nid[4:].isdigit():continue
        if nid in all_o:raise ValueError("Repeated outcome nest identity")
        all_o[nid]=r
    loc={}
    for r in locations:
        nid=str(r.get("nestid","")).strip()
        if nid in loc:raise ValueError("Repeated GPS location nest identity")
        loc[nid]=r
    if set(all_o)!=set(loc):raise ValueError("GPS nest identity crosswalk incomplete")
    if require_original and (len(all_o)!=50 or len(checks)!=439):
        raise ValueError("Not exact source scope of 50 nests and 439 serial checks")
    included=[nid for nid,r in all_o.items()
              if str(r.get("breeder","")).strip()=="1" and nid!="solo27"]
    if require_original and len(included)!=36:
        raise ValueError("Expected 36 originally active nests excluding poorly sampled solo27")
    observed=defaultdict(list)
    nbad=0
    for r in checks:
        nid=str(r.get("nestid","")).strip()
        if nid not in all_o:raise ValueError("Unknown observation nest identity")
        day=source_check_date(r.get("date"))
        if day is None:
            nbad+=1
            continue
        n=num(r.get("n_neighbors"))
        if n is not None and n<0:
            raise ValueError("Negative observed neighbor count")
        observed[nid].append((day,n,r))
    def group_stats(ids):
        cr=sum(num(all_o[x].get("cr_confirm")) is not None and
               num(all_o[x].get("cr_confirm"))>0 for x in ids)
        dist=[num(loc[x].get("dist_nearest_subcol_nest_m")) for x in ids]
        dist=[x for x in dist if x is not None]
        rocks=[num(loc[x].get("rocksize_cm")) for x in ids]
        rocks=[x for x in rocks if x is not None]
        area=dict(sorted(Counter(str(loc[x].get("area","")).strip() for x in ids).items()))
        return {
            "n_nests":len(ids),
            "n_creche_directly_confirmed":cr,
            "confirmed_fraction_NOT_survival_rate":cr/len(ids) if ids else None,
            "n_large_shelter_rock_at_least15cm":sum(x>=15 for x in rocks),
            "n_valid_rock_values":len(rocks),
            "mean_source_distance_to_subcolony_m":(
                sum(dist)/len(dist) if dist else None),
            "n_valid_distance":len(dist),
            "source_area_codes":area
        }
    cutoffs={}
    for t in CUTOFFS:
        bound=datetime.fromisoformat(t).date()
        early={}
        for nid in included:
            elig=[(date,n) for date,n,r in observed[nid]
                  if date.year==2021 and date<=bound and n is not None]
            if not elig:raise ValueError("Missing pre-cutoff neighbor observation")
            early[nid]=any(n>0 for date,n in elig)
        positive=[nid for nid in included if early[nid]]
        negative=[nid for nid in included if not early[nid]]
        cutoffs[t]={
            "cutoff_date":t,
            "pre_cutoff_social_neighbor_detected":group_stats(positive),
            "pre_cutoff_social_neighbor_not_detected":group_stats(negative),
            "exposure_temporal_horizon":"before 2021-12-23 original median hatch, not before original nest selection",
            "no_exposure_observation_after_cutoff_used":True
        }
    pre_dated=[
        (nid,str(r.get("date",""))) for nid,seq in observed.items() for date,n,r in seq if date.year==2022
    ]
    return {
        "status":"CROZIER_SINGLE_SITE_EXPLORATORY_EARLY_NEIGHBOR_CRECHE_SOURCE_SCREEN",
        "publication":"Cox et al 2024 10.1007/s00300-024-03246-9",
        "source_commit":"04517cedac18950408abd4d0b510f4aae3447f05",
        "source_total_nests":len(all_o),
        "original_observation_rows":len(checks),
        "n_original_breeder_nests_in_analysis":len(included),
        "author_exclusion":"solo27 poorly observed removed",
        "original_median_hatch_date":"2021-12-23",
        "cutoff_comparisons":cutoffs,
        "source_2022_followup_rows_in_2021_checks":len(pre_dated),
        "n_invalid_or_missing_2021_check_dates":nbad,
        "direct_creche_2021_nests_included":sum(num(all_o[x].get("cr_confirm")) is not None and
            num(all_o[x].get("cr_confirm"))>0 for x in included),
        "outcome_detection_is_imperfect":True,
        "neighbor_acquisition_may_be_caused_by_earlier_egg_or_territory_quality":True,
        "no_causal_social_rescue_or_predation_result":True,
        "not_an_island_generalization":True,
        "not_a_confirmatory_preregistered_test":True,
        "no_pvalue":True,
        "PR189_frozen":True
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checks",type=Path,required=True)
    p.add_argument("--outcomes",type=Path,required=True)
    p.add_argument("--locations",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=score(csv_author(a.checks,SHA["checks"]),
            csv_author(a.outcomes,SHA["outcomes"]),
            csv_author(a.locations,SHA["locations"]))
    a.out.write_text(json.dumps(d,indent=2)+"\n",encoding="utf8")
    print("SOURCE_NESTS",d["n_original_breeder_nests_in_analysis"])
    for k,v in d["cutoff_comparisons"].items():
        x=v["pre_cutoff_social_neighbor_detected"]
        y=v["pre_cutoff_social_neighbor_not_detected"]
        print("BEFORE_HATCH_NEIGHBOR_DATE",k,"NEIGHBORS",x["n_creche_directly_confirmed"],
              "/",x["n_nests"],"NONE",y["n_creche_directly_confirmed"],"/",y["n_nests"])
        print("COVARIATE_BALANCE",k,"NEAR_DIST",x["mean_source_distance_to_subcolony_m"],
              "FAR_DIST",y["mean_source_distance_to_subcolony_m"])
    print("NO_CAUSAL_INFERENCE_NO_P_VALUES")


if __name__=="__main__": main()
