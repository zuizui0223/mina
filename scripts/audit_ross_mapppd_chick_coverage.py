#!/usr/bin/env python3
"""Outcome-blind coverage audit for Ross Island MAPPPD chick counts.

This script deliberately does not print or save chick-count magnitudes. It
audits only site/year/date/method coverage needed to decide whether a
three-colony independent late-season state can be defined before opening Ross
individual movement outcomes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr

PINNED_MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
COMPONENTS = {
    "ROYD": ["ROYD"],
    "BIRD": ["BRDN", "BRDM", "BRDS"],
    "CROZ": ["CRZE", "CRZW"],
}
PARENT_NAMES = {
    "ROYD": "Cape Royds",
    "BIRD": "Cape Bird",
    "CROZ": "Cape Crozier",
}


def _load(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        frame = result[expected]
    elif len(result) == 1:
        frame = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected} in {path}")
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(expected)
    return frame


def audit(root: Path) -> dict[str, object]:
    data = root / "data"
    sites = _load(data / "sites.rda", "sites")
    species = _load(data / "species.rda", "species")
    obs = _load(data / "penguin_obs.rda", "penguin_obs")

    common = species["common_name"].fillna("").astype(str).str.lower()
    adelie = species[
        common.str.contains("adel")
        | (
            (species["genus"].astype(str) == "Pygoscelis")
            & (species["species"].astype(str) == "adeliae")
        )
    ]
    if len(adelie) != 1:
        raise ValueError(f"expected one Adelie row, observed {len(adelie)}")
    species_id = adelie.iloc[0]["species_id"]

    site_by_id = dict(
        zip(sites["site_id"].astype(str), sites["site_name"].astype(str))
    )
    parent_ids: dict[str, str] = {}
    for colony, name in PARENT_NAMES.items():
        matches = sites[sites["site_name"].astype(str) == name]
        if len(matches) != 1:
            raise ValueError(
                f"expected one parent site for {colony}={name!r}, observed {len(matches)}"
            )
        parent_ids[colony] = str(matches.iloc[0]["site_id"])

    wanted_ids = {
        component
        for components in COMPONENTS.values()
        for component in components
    } | set(parent_ids.values())
    missing_site_ids = sorted(wanted_ids - set(site_by_id))
    if missing_site_ids:
        raise ValueError(f"missing MAPPPD site ids: {missing_site_ids!r}")

    local = obs[
        obs["site_id"].astype(str).isin(wanted_ids)
        & (obs["species_id"] == species_id)
        & (obs["type"] == "chicks")
        & obs["count"].notna()
    ].copy()
    local["site_id"] = local["site_id"].astype(str)
    local["year_numeric"] = pd.to_numeric(local["year"], errors="coerce")
    local["month_numeric"] = pd.to_numeric(local["month"], errors="coerce")
    local["day_numeric"] = pd.to_numeric(local["day"], errors="coerce")

    # No count magnitudes are exported.
    component: dict[str, object] = {}
    for sid in sorted(wanted_ids):
        x = local[local["site_id"] == sid]
        years = sorted(set(int(v) for v in x["year_numeric"].dropna()))
        per_year = x.groupby("year_numeric", dropna=True).size().to_dict()
        months = sorted(set(int(v) for v in x["month_numeric"].dropna()))
        component[sid] = {
            "site_name": site_by_id[sid],
            "n_records": int(len(x)),
            "year_min": min(years) if years else None,
            "year_max": max(years) if years else None,
            "distinct_years": len(years),
            "months_observed": months,
            "records_per_year": {
                str(int(k)): int(v) for k, v in sorted(per_year.items())
            },
            "vantage_values": sorted(
                set(str(v) for v in x["vantage"].dropna().unique())
            ),
            "accuracy_values": sorted(
                set(str(v) for v in x["accuracy"].dropna().unique())
            ),
        }

    # A site-year is source-unambiguous only with exactly one finite record.
    unambiguous: dict[str, set[int]] = {}
    ambiguous: dict[str, list[int]] = {}
    for sid in sorted(wanted_ids):
        x = local[local["site_id"] == sid]
        counts = x.groupby("year_numeric", dropna=True).size()
        unambiguous[sid] = {
            int(year) for year, n in counts.items() if int(n) == 1
        }
        ambiguous[sid] = sorted(
            int(year) for year, n in counts.items() if int(n) > 1
        )

    colony_complete: dict[str, list[int]] = {}
    for colony, components in COMPONENTS.items():
        years = None
        for sid in components:
            years = (
                set(unambiguous[sid])
                if years is None
                else years & unambiguous[sid]
            )
        colony_complete[colony] = sorted(years or [])

    component_common = (
        set(colony_complete["ROYD"])
        & set(colony_complete["BIRD"])
        & set(colony_complete["CROZ"])
    )
    component_mark_window = sorted(
        y for y in component_common if 1996 <= y <= 2012
    )

    parent_complete: dict[str, list[int]] = {}
    parent_ambiguous: dict[str, list[int]] = {}
    for colony, sid in parent_ids.items():
        x = local[local["site_id"] == sid]
        counts = x.groupby("year_numeric", dropna=True).size()
        parent_complete[colony] = sorted(
            int(year) for year, n in counts.items() if int(n) == 1
        )
        parent_ambiguous[colony] = sorted(
            int(year) for year, n in counts.items() if int(n) > 1
        )
    parent_common = (
        set(parent_complete["ROYD"])
        & set(parent_complete["BIRD"])
        & set(parent_complete["CROZ"])
    )
    parent_mark_window = sorted(
        y for y in parent_common if 1996 <= y <= 2012
    )

    return {
        "schema_version": 1,
        "audit_id": "mina-ross-mapppd-chick-coverage-v1",
        "mapppdr_commit": PINNED_MAPPPDR_COMMIT,
        "movement_behavioral_rows_read": 0,
        "chick_count_magnitudes_exported": False,
        "species_id": str(species_id),
        "site_coverage": component,
        "parent_site_ids": parent_ids,
        "ambiguous_component_years": ambiguous,
        "component_complete_years_by_colony": colony_complete,
        "component_common_complete_years_all_three": sorted(component_common),
        "component_common_prior_performance_years_1996_2012": component_mark_window,
        "n_component_common_prior_performance_years_1996_2012": len(component_mark_window),
        "parent_ambiguous_years": parent_ambiguous,
        "parent_complete_years_by_colony": parent_complete,
        "parent_common_complete_years_all_three": sorted(parent_common),
        "parent_common_prior_performance_years_1996_2012": parent_mark_window,
        "n_parent_common_prior_performance_years_1996_2012": len(parent_mark_window),
        "component_three_colony_coverage_gate": bool(len(component_mark_window) >= 8),
        "parent_three_colony_coverage_gate": bool(len(parent_mark_window) >= 8),
        "three_colony_coverage_gate": bool(
            len(component_mark_window) >= 8 or len(parent_mark_window) >= 8
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.mapppdr_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
