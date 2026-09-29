#!/usr/bin/env python3
"""Outcome-blind forcing-support audit for Paper 2 Gate 2C."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd
import pyreadr

MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
SPECIES = ("ADPE", "CHPE", "GEPE")
WINDOW = (1980, 2025)
EXPECTED_GATE0 = {"ADPE": 57, "CHPE": 46, "GEPE": 49}
EXPECTED_GATE0_TOTAL = 152
EXPECTED_BRIDGED_TOTAL = 107


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
    covered_seasons_ge50 = (
        sum(v >= coverage_threshold for v in covered_by_season.values())
        if coverage_threshold
        else 0
    )

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


def validate_frozen_cohort(gate0_total: int, bridged_total: int) -> None:
    if gate0_total != EXPECTED_GATE0_TOTAL:
        raise ValueError(
            f"Gate0 cohort drift: {gate0_total} != {EXPECTED_GATE0_TOTAL}"
        )
    if bridged_total != EXPECTED_BRIDGED_TOTAL:
        raise ValueError(
            f"season cohort drift: {bridged_total} != {EXPECTED_BRIDGED_TOTAL}"
        )


def _label(value) -> str | None:
    if pd.isna(value):
        return None
    value = str(value).strip()
    if not value or value.lower() in {"nan", "none", "na"}:
        return None
    return value


def _level_summary(
    rows: list[dict],
    label_field: str | None,
    start: int,
    end: int,
) -> dict:
    missing = 0
    grouped: dict[str, dict[str, list[int]]] = {}
    for row in rows:
        if label_field is None:
            label = "ALL"
        else:
            label = _label(row.get(label_field))
            if label is None:
                missing += 1
                continue
        grouped.setdefault(label, {})[str(row["unit_id"])] = list(row["seasons"])

    groups = []
    for label in sorted(grouped):
        unit_seasons = grouped[label]
        support = evaluate_group(unit_seasons, start, end)
        groups.append(
            {
                "group": label,
                "unit_ids": sorted(unit_seasons),
                **support,
            }
        )
    return {
        "missing_label_units": missing,
        "groups": groups,
    }


def summarize_forcing_support(
    rows: list[dict],
    start: int = WINDOW[0],
    end: int = WINDOW[1],
) -> dict:
    """Summarize support using only identities, geography, seasons and record presence."""
    species_result = {}
    for species_id in sorted({str(r["species_id"]) for r in rows}):
        local = sorted(
            (r for r in rows if str(r["species_id"]) == species_id),
            key=lambda r: str(r["unit_id"]),
        )
        unit_ids = {str(r["unit_id"]) for r in local}
        levels = {
            "apbp_region": _level_summary(local, "region", start, end),
            "ccamlr": _level_summary(local, "ccamlr_id", start, end),
            "species_wide": _level_summary(local, None, start, end),
        }
        species_result[species_id] = {
            "n_units": len(unit_ids),
            "levels": levels,
            "selected_level": select_level(levels, unit_ids),
        }

    return {
        "primary_window": [start, end],
        "species": species_result,
        "selection_order": ["apbp_region", "ccamlr", "species_wide"],
        "no_demographic_magnitudes_opened": True,
    }


def _load_rda(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        frame = result[expected]
    elif len(result) == 1:
        frame = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(expected)
    return frame


def build_frozen_cohort(root: Path) -> tuple[list[dict], pd.DataFrame]:
    """Rebuild Gate 0 and the frozen 1980-2025 breeding-season cohort."""
    sites = _load_rda(root / "data" / "sites.rda", "sites")
    obs = _load_rda(root / "data" / "penguin_obs.rda", "penguin_obs")

    # Count values are used only as missing/non-missing eligibility flags here.
    # The magnitude column is discarded immediately after this filter.
    nest = obs[
        obs["species_id"].isin(SPECIES)
        & (obs["type"] == "nests")
        & obs["count"].notna()
    ][["site_id", "species_id", "year", "season"]].copy()
    nest["year"] = pd.to_numeric(nest["year"], errors="coerce")
    nest["season"] = pd.to_numeric(nest["season"], errors="coerce")

    gate0_units: list[tuple[str, str]] = []
    for (site_id, species_id), local in nest.dropna(subset=["year"]).groupby(
        ["site_id", "species_id"]
    ):
        years = sorted({int(v) for v in local["year"]})
        if len(years) >= 5 and max(years) - min(years) >= 10:
            gate0_units.append((str(site_id), str(species_id)))

    gate0_by_species = pd.Series(
        [species_id for _, species_id in gate0_units], dtype="object"
    ).value_counts().to_dict()
    observed_gate0 = {
        sp: int(gate0_by_species.get(sp, 0))
        for sp in SPECIES
    }
    if observed_gate0 != EXPECTED_GATE0:
        raise ValueError(f"Gate0 species drift: {observed_gate0} != {EXPECTED_GATE0}")

    start, end = WINDOW
    first, _, last = _thirds(start, end)
    grouped = {
        (str(site), str(sp)): local
        for (site, sp), local in nest.groupby(["site_id", "species_id"])
    }

    site_meta = sites.copy()
    site_meta["site_id"] = site_meta["site_id"].astype(str)
    site_meta = site_meta.set_index("site_id")

    rows: list[dict] = []
    for site_id, species_id in sorted(gate0_units):
        local = grouped[(site_id, species_id)]
        seasons = sorted(
            {
                int(v)
                for v in local["season"].dropna()
                if start <= int(v) <= end
            }
        )
        span = max(seasons) - min(seasons) if seasons else 0
        has_first = any(first[0] <= v <= first[1] for v in seasons)
        has_last = any(last[0] <= v <= last[1] for v in seasons)
        bridged = (
            len(seasons) >= 5
            and span >= 10
            and has_first
            and has_last
        )
        if not bridged:
            continue

        meta = site_meta.loc[site_id]
        rows.append(
            {
                "unit_id": f"{species_id}|{site_id}",
                "site_id": site_id,
                "species_id": species_id,
                "region": _label(meta.get("region")),
                "ccamlr_id": _label(meta.get("ccamlr_id")),
                "seasons": seasons,
                "n_observed_seasons": len(seasons),
                "first_observed_season": min(seasons),
                "last_observed_season": max(seasons),
            }
        )

    validate_frozen_cohort(len(gate0_units), len(rows))
    unit_frame = pd.DataFrame(
        [
            {
                k: v
                for k, v in row.items()
                if k != "seasons"
            }
            for row in rows
        ]
    )
    return rows, unit_frame


def audit(root: Path) -> tuple[dict, pd.DataFrame]:
    rows, unit_frame = build_frozen_cohort(root)
    support = summarize_forcing_support(rows, *WINDOW)
    result = {
        "schema_version": 1,
        "audit_id": "mina-paper2-forcing-support-audit-v1",
        "mapppdr_commit": MAPPPDR_COMMIT,
        "frozen_gate0_units": EXPECTED_GATE0_TOTAL,
        "bridged_site_species_units": EXPECTED_BRIDGED_TOTAL,
        "primary_time_field": "season",
        **support,
        "decision": {
            sp: details["selected_level"]
            for sp, details in support["species"].items()
        },
    }
    return result, unit_frame


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    args = parser.parse_args()

    result, unit_frame = audit(args.mapppdr_dir)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    unit_frame.to_csv(args.out_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
