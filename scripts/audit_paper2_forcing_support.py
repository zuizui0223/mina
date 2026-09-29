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



def validate_frozen_cohort(candidate_units: int, bridged_units: int) -> None:
    """Fail closed if the previously frozen Gate 0 / Gate 2A cohort drifts."""
    if candidate_units != 152:
        raise ValueError(f"Gate0 cohort drift: {candidate_units} != 152")
    if bridged_units != 107:
        raise ValueError(f"bridged cohort drift: {bridged_units} != 107")


def _usable_label(value) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return bool(text and text.lower() not in {"nan", "na", "none"})


def summarize_forcing_support(
    unit_rows: list[dict],
    start: int,
    end: int,
) -> dict:
    """Summarize support metadata without using demographic count magnitudes."""
    rows = sorted(
        unit_rows,
        key=lambda r: (str(r["species_id"]), str(r["unit_id"])),
    )
    species_result: dict[str, dict] = {}

    for species_id in sorted({str(r["species_id"]) for r in rows}):
        local = [r for r in rows if str(r["species_id"]) == species_id]
        target = {str(r["unit_id"]) for r in local}
        levels: dict[str, dict] = {}

        for level, field in (
            ("apbp_region", "region"),
            ("ccamlr", "ccamlr_id"),
        ):
            missing = sum(not _usable_label(r.get(field)) for r in local)
            labels = sorted(
                {
                    str(r[field])
                    for r in local
                    if _usable_label(r.get(field))
                }
            )
            groups = []
            for label in labels:
                members = [r for r in local if str(r.get(field)) == label]
                seasons = {
                    str(r["unit_id"]): [int(v) for v in r.get("seasons", [])]
                    for r in members
                }
                summary = evaluate_group(seasons, start, end)
                groups.append(
                    {
                        "group": label,
                        "unit_ids": sorted(seasons),
                        **summary,
                    }
                )
            qualifying_covered = sorted(
                {
                    unit
                    for g in groups
                    if g["qualifies"]
                    for unit in g["unit_ids"]
                }
            )
            levels[level] = {
                "missing_label_units": int(missing),
                "groups": groups,
                "qualifying_covered_units": qualifying_covered,
                "complete_qualifying_coverage": set(qualifying_covered) == target,
            }

        seasons = {
            str(r["unit_id"]): [int(v) for v in r.get("seasons", [])]
            for r in local
        }
        species_group = {
            "group": species_id,
            "unit_ids": sorted(seasons),
            **evaluate_group(seasons, start, end),
        }
        levels["species_wide"] = {
            "missing_label_units": 0,
            "groups": [species_group],
            "qualifying_covered_units": (
                sorted(target) if species_group["qualifies"] else []
            ),
            "complete_qualifying_coverage": bool(species_group["qualifies"]),
        }

        selected = select_level(levels, target)
        species_result[species_id] = {
            "n_units": len(target),
            "selected_level": selected,
            "levels": levels,
        }

    return {
        "window": [start, end],
        "species": species_result,
    }
