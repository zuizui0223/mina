#!/usr/bin/env python3
"""Outcome-blind forcing-support audit helpers for Paper 2 Gate 2C."""
from __future__ import annotations

import math


def _thirds(start: int, end: int) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    width = end - start + 1
    cut1 = start + (width // 3) - 1
    cut2 = start + (2 * width // 3) - 1
    return (start, cut1), (cut1 + 1, cut2), (cut2 + 1, end)


def evaluate_group(
    unit_seasons: dict[str, list[int]],
    start: int,
    end: int,
) -> dict:
    """Evaluate predeclared temporal support for one candidate forcing group."""
    cleaned = {
        str(unit): sorted({int(s) for s in seasons if start <= int(s) <= end})
        for unit, seasons in unit_seasons.items()
    }
    n_units = len(cleaned)

    observed_by_season = {
        season: sum(season in seasons for seasons in cleaned.values())
        for season in range(start, end + 1)
    }
    observed_seasons_ge3 = sum(v >= 3 for v in observed_by_season.values())

    coverage_threshold = math.ceil(0.5 * n_units) if n_units else 0
    covered_by_season = {}
    for season in range(start, end + 1):
        covered = 0
        for seasons in cleaned.values():
            if seasons and min(seasons) <= season <= max(seasons):
                covered += 1
        covered_by_season[season] = covered
    covered_seasons_ge50 = sum(
        v >= coverage_threshold
        for v in covered_by_season.values()
    ) if coverage_threshold else 0

    first, _, last = _thirds(start, end)
    spanning = 0
    for seasons in cleaned.values():
        has_first = any(first[0] <= s <= first[1] for s in seasons)
        has_last = any(last[0] <= s <= last[1] for s in seasons)
        if has_first and has_last:
            spanning += 1

    qualifies = bool(
        n_units >= 5
        and observed_seasons_ge3 >= 15
        and covered_seasons_ge50 >= 10
        and spanning >= 3
    )
    return {
        "n_units": n_units,
        "observed_seasons_ge3_units": observed_seasons_ge3,
        "coverage_unit_threshold": coverage_threshold,
        "covered_seasons_ge50pct_units": covered_seasons_ge50,
        "spanning_first_last_thirds_units": spanning,
        "qualifies": qualifies,
    }


def select_level(level_summaries: dict[str, dict], unit_ids: set[str]) -> str | None:
    """Choose the finest level whose qualifying groups cover every target unit."""
    target = {str(v) for v in unit_ids}
    for level in ("apbp_region", "ccamlr", "species_wide"):
        groups = level_summaries.get(level, {}).get("groups", [])
        covered: set[str] = set()
        for group in groups:
            if group.get("qualifies"):
                covered.update(str(v) for v in group.get("unit_ids", []))
        if covered == target:
            return level
    return None
