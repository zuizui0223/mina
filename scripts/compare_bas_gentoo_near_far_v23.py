#!/usr/bin/env python3
"""V23: original BAS three-physical-landmass, same-year Gentoo near/far contrast.

Exploratory follow-up to already opened V22 near result; no causal test or p values.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
import audit_bas_south_georgia_source_v21 as v21
import fit_bas_bird_maiviken_nests_v22 as v22

SIGNY_URL=("https://ramadda.data.bas.ac.uk/repository/entry/get/"
    "signy_gentoo_breeding_success.csv?"
    "entryid=synth%3A883c6b40-024e-41e8-9c3e-2668a44b5751"
    "%3AL3NpZ255X2dlbnRvb19icmVlZGluZ19zdWNjZXNzLmNzdg%3D%3D")
SIGNY_SHA="53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b"
ORIGINAL_V22_R=0.5621534427494942
MIN_SAME_WINDOWS=8

def signy_records(rows):
    """Source-year and species keys are checked before using pair values."""
    if not rows or not {"SEASON","SPECIES","TOTAL_NUMBER_OF_PAIRS"}.issubset(rows[0]):
        raise ValueError("SCHEMA_STOP Signy original season/species/pair columns changed")
    byyear=defaultdict(list)
    bad_label=0
    outside_period=0
    wrong_species=0
    for item in rows:
        species=str(item.get("SPECIES","")).strip().lower()
        if not ("gentoo" in species or "pygoscelis papua" in species):
            wrong_species+=1
            continue
        raw_year=str(item.get("SEASON",""))
        year=v22.season_year(raw_year)
        if year is None:
            bad_label+=1
            continue
        if not (v22.YEAR_START<=year<=v22.YEAR_STOP):
            outside_period+=1
            continue
        byyear[year].append(item)
    duplicate=[yr for yr,v in byyear.items() if len(v)>1]
    single={yr:records[0] for yr,records in byyear.items() if len(records)==1}
    # Only source seasons matching the pre-declared V22 range are opened.
    result={year:v22.raw_count(row.get("TOTAL_NUMBER_OF_PAIRS"))
            for year,row in single.items()}
    return result,{
        "original_source_rows":len(rows),
        "invalid_original_season_rows":bad_label,
        "other_years_outside_fixed_V22_period":outside_period,
        "rows_not_explicitly_Gentoo":wrong_species,
        "duplicate_season_groups_excluded":len(duplicate),
        "eligible_unambiguous_source_years":sorted(single),
        "numeric_original_pair_count_years":sum(value is not None for value in result.values()),
        "invalid_unknown_pair_count_years":sum(value is None for value in result.values()),
    }

def preserved_v22_growth(candidate,windows):
    """Reconstruct V22 precisely rather than tuning years or colony roster."""
    parsed={}
    for year,record in candidate.items():
        main=v22.raw_count(record["main"][1].get("Number of incubating nests"))
        if main is None:
            continue
        colony_counts={}
        for colony,(_,row) in record["bird"].items():
            value=v22.raw_count(row.get("Number of nests"))
            if value is not None:
                colony_counts[colony]=value
        if len(colony_counts)>=v22.MIN_BIRD:
            parsed[year]={"main":main,"bird":colony_counts}
    growth={}
    for year,_ in windows:
        if year not in parsed or year+1 not in parsed:
            continue
        common=sorted(set(parsed[year]["bird"])&set(parsed[year+1]["bird"]))
        if len(common)<v22.MIN_BIRD:
            continue
        bird=mean(math.log1p(parsed[year+1]["bird"][colony])
                  -math.log1p(parsed[year]["bird"][colony]) for colony in common)
        maiv=(math.log1p(parsed[year+1]["main"])
              -math.log1p(parsed[year]["main"]))
        growth[year]={"bird":bird,"maiviken":maiv}
    return growth

def compare_near_far(v22_growth,signy):
    complete={}
    for year,row in v22_growth.items():
        if year not in signy or year+1 not in signy:
            continue
        a,b=signy[year],signy[year+1]
        if a is None or b is None:
            continue
        complete[year]={**row,"signy":math.log1p(b)-math.log1p(a)}
    years=sorted(complete)
    metadata={
        "common_adjacent_year_windows":len(years),
        "common_growth_start_years":years,
        "fixed_minimum_windows":MIN_SAME_WINDOWS,
        "original_physical_landmass_n":3,
        "all_three_pairwise_correlations_use_identical_years":True,
    }
    if len(years)<MIN_SAME_WINDOWS:
        return {**metadata,"status":"STOP_INSUFFICIENT_THREE_SOURCE_COMMON_YEAR_WINDOWS",
                "effect_computed":False}
    pairs=(("near_Bird_Maiviken","bird","maiviken"),
           ("far_Bird_Signy","bird","signy"),
           ("far_Maiviken_Signy","maiviken","signy"))
    def corr(rows,x,y):
        ordered=[rows[k] for k in sorted(rows)]
        return v22.pearson([r[x] for r in ordered],[r[y] for r in ordered])
    correlations={key:corr(complete,a,b) for key,a,b in pairs}
    if any(r is None or not math.isfinite(r) for r in correlations.values()):
        return {**metadata,"status":"STOP_ZERO_VARIANCE_IN_COMMON_YEAR_SERIES",
                "effect_computed":False}
    near=correlations["near_Bird_Maiviken"]
    delta=near-.5*(correlations["far_Bird_Signy"]+correlations["far_Maiviken_Signy"])
    loo=[]
    for y in years:
        rest={k:v for k,v in complete.items() if k!=y}
        r={key:corr(rest,a,b) for key,a,b in pairs}
        if all(val is not None and math.isfinite(val) for val in r.values()):
            loo.append(r["near_Bird_Maiviken"]-.5*(r["far_Bird_Signy"]+r["far_Maiviken_Signy"]))
    signs={}
    for key,a,b in pairs:
        nonzero=sum(complete[y][a]!=0 and complete[y][b]!=0 for y in years)
        concordant=sum(complete[y][a]*complete[y][b]>0 for y in years)
        signs[key]={"both_nonzero_windows":nonzero,
                    "same_direction_windows":concordant,
                    "fraction_same_direction":concordant/nonzero if nonzero else None}
    return {
        **metadata,
        "status":"EXPLORATORY_WITHIN_BAS_NEAR_VS_FAR_GENTOO",
        "effect_computed":True,
        "pearson_r":correlations,
        "near_minus_mean_far_r":delta,
        "leave_one_window_out_delta_min_max":[min(loo),max(loo)] if loo else None,
        "annual_change_sign_agreement":signs,
        "spatial_distance_causes_synchrony":False,
        "physical_island_boundary_causes_synchrony":False,
        "regional_sea_ice_wind_or_prey_causation_supported":False,
        "no_inferential_p_value":True,
        "decision":("DESCRIPTIVE_WITHIN_BAS_NEAR_GREATER_THAN_FAR_CAUSAL_HOLD"
                    if delta>0 else "NO_DESCRIPTIVE_NEAR_GREATER_THAN_FAR_PATTERN"),
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--json",type=Path,required=True)
    args=parser.parse_args()
    result={"status":"HOLD_ORIGINAL_INPUT","effect_computed":False}
    try:
        records={}
        original_hashes={}
        for label,spec in v21.SOURCES.items():
            raw,meta=v21.get_raw(spec["url"])
            expected={"bird_island_v1":v22.SHA_BIRD,
                      "south_georgia_maiviken":v22.SHA_MAIN}[label]
            if meta["sha256"]!=expected:
                raise ValueError("SOURCE_STOP Bird Island or Maiviken original SHA mismatch")
            records[label]=v22.rows_csv(raw)
            original_hashes[label]=expected
        eligible,windows,qa=v22.source_metadata_only(
            records["bird_island_v1"],records["south_georgia_maiviken"])
        if not v22.nested_support_pass(qa):
            raise ValueError("SOURCE_STOP V22 original cohort no longer passes")
        old=v22.analyze_counts(eligible,windows)
        if not old.get("ecological_effect_fitted"):
            raise ValueError("SOURCE_STOP original V22 numeric sample no longer passes")
        r=old["coastal_small_island_vs_large_main_island_growth_pearson_r"]
        if r is None or abs(r-ORIGINAL_V22_R)>1e-10:
            raise ValueError("SOURCE_STOP original V22 r has changed")
        original_growth=preserved_v22_growth(eligible,windows)
        if sorted(original_growth)!=old["source_matched_growth_years"]:
            raise ValueError("SOURCE_STOP V22 annual windows drifted")
        check=v22.pearson([original_growth[y]["bird"] for y in sorted(original_growth)],
                          [original_growth[y]["maiviken"] for y in sorted(original_growth)])
        if check is None or abs(check-ORIGINAL_V22_R)>1e-10:
            raise ValueError("SOURCE_STOP annual source reconciliation failed")
        source_raw,meta=v21.get_raw(SIGNY_URL)
        if meta["sha256"]!=SIGNY_SHA:
            raise ValueError("SOURCE_STOP Signy original SHA mismatch")
        signy,signyqa=signy_records(v22.rows_csv(source_raw))
        comparison=compare_near_far(original_growth,signy)
        result={
            "status":"V23_THREE_ORIGINAL_BAS_SOURCES_RECONCILED",
            "source_sha256":{**original_hashes,"signy":SIGNY_SHA},
            "frozen_contract":"contracts/BAS_GENTOO_NEAR_FAR_REGION_V23.md",
            "known_v22_before_far_contrasts_r":ORIGINAL_V22_R,
            "v22_exact_reproduction":True,
            "v22_original_common_years":sorted(original_growth),
            "signy_source_QA":signyqa,
            "comparison":comparison,
            "ecological_effect_fitted":comparison["effect_computed"],
            "scientific_decision":comparison.get("decision",comparison["status"]),
        }
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:700]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]=="HOLD_ORIGINAL_INPUT":
        raise SystemExit(2)

if __name__=="__main__":
    main()
