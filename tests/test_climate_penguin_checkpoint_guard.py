"""Read-only science/checkpoint guards for climate-penguin draft PR #206.

Only committed source-support and post-exploration inference *outputs* are read.
These tests do not estimate new ecological effects or imply independence of
repeat site-years, years, colonies or administrative monitoring regions.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKPOINT = REPO / "research" / "climate-penguin"
OUT = CHECKPOINT / "outputs" / "climate_penguin"


def read_csv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def truth(x: str) -> bool:
    assert x in {"True", "False"}, f"Unexpected boolean status: {x!r}"
    return x == "True"


def region_support(rows: list[dict[str, str]], flag: str | None = None) -> dict:
    subset = [r for r in rows if flag is None or truth(r[flag])]
    counts = Counter(r["region"] for r in subset)
    total = len(subset)
    return {
        "intervals": total,
        "sites": len({r["site_id"] for r in subset}),
        "regions": len(counts),
        "by_region": dict(sorted(counts.items())),
        "victoria_share": counts["Victoria Land"] / total if total else None,
        # Descriptive diversity of *interval distribution*, NOT independent
        # region replicates or a sampling-theory effective sample size.
        "inverse_simpson_regions": (
            total**2 / sum(v * v for v in counts.values()) if total else None
        ),
    }


def independent_fdr(p_values: list[float], by: bool) -> list[float]:
    """BH/BY step-up adjustment written independently of statsmodels."""
    m = len(p_values)
    order = sorted(range(m), key=lambda i: p_values[i])
    harmonic = sum(1.0 / k for k in range(1, m + 1)) if by else 1.0
    out = [1.0] * m
    trailing = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        trailing = min(trailing, p_values[i] * m * harmonic / rank, 1.0)
        out[i] = trailing
    return out


def test_complete_snapshot_manifest_file_integrity():
    # Byte-level integrity is intentionally distinct from regenerating
    # excluded external caches or repeating the original scientific fits.
    ledger = json.loads((CHECKPOINT / "SNAPSHOT_MANIFEST.json").read_text())
    assert len(ledger) == 283
    assert len({item["path"] for item in ledger}) == len(ledger)
    for item in ledger:
        rel = Path(item["path"])
        assert not rel.is_absolute() and ".." not in rel.parts
        data = (CHECKPOINT / rel).read_bytes()
        assert len(data) == item["bytes"], item["path"]
        assert hashlib.sha256(data).hexdigest() == item["sha256"], item["path"]


def test_historical_count_timing_nestedness_and_geographical_support():
    rows = read_csv("historical_count_interval_timing.csv")
    assert len(rows) == 301
    assert all(r["species_id"] == "ADPE" for r in rows)
    assert all(truth(r["same_known_method"]) for r in rows)
    assert all(int(r["end"]) == int(r["start"]) + 1 for r in rows)
    assert all(float(r["n_start"]) > 0 and float(r["n_end"]) > 0 for r in rows)
    assert len({(r["site_id"], r["species_id"], r["start"], r["end"]) for r in rows}) == 301
    for r in rows:
        assert not truth(r["both_all_after_november"]) or truth(r["both_all_after_september"])
        assert not truth(r["both_all_after_september"]) or truth(r["both_all_months_known"])

    all_years = region_support(rows)
    september = region_support(rows, "both_all_after_september")
    november = region_support(rows, "both_all_after_november")
    assert (all_years["intervals"], all_years["sites"], all_years["regions"]) == (301, 33, 6)
    assert (september["intervals"], september["sites"], september["regions"]) == (203, 26, 3)
    assert (november["intervals"], november["sites"], november["regions"]) == (191, 23, 3)
    assert all_years["by_region"] == {
        "Adelie Land": 24,
        "Central-west Antarctic Peninsula": 28,
        "Mac. Robertson Land": 10,
        "South Orkney Islands": 2,
        "South Shetland Islands": 48,
        "Victoria Land": 189,
    }
    assert september["by_region"] == {
        "Central-west Antarctic Peninsula": 9,
        "South Shetland Islands": 7,
        "Victoria Land": 187,
    }
    assert november["by_region"] == {
        "Central-west Antarctic Peninsula": 3,
        "South Shetland Islands": 1,
        "Victoria Land": 187,
    }
    for result, numerator, denominator in (
        (all_years, 301**2, 39489),
        (september, 203**2, 35099),
        (november, 191**2, 34979),
    ):
        assert math.isclose(result["inverse_simpson_regions"], numerator / denominator)
    # The timing audit's own scope summary must agree with the original
    # interval-level rows. It cannot silently change the eligible cohort.
    summary = {
        (r["scope"], r["criterion"]): r
        for r in read_csv("historical_count_timing_summary.csv")
    }
    for flag, calculated in (
        ("all_intervals", all_years),
        ("both_all_after_september", september),
        ("both_all_after_november", november),
    ):
        row = summary[("all", flag)]
        assert (int(row["intervals"]), int(row["sites"]), int(row["regions"])) == (
            calculated["intervals"], calculated["sites"], calculated["regions"]
        )


def test_wild_cluster_family_and_independent_bh_by_recalculation():
    rows = read_csv("wild_cluster_sensitivity_results.csv")
    assert len(rows) == 216
    assert Counter(r["status"] for r in rows) == {
        "computed": 214,
        "insufficient_support": 2,
    }
    assert len({
        (r["cohort"], r["species"], r["predictor"], r["time_mode"])
        for r in rows
    }) == 216
    for r in rows:
        if r["status"] != "computed":
            assert not r["p_wild_site"] and not r["p_wild_year"]
            continue
        for group in ("site", "year"):
            n_cluster = int(r["sites"] if group == "site" else r["years"])
            expected_draws = 2**n_cluster if n_cluster <= 12 else 9999
            assert int(float(r[f"weights_{group}"])) == expected_draws
            assert int(float(r[f"valid_weights_{group}"])) == expected_draws
            assert truth(r[f"enumerated_{group}"]) == (n_cluster <= 12)
        assert math.isclose(
            float(r["p_wild_max"]),
            max(float(r["p_wild_site"]), float(r["p_wild_year"])),
            abs_tol=1e-12,
        )
    for group, nominal_count in (("site", 32), ("year", 30), ("max", 9)):
        raw_name = f"p_wild_{group}"
        ps = [float(r[raw_name]) if r[raw_name] else 1.0 for r in rows]
        assert sum(0 < float(r[raw_name]) < 0.05 for r in rows if r[raw_name]) == nominal_count
        for method in ("bh", "by"):
            adjusted = independent_fdr(ps, by=(method == "by"))
            displayed = f"q_wild_{group}_{method}"
            for r, expected in zip(rows, adjusted):
                if not r[raw_name]:
                    assert not r[displayed]
                else:
                    assert math.isclose(float(r[displayed]), expected, abs_tol=1e-11)
            assert not any(float(r[displayed]) < 0.05 for r in rows if r[displayed])


def test_seasonally_heterogeneous_ice_trends_and_duplicate_grid_support():
    # These are ten-year DESCRIPTIVE climate slopes, not climate attribution.
    from collections import defaultdict
    from statistics import median
    monthly = read_csv("macro_monthly_seaice_2011_2020.csv")
    assert len(monthly) == 40 * 10 * 4 * 2 == 3200
    assert all(r["complete_month"] == "True" for r in monthly)
    assert len({
        (r["site_id"], r["year"], r["month"], r["inner_km"])
        for r in monthly
    }) == len(monthly)

    def trend(points):
        xx = [float(r["year"]) for r in points]
        yy = [float(r["sic_mean"]) for r in points]
        mx = sum(xx) / len(xx)
        my = sum(yy) / len(yy)
        return 10 * sum((x - mx) * (y - my) for x, y in zip(xx, yy)) / sum((x - mx)**2 for x in xx)

    grouped = defaultdict(list)
    near = defaultdict(list)
    for row in monthly:
        if row["inner_km"] != "0":
            continue
        grouped[(row["site_id"], int(row["month"]))].append(row)
        near[row["site_id"]].append(row)
    assert len(near) == 40
    expected = {
        8: (36, -3.444180585660246),
        9: (14, +0.4818357683982658),
        10: (31, -0.8400439147722665),
        11: (23, -0.5638232006337889),
    }
    for month, (negatives, midpoint) in expected.items():
        slopes = [trend(grouped[(sid, month)]) for sid in sorted(near)]
        assert all(len(grouped[(sid, month)]) == 10 for sid in near)
        assert sum(v < 0 for v in slopes) == negatives
        assert math.isclose(median(slopes), midpoint, abs_tol=1e-8)

    signatures = defaultdict(list)
    for sid, rows in near.items():
        series = tuple(
            r["sic_mean"] for r in sorted(rows, key=lambda r: (int(r["year"]), int(r["month"])))
        )
        assert len(series) == 40
        signatures[series].append(sid)
    assert len(signatures) == 38
    assert sorted(tuple(sorted(ids)) for ids in signatures.values() if len(ids) > 1) == [
        ("BRDM", "BRDS"), ("LLAN", "PTHO")
    ]


def test_short_overlap_seaice_count_growth_is_not_region_general():
    # Exploration only: changing the aggregation (pooled versus within-site)
    # reverses the sign. Never infer anthropogenic warming causation.
    monthly = read_csv("macro_monthly_seaice_2011_2020.csv")
    september = {
        (r["site_id"], int(r["year"])): float(r["sic_mean"])
        for r in monthly if int(r["month"]) == 9 and int(r["inner_km"]) == 0
    }
    pairs = []
    for r in read_csv("historical_count_interval_timing.csv"):
        start, end = int(r["start"]), int(r["end"])
        if not (2011 <= start and end <= 2020):
            continue
        k0, k1 = (r["site_id"], start), (r["site_id"], end)
        if k0 not in september or k1 not in september:
            continue
        pairs.append({
            "site": r["site_id"],
            "region": r["region"],
            "valid": truth(r["both_all_after_september"]),
            "x": september[k1] - september[k0],
            "y": math.log(float(r["n_end"]) / float(r["n_start"])),
        })
    assert len(pairs) == 76
    strict = [r for r in pairs if r["valid"]]
    assert (len(strict), len({r["site"] for r in strict})) == (61, 16)
    assert sum(r["region"] == "Victoria Land" for r in strict) == 55
    from collections import defaultdict

    def univariate_slope(rows, within_site):
        centered = []
        if within_site:
            groups = defaultdict(list)
            for r in rows:
                groups[r["site"]].append(r)
            for values in groups.values():
                mx = sum(v["x"] for v in values) / len(values)
                my = sum(v["y"] for v in values) / len(values)
                centered.extend((v["x"] - mx, v["y"] - my) for v in values)
        else:
            mx = sum(r["x"] for r in rows) / len(rows)
            my = sum(r["y"] for r in rows) / len(rows)
            centered = [(r["x"] - mx, r["y"] - my) for r in rows]
        return 10 * sum(x * y for x, y in centered) / sum(x * x for x, _ in centered)

    assert math.isclose(univariate_slope(strict, False), 0.02873083794615691, abs_tol=1e-9)
    assert math.isclose(univariate_slope(strict, True), -0.06511999674708197, abs_tol=1e-9)
