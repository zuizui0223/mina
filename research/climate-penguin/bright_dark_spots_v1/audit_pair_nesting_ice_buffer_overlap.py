#!/usr/bin/env python3
"""Original OSI SAF 25km source-grid buffer overlap for all observed local pairs.

Purely descriptive postselection audit across ALL source-matched local pairs.
No fitting or p value. Overlap is from archived native *ocean* cell IDs, never
geometric circle intersections ignoring Antarctic land or seasonal validity.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from discover_bright_dark_colonies import readcsv, savecsv

EXPECTED_SITES=595
EXPECTED_PAIRS=147
SPECIES=("ADPE","CHPE","GEPE")
NAMED={"CRZW","ROYD"}
ORIGINAL_SOURCE="EUMETSAT OSI SAF v3.1 1993-09 native 25km ocean mask"


def source_pixel_memberships(csv_path):
    rows=readcsv(csv_path)
    if len(rows)!=EXPECTED_SITES:
        raise ValueError("595 original 1993-09 source sites required")
    by={}
    for row in rows:
        site=row["site_id"]
        if site in by:raise ValueError("Duplicate source site ID")
        pix=tuple(int(v) for v in row["native_original_25km_flat_pixel_ids"].split(";") if v.strip())
        if len(pix)!=int(row["n_frozen_native_ocean_pixels"]) or len(pix)!=len(set(pix)):
            raise ValueError("Original native fixed cell counts or identities mismatch")
        if not pix or min(pix)<0 or max(pix)>=432*432:
            raise ValueError("No source 25km ocean pixels or raster cell identity invalid")
        by[site]=set(pix)
    return by


def overlap(a,b):
    a=set(a);b=set(b)
    if not a or not b:
        raise ValueError("Native ocean pixel membership empty")
    ni=len(a&b)
    union=len(a|b)
    return {
        "n_native_frozen_ocean_pixels_left":len(a),
        "n_native_frozen_ocean_pixels_right":len(b),
        "n_shared_native_25km_ocean_pixels":ni,
        "n_native_ocean_pixel_union":union,
        "native_ocean_pixel_jaccard":ni/union,
        "fraction_of_smaller_buffer_source_pixels_shared":ni/min(len(a),len(b)),
        "exact_same_original_25km_ocean_cell_set":a==b,
        "partial_shared_buffer_source_not_independent_ice_exposure":ni>0,
    }


def numeric(row,key):
    v=float(row[key])
    if not math.isfinite(v):
        raise ValueError(f"Nonfinite observed metric {key}")
    return v


def compare(pairs,membership):
    if len(pairs)!=EXPECTED_PAIRS:
        raise ValueError("Source prior local pair cohort drift; expected 147")
    out=[];seen=set()
    for orig in pairs:
        sp=orig["species"]
        if sp not in SPECIES:raise ValueError("Unexpected original species")
        a,b=orig["left_site_id"],orig["right_site_id"]
        if a==b or a not in membership or b not in membership:
            raise ValueError("Invalid original pair site identity")
        key=(sp,tuple(sorted((a,b))))
        if key in seen:raise ValueError("Pair duplicate")
        seen.add(key)
        if orig["status"]!="EXACT_ORIGINAL_MATCHED_COUNT_YEAR_LOCAL_MARINE_SIC":
            raise ValueError("Incomplete original marine SIC in prior accepted pair")
        ol=overlap(membership[a],membership[b])
        nest_delta=numeric(orig,"left_minus_right_nest_log1p_slope_difference_decade")
        sic_diff=numeric(orig,"mean_absolute_site_sic_difference_pp")
        ice_change_diff=numeric(orig,"site_minus_peer_SIC_slope_difference_pp_per_decade")
        source_n=int(orig["n_same_original_count_seasons"])
        if source_n<5:
            raise ValueError("Not a source-supported multi-year pair")
        same_method=str(orig["same_source_method"]).lower()=="true"
        recorded_zero=(int(orig["original_focal_recorded_zero_seasons"])>0
                or int(orig["original_peer_recorded_zero_seasons"])>0)
        rec={
            "species":sp,"source_region":orig["source_region"],
            "polar_250km_fixed_block":orig["polar_250km_fixed_block"],
            "left_site_id":a,"right_site_id":b,
            "left_site_name":orig["left_site_name"],
            "right_site_name":orig["right_site_name"],
            "site_distance_km":numeric(orig,"observed_site_distance_km"),
            "within_original_100km_buffer_radius":str(orig["site_separation_le_100km_buffer_radius"]).lower()=="true",
            "n_identical_original_observed_nest_seasons":source_n,
            "source_method_same":same_method,
            "either_original_long_count_series_contains_real_zero_count":recorded_zero,
            "mean_absolute_source_original_aug_nov_sic_diff_pp":sic_diff,
            "source_original_aug_nov_sic_slope_difference_pp_per_decade":ice_change_diff,
            "absolute_nest_log1p_OLS_slope_difference_per_decade":abs(nest_delta),
            "signed_left_minus_right_nest_log1p_OLS_slope_per_decade":nest_delta,
            "original_source_is_not_independent_foraging_or_colony_demography":True,
            **ol
        }
        out.append(rec)
    return out


def summarize(rows):
    grouped=defaultdict(list)
    for row in rows:grouped[row["species"],row["source_region"],row["polar_250km_fixed_block"]].append(row)
    strata=[]
    for (sp,region,block),items in sorted(grouped.items()):
        score="absolute_nest_log1p_OLS_slope_difference_per_decade"
        filtered=[r for r in items if r["within_original_100km_buffer_radius"]
                  and r["source_method_same"]
                  and not r["either_original_long_count_series_contains_real_zero_count"]]
        strongest=max(filtered,key=lambda r:r[score],default=None)
        strata.append({
            "species":sp,"source_region":region,"source_block":block,
            "n_original_source_5year_10span_pairs":len(items),
            "n_within_100km":sum(r["within_original_100km_buffer_radius"] for r in items),
            "n_same_count_method":sum(r["source_method_same"] for r in items),
            "n_no_original_zero_count_years":sum(not r["either_original_long_count_series_contains_real_zero_count"] for r in items),
            "n_distinct_original_colonies":len({p for r in items for p in (r["left_site_id"],r["right_site_id"])}),
            "n_distinct_marine_ice_source_buffer_comparisons":len({
                tuple(sorted((r["left_site_id"],r["right_site_id"]))) for r in items}),
            "median_abs_between_colony_nest_slope_difference_log1p_per_decade":
                median(r[score] for r in items),
            "median_native_original_ocean_pixel_jaccard":
                median(r["native_ocean_pixel_jaccard"] for r in items),
            "median_absolute_original_site_sic_difference_pp":
                median(r["mean_absolute_source_original_aug_nov_sic_diff_pp"] for r in items),
            "max_same_method_close_zero_free_pair":(
                f'{strongest["left_site_id"]}:{strongest["right_site_id"]}'
                if strongest else None),
            "max_close_same_method_zero_free_pair_original_abs_nest_slope_diff":
                strongest[score] if strongest else None,
            "multiple_pairs_with_one_colony_not_independent_ecological_replicates":True
        })
    return strata


def rank_named_pair(rows):
    chosen=[r for r in rows if r["species"]=="ADPE"
           and {r["left_site_id"],r["right_site_id"]}==NAMED]
    if len(chosen)!=1:raise ValueError("One exact known Ross colony pair required")
    rec=chosen[0]
    def desc(v,subset):
        return {"scope":v,"n_original_compared_pairs":len(subset),
                "rank_abs_nest_trend_difference_1_is_largest":
                    1+sum(z["absolute_nest_log1p_OLS_slope_difference_per_decade"]>
                          rec["absolute_nest_log1p_OLS_slope_difference_per_decade"]+1e-12 for z in subset),
                "rank_original_SIC_mean_absolute_difference_1_is_most_similar":
                    1+sum(z["mean_absolute_source_original_aug_nov_sic_diff_pp"]<
                          rec["mean_absolute_source_original_aug_nov_sic_diff_pp"]-1e-12 for z in subset),
                "jaccard_rank_1_is_most_shared_native_pixels":
                    1+sum(z["native_ocean_pixel_jaccard"]>
                          rec["native_ocean_pixel_jaccard"]+1e-12 for z in subset),
                "not_an_independent_pvalue_or_unbiased_case_control_probability":True}
    species=[r for r in rows if r["species"]=="ADPE"]
    close=[r for r in rows if r["within_original_100km_buffer_radius"]]
    compar=[r for r in rows if r["within_original_100km_buffer_radius"]
            and r["source_method_same"]
            and r["n_identical_original_observed_nest_seasons"]>=15
            and not r["either_original_long_count_series_contains_real_zero_count"]]
    if rec not in compar:raise ValueError("Named robust case dropped from strong original comparator set")
    return {"named_original_pair":rec,
            "original_all_source_local_same_block_pairs":desc("all_147_source_pairs",rows),
            "same_species_adpe_source_local_pairs":desc("same_original_ADPE_species",species),
            "close_100km_same_block_pairs":desc("all_species_within_original_100km",close),
            "same_method_close_15plus_common_year_no_original_count_zeros":
                desc("same_method_close_15plus_year_zero_free",compar)}


def run(args):
    membership=source_pixel_memberships(args.membership)
    raw=readcsv(args.pairs)
    rows=compare(raw,membership)
    strata=summarize(rows)
    named=rank_named_pair(rows)
    summary={
        "status":"ORIGINAL_LOCAL_NEST_SLOPE_VERSUS_OVERLAPPING_NATIVE_OCEAN_ICE_PIXELS_AUDITED",
        "source_original_site_frame":595,"source_identical_year_local_pairs":147,
        "n_distinct_source_regions":len({r["source_region"] for r in rows}),
        "n_distinct_original_species_region_250km_strata":len(strata),
        "species_pair_counts":dict(Counter(r["species"] for r in rows)),
        "n_original_close_100km_pairs":sum(r["within_original_100km_buffer_radius"] for r in rows),
        "n_original_pairs_with_any_same_25km_marine_source_pixels":sum(
            r["n_shared_native_25km_ocean_pixels"]>0 for r in rows),
        "n_original_pairs_with_identical_marine_pixel_memberships":sum(
            r["exact_same_original_25km_ocean_cell_set"] for r in rows),
        "median_original_pair_marine_pixel_jaccard":median(
            r["native_ocean_pixel_jaccard"] for r in rows),
        "named_original_ross_island_cape_crozier_west_vs_royds":named,
        "decision":{
            "case_is_source_verified":True,
            "known_case_prior_literature":"Lyver et al 2014; Ainley et al 2024",
            "already_known_ross_island_divergence_is_not_a_new_ecological_mechanism":True,
            "interpretation":"If marine-pixel sharing is high, small 100km mean SIC difference is expected partly from averaging largely common ocean pixels.",
            "cross_species_and_regions_are_exploratory_only":True,
            "not_a_iceberg_polynya_foraging_or_colony_survival_causal_estimate":True,
        },
        "source_notes":[
            "Source membership archived from original 1993-09 ocean mask, not geometric circle overlap.",
            "The 100km radii can smooth over the ocean conditions separating sites; this cannot rule out local access limitation.",
            "Pairwise rows sharing original colonies and ice pixels are not independent ecological observations.",
            "Rank of selected known pair is descriptive postselection only; not a hypothesis p-value.",
            "No external environmental drivers, new sea-ice threshold, absence, or trait hypotheses are fitted.",
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    savecsv(args.out/"all_original_147_local_colony_pairs_ocean_pixel_overlap.csv",rows)
    savecsv(args.out/"original_species_region_source_block_pair_profiles.csv",strata)
    full=sorted([r for r in rows if r["within_original_100km_buffer_radius"]
            and r["source_method_same"]
            and not r["either_original_long_count_series_contains_real_zero_count"]],
         key=lambda r:-r["absolute_nest_log1p_OLS_slope_difference_per_decade"])
    savecsv(args.out/"local_source_zero_free_method_matched_large_colony_difference_candidates.csv",full)
    (args.out/"marine_ice_native_pixel_overlap_and_robust_local_colony_contrast.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ORIGINAL_ICE_PIXEL_OVERLAP_AUDIT="+json.dumps({
        "n_pairs":len(rows),
        "n_species_region_blocks":len(strata),
        "n_overlapping_25km_ocean_cell_pairs":
            summary["n_original_pairs_with_any_same_25km_marine_source_pixels"],
        "n_identical_25km_source_cell_pairs":
            summary["n_original_pairs_with_identical_marine_pixel_memberships"],
        "median_jaccard":summary["median_original_pair_marine_pixel_jaccard"],
        "named_pair":named
    },ensure_ascii=False),flush=True)
    print("ORIGINAL_LOCAL_NESTING_GROUP_PROFILE="+json.dumps(strata,ensure_ascii=False),flush=True)
    print("ORIGINAL_LOCAL_ZERO_FREE_SAME_METHOD_TOP="+json.dumps(full[:15],ensure_ascii=False),flush=True)
    return summary


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--pairs",type=Path,required=True)
    parser.add_argument("--membership",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    run(parser.parse_args())
