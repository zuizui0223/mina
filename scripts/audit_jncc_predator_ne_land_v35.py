#!/usr/bin/env python3
"""V35 outcome-blind: JNCC structural child sites -> RSPB predator islands.

STRICT primary: each original JNCC child coordinate and an RSPB original
island reference point are INTERIOR to the same *unique* NE 10m merged
connected SMALL land polygon, containing exactly one original RSPB lowid.
No name-based matches or coastal snaps; source vintage and point precision
are unverified. JNCC L/O count magnitudes, E and bird movement unopened.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
import audit_jncc_two_censuses_source_v28 as v28
import audit_jncc_comparable_site_panels_v29 as v29
import model_jncc_component_concentration_v30 as v30
import audit_jncc_naturalearth_landmass_v31 as geo
import model_jncc_predator_reported_niche_v34 as pred
import audit_jncc_predator_island_source_v33 as src

MIN_MIXED_PARENTS = 20
MIN_MIXED_LANDMASSES = 5
MIN_MIXED_SPECIES = 5

def strict_RSPB_landmass_bridge(labels,polygons_km2):
    """Map only a unique source island point INSIDE an original small polygon."""
    by_land=defaultdict(set)
    states=Counter()
    for key,item in labels.items():
        state=item.get("status","UNRESOLVED")
        states[state]+=1
        if state!="INTERIOR":
            continue
        physical=item["physical_id"]
        # Make source area class explicit: Great Britain/Ireland never get a
        # phantom point-derived 'predator status' from adjacent islets.
        if geo.land_type(polygons_km2[physical])!="SMALL_OFFSHORE_LANDMASS":
            continue
        by_land[physical].add(key)
    unique={polygon:next(iter(ids)) for polygon,ids in by_land.items() if len(ids)==1}
    return unique,{
        "RSPB_source_island_point_states":dict(states),
        "physical_small_land_polygons_with_one_strict_RSPB_lowid":len(unique),
        "small_polygons_with_multiple_source_RSPB_lowids_HOLD":sum(len(z)>1 for z in by_land.values()),
        "large_landmasses_NEVER_as_RSPB_island_status":True,
    }

def panel_support(source_panels, site_states, strict_land_to_lowid,esm):
    parent_state=Counter()
    direct_species=Counter()
    candidate_parent_groups=[]
    candidate_ids=set()
    total_child=0;strict_child=0;all_child_matched=0
    for parent, original_children in sorted(source_panels.items()):
        records=[]
        for original,_ in original_children:
            total_child+=1
            key=(original["species"],original["country"],original["master"],
                 original["unit"],original["site_id"])
            loc=site_states.get(key,{})
            fid=loc.get("physical_id") if loc.get("status")=="INTERIOR" else None
            lowid=strict_land_to_lowid.get(fid)
            if lowid is None:
                records.append(None)
            else:
                strict_child+=1
                records.append((fid,lowid,esm[lowid]["statuses"]))
        if any(r is None for r in records):
            parent_state["INCOMPLETE_STRICT_SOURCE_CHILD_ISLAND_GEOGRAPHY"]+=1
            continue
        all_child_matched+=len(records)
        parent_state["ALL_CHILDREN_ONE_RSPB_ISLAND"]+=int(len({r[1] for r in records})==1)
        if len({r[1] for r in records})<2:
            continue
        parent_state["COMPLETE_MIXED_SOURCE_ISLAND_PARENT"]+=1
        candidate_ids.update(r[1] for r in records)
        direct_species[parent[0]]+=1
        label_status={}
        for p in pred.PREDATORS:
            binary={r[2][p] in {"1","2"} for r in records}
            label_status[p]=len(binary)==2
            if label_status[p]:
                parent_state["MIXED_REPORTED_"+p.upper().replace(" ","_")]+=1
        candidate_parent_groups.append({
            "species":parent[0],
            "source_country":parent[1],
            "source_unit":parent[3],
            "original_child_count":len(records),
            "independent_RSPB_source_island_lowids":len({r[1] for r in records}),
            "has_both_reported_presence_label_categories":label_status,
        })
    support=(
        parent_state["COMPLETE_MIXED_SOURCE_ISLAND_PARENT"]>=MIN_MIXED_PARENTS
        and len(candidate_ids)>=MIN_MIXED_LANDMASSES
        and len(direct_species)>=MIN_MIXED_SPECIES
    )
    return {
        "source_original_structural_parent_panels":len(source_panels),
        "all_original_child_rows_structurally_eligible":total_child,
        "child_rows_strict_exact_small_land_to_unique_RSPB":strict_child,
        "complete_parent_strict_source_child_rows":all_child_matched,
        "parent_support_categories":dict(parent_state),
        "mixed_source_island_parents_across_taxa":dict(direct_species),
        "mixed_source_island_unique_lowid_count":len(candidate_ids),
        "mixed_source_island_parent_count":len(candidate_parent_groups),
        "predeclared_within_parent_mixed_island_support_pass":bool(support),
        "date_appropriate_true_predator_observation_status_available":False,
        "model_JNCC_predator_effect_fitted":False,
        "NO_JNCC_count_magnitudes_opened":True,
        "interpretation":"Full parent and all component geography required. Source-reported predator label variation is neither true predator absence nor dated 1998–2021.",
        "candidate_mixed_parent_metadata_without_site_ID_or_count_values":candidate_parent_groups[:30],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    result={
      "status":"SOURCE_ONLY_V35_START",
      "no_JNCC_observed_breeding_abundance_cells_accessed":True,
      "no_predator_seabird_2024_E_association_fitted":True,
      "physical_mapping":"Natural Earth 1:10m source-only continuity provisional, not full-resolution GSHHG or independent nest GPS",
    }
    try:
        raw,jnccsource=v28.download_original()
        if hashlib.sha256(raw).hexdigest()!=v29.ORIGINAL_SHA:
            raise ValueError("JNCC_OFFICIAL_SOURCE_SHA_CHANGED")
        panels,qa=v30.extract_structural(v29.original_rows(raw))
        if not qa["pre_count_structural_gate_pass"] or len(panels)!=1483:
            raise ValueError("JNCC_SOURCE_STRUCTURAL_GATE_CHANGED")
        ne=geo.download_ne()
        polygons=geo.source_only_geometry(ne)
        shapes,area,geo_qa=geo.geometric_components(polygons["land"])
        island_meta=pred.source_islands()
        islands={k:(v["lat"],v["lon"]) for k,v in island_meta.items()}
        island_states,_=geo.attach_points(shapes,area,islands)
        unique,bridge=strict_RSPB_landmass_bridge(island_states,area)
        original=src.bounded_get(src.SUPPLEMENTS["ESM5"],src.MAX_SUPP_BYTES)
        esm,esm_qa=pred.load_original_ESM5(original)
        if set(esm)!=set(island_meta):raise ValueError("RSPB_ESM5_LOWID_SUPPORT_CHANGED")
        sites={}
        for parent,children in panels.items():
            for r,_ in children:
                sitekey=(r["species"],r["country"],r["master"],r["unit"],r["site_id"])
                point=(r["lat"],r["lon"])
                if sitekey in sites and sites[sitekey]!=point:
                    raise ValueError("JNCC_GEO_SOURCE_ID_COORDINATE_DRIFT")
                sites[sitekey]=point
        state,_=geo.attach_points(shapes,area,sites)
        support=panel_support(panels,state,unique,esm)
        result.update({
            "status":"JNCC_V35_SOURCE_ONLY_GEOGRAPHIC_PREDATOR_JOIN_SUPPORT",
            "original_JNCC_sha256":v29.ORIGINAL_SHA,
            "original_Stanbury_sha256":esm_qa["sha256"],
            "original_RSPB_islands":len(island_meta),
            "original_NaturalEarth_landmass_count":len(shapes),
            "original_JNCC_source_unique_structural_child_keys":len(sites),
            "geographic_source_island_bridge":bridge,
            "support":support,
            "scientific_decision":(
                "PROVISIONAL_GEOGRAPHY_SUPPORT_ONLY_TIME_CORRECT_STATUS_MISSING"
                if support["predeclared_within_parent_mixed_island_support_pass"]
                else "STOP_V35_STRICT_MIXED_SOURCE_ISLAND_H2_TEST_SUPPORT_FAILED"
            ),
        })
    except Exception as ex:
        result["status"]="SOURCE_OR_STRUCTURAL_HOLD_NO_PREDATOR_JNCC_EFFECT"
        result["error"]=type(ex).__name__+": "+str(ex)[:500]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]!="JNCC_V35_SOURCE_ONLY_GEOGRAPHIC_PREDATOR_JOIN_SUPPORT":
        raise SystemExit(2)

if __name__=="__main__":main()
