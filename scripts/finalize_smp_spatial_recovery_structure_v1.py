#!/usr/bin/env python3
"""Resolve SMP SiteID identity continuity before hysteresis state outcomes.

Consumes the count-blind structural support JSON and a provider/site-history
resolution table. It never reads count or zero/positive occupancy state.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd


MIN_SITES=3
MIN_YEARS=10
MIN_SPAN=12
MIN_PANELS=10
MIN_SPECIES=5
MIN_MASTERS=10

REQUIRED={
    "species","MasterSite","SiteID","stable_identity","mutually_exclusive_child",
    "overlaps_parent_or_sibling","boundary_change_during_panel","retired_or_replaced","notes"
}


def as_bool(x)->bool:
    s=str(x).strip().casefold()
    if s in {"true","1","yes","y"}: return True
    if s in {"false","0","no","n"}: return False
    raise ValueError(f"cannot parse boolean: {x!r}")


def run(support_json:Path,resolution_csv:Path)->dict:
    support=json.loads(support_json.read_text(encoding="utf-8"))
    if support.get("analysis_id") != "mina-smp-spatial-recovery-hysteresis-structure-v1":
        raise ValueError("identity finalizer requires the dedicated count-blind hysteresis structure output")
    if not support.get("decision",{}).get("structural_gate_passed"):
        raise ValueError("dedicated count-blind hysteresis structure gate did not pass")

    res=pd.read_csv(resolution_csv,dtype=str).fillna("")
    missing=REQUIRED-set(res.columns)
    if missing:
        raise ValueError(f"missing identity-resolution fields: {sorted(missing)}")

    keycols=["species","MasterSite","SiteID"]
    if res.duplicated(keycols).any():
        raise ValueError("duplicate SiteID identity-resolution keys")

    canonical_unit={}
    if "canonical_unit" in res.columns:
        for (species, master), g in res.groupby(["species","MasterSite"], sort=False):
            vals=sorted({str(v).strip() for v in g["canonical_unit"] if str(v).strip()})
            if len(vals)>1:
                raise ValueError(f"conflicting canonical_unit values for {(species, master)}: {vals}")
            if vals:
                canonical_unit[(str(species),str(master))]=vals[0]

    support_units={}
    for p in support["eligible_panels"]:
        key=(str(p["species"]),str(p["master_site"]))
        support_units.setdefault(key,set()).add(str(p["unit"]))

    lookup={}
    for r in res.itertuples(index=False):
        key=(str(r.species),str(r.MasterSite),str(r.SiteID))
        eligible=(
            as_bool(r.stable_identity)
            and as_bool(r.mutually_exclusive_child)
            and not as_bool(r.overlaps_parent_or_sibling)
            and not as_bool(r.boundary_change_during_panel)
            and not as_bool(r.retired_or_replaced)
        )
        lookup[key]={"eligible":eligible,"notes":str(r.notes)}

    panels=[]
    excluded=[]
    excluded_multi_unit=[]
    for p in support["eligible_panels"]:
        species=str(p["species"]); master=str(p["master_site"]); unit=str(p["unit"])
        sm_key=(species,master)
        units=sorted(support_units.get(sm_key,set()))
        if len(units)>1:
            chosen=canonical_unit.get(sm_key)
            if chosen is None:
                excluded_multi_unit.append({
                    "species":species,"master_site":master,
                    "eligible_units":units,
                    "reason":"multiple structurally eligible count Units and no provider canonical_unit"
                })
                continue
            if unit!=chosen:
                continue

        original=[str(x) for x in p["retained_site_ids"]]
        kept=[]
        for site in original:
            key=(species,master,site)
            if key not in lookup:
                raise ValueError(f"unresolved SiteID identity: {key}")
            if lookup[key]["eligible"]:
                kept.append(site)
            else:
                excluded.append({
                    "species":species,"master_site":master,"site_id":site,
                    "notes":lookup[key]["notes"]
                })
        if len(kept)<MIN_SITES:
            continue

        # Stage-A complete years remain valid after site removal; use the exact
        # inherited year set rather than opening count/occupancy information.
        years=[int(x) for x in p["complete_years"]]
        if len(years)<MIN_YEARS or max(years)-min(years)+1<MIN_SPAN:
            continue

        q=dict(p)
        q["retained_site_ids"]=sorted(kept)
        q["n_sites"]=len(kept)
        q["identity_gate_removed_site_ids"]=sorted(set(original)-set(kept))
        q["identity_gate_resolved"]=True
        panels.append(q)

    species=sorted({p["species"] for p in panels})
    masters=sorted({p["master_site"] for p in panels})
    passed=bool(
        len(panels)>=MIN_PANELS
        and len(species)>=MIN_SPECIES
        and len(masters)>=MIN_MASTERS
    )

    return {
        "schema_version":1,
        "analysis_id":"mina-smp-spatial-recovery-structure-v1",
        "status":"identity_resolved_count_blind_structure",
        "eligible_panel_count":len(panels),
        "eligible_species_count":len(species),
        "distinct_master_site_count":len(masters),
        "dedicated_hysteresis_thresholds":{
            "minimum_panels":MIN_PANELS,
            "minimum_species":MIN_SPECIES,
            "minimum_master_sites":MIN_MASTERS,
        },
        "excluded_siteids":excluded,
        "excluded_multi_unit_masterSites":excluded_multi_unit,
        "eligible_panels":panels,
        "decision":{
            "structural_gate_passed":passed,
            "zero_positive_state_scan_authorized":passed,
            "if_failed":"Stop without relaxing identity, count-unit, or dedicated hysteresis program thresholds."
        },
        "forbidden_outputs_confirmed_absent":[
            "count magnitudes","zero/positive occupancy histories","abundance trends",
            "E","kappa","hysteresis width H"
        ]
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--support-json",required=True,type=Path)
    p.add_argument("--identity-resolution-csv",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=run(a.support_json,a.identity_resolution_csv)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in {"eligible_panels","excluded_siteids"}},indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
