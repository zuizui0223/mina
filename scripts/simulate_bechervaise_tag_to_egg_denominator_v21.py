#!/usr/bin/env python3
"""Synthetic ONLY: tagged penguin gateway->OWN verified-egg observation gate.

THIS IS NOT the published AADC CSV parser. The genuine AAS_4086 RFID raw
encoding and AAS_4518 nest-resight formats have NOT been retrieved. Uses a
purpose-built mock normalized event stream to enforce causal ordering and
demonstrate missing-outcome bounds. No real tag IDs or wildlife events opened.

A tag's first gate observation is NOT its actual first colony arrival.
A missed nest reader scan is NEVER a proof of nonbreeding.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime
import argparse,json
from pathlib import Path

EVENTS=("gate_in","gate_out","tag_at_nest","direct_egg_with_same_tag")

def parse_date(s):
    try:
        return datetime.strptime(str(s),"%Y-%m-%dT%H:%M:%S")
    except ValueError as err:
        raise ValueError("Source date must be full ISO second-resolution, not inferred") from err

def source_free_event_gate(events):
    seen=set()
    by=defaultdict(list)
    for e in events:
        needed=("mock_tag","season","time","kind")
        if any(k not in e for k in needed):
            raise ValueError("Missing compulsory normalized mock source fields")
        tag=e["mock_tag"]
        season=e["season"]
        if not str(tag).startswith("SYNTH_"):
            raise ValueError("Only SYNTHETIC tag labels accepted; original penguin tags forbidden")
        if not isinstance(season,str) or not season:
            raise ValueError("Breeding season must be explicit source-specific label")
        kind=e["kind"]
        if kind not in EVENTS:
            raise ValueError("Cannot automatically promote unknown code to breeding evidence")
        t=parse_date(e["time"])
        eventkey=(tag,season,t,kind)
        if eventkey in seen:
            raise ValueError("Exact duplicate standardized source event must be QC'd")
        seen.add(eventkey)
        by[(tag,season)].append((t,kind))
    in_s={x for x in by if any(k=="gate_in" for _,k in by[x])}
    direct_laying_s={x for x in by if any(k=="direct_egg_with_same_tag" for _,k in by[x])}
    positives=[]
    eggs_before_first_gate=[]
    nest_scanned_without_direct_egg=[]
    unknown_at_nest=[]
    for key in sorted(in_s):
        seq=sorted(by[key])
        ins=[d for d,k in seq if k=="gate_in"]
        eggs=[d for d,k in seq if k=="direct_egg_with_same_tag"]
        scans=[d for d,k in seq if k=="tag_at_nest"]
        first_in=min(ins)
        if eggs and min(eggs)>first_in:
            positives.append(key)
        elif eggs:
            eggs_before_first_gate.append(key)
        elif scans:
            nest_scanned_without_direct_egg.append(key)
        else:
            unknown_at_nest.append(key)
    n=len(in_s)
    if n==0:raise ValueError("No synthetic tagged cohort with observed inbound gate crossing")
    return {
        "scientific_status":"SYNTHETIC_SAME_ID_TEMPORAL_ORDER_PROOF_ONLY",
        "source_event_schema":"USER_DEFINED_MOCK_NOT_AUTHOR_AADC_FIELDS",
        "n_unique_tag_seasons_with_gate_in":n,
        "n_raw_gate_in_rows":sum(k=="gate_in" for a in by.values() for d,k in a),
        "n_same_tag_direct_egg_AFTER_first_observed_gate_in":len(positives),
        "n_same_tag_direct_egg_before_or_at_first_gate_in":len(eggs_before_first_gate),
        "n_tag_at_nest_but_NO_DIRECT_EGG":len(nest_scanned_without_direct_egg),
        "n_unobserved_nest_status_given_tag_gate":len(unknown_at_nest),
        "individual_tag_keys_in_positive_group":sorted("_".join(x) for x in positives),
        "lower_bound_fraction_with_observed_first_documented_egg_post_gate":len(positives)/n,
        "upper_bound_fraction_with_first_documented_egg_post_gate_if_unknown_resolved":(n-len(eggs_before_first_gate))/n,
        "first_documented_egg_before_gate_EXCLUDED_FROM_POSSIBLE_FIRST_POST_GATE":len(eggs_before_first_gate),
        "no_true_population_arrival_rate_identified":True,
        "first_logged_gate_pass_not_first_island_arrival":True,
        "past_reproductive_history_of_mock_tags_known":False,
        "true_first_breeding_transition_identified":False,
        "at_risk_nonbreeder_denominator_detected_completely":False,
        "nest_reader_negative_not_verified_no_egg":True,
        "same_tag_nest_scan_not_equal_verified_egg":True,
        "no_real_original_Bechervaise_source_bird_rows_loaded":True,
        "actual_source_nest_gate_tag_encoding_unverified":True,
        "no_new_causal_result":True,
        "PR189_science_unchanged":True
    }

def demo_events():
    return [
      # Bird A crossed 3 times, later egg confirmed in same mock season.
      {"mock_tag":"SYNTH_A","season":"2008/09","time":"2008-11-09T07:30:00","kind":"gate_in"},
      {"mock_tag":"SYNTH_A","season":"2008/09","time":"2008-11-10T08:00:00","kind":"gate_out"},
      {"mock_tag":"SYNTH_A","season":"2008/09","time":"2008-11-14T08:00:00","kind":"gate_in"},
      {"mock_tag":"SYNTH_A","season":"2008/09","time":"2008-11-21T08:00:00","kind":"tag_at_nest"},
      {"mock_tag":"SYNTH_A","season":"2008/09","time":"2008-11-21T09:00:00","kind":"direct_egg_with_same_tag"},
      # Bird B appeared on nest, but no verified egg; cannot call breeder.
      {"mock_tag":"SYNTH_B","season":"2008/09","time":"2008-11-08T10:00:00","kind":"gate_in"},
      {"mock_tag":"SYNTH_B","season":"2008/09","time":"2008-11-26T07:00:00","kind":"tag_at_nest"},
      # Bird C recorded inbound, egg already observed before this gate record.
      {"mock_tag":"SYNTH_C","season":"2008/09","time":"2008-11-02T10:00:00","kind":"direct_egg_with_same_tag"},
      {"mock_tag":"SYNTH_C","season":"2008/09","time":"2008-11-05T09:30:00","kind":"gate_in"},
      # Bird D inbound but not seen at monitored nest.
      {"mock_tag":"SYNTH_D","season":"2008/09","time":"2008-11-09T09:00:00","kind":"gate_in"},
    ]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    z=source_free_event_gate(demo_events())
    args.out.write_text(json.dumps(z,indent=2)+"\n",encoding="utf-8")
    print("SYNTHETIC_GATE_TAG_SEASONS",z["n_unique_tag_seasons_with_gate_in"])
    print("SYNTHETIC_CONFIRMED_DIRECT_EGG_AFTER_GATE",z["n_same_tag_direct_egg_AFTER_first_observed_gate_in"])
    print("SYNTHETIC_NO_NEST_EGG_STATUS_AFTER_GATE",z["n_unobserved_nest_status_given_tag_gate"])
    print("SOURCE_2019_ALREADY_LINKED_ID_AND_BREEDER_STATUS",True)
    print("SYNTHETIC_FIRST_DOCUMENTED_EGG_FRACTION_BOUNDS",z["lower_bound_fraction_with_observed_first_documented_egg_post_gate"],z["upper_bound_fraction_with_first_documented_egg_post_gate_if_unknown_resolved"])
    print("ACTUAL_FIRST_BREEDING_PROBABILITY", "NOT_IDENTIFIED")
if __name__=="__main__":main()
