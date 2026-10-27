#!/usr/bin/env python3
"""V44 source-only cohort: same JNCC Master × count unit guild comparisons.

Species nest-accessibility map/filters fixed in V44 contract BEFORE inspecting
the new high-vs-cliff concentration guild differences. Absolutely never opens
original L/O biological count magnitudes or V30 E in this source-only step.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

import audit_jncc_two_censuses_source_v28 as v28
import audit_jncc_comparable_site_panels_v29 as v29
import model_jncc_component_concentration_v30 as v30

ACCESSIBLE=(
    "Arctic Skua","Arctic Tern","Atlantic Puffin","Black-headed Gull",
    "Common Gull","Common Tern","Great Black-backed Gull","Great Skua",
    "Herring Gull","Lesser Black-backed Gull",
)
CLIFF=(
    "Black-legged Kittiwake","Common Guillemot",
)
UNCERTAIN=(
    "Black Guillemot","European Shag","Great Cormorant",
    "Northern Fulmar","Razorbil",
)
TRAITS={**{s:"ACCESSIBLE" for s in ACCESSIBLE},
        **{s:"CLIFF_PROTECTED" for s in CLIFF},
        **{s:"UNCERTAIN" for s in UNCERTAIN}}
MAX_YEARS_APART=1
MAX_CENTROID_DISTANCE_KM=5.0
MIN_SOURCE_NETWORKS=10
MIN_ACCESSIBLE_SPECIES=2
MIN_CLIFF_SPECIES=1


def gc_km(p1,p2):
    a,b=map(math.radians,p1)
    c,d=map(math.radians,p2)
    hav=(math.sin((c-a)/2)**2
         +math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2)
    return 6371.0088*2*math.atan2(math.sqrt(hav),math.sqrt(max(0,1-hav)))


def source_panel_info(key,records):
    r=[x for x,_ in records]
    earlier={x["year_2000"] for x in r}
    later={x["year_recent"] for x in r}
    lat=sum(x["lat"] for x in r)/len(r)
    lon=sum(x["lon"] for x in r)/len(r)
    return {
        "key":key,"species":key[0],"country":key[1],"master":key[2],"unit":key[3],
        "guild":TRAITS[key[0]],
        "earlier_year":next(iter(earlier)) if len(earlier)==1 else None,
        "later_year":next(iter(later)) if len(later)==1 else None,
        "both_years_uniform":len(earlier)==1 and len(later)==1,
        "centroid":(lat,lon),
        "child_original_site_ids":frozenset(x["site_id"] for x in r),
        "child_count":len(r),
    }


def pair_quality(high,low):
    if high["country"]!=low["country"] or high["master"]!=low["master"]:
        raise ValueError("NOT_SAME_SOURCE_COUNTRY_MASTER")
    sameunit=high["unit"]==low["unit"]
    bothuniform=high["both_years_uniform"] and low["both_years_uniform"]
    closeyear=(bothuniform
               and abs(high["earlier_year"]-low["earlier_year"])<=MAX_YEARS_APART
               and abs(high["later_year"]-low["later_year"])<=MAX_YEARS_APART)
    d=gc_km(high["centroid"],low["centroid"])
    return {
        "same_original_count_unit":sameunit,
        "each_original_species_panel_year_uniform":bothuniform,
        "two_source_census_year_pairs_within_1_year":closeyear,
        "centroid_distance_km":d,
        "centroids_within_5km":d<=MAX_CENTROID_DISTANCE_KM,
        "overlapping_original_Site_ID_n":len(high["child_original_site_ids"] & low["child_original_site_ids"]),
        "source_metadata_primary_pair":bool(sameunit and closeyear and d<=MAX_CENTROID_DISTANCE_KM)
    }


def source_metadata_cohort(parents):
    if len(parents)!=1483:raise ValueError("V30_ORIGINAL_SOURCE_PARENT_COUNT_DRIFT")
    observed=set(k[0] for k in parents)
    unknown=observed-set(TRAITS)
    if unknown:
        raise ValueError("SOURCE_TRAIT_CROSSWALK_UNKNOWN: "+repr(sorted(unknown)))
    grouped=defaultdict(list)
    counts=Counter()
    by_guild=Counter()
    for k,records in parents.items():
        p=source_panel_info(k,records)
        by_guild[p["guild"]]+=1
        grouped[(k[1],k[2])].append(p)
    accepted={}
    pair_counters=Counter()
    primary_species=defaultdict(set)
    primary_countries=Counter()
    maxdist=[]
    child_overlap_positive=0
    for master,panels in grouped.items():
        hi=[p for p in panels if p["guild"]=="ACCESSIBLE"]
        lo=[p for p in panels if p["guild"]=="CLIFF_PROTECTED"]
        if hi and lo:
            counts["Country_Master_with_both_nesting_guilds"]+=1
            pairs=[]
            for a in hi:
                for b in lo:
                    q=pair_quality(a,b)
                    pair_counters["any_accessible_vs_cliff_species_pair_in_master"]+=1
                    if q["same_original_count_unit"]:
                        pair_counters["pairs_original_count_unit_exact"]+=1
                        if q["each_original_species_panel_year_uniform"]:
                            pair_counters["pairs_original_count_unit_and_internal_year_uniform"]+=1
                            if q["two_source_census_year_pairs_within_1_year"]:
                                pair_counters["pairs_original_count_unit_and_years_match"]+=1
                                if q["centroids_within_5km"]:
                                    pair_counters["pairs_strict_primary_all_source_gates"]+=1
                    if q["overlapping_original_Site_ID_n"]>0:
                        child_overlap_positive+=1
                    if q["source_metadata_primary_pair"]:
                        pairs.append((a["key"],b["key"]))
                        maxdist.append(q["centroid_distance_km"])
                        primary_species["accessible"].add(a["species"])
                        primary_species["cliff"].add(b["species"])
            if pairs:
                accepted[master]=pairs
                primary_countries[master[0]]+=1
    qa={
        "exact_original_source_structural_parent_panels":len(parents),
        "exact_original_source_species_n":len(observed),
        "source_panels_by_frozen_nesting_access_trait":dict(by_guild),
        "original_distinct_Country_Master_monitoring_networks":len(grouped),
        "source_networks_containing_both_guilds_without_other_gates":counts["Country_Master_with_both_nesting_guilds"],
        "all_source_pair_gate_funnel":dict(pair_counters),
        "source_pairs_with_original_Site_ID_overlap_NOT_verified_same_colony_polygon":child_overlap_positive,
        "strict_primary_same_master_networks_n":len(accepted),
        "strict_primary_accessible_species":sorted(primary_species["accessible"]),
        "strict_primary_cliff_species":sorted(primary_species["cliff"]),
        "strict_primary_by_country":dict(primary_countries),
        "strict_primary_centroid_distance_max_km":max(maxdist) if maxdist else None,
        "minimum_networks_before_new_outcome":MIN_SOURCE_NETWORKS,
        "minimum_accessible_species":MIN_ACCESSIBLE_SPECIES,
        "minimum_cliff_species":MIN_CLIFF_SPECIES,
        "original_biological_count_magnitudes_read":0,
        "species_level_accessibility_not_local_verified_predator_exposure":True,
        "same_original_master_site_not_same_verified_physical_colony_patch":True,
    }
    ready=(len(accepted)>=MIN_SOURCE_NETWORKS
           and len(primary_species["accessible"])>=MIN_ACCESSIBLE_SPECIES
           and len(primary_species["cliff"])>=MIN_CLIFF_SPECIES)
    qa["V44_primary_source_only_comparison_gate_pass"]=bool(ready)
    return accepted,qa


def fetch_and_gate():
    raw,meta=v28.download_original()
    if meta["original_sha256"]!=v29.ORIGINAL_SHA or hashlib.sha256(raw).hexdigest()!=v29.ORIGINAL_SHA:
        raise ValueError("ORIGINAL_JNCC_SHA_CHANGED")
    rows=list(v29.original_rows(raw))
    original=v29.coverage(rows)
    if (original["unique_original_two_census_site_species_rows_after_literal_QA"]!=14112
        or original["qualified_species_country_master_unit_panels_with_ge3_sites"]!=1485):
        raise ValueError("V29_ORIGINAL_SITE_NETWORK_FRAME_CHANGED")
    parents,sourceqa=v30.extract_structural(rows)
    if not sourceqa["pre_count_structural_gate_pass"]:
        raise ValueError("V30_PRE_COUNT_SOURCE_INTEGRITY_FAILED")
    return parents,*source_metadata_cohort(parents)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    result={
       "status":"V44_SOURCE_ONLY_UNSTARTED",
       "original_JNCC_SHA256":v29.ORIGINAL_SHA,
       "trait_contract":"contracts/JNCC_WITHIN_MASTER_NEST_ACCESS_GUILD_V44_FROZEN.md",
       "frozen_species_traits":TRAITS,
       "n_recorded_site_level_mammal_predator_observations":0,
       "original_JNCC_L_O_count_magnitudes_accessed":0,
       "JNCC_E_guild_difference_fitted":False,
    }
    try:
        parents,comparators,qa=fetch_and_gate()
        result["original_source_metadata_comparability"]=qa
        result["status"]=(
            "V44_SOURCE_MASTER_GUILD_STRICT_COMPARISON_ELIGIBLE"
            if qa["V44_primary_source_only_comparison_gate_pass"]
            else "STOP_V44_WITHIN_MASTER_GUILD_SOURCE_COHORT_TOO_SMALL"
        )
    except Exception as exc:
        result["status"]="V44_ORIGINAL_JNCC_SOURCE_OR_TRAIT_HOLD"
        result["error"]=type(exc).__name__+": "+str(exc)[:850]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]=="V44_ORIGINAL_JNCC_SOURCE_OR_TRAIT_HOLD":
        raise SystemExit(2)


if __name__=="__main__":
    main()
