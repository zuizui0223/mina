"""Descriptive audit of Palmer LTER island and subcolony census timing."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date, datetime
from itertools import combinations
from pathlib import Path

from .lter import ISLANDS


def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def _median(values: list[int]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    n = len(ordered)
    if n % 2:
        return float(ordered[n // 2])
    return float((ordered[n // 2 - 1] + ordered[n // 2]) / 2)


def _ordinal_to_iso(value: float) -> str:
    # Median can fall halfway between two dates; retain the numeric ordinal
    # separately and use the earlier calendar date only as a display label.
    return str(date.fromordinal(int(value)))


def audit(path: str | Path) -> dict[str, object]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    cell_rows: dict[tuple[int, str], list[date]] = defaultdict(list)
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        value = str(row.get("time", "")).strip()
        try:
            census_date = _parse_date(value)
        except (ValueError, TypeError):
            continue
        if 1991 <= census_date.year <= 2017:
            cell_rows[(census_date.year, island)].append(census_date)

    cells: dict[tuple[int, str], dict[str, object]] = {}
    for (year, island), local in sorted(cell_rows.items()):
        ordinals = [d.toordinal() for d in local]
        unique = sorted(set(local))
        counts = Counter(local)
        modal_n = max(counts.values())
        median_ordinal = float(_median(ordinals))
        cells[(year, island)] = {
            "year": year,
            "island": island,
            "n_colony_rows": len(local),
            "n_unique_dates": len(unique),
            "unique_dates": [str(d) for d in unique],
            "within_island_span_days": max(ordinals) - min(ordinals),
            "modal_date_fraction": modal_n / len(local),
            "median_date_ordinal": median_ordinal,
            "median_date_display": _ordinal_to_iso(median_ordinal),
        }

    complete_years = [
        year
        for year in range(1991, 2018)
        if all((year, island) in cells for island in ISLANDS)
    ]
    yearly = []
    cross_pair_diffs: list[float] = []
    for year in complete_years:
        local = {
            island: float(cells[(year, island)]["median_date_ordinal"])
            for island in ISLANDS
        }
        values = list(local.values())
        diffs = {}
        for a, b in combinations(ISLANDS, 2):
            difference = abs(local[a] - local[b])
            diffs[f"{a}__{b}"] = difference
            cross_pair_diffs.append(difference)
        yearly.append(
            {
                "year": year,
                "median_dates": {
                    island: cells[(year, island)]["median_date_display"]
                    for island in ISLANDS
                },
                "five_island_median_date_span_days": max(values) - min(values),
                "pairwise_absolute_median_date_differences": diffs,
            }
        )

    internal_spans = [
        int(cell["within_island_span_days"]) for cell in cells.values()
    ]
    multi_date = [
        cell for cell in cells.values() if int(cell["n_unique_dates"]) > 1
    ]
    cross_spans = [
        float(row["five_island_median_date_span_days"]) for row in yearly
    ]

    return {
        "schema_version": 2,
        "analysis_id": "mina-palmer-census-timing-audit-v2",
        "n_complete_years": len(complete_years),
        "n_island_year_cells": len(cells),
        "within_island_year_timing": {
            "n_multi_date_cells": len(multi_date),
            "fraction_single_date": (
                sum(span == 0 for span in internal_spans) / len(internal_spans)
                if internal_spans else None
            ),
            "median_span_days": _median(internal_spans),
            "max_span_days": max(internal_spans) if internal_spans else None,
            "multi_date_cells": multi_date,
        },
        "cross_island_median_timing": {
            "yearly": yearly,
            "median_five_island_span_days": _median(cross_spans),
            "max_five_island_span_days": max(cross_spans) if cross_spans else None,
            "pairwise_median_absolute_difference_days": _median(cross_pair_diffs),
            "pairwise_max_absolute_difference_days": (
                max(cross_pair_diffs) if cross_pair_diffs else None
            ),
            "pairwise_fraction_same_median_date": (
                sum(x == 0 for x in cross_pair_diffs) / len(cross_pair_diffs)
                if cross_pair_diffs else None
            ),
            "pairwise_fraction_within_3_days": (
                sum(x <= 3 for x in cross_pair_diffs) / len(cross_pair_diffs)
                if cross_pair_diffs else None
            ),
        },
        "interpretation_boundary": {
            "descriptive_only": True,
            "subcolonies_within_an_island_are_not_always_counted_same_day": True,
            "timing_audit_alone_does_not_rule_out_shared_observer_error": True,
            "date_separated_pair_test_is_required_to_address_same_day_batching": True,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--census", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = audit(args.census)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
