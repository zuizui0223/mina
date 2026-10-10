#!/usr/bin/env python3
"""Retrospective source-sequence check, NOT causal neighbor effect estimation.

First observed egg and first observed neighbor are interval-censored detection
times, not laying or neighbor-arrival times. Uses frozen 2021 early-neighbor
cutoff and exactly 36 monitored breeder nest sites (solo27 excluded).
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import screen_crozier_early_neighbor_creche_v1 as src

CUTOFF=date(2021,12,1)

def ordered_source_audit(observations,outcomes,locations,strict=True):
    # Reuse the verified original source/identity/exposure gate.
    baseline=src.score(observations,outcomes,locations,require_original=strict)
    source_out={r["nestid"]:r for r in outcomes
                if str(r.get("nestid","")).startswith("solo")
                and str(r["nestid"])[4:].isdigit()}
    original=[id for id,r in source_out.items()
              if str(r.get("breeder","")).strip()=="1" and id!="solo27"]
    by=defaultdict(list)
    for r in observations:
        nid=str(r.get("nestid","")).strip()
        if nid not in source_out:continue
        day=src.source_check_date(r.get("date"))
        if day is None or day.year!=2021 or day>CUTOFF:continue
        by[nid].append((day,src.num(r.get("n_neighbors")),src.num(r.get("egg_n")),str(r.get("status","")).strip().upper()))

    exposure=[]
    unexposed=[]
    ordering=Counter()
    row_details=[]
    for nid in original:
        checks=sorted(by[nid],key=lambda z:z[0])
        if not checks:raise ValueError("No valid pre-cutoff observation for an original breeder")
        positives=[z[0] for z in checks if z[1] is not None and z[1]>0]
        eggs=[z[0] for z in checks if z[2] in (1,2)]
        incub=[z[0] for z in checks if "INC" in z[3] and z[3] not in ("INC?",)]
        if positives:
            first_neighbor=min(positives)
            first_egg=min(eggs) if eggs else None
            first_incub=min(incub) if incub else None
            if first_egg is None:
                order="NO_CONFIRMED_EGG_BY_CUTOFF"
            elif first_egg<first_neighbor: order="EGG_DETECTED_BEFORE_NEIGHBOR"
            elif first_egg==first_neighbor: order="SAME_OBSERVATION_DAY"
            else: order="NEIGHBOR_DETECTED_BEFORE_FIRST_EGG_SIGHTING"
            last_zero=max((z[0] for z in checks
                           if z[0]<first_neighbor and z[1]==0),default=None)
            ordering[order]+=1
            exposure.append(nid)
            row_details.append({
                "nest":nid,
                "first_positive_neighbor_date":first_neighbor.isoformat(),
                "last_zero_neighbor_date_before_positive":last_zero.isoformat() if last_zero else None,
                "first_observed_egg_date":first_egg.isoformat() if first_egg else None,
                "first_observed_incubation_date":first_incub.isoformat() if first_incub else None,
                "egg_vs_neighbor_order":order,
                "incubation_already_observed_at_or_before_neighbor":(
                    first_incub is not None and first_incub<=first_neighbor),
                "site_observation_days_by_cutoff":len({z[0] for z in checks}),
                "direct_creche_confirmation":src.num(source_out[nid].get("cr_confirm")) is not None
                 and src.num(source_out[nid].get("cr_confirm"))>0
            })
        else:
            unexposed.append(nid)
    if strict and (len(exposure)!=9 or len(unexposed)!=27):
        raise ValueError("2021 frozen early neighbor exposure 9/27 changed")
    assert len(row_details)==len(exposure)
    exposure_obs=[len({z[0] for z in by[id]}) for id in exposure]
    unexposed_obs=[len({z[0] for z in by[id]}) for id in unexposed]
    return {
        "status":"SOURCE_OBSERVATION_TIME_ORDER_AUDIT_NONCAUSAL",
        "source_frozen_release":"pointblue/solo_nests@04517cedac18950408abd4d0b510f4aae3447f05",
        "cutoff":"2021-12-01",
        "n_original_breeders":len(original),
        "n_neighbor_positive_before_cutoff":len(exposure),
        "n_neighbor_never_detected_before_cutoff":len(unexposed),
        "first_detected_egg_relative_to_first_positive_neighbor":dict(sorted(ordering.items())),
        "n_with_incubation_detected_by_or_before_first_neighbor":sum(
            x["incubation_already_observed_at_or_before_neighbor"] for x in row_details),
        "n_with_prior_observed_neighbor_zero":sum(x["last_zero_neighbor_date_before_positive"] is not None for x in row_details),
        "mean_distinct_pre_cutoff_observation_days_with_early_neighbor":sum(exposure_obs)/len(exposure),
        "mean_distinct_pre_cutoff_observation_days_no_detected_neighbor":sum(unexposed_obs)/len(unexposed),
        "nest_source_intervals":row_details,
        "new_confirmatory_causal_result":False,
        "neighbor_arrival_date_observed_without_interval_censoring":False,
        "first_egg_sighting_equivalent_to_egg_laying_date":False,
        "status_not_a_social_settlement_effect":True,
        "frozen_PR189_unmodified":True,
        "source_result_from_same_already_exposed_cohort":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--checks",type=Path,required=True)
    p.add_argument("--outcomes",type=Path,required=True)
    p.add_argument("--locations",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=ordered_source_audit(
       src.csv_author(a.checks,src.SHA["checks"]),
       src.csv_author(a.outcomes,src.SHA["outcomes"]),
       src.csv_author(a.locations,src.SHA["locations"]))
    a.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("SOURCE_TIME_ORDERING",report["first_detected_egg_relative_to_first_positive_neighbor"])
    print("OBSERVED_INCUBATION_AT_OR_BEFORE_NEIGHBOR",
          report["n_with_incubation_detected_by_or_before_first_neighbor"])
    print("OBSERVATION_DAY_MEANS",
          report["mean_distinct_pre_cutoff_observation_days_with_early_neighbor"],
          report["mean_distinct_pre_cutoff_observation_days_no_detected_neighbor"])
    print("NO_CAUSAL_ECOLOGICAL_EFFECT")


if __name__=="__main__":main()
