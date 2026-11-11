#!/usr/bin/env python3
"""Temporal comparability for original penguin relative bright/dark sites.

Both slopes for each original same-species same-region site pair are fitted
on the IDENTICAL true observed years. Missing does not mean colony absence.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import defaultdict, Counter
from pathlib import Path
from statistics import median

from discover_bright_dark_colonies import (
    readcsv, savecsv, original_source_rows, slope, sign,
)


def pair_original_years(focal_by_year, peer_by_year, *, omit_real_zeros=False):
    """Original coincident years only, without any interp or imputation."""
    if omit_real_zeros:
        years = sorted(y for y in focal_by_year.keys() & peer_by_year.keys()
                       if focal_by_year[y] != 0 and peer_by_year[y] != 0)
    else:
        years = sorted(focal_by_year.keys() & peer_by_year.keys())
    if len(years) < 5 or years[-1] - years[0] < 10:
        return {
            "status": "INSUFFICIENT_FIVE_COOBSERVED_YEARS_OVER_TEN_YEAR_SPAN",
            "n_same_original_observed_years": len(years),
            "first_common_year": years[0] if years else None,
            "last_common_year": years[-1] if years else None,
            "years": years
        }
    first = slope([(y,focal_by_year[y]) for y in years])
    second = slope([(y,peer_by_year[y]) for y in years])
    if first is None or second is None:
        raise AssertionError("Original common-year fitted slopes should be valid")
    return {
        "status": "EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED",
        "n_same_original_observed_years": len(years),
        "first_common_year": years[0],
        "last_common_year": years[-1],
        "years": years,
        "focal_log1p_nest_slope_per_decade_same_years": first,
        "peer_log1p_nest_slope_per_decade_same_years": second,
        "paired_relative_log1p_nest_decadal_slope": first-second,
        "n_focal_actual_zero_counts_in_common_years": sum(focal_by_year[y] == 0 for y in years),
        "n_peer_actual_zero_counts_in_common_years": sum(peer_by_year[y] == 0 for y in years)
    }


def original_robust(source):
    return source.get("robust_source_candidate_status","").startswith("SOURCE_ROBUST_RELATIVE_")


def audit(roster, bycount):
    # The first source-backed residual discovery gives a frozen 100-site roster
    # and peer assignment; this audit MUST NOT redefine that universe.
    if len(roster) != 100:
        raise ValueError("Original bright-dark 100-cohort drift")
    if len({(r["site_id"],r["species"]) for r in roster}) != 100:
        raise ValueError("Original bright-dark roster contains duplicates")
    groups = defaultdict(list)
    for site in roster:
        if (site["site_id"],site["species"]) not in bycount:
            raise ValueError("Missing original exact nest observations for candidate")
        groups[(site["species"],site["source_region"])].append(site)
        actual = bycount[site["site_id"],site["species"]]
        if len(actual) != int(site["n_actual_original_census_years"]):
            raise ValueError("Source year counts no longer match original bright/dark output")
        if abs(slope(actual)-float(site["original_OLS_log1p_nest_slope_per_decade"])) > 1e-8:
            raise ValueError("Source original slope identity drifted")

    results=[];pairs=[];source_robust=[]
    for site in sorted(roster,key=lambda r:(r["species"],r["source_region"],r["site_id"])):
        group = groups[site["species"],site["source_region"]]
        supported = site["source_peer_eligibility"] == "SAME_SPECIES_REGION_PAIRED_REFERENCE_AVAILABLE"
        original_sign = site.get("relative_direction","unavailable")
        row = {
            "species":site["species"],"site_id":site["site_id"],
            "site_name":site["site_name"],"source_region":site["source_region"],
            "polar_250km_block":site["polar_250km_block"],
            "latitude":float(site["latitude"]),"longitude":float(site["longitude"]),
            "n_original_census_years":int(site["n_actual_original_census_years"]),
            "observed_original_survey_method":site["observed_original_nest_method"],
            "original_census_span_years":int(site["actual_year_span"]),
            "original_source_peer_support":site["source_peer_eligibility"],
            "original_region_peer_site_count":len(group)-1,
            "original_relative_direction":original_sign,
            "original_OLS_residual_vs_unmatched_year_peer_median":(
                float(site["relative_log1p_nest_slope_residual_per_decade"])
                if supported else None),
            "original_strict_TheilSen_and_endpoint_sign_gate":bool(original_robust(site)),
            "original_first_real_observed_count_is_zero":int(site["first_original_observed_nest_count"]) == 0,
            "original_last_real_observed_count_is_zero":int(site["last_original_observed_nest_count"]) == 0,
            "n_actual_zero_census_seasons":int(site["original_observed_zero_count_years"]),
            "cannot_infer_new_colony_or_real_absence_from_recorded_zero":True,
        }
        if not supported:
            row["same_year_matched_support"] = "NO_COMPARABLE_ORIGINAL_SPECIES_REGION"
            results.append(row)
            continue

        focal = dict(bycount[site["site_id"],site["species"]])
        matches=[];zerofree=[]
        for peer in group:
            if peer["site_id"] == site["site_id"]:
                continue
            original = dict(bycount[peer["site_id"],peer["species"]])
            matched = pair_original_years(focal, original)
            nomatch = pair_original_years(focal, original,omit_real_zeros=True)
            rec={
                "species":site["species"],"source_region":site["source_region"],
                "focal_site_id":site["site_id"],"peer_site_id":peer["site_id"],
                "focal_original_method":site["observed_original_nest_method"],
                "peer_original_method":peer["observed_original_nest_method"],
                "original_methods_same":site["observed_original_nest_method"] == peer["observed_original_nest_method"],
                "focal_block":site["polar_250km_block"],"peer_block":peer["polar_250km_block"],
                "peer_outside_250km_focal_block":site["polar_250km_block"] != peer["polar_250km_block"],
                "actual_source_years_coobserved_status":matched["status"],
                "n_same_original_observed_years":matched["n_same_original_observed_years"],
                "first_common_year":matched["first_common_year"],
                "last_common_year":matched["last_common_year"],
                "coobserved_year_list":";".join(str(y) for y in matched["years"]),
                "source_years_zero_free_status":nomatch["status"],
                "n_same_original_zero_free_observed_years":nomatch["n_same_original_observed_years"],
            }
            if matched["status"] == "EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED":
                rec.update({
                    "paired_relative_log1p_nest_decadal_slope":
                        matched["paired_relative_log1p_nest_decadal_slope"],
                    "focal_common_year_log1p_nest_slope":
                        matched["focal_log1p_nest_slope_per_decade_same_years"],
                    "peer_common_year_log1p_nest_slope":
                        matched["peer_log1p_nest_slope_per_decade_same_years"],
                    "n_real_zero_counts_in_focal_on_paired_years":
                        matched["n_focal_actual_zero_counts_in_common_years"],
                    "n_real_zero_counts_in_peer_on_paired_years":
                        matched["n_peer_actual_zero_counts_in_common_years"],
                })
                matches.append(rec)
            if nomatch["status"] == "EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED":
                rec["zero_free_paired_relative_log1p_nest_decadal_slope"] = (
                    nomatch["paired_relative_log1p_nest_decadal_slope"])
                zerofree.append(rec)
            pairs.append(rec)

        outside=[r for r in matches if r["peer_outside_250km_focal_block"]]
        distinct_outside_blocks=len({r["peer_block"] for r in outside})
        row.update({
            "n_actual_year_matched_original_peer_sites":len(matches),
            "n_actual_year_matched_outside_block_peer_sites":len(outside),
            "n_distinct_actual_year_matched_outside_polar_blocks":distinct_outside_blocks,
            "n_matched_same_method_original_peer_sites":sum(r["original_methods_same"] for r in matches),
            "n_zero_free_matched_original_peer_sites":len(zerofree),
        })
        if matches:
            values=[r["paired_relative_log1p_nest_decadal_slope"] for r in matches]
            val=float(median(values))
            same=sum(sign(v)==original_sign for v in values)
            row["same_year_peer_median_relative_slope"] = val
            row["same_year_peer_residual_direction"] = sign(val)
            row["n_same_direction_matched_peer_sites"] = same
            row["direction_agreement_fraction_all_matched_peers"] = same/len(values)
            row["n_opposite_direction_matched_peer_sites"] = sum(
                sign(v) not in (original_sign,"zero") for v in values)
            row["n_matching_census_peer_sites_with_recorded_zero"] = sum(
                r["n_real_zero_counts_in_focal_on_paired_years"]>0 or
                r["n_real_zero_counts_in_peer_on_paired_years"]>0 for r in matches)
        if zerofree:
            vs=[r["zero_free_paired_relative_log1p_nest_decadal_slope"] for r in zerofree]
            row["zero_free_matched_peer_median_relative_slope"] = float(median(vs))
            row["zero_free_matched_peer_direction"] = sign(row["zero_free_matched_peer_median_relative_slope"])

        if len(matches)<3 or len(outside)<2:
            support_status="INSUFFICIENT_THREE_COMMON_YEAR_PEERS_OR_TWO_OUTSIDE_BLOCK_PEERS"
        else:
            support_status="DESCRIPTIVE_COMMON_YEAR_PEER_SUPPORT"
        row["same_year_matched_support"]=support_status
        same_year_supported = (
            support_status == "DESCRIPTIVE_COMMON_YEAR_PEER_SUPPORT"
            and row["same_year_peer_residual_direction"] == original_sign
            and row["direction_agreement_fraction_all_matched_peers"] >= .75
            and original_sign in ("positive","negative")
        )
        high_geo = same_year_supported and distinct_outside_blocks>=2
        row["same_year_sign_qualified_candidate"] = bool(
            same_year_supported and original_robust(site))
        row["outside_spatial_block_replicated_lead"] = bool(
            high_geo and original_robust(site))
        row["source_zero_free_same_year_direction_compatible"] = (
            row.get("zero_free_matched_peer_direction")==original_sign
            if zerofree else None
        )
        if row["outside_spatial_block_replicated_lead"]:
            status="ROBUST_SOURCE_AND_COMMON_YEAR_AND_SPATIAL_BLOCK_LEAD"
        elif row["same_year_sign_qualified_candidate"]:
            status="SOURCE_AND_COMMON_YEAR_DESCRIPTIVE_LEAD_SPATIAL_SUPPORT_LIMITED"
        elif original_robust(site):
            status="FORMER_SOURCE_STRICT_LEAD_NOT_ESTABLISHED_IN_SAME_YEAR_PAIRS"
        else:
            status="EXPLORATORY_ONLY_NO_ORIGINAL_SOURCE_STRICT_LEAD"
        row["overall_source_candidate_status"]=status
        results.append(row)
        if original_robust(site):
            source_robust.append(row)
    if len(results)!=100:
        raise AssertionError("Missing any original 100 source site-series")
    assert len(source_robust)==25, f"Prior source strict candidate count drift {len(source_robust)}"
    return results,pairs,source_robust


def run(args):
    original=readcsv(args.previous)
    if len(original)!=100:
        raise ValueError("Prior 100 source candidate table missing")
    geo,bycount=original_source_rows(args.census,args.atlas)
    rows,pairs,strict=audit(original,bycount)
    comp=[r for r in rows if r["original_source_peer_support"]==
          "SAME_SPECIES_REGION_PAIRED_REFERENCE_AVAILABLE"]
    eligible=[r for r in comp if r["same_year_matched_support"]==
              "DESCRIPTIVE_COMMON_YEAR_PEER_SUPPORT"]
    lead=[r for r in strict if r["same_year_sign_qualified_candidate"]]
    strongest=[r for r in strict if r["outside_spatial_block_replicated_lead"]]
    zero_robust=[r for r in lead if r["source_zero_free_same_year_direction_compatible"] is True]
    source={
        "status":"ORIGINAL_SOURCE_COMMON_CENSUS_YEAR_PEER_BRIGHT_DARK_AUDIT_COMPLETE",
        "input_source":{
            "original_site_ledger_total":595,"original_method_fixed_nest_count_records":2456,
            "strict_initial_source_cohort_site_species":100,
            "species_region_original_comparable_site_species":90,
            "strict_TheilSen_endpoint_candidate_before_time_matching":25,
            "co_observation_years_min":5,"co_observation_year_span_min":10,
            "matched_peer_support_min":3,"outside_block_peer_support_min":2,
            "residual_direction_agreement_fraction_min":.75,
            "distinct_outside_250km_blocks_for_strong_geo":2,
            "original_survey_absences_fabricated":False
        },
        "n_comparable_original_species_region_sites":len(comp),
        "n_sites_with_three_common_year_peers_and_two_outside_block_peers":len(eligible),
        "n_original_strict_candidates":len(strict),
        "n_original_strict_candidates_retaining_actual_common_year_sign":len(lead),
        "n_original_strict_candidates_with_two_distinct_outside_blocks":len(strongest),
        "n_actual_same_year_strict_leads_with_zero_free_direction_compatible":len(zero_robust),
        "n_actual_pairwise_comparisons_total":len(pairs),
        "n_supported_common_original_year_site_pairs":sum(
            r["actual_source_years_coobserved_status"]=="EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED"
            for r in pairs),
        "n_supported_zero_free_original_year_site_pairs":sum(
            r["source_years_zero_free_status"]=="EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED"
            for r in pairs),
        "strict_former_candidates_sorted":[{
            "species":r["species"],"site_id":r["site_id"],"site_name":r["site_name"],
            "region":r["source_region"],"direction":r["original_relative_direction"],
            "initial_log1p_decadal_deviation":r["original_OLS_residual_vs_unmatched_year_peer_median"],
            "matched_peer_count":r.get("n_actual_year_matched_original_peer_sites",0),
            "matched_peer_outside_block_count":r.get("n_actual_year_matched_outside_block_peer_sites",0),
            "matched_peer_external_block_count":r.get("n_distinct_actual_year_matched_outside_polar_blocks",0),
            "matched_peer_sign_agreement":r.get("direction_agreement_fraction_all_matched_peers"),
            "matched_peer_median_decadal_difference":r.get("same_year_peer_median_relative_slope"),
            "matched_zero_free_direction_same":r.get("source_zero_free_same_year_direction_compatible"),
            "has_actual_zero_census_seasons":r["n_actual_zero_census_seasons"]>0,
            "status":r.get("overall_source_candidate_status","no_comparable_regional_peers")
        } for r in sorted(strict,key=lambda r:(r["species"],r["original_relative_direction"],
                  -(abs(r["original_OLS_residual_vs_unmatched_year_peer_median"]))))],
        "limits":[
           "Same-site and same-year survey records have not been corrected for detection and spatial census-footprint changes.",
           "A recorded zero is not proof of long-term ecological local extinction or colonization.",
           "Common-year median pair differences are region-specific exploratory ranks, not p-values or species-wide causal climate effects.",
           "Spatially adjacent sites share ice, foraging grounds and survey programs; block supports are minimum checks only.",
           "Even fully matching census years across sites does not calibrate marine productivity, prey or migration mechanisms.",
           "Original CDR 60 percent marine isopleth and bathymetry remain unmodeled until independent source collection."
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    savecsv(args.out/"all_100_same_year_comparability.csv",rows)
    savecsv(args.out/"all_original_same_year_site_pair_details.csv",pairs)
    savecsv(args.out/"previous_25_strict_source_candidates_same_year_checked.csv",strict)
    savecsv(args.out/"same_year_source_sign_surviving_bright_dark.csv",lead)
    savecsv(args.out/"same_year_two_external_block_strong_leads.csv",strongest)
    (args.out/"common_year_peer_verdict.json").write_text(
        json.dumps(source,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("COMMON_YEAR_SUPPORT="+json.dumps({
        k:v for k,v in source.items() if k.startswith("n_")
    },ensure_ascii=False),flush=True)
    print("COMMON_YEAR_STRICT_25="+json.dumps(source["strict_former_candidates_sorted"],
                                          ensure_ascii=False),flush=True)
    return source


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous",required=True,type=Path)
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--atlas",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    run(args)


if __name__=="__main__":
    main()
