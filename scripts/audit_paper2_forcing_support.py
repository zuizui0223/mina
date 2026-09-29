#!/usr/bin/env python3
"""Outcome-blind forcing-support audit helpers for Paper 2 Gate 2C."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd
import pyreadr


MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
SPECIES = ("ADPE", "CHPE", "GEPE")
EXPECTED_GATE0 = {"ADPE": 57, "CHPE": 46, "GEPE": 49}
EXPECTED_BRIDGED = {"ADPE": 44, "CHPE": 34, "GEPE": 29}
WINDOW = (1980, 2025)


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


def select_modeling_level(
    level_summaries: dict[str, dict],
    unit_ids: set[str],
    min_coverage: float = 0.95,
) -> dict:
    """Choose the finest estimable multi-group level for the coupling model."""
    target = {str(v) for v in unit_ids}
    if not target:
        return {
            "level": None,
            "coverage_fraction": 0.0,
            "qualifying_groups": [],
            "covered_units": [],
            "excluded_units": [],
        }

    for level in ("apbp_region", "ccamlr"):
        groups = [
            g for g in level_summaries.get(level, {}).get("groups", [])
            if g.get("qualifies")
        ]
        covered = {
            str(v)
            for group in groups
            for v in group.get("unit_ids", [])
        }
        fraction = len(covered & target) / len(target)
        if fraction >= min_coverage and len(groups) >= 2:
            return {
                "level": level,
                "coverage_fraction": fraction,
                "qualifying_groups": [str(g.get("group")) for g in groups],
                "covered_units": sorted(covered & target),
                "excluded_units": sorted(target - covered),
            }

    sw_groups = level_summaries.get("species_wide", {}).get("groups", [])
    if len(sw_groups) == 1 and sw_groups[0].get("qualifies"):
        return {
            "level": "species_wide",
            "coverage_fraction": 1.0,
            "qualifying_groups": [str(sw_groups[0].get("group"))],
            "covered_units": sorted(target),
            "excluded_units": [],
        }

    return {
        "level": None,
        "coverage_fraction": 0.0,
        "qualifying_groups": [],
        "covered_units": [],
        "excluded_units": sorted(target),
    }



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
        modeling = select_modeling_level(levels, target, 0.95)
        species_result[species_id] = {
            "n_units": len(target),
            "selected_level": selected,
            "modeling_eligibility": modeling,
            "levels": levels,
        }

    return {
        "window": [start, end],
        "species": species_result,
    }



def _load_rda(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        value = result[expected]
    elif len(result) == 1:
        value = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(value, pd.DataFrame):
        raise TypeError(expected)
    return value


def _clean_label(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def build_frozen_unit_rows(
    obs: pd.DataFrame,
    sites: pd.DataFrame,
) -> list[dict]:
    """Reconstruct the frozen 107 units and discard count magnitudes immediately."""
    nest = obs[
        obs["species_id"].isin(SPECIES)
        & (obs["type"] == "nests")
        & obs["count"].notna()
    ].copy()
    nest["year"] = pd.to_numeric(nest["year"], errors="coerce")
    nest["season"] = pd.to_numeric(nest["season"], errors="coerce")

    candidates: list[tuple[str, str]] = []
    for (site_id, species_id), local in nest.dropna(subset=["year"]).groupby(
        ["site_id", "species_id"]
    ):
        years = sorted({int(v) for v in local["year"]})
        if len(years) >= 5 and max(years) - min(years) >= 10:
            candidates.append((str(site_id), str(species_id)))

    gate0_by_species = {
        sp: sum(species_id == sp for _, species_id in candidates)
        for sp in SPECIES
    }
    if gate0_by_species != EXPECTED_GATE0:
        raise ValueError(f"Gate0 species drift: {gate0_by_species} != {EXPECTED_GATE0}")

    grouped = {
        (str(site_id), str(species_id)): local
        for (site_id, species_id), local in nest.groupby(["site_id", "species_id"])
    }
    start, end = WINDOW
    first, _, last = _thirds(start, end)
    bridged: list[tuple[str, str, list[int]]] = []
    for site_id, species_id in candidates:
        local = grouped[(site_id, species_id)]
        seasons = sorted(
            {
                int(v)
                for v in pd.to_numeric(local["season"], errors="coerce").dropna()
                if start <= int(v) <= end
            }
        )
        n = len(seasons)
        span = max(seasons) - min(seasons) if seasons else 0
        has_first = any(first[0] <= v <= first[1] for v in seasons)
        has_last = any(last[0] <= v <= last[1] for v in seasons)
        if n >= 5 and span >= 10 and has_first and has_last:
            bridged.append((site_id, species_id, seasons))

    validate_frozen_cohort(len(candidates), len(bridged))
    bridged_by_species = {
        sp: sum(species_id == sp for _, species_id, _ in bridged)
        for sp in SPECIES
    }
    if bridged_by_species != EXPECTED_BRIDGED:
        raise ValueError(
            f"bridged species drift: {bridged_by_species} != {EXPECTED_BRIDGED}"
        )

    meta = sites.copy()
    meta["site_id"] = meta["site_id"].astype(str)
    meta = meta.set_index("site_id")

    rows: list[dict] = []
    for site_id, species_id, seasons in bridged:
        if site_id not in meta.index:
            raise ValueError(f"missing site metadata: {site_id}")
        m = meta.loc[site_id]
        rows.append(
            {
                "unit_id": f"{species_id}|{site_id}",
                "site_id": site_id,
                "species_id": species_id,
                "region": _clean_label(m.get("region")),
                "ccamlr_id": _clean_label(m.get("ccamlr_id")),
                "first_observed_season": min(seasons),
                "last_observed_season": max(seasons),
                "n_observed_seasons": len(seasons),
                "seasons": seasons,
            }
        )
    return sorted(rows, key=lambda r: (r["species_id"], r["site_id"]))


def audit(root: Path) -> dict:
    data = root / "data"
    obs = _load_rda(data / "penguin_obs.rda", "penguin_obs")
    sites = _load_rda(data / "sites.rda", "sites")
    rows = build_frozen_unit_rows(obs, sites)
    support = summarize_forcing_support(rows, WINDOW[0], WINDOW[1])
    selected = {
        sp: support["species"][sp]["selected_level"]
        for sp in SPECIES
    }
    modeling = {
        sp: support["species"][sp]["modeling_eligibility"]
        for sp in SPECIES
    }
    return {
        "schema_version": 1,
        "audit_id": "mina-paper2-forcing-support-audit-v1",
        "mapppdr_commit": MAPPPDR_COMMIT,
        "primary_time_field": "season",
        "primary_window": list(WINDOW),
        "bridged_site_species_units": len(rows),
        "species_units": {
            sp: sum(r["species_id"] == sp for r in rows)
            for sp in SPECIES
        },
        "support": support,
        "decision": {
            "strict_complete_coverage_level_by_species": selected,
            "modeling_eligibility_by_species": modeling,
            "primary_coupling_units": int(sum(len(v["covered_units"]) for v in modeling.values())),
            "all_species_forcing_identifiable": all(v["level"] is not None for v in modeling.values()),
            "selection_rule": (
                "choose APBP region, else CCAMLR, else species-wide; "
                "a level is selectable only when every frozen unit belongs "
                "to a qualifying group at that level"
            ),
            "no_count_magnitudes_opened": True,
        },
        "unit_rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapppdr-dir", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    args = parser.parse_args()

    result = audit(args.mapppdr_dir)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    json_result = {k: v for k, v in result.items() if k != "unit_rows"}
    args.out_json.write_text(
        json.dumps(json_result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    csv_rows = []
    for row in result["unit_rows"]:
        out = dict(row)
        out["seasons"] = ";".join(str(v) for v in row["seasons"])
        csv_rows.append(out)
    pd.DataFrame(csv_rows).to_csv(args.out_csv, index=False)

    print(json.dumps(json_result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
