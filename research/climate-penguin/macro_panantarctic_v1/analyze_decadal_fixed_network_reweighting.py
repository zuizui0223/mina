#!/usr/bin/env python3
"""Fixed-panel penguin nesting redistribution and sea-ice exposure decomposition.

No missing count is set to zero; no colonization, extinction, individual movement,
ice isopleth velocity, or range boundary is inferred from a fixed observed roster.
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
PERIODS = ((1991, 2000), (2001, 2010), (2011, 2020))
PAIRS = ((0, 1), (1, 2), (0, 2))
MONTHS = {8, 9, 10, 11}
KM_PER_LAT_DEGREE = 111.195
SOURCE_ROOT = Path(__file__).resolve().parent


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def period_index(year: int) -> int | None:
    for i, (start, end) in enumerate(PERIODS):
        if start <= year <= end:
            return i
    return None


def label(i: int) -> str:
    start, end = PERIODS[i]
    return f"{start}-{end}"


def source_data(census: Path, atlas: Path, ice: Path, ice_summary: Path):
    sites_raw = read_csv(atlas)
    counts_raw = read_csv(census)
    monthly = read_csv(ice)
    source = json.loads(ice_summary.read_text(encoding="utf-8"))
    if (len(sites_raw), len(counts_raw), len(monthly)) != (595, 2456, 71400):
        raise ValueError("Frozen 595-site/2456-count/71400-month input drift")
    if source["status"] != "PANANTARCTIC_ORIGINAL_30YR_MONTHLY_SIC_MACRO_SOURCE_COMPLETE":
        raise ValueError("Original satellite SIC source did not complete")
    sites = {r["site_id"]: r for r in sites_raw}
    if len(sites) != 595:
        raise ValueError("Original site IDs not unique")
    for site, meta in sites.items():
        lat = float(meta["latitude"])
        if not -90 <= lat <= -55:
            raise ValueError(f"Invalid site latitude {site}")

    by_site_year: dict[tuple[str, int], dict[int, float | None]] = defaultdict(dict)
    for r in monthly:
        site, year, month = r["site_id"], int(r["year"]), int(r["month"])
        if site not in sites or year not in range(1991, 2021) or month not in MONTHS:
            raise ValueError("Unexpected monthly original SIC record")
        key = (site, year)
        if month in by_site_year[key]:
            raise ValueError(f"Repeated original SIC calendar month {key} {month}")
        if r["source_full_595_site_monthly_support"] == "OK":
            value = float(r["source_25km_buffer_mean_SIC_pct"])
            if not math.isfinite(value) or not 0 <= value <= 100:
                raise ValueError("Original source SIC not in 0-100 percent")
        else:
            value = None
        by_site_year[key][month] = value
    if len(by_site_year) != 595 * 30:
        raise ValueError("Missing original SIC site-years")
    annual: dict[tuple[str, int], float | None] = {}
    for key, months in by_site_year.items():
        if set(months) != MONTHS:
            raise ValueError("Incomplete Aug-Nov month list")
        annual[key] = mean(months.values()) if all(v is not None for v in months.values()) else None

    # Frozen annual ice mean requires ten source-complete years per decade.
    sic: dict[tuple[str, int], float | None] = {}
    sic_years: dict[tuple[str, int], int] = {}
    for site in sites:
        for pi, (start, end) in enumerate(PERIODS):
            vals = [annual[site, y] for y in range(start, end + 1)]
            available = [v for v in vals if v is not None]
            sic_years[site, pi] = len(available)
            sic[site, pi] = mean(available) if len(available) == 10 else None

    observed: dict[tuple[str, str, int], list[tuple[int, int]]] = defaultdict(list)
    seen = set()
    for row in counts_raw:
        site, sp = row["site_id"], row["species"]
        if site not in sites or sp not in SPECIES:
            raise ValueError("Unexpected observed site or focal species")
        year = int(row["season"])
        count = int(row["observed_nest_count"])
        if count < 0:
            raise ValueError("Negative original observed nest count")
        if (site, sp, year) in seen:
            raise ValueError("Duplicate original colony×species×season")
        seen.add((site, sp, year))
        pi = period_index(year)
        if pi is not None:
            observed[site, sp, pi].append((year, count))
    if len(seen) != 2456:
        raise ValueError("Original source count identities drifted")
    return sites, observed, sic, sic_years, source


def matched_rows(sites: dict, observed: dict, sic: dict, pi: int, pj: int,
                 species: str) -> list[dict]:
    result = []
    for site, meta in sorted(sites.items()):
        a = observed.get((site, species, pi), [])
        b = observed.get((site, species, pj), [])
        ice0, ice1 = sic[site, pi], sic[site, pj]
        if not a or not b or ice0 is None or ice1 is None:
            continue
        result.append({
            "site_id": site,
            "species": species,
            "source_region": meta["source_region"],
            "polar_250km_block": meta["polar_250km_fixed_grid_block"],
            "latitude": float(meta["latitude"]),
            "first_window": label(pi),
            "last_window": label(pj),
            "n_original_count_years_early": len(a),
            "n_original_count_years_late": len(b),
            "median_original_count_year_early": median(y for y, _ in a),
            "median_original_count_year_late": median(y for y, _ in b),
            "site_median_observed_nests_early": median(n for _, n in a),
            "site_median_observed_nests_late": median(n for _, n in b),
            "decadal_original_aug_nov_SIC_early_pp": ice0,
            "decadal_original_aug_nov_SIC_late_pp": ice1,
            "source_is_observed_site_not_an_absence": True,
        })
    return result


def decompose(rows: list[dict], pi: int, pj: int) -> dict | None:
    """Symmetric two-factor Kitagawa identity at the same fixed observed sites."""
    n0 = [float(r["site_median_observed_nests_early"]) for r in rows]
    n1 = [float(r["site_median_observed_nests_late"]) for r in rows]
    total0, total1 = sum(n0), sum(n1)
    if len(rows) < 3 or total0 <= 0 or total1 <= 0:
        return None
    w0 = [v / total0 for v in n0]
    w1 = [v / total1 for v in n1]
    s0 = [float(r["decadal_original_aug_nov_SIC_early_pp"]) for r in rows]
    s1 = [float(r["decadal_original_aug_nov_SIC_late_pp"]) for r in rows]
    lats = [float(r["latitude"]) for r in rows]
    exposure0 = sum(a * b for a, b in zip(w0, s0))
    exposure1 = sum(a * b for a, b in zip(w1, s1))
    climate = sum((a + b) * (d - c) / 2 for a, b, c, d in zip(w0, w1, s0, s1))
    redistribution = sum((d - c) * (a + b) / 2 for a, b, c, d in zip(s0, s1, w0, w1))
    if not math.isclose(exposure1 - exposure0, climate + redistribution,
                        rel_tol=1e-11, abs_tol=1e-9):
        raise AssertionError("Exposure climate + redistribution identity failed")
    lat0 = sum(w * lat for w, lat in zip(w0, lats))
    lat1 = sum(w * lat for w, lat in zip(w1, lats))
    shift = (lat0 - lat1) * KM_PER_LAT_DEGREE
    center_separation_years = (mean(PERIODS[pj]) - mean(PERIODS[pi]))
    blocks = {r["polar_250km_block"] for r in rows}
    regions = {r["source_region"] for r in rows}
    # A positive redistribution term offsets negative physical SIC change.
    compensate = redistribution / (-climate) if climate < -1e-9 and redistribution > 0 else None
    return {
        "n_balanced_observed_sites": len(rows),
        "n_original_regions": len(regions),
        "n_polar_250km_blocks": len(blocks),
        "n_sites_with_2plus_count_years_both_periods": sum(
            r["n_original_count_years_early"] >= 2
            and r["n_original_count_years_late"] >= 2 for r in rows),
        "n_effective_count_weighted_sites_early": 1 / sum(v*v for v in w0),
        "n_effective_count_weighted_sites_late": 1 / sum(v*v for v in w1),
        "largest_site_nest_weight_early": max(w0),
        "largest_site_nest_weight_late": max(w1),
        "source_site_median_nest_sum_early": total0,
        "source_site_median_nest_sum_late": total1,
        "weighted_latitude_early_deg": lat0,
        "weighted_latitude_late_deg": lat1,
        "southward_positive_latitudinal_reweighting_km": shift,
        "southward_positive_km_per_nominal_decade": shift * 10 / center_separation_years,
        "weighted_original_SIC_early_pp": exposure0,
        "weighted_original_SIC_late_pp": exposure1,
        "experienced_SIC_change_pp": exposure1 - exposure0,
        "physical_SIC_change_component_pp": climate,
        "count_reweighting_component_pp": redistribution,
        "observational_compensation_fraction": compensate,
        "note": "Within a common sampled-site panel only; no actual dispersal or distribution edge is identified.",
    }


def result_for(rows: list[dict], pi: int, pj: int, scale: str, group: str) -> dict:
    out = {
        "scale": scale, "group": group,
        "start_window": label(pi), "end_window": label(pj),
        "n_paired_sites": len(rows),
        "n_paired_regions": len({r["source_region"] for r in rows}),
        "n_paired_250km_blocks": len({r["polar_250km_block"] for r in rows}),
    }
    core = decompose(rows, pi, pj)
    if core is None:
        out["classification"] = "INSUFFICIENT_THREE_SITES_OR_POSITIVE_NEST_TOTALS"
        return out
    out.update(core)
    out["classification"] = (
        "OBSERVED_FIXED_PANEL_WITH_MULTIREGION_SPATIAL_SUPPORT"
        if out["n_paired_250km_blocks"] >= 5 and out["n_paired_regions"] >= 2
        else "DESCRIPTIVE_ONLY_LIMITED_SPATIAL_SUPPORT"
    )
    # Predefined leave-one-250km-block sensitivity: not a spatial-bootstrap CI.
    jackknife = []
    for block in sorted({r["polar_250km_block"] for r in rows}):
        trial = [r for r in rows if r["polar_250km_block"] != block]
        checked = decompose(trial, pi, pj)
        if checked is not None:
            jackknife.append(checked)
    if jackknife:
        metrics = [
            "southward_positive_latitudinal_reweighting_km",
            "count_reweighting_component_pp",
            "physical_SIC_change_component_pp",
        ]
        out["leave_one_spatial_block_out_range"] = {
            m: [min(v[m] for v in jackknife), max(v[m] for v in jackknife)]
            for m in metrics
        }
        out["n_valid_leave_block_out_recalculations"] = len(jackknife)
    return out


def analyze(census: Path, atlas: Path, ice: Path, ice_summary: Path, output: Path):
    sites, observed, sic, sic_years, source = source_data(census, atlas, ice, ice_summary)
    coverage = []
    for sp in SPECIES:
        for pi in range(3):
            support = [(site, observed[(site, sp, pi)]) for site in sites
                       if observed.get((site, sp, pi))]
            coverage.append({
                "species": sp, "window": label(pi),
                "original_census_rows": sum(len(a) for _, a in support),
                "observed_site_ids": len(support),
                "source_regions": len({sites[site]["source_region"] for site, _ in support}),
                "n_sites_with_complete_10year_SIC": sum(sic[site, pi] is not None for site, _ in support),
                "n_sites_with_2plus_source_census_years": sum(len(a) >= 2 for _, a in support),
            })
    matched = []
    all_results = []
    regions = sorted({r["source_region"] for r in sites.values()})
    for pi, pj in PAIRS:
        for sp in SPECIES:
            rows = matched_rows(sites, observed, sic, pi, pj, sp)
            matched.extend(rows)
            all_results.append(result_for(rows, pi, pj, "all_original_regions", sp))
            for region in regions:
                sub = [r for r in rows if r["source_region"] == region]
                if sub:  # Do not populate empty unobserved region as zero
                    all_results.append(result_for(sub, pi, pj, "within_original_region", sp + "|" + region))
    summary = {
        "status": "FIXED_OBSERVED_COLONY_NETWORK_REWEIGHTING_CALCULATED",
        "method_version": 1,
        "source": {
            "original_ice_status": source["status"],
            "original_ice_years": [1991, 2020],
            "fixed_sites": 595,
            "observed_count_rows": 2456,
            "original_ice_site_months": 71400,
            "ice_aggregation": "Each site's all ten original Aug-Nov annual means in each decade",
            "nest_aggregation": "Within-period median original method-consistent observed nest counts",
            "missing_census_handling": "missing remains missing; true original zero remains zero",
        },
        "decade_census_coverage": coverage,
        "decade_SIC_coverage": [
            {"window": label(pi),
             "sites_with_all_10_original_SIC_years": sum(sic[site, pi] is not None for site in sites),
             "sites_with_fewer_than_10_SIC_years": sum(sic[site, pi] is None for site in sites)}
            for pi in range(3)
        ],
        "continental_balanced_panel_results": [r for r in all_results if r["scale"] == "all_original_regions"],
        "regional_balanced_panel_results": [r for r in all_results if r["scale"] == "within_original_region"],
        "n_matched_source_site_species_pair_records": len(matched),
        "climate_isopleth_velocity": {
            "status": "NOT_IDENTIFIED_FROM_SITE_BUFFER_MEANS",
            "reason": "The 595 colony-centered SIC means are neither a systematic fixed coastline transect nor gridded 60% ice isocontours; no along-coast km-per-decade is computed.",
        },
        "interpretation": [
            "Same observed site IDs are used in both windows, hence neither range edges nor colonization/extinction can be estimated from this matched analysis.",
            "Southward positive km is 111.195 times the change in count-weighted mean latitude, not geodesic coastline movement or individual tracking.",
            "Source-method-consistent counts from separate census years are represented by within-decade medians; comparison is descriptive and not a synchronized Antarctic population census.",
            "All three species are tested under one identical source and period rule; no source absence is manufactured.",
            "Symmetric physical-change plus count-reweighting components add exactly to the change in weighted mean ice; this is an accounting identity, not an identified causal mechanism.",
            "The sea-ice regime need not be preferred by each species; positive compensation is not proof of niche tracking or climate debt.",
            "Site counts, local colony codes, 250km blocks and regional names do not represent independent climate experiments or unbiased true species ranges.",
            "No p-values, SDM suitability, species-level range-edge speeds, or 2050/2100 population forecasts are inferred here.",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "observed_balanced_site_pair_rows.csv", matched)
    write_csv(output / "original_source_decade_coverage.csv", coverage)
    write_csv(output / "regional_fixed_panel_results.csv", summary["regional_balanced_panel_results"])
    (output / "decade_reweighting_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("DECADE_SOURCE_SUPPORT=" + json.dumps(coverage, ensure_ascii=False))
    print("DECADE_FIXED_PANEL_RESULTS=" + json.dumps(summary["continental_balanced_panel_results"], ensure_ascii=False))
    print("DECADE_TOTAL_MATCHED_ROWS=" + str(len(matched)))
    return summary


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--census", type=Path, required=True)
    p.add_argument("--atlas", type=Path, required=True)
    p.add_argument("--ice", type=Path, required=True)
    p.add_argument("--ice-summary", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    analyze(args.census, args.atlas, args.ice, args.ice_summary, args.output)


if __name__ == "__main__":
    main()
