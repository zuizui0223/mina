"""Descriptive audit of Palmer LTER island census timing."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

from .lter import ISLANDS


def _parse_date(value: str):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def audit(path: str | Path) -> dict[str, object]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    dates: dict[tuple[int, str], set] = defaultdict(set)
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        value = str(row.get("time", "")).strip()
        try:
            date = _parse_date(value)
        except (ValueError, TypeError):
            continue
        if 1991 <= date.year <= 2017:
            dates[(date.year, island)].add(date)

    multi_date_cells = {
        f"{year}_{island}": sorted(str(x) for x in local)
        for (year, island), local in dates.items()
        if len(local) != 1
    }
    if multi_date_cells:
        raise ValueError(f"multiple census dates within island-year: {multi_date_cells}")

    yearly = []
    pair_diffs = []
    for year in range(1991, 2018):
        if not all((year, island) in dates for island in ISLANDS):
            continue
        local = {
            island: next(iter(dates[(year, island)]))
            for island in ISLANDS
        }
        ordinals = [date.toordinal() for date in local.values()]
        span = max(ordinals) - min(ordinals)
        diffs = {}
        for a, b in combinations(ISLANDS, 2):
            value = abs((local[a] - local[b]).days)
            diffs[f"{a}__{b}"] = value
            pair_diffs.append(value)
        yearly.append(
            {
                "year": year,
                "dates": {island: str(local[island]) for island in ISLANDS},
                "five_island_span_days": span,
                "pairwise_absolute_day_differences": diffs,
            }
        )

    spans = [int(row["five_island_span_days"]) for row in yearly]
    pair_diffs_sorted = sorted(pair_diffs)

    def median(values):
        n = len(values)
        if n == 0:
            return None
        ordered = sorted(values)
        if n % 2:
            return float(ordered[n // 2])
        return float((ordered[n // 2 - 1] + ordered[n // 2]) / 2)

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-census-timing-audit-v1",
        "n_complete_years": len(yearly),
        "yearly": yearly,
        "five_island_span_days": {
            "median": median(spans),
            "max": max(spans) if spans else None,
            "fraction_same_day": (
                sum(x == 0 for x in spans) / len(spans) if spans else None
            ),
            "fraction_within_1_day": (
                sum(x <= 1 for x in spans) / len(spans) if spans else None
            ),
            "fraction_within_3_days": (
                sum(x <= 3 for x in spans) / len(spans) if spans else None
            ),
            "fraction_within_7_days": (
                sum(x <= 7 for x in spans) / len(spans) if spans else None
            ),
        },
        "all_pairwise_day_difference": {
            "n": len(pair_diffs_sorted),
            "median": median(pair_diffs_sorted),
            "max": max(pair_diffs_sorted) if pair_diffs_sorted else None,
            "fraction_same_day": (
                sum(x == 0 for x in pair_diffs_sorted) / len(pair_diffs_sorted)
                if pair_diffs_sorted else None
            ),
            "fraction_within_1_day": (
                sum(x <= 1 for x in pair_diffs_sorted) / len(pair_diffs_sorted)
                if pair_diffs_sorted else None
            ),
            "fraction_within_3_days": (
                sum(x <= 3 for x in pair_diffs_sorted) / len(pair_diffs_sorted)
                if pair_diffs_sorted else None
            ),
        },
        "interpretation_boundary": {
            "descriptive_only": True,
            "small_date_offsets_do_not_rule_out_counting_error": True,
            "large_date_offsets_would_motivate_explicit_timing_sensitivity": True,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--census", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = audit(args.census)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
