#!/usr/bin/env python3
"""Post-result predeclared-all-147 support depth of original exclusive SIC result.

This is outcome-aware SOURCE RESOLUTION robustness, not an independently
preregistered ecological hypothesis, parameter search, or causal ice effect.
"""
from __future__ import annotations
import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from discover_bright_dark_colonies import readcsv,savecsv

EXPECTED=147
SOURCE_OK="SOURCE_FULL_120MONTH_EXCLUSIVE_MARINE_COMPARISON"
GRID_TOO_FEW="SOURCE_EXCLUSIVE_GRID_SUPPORT_INSUFFICIENT"
NAME={
    ("ADPE",frozenset(("CRZW","ROYD"))):"Ross Island Adélie Crozier-Royds",
    ("CHPE",frozenset(("BART","DEMA"))):"South Shetland chinstrap Barton-Demay",
    ("GEPE",frozenset(("BISC","LOCK"))):"Antarctic Peninsula gentoo Biscoe-Lockroy"
}

def boolean(s):
    if isinstance(s,bool):return s
    if str(s).lower() not in ("true","false"):
        raise ValueError("Source boolean column contains non-boolean")
    return str(s).lower()=="true"

def validrows(rows):
    if len(rows)!=EXPECTED:
        raise ValueError("Prior all 147 source pair universe changed")
    good=[];missing=[]
    for r in rows:
        src=r["exclusive_source_support"]
        if src==SOURCE_OK:
            r["delta"]=float(r["exclusive_minus_original_full_mean_abs_difference_pp"])
            if not math.isfinite(r["delta"]):
                raise ValueError("Missing exclusive original source magnitude")
            good.append(r)
        else:
            if src not in (GRID_TOO_FEW,"INSUFFICIENT_VALID_EXCLUSIVE_CLIMATE_YEARS"):
                raise ValueError("Unexpected original source nonidentified status")
            missing.append(r)
    if len(good)!=93 or len(missing)!=54:
        raise ValueError("Published 93 valid and 54 original marine grids incomplete source drift")
    return good,missing

def summarize_group(rows,scope):
    if not rows:
        return {"scope":scope,"n_original_source_pairs":0,
                "n_source_blocks":0,"medians":None,
                "cannot_claim_any_source_conclusion":True}
    return {
        "scope":scope,
        "n_original_source_pairs":len(rows),
        "n_source_region_species_250km_blocks":len({
            (r["species"],r["source_region"],r["original_polar_250km_block"]) for r in rows}),
        "n_unique_breeding_colony_species_site_IDS":len({
            (r["species"],z) for r in rows
            for z in (r["left_site_id"],r["right_site_id"])}),
        "n_original_pairs_exclusive_SIC_difference_larger_than_full":
            sum(float(r["delta"])>1e-10 for r in rows),
        "n_original_pairs_exclusive_SIC_difference_smaller_than_full":
            sum(float(r["delta"])<-1e-10 for r in rows),
        "median_full_100km_SIC_diff_on_identical_actual_census_years_pp":median(
            float(r["original_full_buffer_abs_SIC_diff_on_exclusive_years_pp"]) for r in rows),
        "median_nonoverlapping_25km_marine_SIC_diff_same_years_pp":median(
            float(r["exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp"]) for r in rows),
        "median_pairwise_exclusive_to_full_ratio":median(
            float(r["exclusive_divided_by_full_buffer_abs_difference_ratio"]) for r in rows
            if r.get("exclusive_divided_by_full_buffer_abs_difference_ratio") not in ("",None)),
        "original_pairwise_source_not_independent_ice_or_nest_trials":True
    }

