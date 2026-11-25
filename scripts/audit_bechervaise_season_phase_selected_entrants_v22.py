#!/usr/bin/env python3
"""Purely synthetic gate-visit season phase and personally verified egg audit.

NOT a parser or model for the actual AADC Béchervaise RFID records. Assumes
a season-specific *reference earliest colony egg*, then first colony chick
hatch. This reference threshold is NOT the last date an adult may lay.
Observed pre-hatch, post-hatch entrances are relevant to prospective and
future-season questions but cannot be thrown into the same denominator as
visits preceding the first local egg.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
import argparse,json

def timepoint(value):
    try:return datetime.strptime(str(value),"%Y-%m-%dT%H:%M:%S")
    except (TypeError,ValueError) as exc:
        raise ValueError("Require full source time with date and seconds") from exc

def phase(t,first_egg,first_hatch):
    # Historical nest data often date egg/hatch checks by CALENDAR DAY,
    # not actual event second. Never sort a gate timestamp within that same
    # date using an invented midnight event time.
    if t.date() in (first_egg.date(),first_hatch.date()):
        return "AMBIGUOUS_EGG_OR_HATCH_BOUNDARY_DAY"
    if t<first_egg:return "PRE_COLONY_FIRST_EGG"
    if t<first_hatch:return "AFTER_FIRST_COLONY_EGG_PRE_FIRST_HATCH"
    return "POST_FIRST_COLONY_HATCH"

def audit(events, seasonal_boundaries):
    indexed=defaultdict(list)
    known=set()
    for z in events:
        for k in ("tag","season","time","event"):
            if k not in z:raise ValueError("Missing source-defined synthetic event field: "+k)
        tag=str(z["tag"])
        if not tag.startswith("SYNTH_"):
            raise ValueError("Actual wildlife RFID identifiers cannot be read by synthetic example")
        season=str(z["season"])
        if season not in seasonal_boundaries:
            raise ValueError("No measured stage boundary in mock source season")
        kind=z["event"]
        if kind not in ("gate_in","gate_out","tag_on_nest","direct_own_egg"):
            raise ValueError("Unknown biological observation code")
        t=timepoint(z["time"])
        k=(tag,season,t,kind)
        if k in known:raise ValueError("Duplicate tag-season-time-kind observation")
        known.add(k)
        indexed[(tag,season)].append((t,kind))
    rows=[]
    for (tag,season),seq in sorted(indexed.items()):
        boundary=seasonal_boundaries[season]
        egg_anchor=timepoint(boundary["first_colony_egg_observed"])
        hatch_anchor=timepoint(boundary["first_colony_hatch_observed"])
        if egg_anchor>=hatch_anchor:
            raise ValueError("First egg must predate first hatch in source")
        first_in=min((t for t,kind in seq if kind=="gate_in"),default=None)
        if first_in is None:continue
        eggs=sorted(t for t,k in seq if k=="direct_own_egg")
        scans=[t for t,k in seq if k=="tag_on_nest"]
        ph=phase(first_in,egg_anchor,hatch_anchor)
        first_egg=eggs[0] if eggs else None
        # An egg observed before first inbound pass is NOT an effect of pass.
        future=(first_egg is not None and first_egg>first_in)
        prior=(first_egg is not None and first_egg<=first_in)
        rows.append({
            "tag":tag,"season":season,
            "phase_of_FIRST_OBSERVED_gate_crossing":ph,
            "n_gate_in_events":sum(k=="gate_in" for t,k in seq),
            "directly_confirmed_own_egg_after_first_pass":future,
            "directly_confirmed_own_egg_prior_or_same_time":prior,
            "tag_observed_at_nest_without_direct_egg":bool(scans) and first_egg is None,
            "egg_status_missing_after_first_pass":first_egg is None,
            "is_true_first_arrival_proven":False,
            "first_lifetime_breeding_proven":False
        })
    if not rows:raise ValueError("No actual synthetic gateway entrant denominator")
    groups=defaultdict(list)
    for row in rows:
        groups[row["phase_of_FIRST_OBSERVED_gate_crossing"]].append(row)
    classes=("PRE_COLONY_FIRST_EGG","AFTER_FIRST_COLONY_EGG_PRE_FIRST_HATCH",
             "POST_FIRST_COLONY_HATCH","AMBIGUOUS_EGG_OR_HATCH_BOUNDARY_DAY")
    n_pre=len(groups[classes[0]])
    pre_confirmed=sum(x["directly_confirmed_own_egg_after_first_pass"]
                      for x in groups[classes[0]])
    pre_unknown=sum(x["egg_status_missing_after_first_pass"] for x in groups[classes[0]])
    observed_all=sum(x["directly_confirmed_own_egg_after_first_pass"] for x in rows)
    report={
        "status":"MOCK_FIRST_OBSERVED_ARRIVAL_PHASE_NOT_PENGUIN_DATA",
        "n_synthetic_tag_seasons_with_gate_in":len(rows),
        "n_synthetic_gate_in_events":sum(x["n_gate_in_events"] for x in rows),
        "phase_tag_season_counts":{name:len(groups[name]) for name in classes},
        "pre_first_colony_egg_candidates":n_pre,
        "pre_first_colony_egg_same_tag_direct_own_egg_AFTER_pass":pre_confirmed,
        "pre_first_colony_egg_direct_egg_not_confirmed":pre_unknown,
        "prelay_observed_documented_egg_fraction":pre_confirmed/n_pre if n_pre else None,
        "prelay_max_documented_egg_fraction_if_ALL_unknown_eggs_revealed":(
            (pre_confirmed+pre_unknown)/n_pre if n_pre else None),
        "all_phase_naive_documented_postgate_egg_fraction":observed_all/len(rows),
        "all_phase_fraction_NOT_a_true_breeding_propensity":True,
        "after_hatch_possible_late_egg_not_mathematically_impossible":True,
        "published_nonbreeder_gate_visits_mostly_after_hatch_Emmerson2019":True,
        "equal_season_first_colony_egg_not_individual_latest_laying_date":True,
        "same_calendar_day_gate_vs_egg_or_hatch_censored_not_exactly_ordered":True,
        "no_unobserved_eggs_turned_into_false_negatives":True,
        "no_attempt_to_infer_future_year_natal_recruitment":True,
        "source_publisher_and_methods_bechervaise_original_data_rows_read":0,
        "frozen_Ecology_PR189_unchanged":True,
        "true_same_tag_first_breeding_transition_identified":False,
        "new_island_ecology_causal_effect_fitted":False,
        "individual_mock_event_roles":rows
    }
    return report

def demo():
    boundaries={"2008/09":{
        "first_colony_egg_observed":"2008-11-10T00:00:00",
        "first_colony_hatch_observed":"2008-12-15T00:00:00"
    }}
    def row(tag,time,event):
        return {"tag":"SYNTH_"+tag,"season":"2008/09","time":time,"event":event}
    events=[
        row("A","2008-11-03T08:00:00","gate_in"),
        row("A","2008-11-05T08:00:00","gate_out"),
        row("A","2008-11-07T09:00:00","gate_in"),
        row("A","2008-11-20T12:00:00","direct_own_egg"),
        row("B","2008-12-20T08:00:00","gate_in"),
        row("B","2008-12-24T12:00:00","tag_on_nest"),
        row("C","2008-11-05T10:00:00","gate_in"),
        row("D","2008-11-15T12:00:00","direct_own_egg"),
        row("D","2008-11-20T09:00:00","gate_in"),
        row("E","2008-12-27T08:00:00","gate_in"),
        row("E","2008-12-28T09:00:00","direct_own_egg"),
    ]
    return events,boundaries

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report=audit(*demo())
    args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print("SYNTH_SOURCE_YEAR_PHASES",report["phase_tag_season_counts"])
    print("SYNTH_PRE_COLONY_EGG_DIRECT_OWN_EGG",report["pre_first_colony_egg_same_tag_direct_own_egg_AFTER_pass"],"/",report["pre_first_colony_egg_candidates"])
    print("SYNTH_ILLUSTRATIVE_ALL_PHASES_NAIVE_EGG_FRACTION",report["all_phase_naive_documented_postgate_egg_fraction"])
    print("FIRST_ACTUAL_PENGUIN_BREEDING_PROBABILITY","NOT_IDENTIFIED")
if __name__=="__main__":main()
