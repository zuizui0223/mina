#!/usr/bin/env python3
"""Exploratory original MAPPPD observed-colony relative bright/dark spots.

No unrecorded species/year pseudoabsence; no modeled demographic fitness; no
hypothesis p-values. Exactly rechecks previously frozen source trends.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

SPECIES = ("ADPE", "CHPE", "GEPE")
EXPECTED = {"ADPE": 37, "CHPE": 27, "GEPE": 36}
N_SITES = 77
N_TRENDS = 100
MIN_REGIONAL_SITES = 5
MIN_REGIONAL_BLOCKS = 2


def readcsv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as fp:
        return list(csv.DictReader(fp))


def savecsv(path: Path, records: list[dict]):
    if not records:
        path.write_text("no_eligible_rows\n", encoding="utf-8")
        return
    fields = list(dict.fromkeys(k for item in records for k in item))
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def slope(points: list[tuple[int, int]]) -> float | None:
    if len(points) < 5 or points[-1][0] - points[0][0] < 10:
        return None
    x = [float(y) for y, _ in points]
    z = [math.log1p(float(n)) for _, n in points]
    xbar, zbar = mean(x), mean(z)
    den = sum((v - xbar)**2 for v in x)
    if den <= 0:
        return None
    return 10 * sum((xi - xbar) * (yi - zbar) for xi, yi in zip(x, z)) / den


def theil_sen(points: list[tuple[int, int]]) -> float | None:
    if len(points) < 5 or points[-1][0] - points[0][0] < 10:
        return None
    diffs = []
    for index, (year, count) in enumerate(points):
        for other_year, other_count in points[index+1:]:
            diffs.append(10 * (math.log1p(other_count) - math.log1p(count)) /
                         (other_year - year))
    return float(median(diffs)) if diffs else None


def sign(value: float | None, eps=1e-10):
    if value is None or not math.isfinite(value):
        return "unavailable"
    return "positive" if value > eps else "negative" if value < -eps else "zero"


def peer_baseline(rows: list[dict], target: dict, slope_field: str):
    peers = [r for r in rows if r["site_id"] != target["site_id"]]
    values = [r[slope_field] for r in peers if r.get(slope_field) is not None]
    return float(median(values)) if values else None


def original_source_rows(census_path: Path, atlas_path: Path):
    census = readcsv(census_path)
    atlas = readcsv(atlas_path)
    if len(census) != 2456 or len(atlas) != 595:
        raise ValueError("Original method-consistent census or site source drift")
    geo = {r["site_id"]: r for r in atlas}
    if len(geo) != 595:
        raise ValueError("Not 595 unique source colony IDs")
    by = defaultdict(list)
    seen = set()
    for row in census:
        site, sp, year = row["site_id"], row["species"], int(row["season"])
        if sp not in SPECIES or site not in geo:
            raise ValueError("Unknown original source species or site")
        count = int(row["observed_nest_count"])
        if count < 0:
            raise ValueError("Negative source nest count")
        key = (site, sp, year)
        if key in seen:
            raise ValueError("Duplicate original site×species×year count")
        seen.add(key)
        if 1991 <= year <= 2020:
            by[site, sp].append((year, count))
    if sum(len(v) for v in by.values()) != 1691 or len(by) != 495:
        raise ValueError("Original 1991–2020 count support drift")
    return geo, {k: sorted(v) for k, v in by.items()}


def compute(known_trends: Path, census: Path, atlas: Path, output: Path):
    geo, bycount = original_source_rows(census, atlas)
    trends = readcsv(known_trends)
    if len(trends) != N_TRENDS or len({r["site_id"] for r in trends}) != N_SITES:
        raise ValueError("Original 100-trend 77-colony cohort drift")
    if Counter(r["species"] for r in trends) != Counter(EXPECTED):
        raise ValueError("Species 37/27/36 original trend support drift")
    rows = []
    identities = set()
    for record in trends:
        site, species = record["site_id"], record["species"]
        if (site, species) in identities:
            raise ValueError("Duplicate original trend site-species ID")
        identities.add((site, species))
        points = bycount[site, species]
        if len(points) < 5 or (points[-1][0] - points[0][0]) < 10:
            raise ValueError("Original trend cohort no longer eligible")
        full_slope = slope(points)
        if full_slope is None:
            raise ValueError("Unfittable original OLS trend")
        frozen_slope = float(record["observed_log_nest_trend_per_decade"])
        if abs(full_slope - frozen_slope) > 1e-8:
            raise ValueError(
                f"Original independent OLS trend mismatch {species} {site} "
                f"new={full_slope} frozen={frozen_slope}")
        meta = geo[site]
        if meta["source_region"] != record["source_region"]:
            raise ValueError("Original region identity drift")
        if meta["polar_250km_fixed_grid_block"] != record["polar_250km_block"]:
            raise ValueError("Original polar block identity drift")
        rows.append({
            "species":species,"site_id":site,"site_name":meta["site_name"],
            "source_region":meta["source_region"],
            "polar_250km_block":meta["polar_250km_fixed_grid_block"],
            "latitude":float(meta["latitude"]),
            "longitude":float(meta["longitude"]),
            "observed_original_nest_method":record["observed_method"],
            "n_actual_original_census_years":len(points),
            "original_first_census_year":points[0][0],
            "original_last_census_year":points[-1][0],
            "actual_year_span":points[-1][0]-points[0][0],
            "first_original_observed_nest_count":points[0][1],
            "last_original_observed_nest_count":points[-1][1],
            "original_observed_zero_count_years":sum(n == 0 for _,n in points),
            "original_OLS_log1p_nest_slope_per_decade":full_slope,
            "frozen_original_OLS_slope_verified":True,
            "original_TheilSen_log1p_nest_slope_per_decade":theil_sen(points),
            "first_year_removed_OLS_slope":slope(points[1:]),
            "last_year_removed_OLS_slope":slope(points[:-1]),
            "frozen_same_observed_year_SIC_slope_pp_per_decade":
                float(record["sic_trend_pp_per_decade"]),
            "original_source_unrecorded_year_is_not_zero":True
        })

    grouped = defaultdict(list)
    for item in rows:
        grouped[item["species"],item["source_region"]].append(item)
    support = []
    for (species, region), group in sorted(grouped.items()):
        blocks = {r["polar_250km_block"] for r in group}
        n = len(group)
        qualifies = n >= MIN_REGIONAL_SITES and len(blocks) >= MIN_REGIONAL_BLOCKS
        support.append({
            "species":species,"source_region":region,
            "original_longitudinal_colony_sites":n,
            "original_fixed_250km_blocks":len(blocks),
            "raw_observation_years":sum(z["n_actual_original_census_years"] for z in group),
            "n_10year_or_more_census_years_and_20year_span":sum(
                r["n_actual_original_census_years"] >= 10
                and r["actual_year_span"] >= 20 for r in group),
            "eligible_for_species_region_relative_spots":qualifies,
            "baseline_if_qualifies":"leave-one-site-out same species and region median original OLS log1p nest slope",
            "never_treat_as_true_species_range_or_site_absence":True
        })

        for target in group:
            target["region_species_original_long_series_sites"] = n
            target["region_species_distinct_250km_blocks"] = len(blocks)
            target["n_same_species_region_peer_sites"] = n - 1
            target["n_peer_sites_in_other_250km_blocks"] = sum(
                z["polar_250km_block"] != target["polar_250km_block"]
                for z in group if z["site_id"] != target["site_id"])
            target["n_peer_250km_blocks_outside_focal_block"] = len({
                z["polar_250km_block"] for z in group
                if z["site_id"] != target["site_id"] and
                    z["polar_250km_block"] != target["polar_250km_block"]})
            if not qualifies:
                target["source_peer_eligibility"] = "NO_COMPARABLE_REGIONAL_PEERS"
                continue
            baseline = peer_baseline(group, target, "original_OLS_log1p_nest_slope_per_decade")
            tsbaseline = peer_baseline(group, target, "original_TheilSen_log1p_nest_slope_per_decade")
            residual = target["original_OLS_log1p_nest_slope_per_decade"] - baseline
            target["source_peer_eligibility"] = "SAME_SPECIES_REGION_PAIRED_REFERENCE_AVAILABLE"
            target["leave_site_out_regional_median_OLS_log1p_decadal_trend"] = baseline
            target["relative_log1p_nest_slope_residual_per_decade"] = residual
            target["relative_1plus_nest_count_decadal_change_ratio_exploratory"] = (
                math.exp(residual) if abs(residual)<30 else None)
            target["relative_direction"] = sign(residual)
            target["observed_absolute_log1p_nest_slope_direction"] = sign(
                target["original_OLS_log1p_nest_slope_per_decade"])
            target["relative_TheilSen_residual_per_decade"] = (
                target["original_TheilSen_log1p_nest_slope_per_decade"]-tsbaseline
                if tsbaseline is not None else None)
            target["early_year_dropped_residual_vs_fixed_peer_baseline"] = (
                target["first_year_removed_OLS_slope"]-baseline
                if target["first_year_removed_OLS_slope"] is not None else None)
            target["last_year_dropped_residual_vs_fixed_peer_baseline"] = (
                target["last_year_removed_OLS_slope"]-baseline
                if target["last_year_removed_OLS_slope"] is not None else None)
            peer_elsewhere = [
                z["original_OLS_log1p_nest_slope_per_decade"]
                for z in group if z["site_id"] != target["site_id"]
                and z["polar_250km_block"] != target["polar_250km_block"]
            ]
            target["other_block_reference_residual"] = (
                target["original_OLS_log1p_nest_slope_per_decade"] - median(peer_elsewhere)
                if len(peer_elsewhere)>=2
                and target["n_peer_250km_blocks_outside_focal_block"]>=2 else None)
            strict_sample = (
                target["n_actual_original_census_years"]>=10
                and target["actual_year_span"]>=20
            )
            robust = strict_sample and all(
                sign(z) == sign(residual) and sign(residual) != "zero"
                for z in (
                    target["relative_TheilSen_residual_per_decade"],
                    target["early_year_dropped_residual_vs_fixed_peer_baseline"],
                    target["last_year_dropped_residual_vs_fixed_peer_baseline"]
                ))
            target["robust_source_candidate_status"] = (
                "SOURCE_ROBUST_RELATIVE_BRIGHT_CANDIDATE" if robust and residual>0
                else "SOURCE_ROBUST_RELATIVE_DARK_CANDIDATE" if robust and residual<0
                else "SOURCE_SENSITIVITY_OR_DENSITY_INCOMPLETE_NO_ROBUST_CLAIM")
            target["outside_block_peer_reference_eligible"] = (
                target["other_block_reference_residual"] is not None)
            target["caveat"] = (
                "Relative difference of observed log1p nest-count slopes in source geography; "
                "no ecological refuge, survey detection, breeding success or causal environmental estimate."
            )

    if len(rows)!=100 or len(support)<1:
        raise AssertionError("Original source frame unexpectedly empty")
    eligible=[r for r in rows if r["source_peer_eligibility"]=="SAME_SPECIES_REGION_PAIRED_REFERENCE_AVAILABLE"]
    strict=[r for r in eligible if r["robust_source_candidate_status"].startswith("SOURCE_ROBUST_")]
    bright=sorted((r for r in eligible if r["relative_direction"]=="positive"),
                  key=lambda r:(-r["relative_log1p_nest_slope_residual_per_decade"],r["site_id"],r["species"]))
    dark=sorted((r for r in eligible if r["relative_direction"]=="negative"),
                key=lambda r:(r["relative_log1p_nest_slope_residual_per_decade"],r["site_id"],r["species"]))
    robust_bright=[r for r in bright if r in strict]
    robust_dark=[r for r in dark if r in strict]

    def brief(rows):
        return [{
            "species":r["species"],"site_id":r["site_id"],"site_name":r["site_name"],
            "region":r["source_region"],"n_census_years":r["n_actual_original_census_years"],
            "span_years":r["actual_year_span"],"blocks":r["region_species_distinct_250km_blocks"],
            "observed_log1p_slope_decadal":r["original_OLS_log1p_nest_slope_per_decade"],
            "regional_loo_median_slope_decadal":r["leave_site_out_regional_median_OLS_log1p_decadal_trend"],
            "relative_slope_decadal":r["relative_log1p_nest_slope_residual_per_decade"],
            "relative_change_ratio":r["relative_1plus_nest_count_decadal_change_ratio_exploratory"],
            "strict_source_robust":r["robust_source_candidate_status"],
            "same_direction_other_blocks": (
                sign(r["other_block_reference_residual"])==r["relative_direction"]
                if r["other_block_reference_residual"] is not None else None),
            "first_count":r["first_original_observed_nest_count"],
            "last_count":r["last_original_observed_nest_count"]
        } for r in rows]

    report={
        "status":"EXPLORATORY_SOURCE_BACKED_COLONY_RELATIVE_BRIGHT_DARK_SPOTS_COMPLETE",
        "source":{
            "site_denominator_original":595,
            "source_original_fixed_method_count_rows":2456,
            "longitudinal_census_and_ice_trend_unit_count":100,
            "distinct_monitored_colony_sites_in_trends":77,
            "species_trend_site_count":dict(Counter(x["species"] for x in rows)),
            "original_1991_2020_method_consistent_census_year_count":1691,
            "all_100_original_OLS_trends_exactly_reconstructed":True,
            "original_original_climate_trend_source":"GitHub Actions run 42613076334 original gridded 595 site SIC trend output",
        },
        "eligibility":{
            "min_region_species_original_sites":MIN_REGIONAL_SITES,
            "min_distinct_original_250km_blocks":MIN_REGIONAL_BLOCKS,
            "n_original_source_species_region_groups":len(support),
            "n_comparable_region_species_groups":sum(x["eligible_for_species_region_relative_spots"] for x in support),
            "n_original_sites_with_comparable_species_region_peers":len(eligible),
            "n_original_sites_without_comparable_species_region_peers":len(rows)-len(eligible),
            "n_positive_relative_residual":len(bright),
            "n_negative_relative_residual":len(dark),
            "n_strict_robust_relative_bright_candidates":len(robust_bright),
            "n_strict_robust_relative_dark_candidates":len(robust_dark)
        },
        "region_species_support":support,
        "top_10_descriptive_bright":brief(bright[:10]),
        "top_10_descriptive_dark":brief(dark[:10]),
        "top_10_robust_source_bright_candidates":brief(robust_bright[:10]),
        "top_10_robust_source_dark_candidates":brief(robust_dark[:10]),
        "uninterpreted_observational_boundaries":[
            "Relative comparison to leave-one-site-out species-region median, not a model predicting true fitness or local survival.",
            "Region peers selected only by original data support, not study outcome or significance.",
            "No unobserved colony, year or species is treated as actual ecological absence.",
            "The nest-count series reflects surveyed years, not same-year total population or harmonized observation variance.",
            "Site-year irregularity and mixed geography can create apparent outliers despite fixed source count method.",
            "A site with positive relative residual may have declining absolute observed nests and vice versa.",
            "Theil-Sen and endpoint deletion are diagnostic sign checks, not confidence intervals or external replication.",
            "Spatial site IDs and multiple species share climate cells and survey histories; not independent randomized experiments.",
            "No robust relative brightness label establishes a protected refuge, climatic effect, causal mechanism or future persistence.",
        ]
    }
    output.mkdir(parents=True,exist_ok=True)
    savecsv(output/"original_all_100_site_species_relative_spots.csv", sorted(rows,key=lambda x:(x["species"],x["source_region"],x["site_id"])))
    savecsv(output/"original_species_region_support.csv", support)
    savecsv(output/"original_bright_candidate_ranked.csv", bright)
    savecsv(output/"original_dark_candidate_ranked.csv", dark)
    savecsv(output/"source_robust_bright_candidate_ranked.csv", robust_bright)
    savecsv(output/"source_robust_dark_candidate_ranked.csv", robust_dark)
    (output/"BRIGHT_DARK_SPOT_EXPLORATORY_RECEIPT.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("BRIGHT_DARK_SUPPORT="+json.dumps(report["eligibility"],ensure_ascii=False),flush=True)
    print("BRIGHT_DARK_REGIONS="+json.dumps(support,ensure_ascii=False),flush=True)
    print("BRIGHT_DARK_BRIEF="+json.dumps({
        "top_bright":report["top_10_descriptive_bright"][:7],
        "top_dark":report["top_10_descriptive_dark"][:7],
        "robust_bright":report["top_10_robust_source_bright_candidates"][:7],
        "robust_dark":report["top_10_robust_source_dark_candidates"][:7],
    },ensure_ascii=False),flush=True)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-100-trends",required=True,type=Path)
    p.add_argument("--original-census",required=True,type=Path)
    p.add_argument("--original-sites",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    compute(a.original_100_trends,a.original_census,a.original_sites,a.output)


if __name__=="__main__":
    main()
