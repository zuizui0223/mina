#!/usr/bin/env python3
"""Post-publication original source negative-control/habitat diagnostic.

No causal social treatment, no skua event data, no confirmed chick deaths;
stage-specific observational classification and imbalance only.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from datetime import date
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import screen_crozier_early_neighbor_creche_v1 as source

CUTOFF=date(2021,12,1)
SITE_STATUSES={"GONE","MT","NBS"}
ROCK_THRESHOLD_CM=15

def subset_summary(ids, outcome):
    n=len(ids)
    success=sum(source.num(outcome[i]["cr_confirm"]) is not None and
                source.num(outcome[i]["cr_confirm"])>0 for i in ids)
    return {"n":n,"n_directly_confirmed_creche":success,
            "fraction_confirmation_not_survival":success/n if n else None}

def source_diagnostic(checks,outcomes,locations,strict=True):
    audited=source.score(checks,outcomes,locations,require_original=strict)
    out={r["nestid"]:r for r in outcomes if str(r.get("nestid","")).startswith("solo")
         and str(r.get("nestid",""))[4:].isdigit()}
    geog={r["nestid"]:r for r in locations}
    eligible=sorted((i for i,r in out.items()
                     if str(r.get("breeder","")).strip()=="1" and i!="solo27"),
                    key=lambda i:int(i[4:]))
    history=defaultdict(list)
    for r in checks:
        id=str(r.get("nestid","")).strip()
        if id not in out:continue
        day=source.source_check_date(r.get("date"))
        if day is None or day.year!=2021 or day>CUTOFF:continue
        neighbors=source.num(r.get("n_neighbors"))
        history[id].append((day,neighbors,str(r.get("status","")).strip().upper()))
    assigned={}
    visits={}
    explicit_empty={}
    for id in eligible:
        records=sorted(history[id],key=lambda z:z[0])
        if not records:raise ValueError("Missing exposure-period observations")
        known=[n for d,n,st in records if n is not None]
        if not known:raise ValueError("No neighbor observation for original breeder")
        assigned[id]="early_neighbor" if any(n>0 for n in known) else "none_detected"
        visits[id]=len(set(d for d,n,st in records))
        # Only explicitly documented source 'GONE' by cutoff; never
        # claim an entire ecological colony or chick has failed.
        explicit_empty[id]=any(st=="GONE" for d,n,st in records)
    near=[id for id in eligible if assigned[id]=="early_neighbor"]
    no=[id for id in eligible if assigned[id]=="none_detected"]
    if strict and (len(near),len(no))!=(9,27):
        raise ValueError("Original 9/27 nest source grouping changed")
    rocks={}
    for rockname,lambda_fn in (
        ("rock_ge15",lambda x:x>=ROCK_THRESHOLD_CM),
        ("rock_lt15",lambda x:x<ROCK_THRESHOLD_CM),
    ):
        a=[]
        for id in eligible:
            rock=source.num(geog[id].get("rocksize_cm"))
            if rock is None or rock<0:
                raise ValueError("Missing/invalid original rock-size source value")
            if lambda_fn(rock): a.append(id)
        rocks[rockname]={
            "early_neighbor":subset_summary([x for x in a if x in near],out),
            "none_detected":subset_summary([x for x in a if x in no],out)
        }
    area_counts=Counter((str(geog[x].get("area","")).strip(),assigned[x]) for x in eligible)
    overlap=[area for area in sorted({k[0] for k in area_counts})
             if area_counts[(area,"early_neighbor")]>0 and area_counts[(area,"none_detected")]>0]
    overlap_near=[x for x in near if str(geog[x].get("area","")).strip() in overlap]
    overlap_no=[x for x in no if str(geog[x].get("area","")).strip() in overlap]
    area_details={}
    for name in sorted({k[0] for k in area_counts}):
        area_details[name]={
            "early_neighbor":subset_summary([x for x in near if geog[x].get("area","").strip()==name],out),
            "none_detected":subset_summary([x for x in no if geog[x].get("area","").strip()==name],out)
        }
    noncheck_near=[x for x in near if not explicit_empty[x]]
    noncheck_no=[x for x in no if not explicit_empty[x]]
    successes0=subset_summary(no,out)["n_directly_confirmed_creche"]
    successes1=subset_summary(near,out)["n_directly_confirmed_creche"]
    # One-sided exact arithmetic for alternative unresolved direct nonconfirmations.
    # This is a *logical ascertainment bound* NOT an estimated detection error.
    needed=next((k for k in range(0,len(no)-successes0+1)
                 if (successes0+k)*len(near)>=successes1*len(no)),None)
    return {
        "status":"CROZIER_EARLY_NEIGHBOR_HABITAT_VISIT_NEGATIVE_CONTROL_ONLY",
        "source_release":"pointblue/solo_nests@04517cedac18950408abd4d0b510f4aae3447f05",
        "cutoff":"2021-12-01",
        "n_original_breeding_sites":len(eligible),
        "main_counts":{
            "early_neighbor":subset_summary(near,out),
            "none_detected":subset_summary(no,out)
        },
        "source_rock_size_strata_counts":rocks,
        "area_code_counts":area_details,
        "areas_having_both_neighbor_states":overlap,
        "within_shared_area_raw_counts":{
            "early_neighbor":subset_summary(overlap_near,out),
            "none_detected":subset_summary(overlap_no,out)
        },
        "explicit_GONE_check_by_cutoff":{
            "early_neighbor":len(near)-len(noncheck_near),
            "none_detected":len(no)-len(noncheck_no)
        },
        "exclude_explicit_GONE_from_source_risk_set_only":{
            "early_neighbor":subset_summary(noncheck_near,out),
            "none_detected":subset_summary(noncheck_no,out)
        },
        "mean_distinct_check_days_by_source_neighbor_class":{
            "early_neighbor":sum(visits[x] for x in near)/len(near),
            "none_detected":sum(visits[x] for x in no)/len(no)
        },
        "logical_ascertainment_tipping_min_additional_unconfirmed_creche_positive_no_neighbor":needed,
        "tipping_bound_not_estimated_false_negative_count":True,
        "raw_egg_incubation_order_audit_external":True,
        "source_cr_confirm_0_not_confirmed_chick_death":True,
        "source_spatial_strata_not_confounder_adjusted_randomization":True,
        "source_predator_events_and_parental_quality_not_measured":True,
        "unexposed_species_or_independent_island_replication_not_present":True,
        "causal_social_protection_or_founding_claim_permitted":False,
        "p_values_or_confirmatory_estimates_fitted":False,
        "frozen_PR189_science_changed":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--checks",type=Path,required=True)
    p.add_argument("--outcomes",type=Path,required=True)
    p.add_argument("--locations",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    z=p.parse_args()
    result=source_diagnostic(
        source.csv_author(z.checks,source.SHA["checks"]),
        source.csv_author(z.outcomes,source.SHA["outcomes"]),
        source.csv_author(z.locations,source.SHA["locations"]))
    z.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print("SOURCE_NESTS",result["n_original_breeding_sites"])
    print("MAIN",result["main_counts"])
    print("ROCK_GROUPS",result["source_rock_size_strata_counts"])
    print("SHARED_AREAS",result["areas_having_both_neighbor_states"],
          result["within_shared_area_raw_counts"])
    print("EARLY_GONE",result["explicit_GONE_check_by_cutoff"])
    print("EARLY_GONE_EXCLUDED",result["exclude_explicit_GONE_from_source_risk_set_only"])
    print("EFFORT",result["mean_distinct_check_days_by_source_neighbor_class"])
    print("LOGICAL_NOT_ESTIMATED_TIPPING",result["logical_ascertainment_tipping_min_additional_unconfirmed_creche_positive_no_neighbor"])
    print("NO_CAUSAL_SOCIAL_PROTECTION_CONCLUSION")

if __name__=="__main__":main()
