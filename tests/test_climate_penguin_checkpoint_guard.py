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


def test_checkpoint_input_sha256_matches_source_manifest():
    manifest = {
        item["path"]: item
        for item in json.loads((CHECKPOINT / "SNAPSHOT_MANIFEST.json").read_text())
    }
    for name in (
        "historical_count_interval_timing.csv",
        "historical_count_timing_summary.csv",
        "wild_cluster_sensitivity_results.csv",
    ):
        rel = "outputs/climate_penguin/" + name
        data = (OUT / name).read_bytes()
        assert rel in manifest
        assert len(data) == manifest[rel]["bytes"]
        assert hashlib.sha256(data).hexdigest() == manifest[rel]["sha256"]


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
