"""Exploratory warming–count link, with support and regional limits explicit.

No anthropogenic attribution, no p-value search, no phenotype recategorization.
The count outcomes and ice screens were seen before the ERA5 exposure retrieval,
so this is NOT independent confirmation of a warming effect.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs/climate_penguin"
PRESET_SCALES = {"air_september": "delta_t_september_c", "air_aug_nov": "delta_t_aug_nov_c"}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def demeaning(values, rows, group_keys):
    """Residualize numeric vector on two potentially unbalanced FE factors."""
    res = values[:]
    for _ in range(500):
        maximum = 0.0
        for col in group_keys:
            groups = defaultdict(list)
            for i, row in enumerate(rows):
                groups[row[col]].append(i)
            for idxs in groups.values():
                mean = statistics.mean(res[i] for i in idxs)
                maximum = max(maximum, abs(mean))
                for i in idxs:
                    res[i] -= mean
        if maximum < 1e-11:
            break
    return res


def slope(rows, x, groups):
    eligible = [r for r in rows if r.get(x) is not None]
    if len(eligible) < 5 or len(set(r["site_id"] for r in eligible)) < 2:
        return None
    xx = demeaning([r[x] for r in eligible], eligible, groups)
    yy = demeaning([r["delta_log_count"] for r in eligible], eligible, groups)
    denominator = sum(v * v for v in xx)
    if denominator < 1e-12:
        return None
    return sum(a * b for a, b in zip(xx, yy)) / denominator


def support_and_effect(rows, x, groups):
    rows = [r for r in rows if r.get(x) is not None]
    site_ids = sorted({r["site_id"] for r in rows})
    coefficient = slope(rows, x, groups)
    los = [slope([r for r in rows if r["site_id"] != site], x, groups) for site in site_ids]
    los = sorted(a for a in los if a is not None and math.isfinite(a))
    # Post-outcome source-dependence audit: different sites can use exactly the
    # same ERA5 nearest-grid series. This is not an independent inferential CI.
    grid_ids = sorted({r.get("era5_grid_id", r["site_id"]) for r in rows})
    log = [
        slope([r for r in rows if r.get("era5_grid_id", r["site_id"]) != grid], x, groups)
        for grid in grid_ids
    ]
    log = sorted(a for a in log if a is not None and math.isfinite(a))
    return {
        "n_intervals": len(rows),
        "n_sites": len(site_ids),
        "n_era5_grid_clusters": len(grid_ids),
        "n_grid_omission_estimable": len(log),
        "leave_one_era5_grid_out_range": [round(log[0], 8), round(log[-1], 8)] if log else None,
        "n_regions": len({r["region"] for r in rows}),
        "victoria_n": sum(r["region"] == "Victoria Land" for r in rows),
        "model_adjustment": groups,
        "beta_logN_per_1C_change": round(coefficient, 8) if coefficient is not None else None,
        "leave_one_site_out_range": [round(los[0], 8), round(los[-1], 8)] if los else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--era5-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source_era5 = args.era5_dir / "era5_monthly_1991_2020.csv"
    source_count = SOURCE / "historical_count_interval_timing.csv"
    monthly = read_csv(source_era5)
    intervals = read_csv(source_count)
    assert len(intervals) == 301
    assert len(monthly) == 40 * 30 * 12, "Requires full-site source, not a pilot"
    assert len({r["site_id"] for r in monthly}) == 40
    lookup, grids = {}, {}
    for row in monthly:
        key = (row["site_id"], int(row["year"]), int(row["month"]))
        assert key not in lookup
        lookup[key] = float(row["air2m_mean_c"]) if row["complete_month"] == "True" and row["air2m_mean_c"] else None
        # Use the actually returned ERA5 grid, not requested breeding-site
        # coordinates. A repeated site must never migrate between grids.
        lat, lon = float(row["returned_grid_latitude"]), float(row["returned_grid_longitude"])
        assert math.isfinite(lat) and math.isfinite(lon)
        grid_id = f"{lat:.6f}|{lon:.6f}"
        site = row["site_id"]
        if site in grids:
            assert grids[site] == grid_id, f"ERA5 grid mismatch for {site}"
        else:
            grids[site] = grid_id
    assert len(grids) == 40

    joined = []
    for row in intervals:
        sid, start, end = row["site_id"], int(row["start"]), int(row["end"])
        assert end - start == 1
        assert float(row["n_start"]) > 0 and float(row["n_end"]) > 0
        def mean_or_none(year, months):
            vals = [lookup.get((sid, year, m)) for m in months]
            return statistics.mean(vals) if all(v is not None for v in vals) else None
        a9, b9 = mean_or_none(start, [9]), mean_or_none(end, [9])
        a4, b4 = mean_or_none(start, [8, 9, 10, 11]), mean_or_none(end, [8, 9, 10, 11])
        joined.append({
            "site_id": sid, "region": row["region"],
            "era5_grid_id": grids[sid],
            "start_year": start, "end_year": end,
            "both_after_september": row["both_all_after_september"] == "True",
            "both_after_november": row["both_all_after_november"] == "True",
            "delta_log_count": math.log(float(row["n_end"]) / float(row["n_start"])),
            "delta_t_september_c": b9 - a9 if a9 is not None and b9 is not None else None,
            "delta_t_aug_nov_c": b4 - a4 if a4 is not None and b4 is not None else None,
        })
    sep = [r for r in joined if r["both_after_september"]]
    nov = [r for r in joined if r["both_after_november"]]
    assert len(sep) == 203 and len(nov) == 191
    report = {
        "schema": 1,
        "status": "post_outcome_exploratory_not_climate_attribution",
        "source_era5_sha256": sha256(source_era5),
        "source_count_sha256": sha256(source_count),
        "n_era5_grids_all_sites": len(set(grids.values())),
        "grid_omission_audit": "post-result source-dependence sensitivity, not a confidence interval",
        "n_count_intervals": len(joined),
        "n_with_era5_september": sum(r["delta_t_september_c"] is not None for r in joined),
        "n_strict_post_september": len(sep),
        "n_strict_post_november": len(nov),
        "effects": {},
        "interpretation": [
            "Site-season annual air temperature change is short-term weather, NOT attributable climate warming.",
            "Counts describe monitored abundance, NOT breeding success or a random sample of birds.",
            "Most strict intervals fall within Victoria Land; do not generalize to six regions.",
            "Significance/causal inference and a climate change counterfactual are not estimated.",
        ],
    }
    for label, subset, variable in [
        ("september_strict", sep, PRESET_SCALES["air_september"]),
        ("aug_nov_strict", nov, PRESET_SCALES["air_aug_nov"]),
        ("all_descriptive", joined, PRESET_SCALES["air_september"]),
        ("september_victoria", [r for r in sep if r["region"] == "Victoria Land"], PRESET_SCALES["air_september"]),
        ("september_without_victoria", [r for r in sep if r["region"] != "Victoria Land"], PRESET_SCALES["air_september"]),
    ]:
        report["effects"][label] = {
            "site_fixed": support_and_effect(subset, variable, ["site_id"]),
            "site_year_fixed": support_and_effect(subset, variable, ["site_id", "end_year"]),
        }
    with (args.output / "count_temperature_interval_join_v1.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(joined[0]))
        writer.writeheader()
        writer.writerows(joined)
    (args.output / "count_temperature_exploratory_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    print("CLIMATE_COUNT_LINK_RECEIPT=" + json.dumps(report, ensure_ascii=False, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
