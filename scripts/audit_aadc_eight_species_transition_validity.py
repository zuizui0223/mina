#!/usr/bin/env python3
"""AADC eight-species detection-grade annual transition support (no ecological fit).

Strict screening is fixed from publisher's original expert-validation flags and
absence-certainty category H. Original A/P/NR all retained for source audits;
no non-reporting becomes absence and no candidate first arrival is called
colonization or physical-rock occupation.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import requests

from scripts.audit_aadc_2025_eight_species_original_riskset import (
   ORIGINAL_SHA256, SOURCE_COUNTS, TARGET_SHEETS, season_year, strict_state, txt,
   read_source_rows
)
from scripts.audit_aadc_2025_seabird_riskset_original_schema import (
   SETS,download_original
)

SOURCE_TAGS=("2025_penguin","2025_seabird","2025_geographic_sites","2025_certainty")
SOURCE_EVENTS=33107

def read_original_publisher():
    originals={}
    sha={}
    with requests.Session() as session:
        for tag in SOURCE_TAGS:
            spec=SETS[tag]
            raw,meta=download_original(session,spec)
            if meta["sha256"]!=ORIGINAL_SHA256[tag]:
                raise ValueError(f"AADC original source checksum drift {tag}")
            original,_=read_source_rows(raw,spec["name"],TARGET_SHEETS[tag],SOURCE_COUNTS[tag])
            originals[tag]=original
            sha[tag]=meta["sha256"]
    return originals,sha

def year_detection_group_status(rows,certainty,area_category):
    """Compare source observation to demanding validity conditions."""
    occurrences={txt(x.get("occurrence")).upper() for x in rows}
    source=strict_state(occurrences)
    if source not in {"A_REPORTED_ONLY","P_REPORTED_NO_A"}:
        return source,None,"CONFLICT_NR_OR_INCOMPLETE"
    # No original occurrence-level false certainty imputation.
    records=[]
    for row in rows:
        occur=txt(row.get("occurrence")).upper()
        if occur not in {"A","P"}:
            return source,None,"NR_CO_REPORTED"
        species=txt(row.get("species_code")).upper()
        vantage=txt(row.get("vantage")).upper()
        key=(species,occur,vantage,area_category.upper())
        lookup=certainty.get(key,[])
        if len(lookup)!=1:
            return source,None,"NO_EXACT_ABSENCE_CERTAINTY"
        validation=tuple(txt(row.get(col)).upper() for col in (
           "species_expert_validation","site_expert_validation","occurrence_expert_validation"))
        if validation!=("Y","Y","Y"):
            return source,None,"NOT_ALL_EXPERT_VALIDATED"
        absence_grade=txt(lookup[0].get("occurrence_cert_cat")).upper()
        # High-certainty absence H is the published conservative class,
        # not proof of true absence.
        if occur=="A" and absence_grade!="H":
            return source,None,"REPORTED_A_NOT_HIGH_CERTAINTY"
        records.append(occur)
    if not records:
        return source,None,"NO_EXPLICIT_EVENT"
    return source,("A" if source=="A_REPORTED_ONLY" else "P"),"QUALIFIED_HIGH_EVIDENCE"

def summarize_transitions(states,locations):
    per=defaultdict(dict)
    for (site,sp,year),st in states.items():
        per[(site,sp)][year]=st
    pairs=Counter()
    bysp=defaultdict(Counter)
    byfeature=defaultdict(Counter)
    events=[]
    for (site,sp),years in sorted(per.items()):
        cls=txt(locations[site].get("geog_site_feature")).lower() if site in locations else "<unmatched>"
        subgroup=txt(locations[site].get("sub_group")) if site in locations else ""
        for y,a in sorted(years.items()):
            b=years.get(y+1)
            if b not in {"A","P"}:continue
            kind=a+b
            pairs[kind]+=1
            bysp[sp][kind]+=1
            byfeature[cls][kind]+=1
            if kind=="AP":
                events.append({"geog_site_id":site,"species_code":sp,
                               "season_start":y,"season_next":y+1,
                               "geog_site_feature":cls,
                               "sub_group":subgroup,
                               "true_new_settlement_confirmed":False})
    return {
      "pairs":dict(pairs),
      "by_species":{k:dict(v) for k,v in sorted(bysp.items())},
      "by_source_land_class":{k:dict(v) for k,v in sorted(byfeature.items())},
      "AP_events":len(events),
      "AP_distinct_site_ids":len({x["geog_site_id"] for x in events}),
      "AP_distinct_subgroups":len({x["sub_group"] for x in events if x["sub_group"]}),
      "A_risk_pairs":pairs["AA"]+pairs["AP"],
      "AP_event_source_rows":events,
    }

def audit(originals,source_sha):
    files=originals
    rows=files["2025_penguin"]+files["2025_seabird"]
    if len(rows)!=SOURCE_EVENTS:
        raise ValueError("publisher source row count changed")
    geo=files["2025_geographic_sites"]
    loc={txt(x.get("geog_site_id")):x for x in geo if txt(x.get("geog_site_id"))}
    if len(loc)!=7785:
        raise ValueError("original unique geographic site roster changed")
    cert=defaultdict(list)
    for row in files["2025_certainty"]:
        key=tuple(txt(row.get(f)).upper() for f in
             ("species_code","occurrence","vantage","geog_site_area_cat3"))
        cert[key].append(row)
    if len(cert)!=216 or any(len(v)!=1 for v in cert.values()):
        raise ValueError("original certainty lookup has duplicates")
    publisher_absence_grade_codes=defaultdict(Counter)
    for rule in files["2025_certainty"]:
        occ=txt(rule.get("occurrence")).upper()
        grade=txt(rule.get("occurrence_cert_cat")).upper()
        publisher_absence_grade_codes[occ][grade or "<BLANK>"]+=1
    grouped=defaultdict(list)
    dropped=Counter()
    for r in rows:
        site=txt(r.get("geog_site_id"))
        sp=txt(r.get("species_code")).upper()
        y=season_year(r.get("season"))
        if y is None or not site or not sp:
            dropped["bad_source_season_or_site"]+=1
            continue
        if site not in loc:
            dropped["unmatched_original_geo_site_id"]+=1
            continue
        grouped[(site,sp,y)].append(r)
    broad_state={}
    strict_state_dict={}
    strict_rejections=Counter()
    broad_outcomes=Counter()
    for key,events in sorted(grouped.items()):
        area=txt(loc[key[0]].get("geog_site_area_cat3"))
        broad,strict,rejection=year_detection_group_status(events,cert,area)
        broad_outcomes[broad]+=1
        # Use A or P only for fully unambiguous source years, regardless of confidence.
        if broad=="A_REPORTED_ONLY":broad_state[key]="A"
        elif broad=="P_REPORTED_NO_A":broad_state[key]="P"
        if strict in {"A","P"}:strict_state_dict[key]=strict
        elif broad in {"A_REPORTED_ONLY","P_REPORTED_NO_A"}:
            strict_rejections[rejection]+=1
    broad=summarize_transitions(broad_state,loc)
    qualified=summarize_transitions(strict_state_dict,loc)
    # Verify source-only temporal reconstruction against already-audited raw data.
    if broad["AP_events"]!=16:
        raise ValueError(f"source original 16 observed AP transitions drift: {broad['AP_events']}")
    if broad["by_species"].get("ADP",{}).get("AP",0)!=5:
        raise ValueError("source original Adelie five observed AP drift")
    return {
       "schema_version":1,
       "status":"AADC_EIGHT_SPECIES_VERIFIED_DETECTION_QUALITY_SOURCE_GATE",
       "source_count":SOURCE_EVENTS,
       "source_sha256":source_sha,
       "original_2025_geographic_sites":len(loc),
       "original_certainty_source_rules":len(cert),
       "publisher_certainty_grade_code_histogram_by_occurrence":{
          k:dict(v) for k,v in sorted(publisher_absence_grade_codes.items())},
       "publisher_absence_grade_code_has_literal_H":any(
          grade=="H" for occ,vals in publisher_absence_grade_codes.items()
          if occ=="A" for grade in vals),
       "valid_source_site_species_season_groups":len(grouped),
       "source_invalid_rows":dict(dropped),
       "source_year_states":dict(broad_outcomes),
       "broad_unambiguous_observed_AP_support":broad,
       "strict_all_expert_Y_and_high_A_certainty_support":qualified,
       "strict_source_years_eligible":len(strict_state_dict),
       "strict_exclusion_reasons":dict(strict_rejections),
       "frozen_expansion_gate_minimums":{"first_colonization_candidates":10,
                                        "A_risk_pairs":50,
                                        "distinct_subgroups":3},
       "original_GIS_2024_postexposure_paired_surveys":0,
       "new_icefree_rock_exposure_proven":False,
       "new_colonization_proven":False,
       "ecological_effect_fitted":False,
       "limitations":[
         "Publisher expert flags Y support an observation, not certainty of true nesting absence.",
         "H is relative high absence certainty, not absolute or estimated detection probability.",
         "Missing/NR and unscored seasons are never biological absence.",
         "True site boundaries, mainland vs island predator treatment and new bare-rock timing are not identified.",
         "Years are original six-digit source encoding decoded via corroborated successor-year check.",
         "No publication claim of new colonization, retreat response, or causality is supported from these pairs.",
       ]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-json",required=True,type=Path)
    a=ap.parse_args()
    try:
        data,sha=read_original_publisher()
        result=audit(data,sha)
    except Exception as exc:
        result={"status":"HOLD_AADC_HIGH_EVIDENCE_PAIR_SOURCE",
                "error":f"{type(exc).__name__}: {str(exc)}"[:420],
                "ecological_effect_fitted":False}
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":result["status"],"error":result.get("error"),
      "broad_AtoP":result.get("broad_unambiguous_observed_AP_support",{}).get("AP_events"),
      "high_grade_AtoP":result.get("strict_all_expert_Y_and_high_A_certainty_support",{}).get("AP_events")
    },sort_keys=True))

if __name__=="__main__":main()
