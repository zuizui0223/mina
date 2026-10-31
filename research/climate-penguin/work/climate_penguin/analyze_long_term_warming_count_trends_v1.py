"""Long-term ERA5 warming vs observed Adélie count trends, exploratory only.

Two different trends are estimated per qualifying site from original monthly
ERA5 and MAPPPD counts. No p values, causal attribution or threshold mining.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs/climate_penguin"
COUNT = SOURCE / "historical_count_season_timing.csv"
WINDOWS = (
    ("september_after_september", "all_after_september", [9]),
    ("aug_nov_after_november", "all_after_november", [8, 9, 10, 11]),
)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def linear_slope(years, values):
    """Slope per decade with centered moments, no imputed zero records."""
    if len(years) < 2 or len(years) != len(values):
        return None
    mx, my = statistics.mean(years), statistics.mean(values)
    den = sum((x - mx) ** 2 for x in years)
    if den <= 1e-12:
        return None
    return 10 * sum((x - mx) * (y - my) for x, y in zip(years, values)) / den


def pearson(xs, ys):
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    denx = sum((x - mx) ** 2 for x in xs)
    deny = sum((y - my) ** 2 for y in ys)
    if min(denx, deny) < 1e-18:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(denx * deny)


def source_count_eligibility(records, flag):
    """Only count support and fixed field metadata determine membership."""
    groups = defaultdict(list)
    for r in records:
        if (
            r["species_id"] != "ADPE"
            or r["method"] in {"unknown", ""} or "|" in r["method"]
            or int(r["n_counts"]) != 1 or int(r["n_methods"]) != 1
            or not r["count"] or float(r["count"]) <= 0
            or r[flag] != "True"
        ):
            continue
        groups[(r["site_id"], r["method"])].append(r)
    candidates = defaultdict(list)
    for (site, method), part in groups.items():
        years = [int(r["season"]) for r in part]
        if len(years) < 8 or max(years) - min(years) < 12 or len(set(years)) != len(years):
            continue
        candidates[site].append((part, method))
    selected = {}
    for site, options in candidates.items():
        options.sort(key=lambda item: (-len(item[0]), -(max(int(r["season"]) for r in item[0]) - min(int(r["season"]) for r in item[0])), item[1]))
        selected[site] = options[0][0]
    return selected


def load_era5(monthly):
    lookup, grids, seen = {}, {}, set()
    assert len(monthly) == 40 * 30 * 12, "incomplete 40-site ERA5 original source"
    for r in monthly:
        site, year, month = r["site_id"], int(r["year"]), int(r["month"])
        assert 1991 <= year <= 2020 and 1 <= month <= 12
        key = (site, year, month)
        assert key not in seen, f"duplicate ERA5 month: {key}"
        seen.add(key)
        lat, lon = float(r["returned_grid_latitude"]), float(r["returned_grid_longitude"])
        assert math.isfinite(lat) and math.isfinite(lon)
        g = f"{lat:.6f}|{lon:.6f}"
        if site in grids:
            assert grids[site] == g, f"site changed ERA5 cell: {site}"
        grids[site] = g
        v = float(r["air2m_mean_c"]) if r["complete_month"] == "True" and r["air2m_mean_c"] else None
        if v is not None:
            assert math.isfinite(v) and -100 < v < 50
        lookup[key] = v
    assert len(grids) == 40
    return lookup, grids


def site_slope_records(counts, lookup, grids, window):
    label, flag, months = window
    chosen = source_count_eligibility(counts, flag)
    out = []
    for site, part in sorted(chosen.items()):
        years = sorted(int(r["season"]) for r in part)
        first, last = years[0], years[-1]
        dlog = linear_slope(
            [int(r["season"]) for r in part],
            [math.log(float(r["count"])) for r in part],
        )
        temperature_years, temperature_values = [], []
        for year in range(first, last + 1):
            vals = [lookup.get((site, year, month)) for month in months]
            if all(v is not None for v in vals):
                temperature_years.append(year)
                temperature_values.append(statistics.mean(vals))
        full_years = last - first + 1
        if len(temperature_years) < 12 or len(temperature_years) / full_years < .8:
            # Climate source missing; do not substitute a different site/grid.
            continue
        dtemp = linear_slope(temperature_years, temperature_values)
        # A common 1991–2020 climate window avoids cross-site trend-window
        # mismatch, but may include climate years after a site's count series.
        # Therefore it is a post-result DIAGNOSTIC, not an ecological exposure.
        fixed_years, fixed_values = [], []
        for year in range(1991, 2021):
            vals = [lookup.get((site, year, month)) for month in months]
            if all(v is not None for v in vals):
                fixed_years.append(year)
                fixed_values.append(statistics.mean(vals))
        assert len(fixed_years) >= 25, "Original 30-year ERA5 climate support unavailable"
        fixed_dtemp = linear_slope(fixed_years, fixed_values)
        assert dlog is not None and dtemp is not None and fixed_dtemp is not None
        out.append({
            "analysis": label,
            "site_id": site, "region": part[0]["region"], "method": part[0]["method"],
            "era5_grid_id": grids[site],
            "n_count_seasons": len(part), "n_climate_years": len(temperature_years),
            "start": first, "end": last,
            "count_log_slope_per_decade": dlog,
            "temperature_c_slope_per_decade": dtemp,
            "fixed_1991_2020_temperature_c_slope_per_decade": fixed_dtemp,
        })
    return out


def association(rows, temperature_key="temperature_c_slope_per_decade"):
    if len(rows) < 3:
        return {"n_sites": len(rows), "association": None}
    xs = [r[temperature_key] for r in rows]
    ys = [r["count_log_slope_per_decade"] for r in rows]
    g = defaultdict(list)
    for r in rows:
        g[r["era5_grid_id"]].append(r)
    grids = [{
        "grid_id": key,
        "x": statistics.mean(r[temperature_key] for r in group),
        "y": statistics.mean(r["count_log_slope_per_decade"] for r in group),
        "sites": len(group),
    } for key, group in sorted(g.items())]
    r_cent = defaultdict(list)
    for z in rows:
        r_cent[z["region"]].append(z)
    xcenter, ycenter = [], []
    for region, group in r_cent.items():
        a = statistics.mean(z[temperature_key] for z in group)
        b = statistics.mean(z["count_log_slope_per_decade"] for z in group)
        for z in group:
            xcenter.append(z[temperature_key] - a)
            ycenter.append(z["count_log_slope_per_decade"] - b)
    jackknife = []
    for grid in g:
        other = [z for z in rows if z["era5_grid_id"] != grid]
        c = pearson([z[temperature_key] for z in other],
                    [z["count_log_slope_per_decade"] for z in other])
        if c is not None:
            jackknife.append(c)
    return {
        "n_sites": len(rows),
        "n_era5_grids": len(grids),
        "regions": dict(sorted((k, len(v)) for k, v in r_cent.items())),
        "by_region_pearson_r": {
            region: pearson([z[temperature_key] for z in group],
                            [z["count_log_slope_per_decade"] for z in group])
            for region, group in sorted(r_cent.items())
        },
        "climate_exposure_key": temperature_key,
        "warming_positive_sites": sum(x > 0 for x in xs),
        "count_trend_positive_sites": sum(y > 0 for y in ys),
        "median_warming_c_decade": statistics.median(xs),
        "median_log_count_trend_decade": statistics.median(ys),
        "site_pearson_r": pearson(xs, ys),
        "within_region_centered_pearson_r": pearson(xcenter, ycenter),
        "equal_grid_pearson_r": pearson([z["x"] for z in grids], [z["y"] for z in grids]),
        "leave_one_grid_out_r_range": [min(jackknife), max(jackknife)] if jackknife else None,
        "macro_generalization_gate": {
            "minimum_source_regions": 3,
            "minimum_outside_victoria_sites": 5,
            "minimum_unique_climate_grids": 10,
            "pass": len(r_cent) >= 3 and
                sum(z["region"] != "Victoria Land" for z in rows) >= 5 and
                len(grids) >= 10,
        },
        "no_inference": "No p values or inferential intervals; association is not a causal warming effect.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--era5-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    original = args.era5_dir / "era5_monthly_1991_2020.csv"
    counts = read_csv(COUNT)
    climate = read_csv(original)
    lookup, grids = load_era5(climate)
    assert len(grids) == 40
    outputs = {}
    parts = []
    for window in WINDOWS:
        selected = source_count_eligibility(counts, window[1])
        cohort = site_slope_records(counts, lookup, grids, window)
        assert len(cohort) == len(selected), "eligible count series missing original climate support"
        result = association(cohort)
        # Same fixed original dataset and same count rosters: this is an
        # explicit, non-confirmatory window-alignment sensitivity analysis.
        result["fixed_1991_2020_climate_window_sensitivity"] = association(
            cohort,
            temperature_key="fixed_1991_2020_temperature_c_slope_per_decade",
        )
        result["source_eligible_sites"] = len(selected)
        outputs[window[0]] = result
        parts += cohort
    # Frozen support-only check from the source-structure audit before this model.
    assert (len(parts), outputs[WINDOWS[0][0]]["n_sites"],
            outputs[WINDOWS[1][0]]["n_sites"]) == (31, 16, 15)
    assert outputs[WINDOWS[0][0]]["regions"] == {
        "Central-west Antarctic Peninsula": 2, "Victoria Land": 14}
    assert outputs[WINDOWS[1][0]]["regions"] == {
        "Central-west Antarctic Peninsula": 1, "Victoria Land": 14}
    with (args.output / "warming_long_term_site_trends_v1.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=list(parts[0]))
        writer.writeheader()
        writer.writerows(parts)
    report = {
        "schema": 1, "date": "2026-10-29",
        "status": "post_exploration_observational_not_warming_attribution",
        "ERA5_source_sha256": sha(original),
        "count_source_sha256": sha(COUNT),
        "n_original_count_seasons": len(counts),
        "n_original_ERA5_grids": len(set(grids.values())),
        "effects": outputs,
        "qualifications": [
            "Temperature slope is °C/decade; nest abundance slope is log count/decade.",
            "Time span of temperature trend is aligned with the original count-series span.",
            "Most long-term count cohorts are Victoria Land. Region generality gates FAIL.",
            "Shared ERA5 cells are accounted for descriptively, not as independent replicates.",
            "Nonzero monitored count trends exclude true documented absences.",
            "Cross-site trend association is exploratory and not a warming or colony mechanism effect.",
            "The fixed-window sensitivity can include temperature years AFTER counted seasons, and is NOT a lagged or causal exposure.",
        ],
    }
    (args.output / "warming_long_term_trend_results_v1.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )
    print("WARMING_LONG_TERM_TREND_RECEIPT=" +
          json.dumps(report, ensure_ascii=False, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