def compute(rows):
    supported,unsupported=validrows(rows)
    bands=[]
    for q in (3,5,8,12):
        retained=[r for r in supported
                  if int(r["source_exclusive_left_frozen_marine_pixels"])>=q
                  and int(r["source_exclusive_right_frozen_marine_pixels"])>=q]
        bands.append(summarize_group(retained,f"original_fixed_exclusive_marine_cells_each_site_at_least_{q}"))
    matched=[r for r in supported if boolean(r["original_source_count_method_same"])
             and not boolean(r["original_zero_in_any_full_count_series"])
             and int(r["real_common_count_census_years"])>=15]
    strict=summarize_group(matched,"same_original_count_method_no_observed_zeros_15plus_same_census_years")
    block={}
    for r in supported:
        key=(r["species"],r["source_region"],r["original_polar_250km_block"])
        block.setdefault(key,[]).append(r)
    profiles=[]
    for (sp,region,blockid),rs in sorted(block.items()):
        profile=summarize_group(rs,sp+" "+region+" "+blockid)
        profiles.append({"species":sp,"source_region":region,"original_250km_block":blockid,
                         **profile})
    named=[]
    for (sp,siteids),label in NAME.items():
        res=[r for r in rows if r["species"]==sp and
             frozenset((r["left_site_id"],r["right_site_id"]))==siteids]
        if len(res)!=1:raise ValueError(f"Original mandatory named {label} missing")
        z=res[0]
        named.append({
            "label":label,
            "original_source_support":z["exclusive_source_support"],
            "n_identical_observed_census_years":int(z["real_common_count_census_years"]),
            "original_left_exclusive_cells":int(z["source_exclusive_left_frozen_marine_pixels"]),
            "original_right_exclusive_cells":int(z["source_exclusive_right_frozen_marine_pixels"]),
            "full_100km_mean_abs_SIC_diff_pp":float(
                z["original_full_buffer_mean_abs_SIC_difference_all_common_years_pp"]),
            "exclusive_nonoverlapping_SIC_diff_pp":float(z["exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp"])
                if z["exclusive_source_support"]==SOURCE_OK else None,
            "pairwise_exclusive_full_ratio":float(z["exclusive_divided_by_full_buffer_abs_difference_ratio"])
                if z["exclusive_source_support"]==SOURCE_OK else None,
            "passes_5plus_each_exclusive_cell_depth":min(
                int(z["source_exclusive_left_frozen_marine_pixels"]),
                int(z["source_exclusive_right_frozen_marine_pixels"]))>=5,
            "passes_8plus_each_exclusive_cell_depth":min(
                int(z["source_exclusive_left_frozen_marine_pixels"]),
                int(z["source_exclusive_right_frozen_marine_pixels"]))>=8,
        })
    verdict={
        "status":"ORIGINAL_EXCLUSIVE_MARINE_GRID_FOOTPRINT_SENSITIVITY_AUDITED",
        "source_original_all_147_observed_pair_roster":len(rows),
        "source_original_93_accepted_nonoverlap_marine_exposure_pairs":len(supported),
        "source_original_54_unidentified_marine_exclusive_pairs":len(unsupported),
        "post_result_depth_thresholds_are_SENSITIVITY_not_premeditated_hypothesis":True,
        "source_frozen_primary_comparison":summarize_group(supported,"original_acceptance_each_side_3plus_native_ocean_cells"),
        "all_exclusive_cell_depth_sensitivities":bands,
        "same_method_15plus_real_survey_year_no_orig_zeros":strict,
        "source_independent_original_species_region_250km_block_descriptive_profiles":profiles,
        "named_sites_qualifications":named,
        "interpretation_limit":[
            "Every individual pair within same original colony block shares parent sites; no independent p-values.",
            "When all 93 exclusive-site differences exceed whole-buffer differences, the median comparison is not evidence that nesting biology is driven by ice concentration.",
            "The nonoverlapping source cells can differ systematically in latitude, open-ocean access, and bathymetry.",
            "Even disjoint source 25km grid cells may not be independent satellite footprints; 25km grid spacing is not true resolution.",
            "Pairs with fewer than 3 native cells per side are source-unidentified not ice-identical or biologically similar.",
            "Post-result >=5/8/12 original cell depth sensitivity is a geometry audit, not an optimized causal threshold.",
            "The 15+ survey-year and no-zero count support is external to original marine pixel depth and not an ecological population loss estimator."
        ]
    }
    return verdict

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pairs",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    rows=readcsv(args.pairs)
    verdict=compute(rows)
    args.out.mkdir(parents=True,exist_ok=True)
    savecsv(args.out/"original_exclusive_marine_pixel_depth_sensitivity.csv",
        verdict["all_exclusive_cell_depth_sensitivities"])
    savecsv(args.out/"original_exclusive_marine_species_region_block_profile.csv",
        verdict["source_independent_original_species_region_250km_block_descriptive_profiles"])
    (args.out/"original_exclusive_source_147_sensitivity_verdict.json").write_text(
        json.dumps(verdict,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EXCLUSIVE_DEPTH_SENSITIVITY="+json.dumps(verdict["all_exclusive_cell_depth_sensitivities"],ensure_ascii=False),flush=True)
    print("EXCLUSIVE_STRICT_CENSUS_SENSITIVITY="+json.dumps(verdict["same_method_15plus_real_survey_year_no_orig_zeros"],ensure_ascii=False),flush=True)
    print("EXCLUSIVE_DEPTH_NAMED_CASES="+json.dumps(verdict["named_sites_qualifications"],ensure_ascii=False),flush=True)
    return verdict

if __name__=="__main__":
    main()
