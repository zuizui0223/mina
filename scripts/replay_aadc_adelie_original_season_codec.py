#!/usr/bin/env python3
"""Independent original AADC 6-digit season codec / frozen 2016-2025 riskset replay.

Original source 191213 = austral 1912/13. Compare legacy raw-number adjacency
with correctly decoded annual adjacency WITHOUT reoptimizing sample gates.
Source-state 0/P/A are reported observations, not true colony settlement.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from pathlib import Path
import json
import requests
from openpyxl import load_workbook
import io

from scripts.audit_aadc_2025_seabird_riskset_original_schema import SETS,download_original

SHA={
 "2025_penguin":"8b38aa86f0ef2a0a9fe8c5bb13da904a9f2431cd503644b962b6e116ac3187ac",
 "2025_geographic_sites":"ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294"
}
LEGACY_FROZEN={"states":4904,"P":2323,"A":2581,"AA":28,"AP":1,"PP":38,"PA":0}
EXPANSION_MIN_AP=10
EXPANSION_MIN_A_RISK=50
EXPANSION_MIN_SUBGROUPS=3

def source_text(v):
    return "" if v is None else str(v).strip()

def parse_season_sixdigits(v):
    """Independently check two-year successor code, not date guessing."""
    try:
        n=int(float(v))
        if float(v)!=n:return None
    except (TypeError,ValueError,OverflowError):
        return None
    y=n//100
    suffix=n%100
    if not 1850<=y<=2025 or (y+1)%100!=suffix:
        return None
    return y

def legacy_unconverted_season(v):
    """Precisely reproduce previous PR180 season_start for numeric source cell."""
    s=source_text(v)
    for delimiter in ("-","/"):
        if delimiter in s:
            try:return int(float(s.split(delimiter,1)[0].strip()))
            except ValueError:pass
    try:return int(float(s))
    except (ValueError,TypeError):return None

def get_source_rows(session,tag,sheet):
    spec=SETS[tag]
    raw,meta=download_original(session,spec)
    if meta["sha256"]!=SHA[tag]:
        raise ValueError(f"original AADC source sha256 changed for {tag}")
    wb=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    try:
        ws=wb[sheet]
        it=ws.iter_rows(values_only=True)
        header=[source_text(v).lower() for v in next(it)]
        if len(header)!=len(set(header)):
            raise ValueError("source header ambiguous")
        records=[dict(zip(header,row)) for row in it]
    finally:wb.close()
    expected=11089 if tag=="2025_penguin" else 7785
    if len(records)!=expected:raise ValueError(f"source row count drift {tag}: {len(records)}")
    return records,meta["sha256"]

def make_site_states(rows,codec):
    obs=defaultdict(set)
    problems=Counter()
    formats=Counter()
    subgroups=defaultdict(set)
    for row in rows:
        if source_text(row.get("species_code")).upper()!="ADP":
            raise ValueError("publisher Adélie file has other species")
        label=source_text(row.get("season"))
        formats[f"{len(label)}digit_label"]+=1
        yr=codec(row.get("season"))
        if yr is None:
            problems["invalid_or_nonconsecutive_two_year_season"]+=1
            continue
        site=source_text(row.get("geog_site_id"))
        occ=source_text(row.get("occurrence")).upper()
        if not site or occ not in {"P","A","NR"}:
            problems["invalid_site_or_status"]+=1
            continue
        key=(site,yr)
        obs[key].add(occ)
        subgroup=source_text(row.get("sub_group"))
        if subgroup:subgroups[site].add(subgroup)
    result={}
    conflicts=0
    nr_only=0
    for key,values in obs.items():
        if "P" in values and "A" in values:conflicts+=1
        state="P" if "P" in values else ("A" if "A" in values else None)
        if state is None:nr_only+=1;continue
        result[key]=state
    return result,{"unparsed":dict(problems),"source_season_label_lengths":dict(formats),
                   "P_and_A_same_site_season":conflicts,"NR_only_site_seasons":nr_only,
                   "site_subgroups":subgroups}

def transitions(states,site_subgroups,site_features):
    bysite=defaultdict(dict)
    for (site,year),state in states.items():bysite[site][year]=state
    counts=Counter()
    events=[]
    a_risk=[]
    for site,dates in sorted(bysite.items()):
        for year in sorted(dates):
            a=dates[year];b=dates.get(year+1)
            if b not in {"P","A"}:continue
            kind=a+b
            counts[kind]+=1
            if a=="A":a_risk.append((site,year))
            if kind=="AP":
                prev=any(earlier<year and state=="P" for earlier,state in dates.items())
                events.append({"geog_site_id":site,
                               "season_start":year,
                               "season_end":year+1,
                               "history":"recolonization_candidate" if prev else "first_observed_A_to_P",
                               "source_feature":site_features.get(site,"<unmatched>"),
                               "original_subgroups":sorted(site_subgroups.get(site,[])),
                               "confirmed_first_ever_settlement":False})
    by_feature=defaultdict(Counter)
    for site,year in a_risk:
        by_feature[site_features.get(site,"<unmatched>")]["A_risk"]+=1
    for event in events:
        by_feature[event["source_feature"]]["AP"]+=1
    return {
      "pairs":dict(counts),
      "n_total_strict_consecutive_pairs":sum(counts.values()),
      "A_risk_pairs":len(a_risk),
      "AP_first_observed":sum(x["history"]=="first_observed_A_to_P" for x in events),
      "AP_recolonization_candidate":sum(x["history"]=="recolonization_candidate" for x in events),
      "AP_sites":len({x["geog_site_id"] for x in events}),
      "AP_subgroups":len({s for e in events for s in e["original_subgroups"]}),
      "AP_feature_counts":dict(Counter(e["source_feature"] for e in events)),
      "source_feature_support":{k:dict(v) for k,v in by_feature.items()},
      "observed_AP_events":events,
    }

def audit():
    with requests.Session() as s:
        rows,sha_occ=get_source_rows(s,"2025_penguin","2_search events")
        locations,sha_geo=get_source_rows(s,"2025_geographic_sites","2_geog_sites_all")
    feature={source_text(r["geog_site_id"]):source_text(r["geog_site_feature"]).lower()
             for r in locations}
    old_states,old_meta=make_site_states(rows,legacy_unconverted_season)
    fixed_states,fixed_meta=make_site_states(rows,parse_season_sixdigits)
    old_st=Counter(old_states.values())
    if len(old_states)!=LEGACY_FROZEN["states"] or old_st["P"]!=LEGACY_FROZEN["P"] or old_st["A"]!=LEGACY_FROZEN["A"]:
        raise ValueError(f"not original frozen 4,904 site-seasons: {len(old_states)} {dict(old_st)}")
    old=transitions(old_states,old_meta["site_subgroups"],feature)
    recovered={k:old["pairs"].get(k,0) for k in ("AA","AP","PP","PA")}
    if any(recovered[k]!=LEGACY_FROZEN[k] for k in recovered):
        raise ValueError(f"cannot reproduce legacy 77 transition pairs: {recovered}")
    if fixed_meta["unparsed"]:
        raise ValueError(f"publisher source six-digit season decoding failures: {fixed_meta['unparsed']}")
    fixed=transitions(fixed_states,fixed_meta["site_subgroups"],feature)
    expansion_gate=(fixed["AP_first_observed"]>=EXPANSION_MIN_AP
                    and fixed["A_risk_pairs"]>=EXPANSION_MIN_A_RISK
                    and fixed["AP_subgroups"]>=EXPANSION_MIN_SUBGROUPS)
    f=fixed["source_feature_support"]
    feature_gate=all(f.get(name,{}).get("AP",0)>=5 and
                     f.get(name,{}).get("A_risk",0)>=20
                     for name in ("island","continent"))
    return {
      "schema_version":1,
      "status":"ORIGINAL_PUBLISHER_SEASON_CODEC_REPLAY_COMPLETED",
      "source":"AADC publisher original 2025 Adélie search events; same raw source as original PR180",
      "original_penguin_sha256":sha_occ,
      "original_geographic_site_sha256":sha_geo,
      "source_year_codec":"6 digit YYYYZZ interpreted as breeding start YYYY and successor ending year ZZ=(YYYY+1)%100; reject malformed",
      "legacy_code":"PR180 int(float(raw six-digit season)) +1 adjacency, without year decoding",
      "original_site_seasons":len(old_states),
      "original_source_P_site_seasons":old_st["P"],
      "original_source_A_site_seasons":old_st["A"],
      "source_conflicting_A_and_P_site_seasons":fixed_meta["P_and_A_same_site_season"],
      "legacy_raw_source_label_counts":old_meta["source_season_label_lengths"],
      "normalized_breeding_season_min":min(y for _,y in fixed_states),
      "normalized_breeding_season_max":max(y for _,y in fixed_states),
      "legacy_original_frozen_transition_reproduced":old,
      "corrected_source_annual_transition_support":fixed,
      "unchanged_original_expansion_gate_limits":{
        "minimum_first_colonizations":EXPANSION_MIN_AP,
        "minimum_A_risk_pairs":EXPANSION_MIN_A_RISK,
        "minimum_subgroups":EXPANSION_MIN_SUBGROUPS,
        "expansion_gate_pass":expansion_gate,
        "island_vs_continent_A_risk_and_AP_gate_pass":feature_gate,
      },
      "old_replay_same_as_frozen":True,
      "new_biological_occupancy_effect_fitted":False,
      "causal_colonization_claim_allowed":False,
      "note":[
       "This corrects a source temporal-code BUG; the input source and originally frozen thresholds are unchanged.",
       "P-wins-over-A for within-season contradictions replicates PR180, not an endorsement that an unverified P/A conflict is reliable.",
       "Source-reported A->P is a possible detection or search-effort artefact and not necessarily first establishment.",
       "AADC source feature label island/continent is a mapped feature class, not randomized mammalian predation exposure.",
       "This is a new after-the-fact QA of already inspected data, and cannot retrospectively validate a preregistered new ecological effect.",
      ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True,type=Path)
    args=p.parse_args()
    try:
        result=audit()
    except Exception as exc:
        result={"status":"HOLD_ORIGINAL_AADC_SEASON_CODEC_REPLAY",
                "error":f"{type(exc).__name__}: {str(exc)}"[:400],
                "new_ecological_effect_fitted":False}
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
       "status":result["status"],
       "error":result.get("error"),
       "legacy":result.get("legacy_original_frozen_transition_reproduced",{}).get("pairs"),
       "corrected":result.get("corrected_source_annual_transition_support",{}).get("pairs"),
       "original_frozen_expansion_gate":result.get("unchanged_original_expansion_gate_limits")
    },sort_keys=True))
if __name__=="__main__":main()
