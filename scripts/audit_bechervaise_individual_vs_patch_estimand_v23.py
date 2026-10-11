#!/usr/bin/env python3
"""Audit which penguin recolonization question source event fields actually identify.

Consumes only the PUBLIC SOURCE-SCHEMA contract, not private wildlife RFID
values. Adding public source bytes alone does not turn a shared entry gate
into per-nest prospecting or infer exact first lifetime breeding.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

PERMANENT_GEOMETRY_LIMITS={
  "E3_FIDELITY_TO_SPECIFIC_PREVIOUSLY_VISITED_NEST_PATCH",
  "E4_CAUSAL_INTERISLAND_COLONIST_SUPPLY_EFFECT",
}

def inspect(contract,altered_evidence=None):
    observed=contract["available_evidence"].copy()
    if altered_evidence:
        for k,v in altered_evidence.items():
            if k not in observed or type(v) is not bool:
                raise ValueError("Cannot add new invented source variables or nonboolean evidence")
            observed[k]=v
    result={}
    for entry in contract["estimands"]:
        eid=entry["id"]
        missing=[k for k in entry["required"] if not observed[k]]
        if eid in PERMANENT_GEOMETRY_LIMITS:
            status="SOURCE_DESIGN_DOES_NOT_MEASURE_REQUIRED_EVENT_OR_ISLAND_CONTROL"
            # Even granting all current gate and nest source bytes/IDs, the
            # two published monitoring designs lack specific patch positions
            # or independently matched island-scale source/recipient events.
        elif missing:
            status="HOLD_MISSING_OR_UNVERIFIED_SOURCE_FIELDS"
        else:
            status="SOURCE_FIELDS_POTENTIALLY_ELIGIBLE_NOT_CAUSAL_VALIDATION"
        result[eid]={
            "status":status,
            "requirements":list(entry["required"]),
            "currently_missing_fields":missing,
            "possible_in_principle_if_raw_data_obtained":entry["possible_in_principle_if_raw_data_obtained"],
            "scientific_scope":entry["scope"],
            "actual_penguin_effect_fitted":False
        }
    return {
       "status":"BECHERVAISE_SOURCE_FIELD_AND_MEASUREMENT_GRAIN_AUDIT",
       "source_gate_shared_by_several_subcolonies":True,
       "source_nest_scan_is_not_independently_verified_own_egg":True,
       "first_year_own_egg_requires_natal_and_previous_history":True,
       "first_colony_gate_detection_not_first_patch_prospecting":True,
       "published_2019_same_season_breeder_status_link_prior_art":True,
       "published_2022_first_nesting_age_already_in_source":True,
       "current_source_evidence":observed,
       "candidate_estimand_gates":result,
       "source_bird_ID_observations_read":0,
       "current_causal_mechanism_discovered":False,
       "PR189_unchanged":True,
       "PR142_unchanged":True,
       "PR195_unchanged":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contract",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=inspect(json.loads(a.contract.read_text(encoding="utf8")))
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    for item,res in report["candidate_estimand_gates"].items():
        print("IDENTIFIABILITY",item,res["status"],"N_MISSING",len(res["currently_missing_fields"]))
    print("NO_SOURCE_TAGGED_BIRDS_READ_OR_NEW_ISLAND_MECHANISM",True)

if __name__=="__main__":main()
