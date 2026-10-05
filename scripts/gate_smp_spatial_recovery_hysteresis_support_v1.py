#!/usr/bin/env python3
"""Stage-B state-only support gate for SMP spatial-recovery hysteresis.

Uses only positive/explicit-zero/missing count states on the already-frozen
structural panel roster. Count magnitudes are never retained or emitted.

Each completed vacancy spell is assigned to the maximal calendar-consecutive
complete-year block containing the spell. Only spells in blocks of >=6 years
are eligible for the frozen common circular phase null used at Stage C.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from scripts.audit_smp_macro_support import _count_state
from scripts.gate_smp_master_site_support_v1 import (
    EXPOSED_MASTER,
    SENSITIVE,
    _direct_record_mask,
    _find_column,
    _load,
    _norm,
    _not_merged_mask,
    _whole_colony_mask,
    _year_from_date,
)

MIN_SPELLS = 30
MIN_SITES = 20
MIN_MASTERS = 10
MIN_SPECIES = 5
MIN_SPECIES_3SPELLS = 4
MIN_SPECIES_2MASTERS = 3
MIN_PHASE_BLOCK_YEARS = 6


def _state_frame(
    path: Path,
    *,
    compatible_start_year: int,
    compatible_end_year: int,
    assume_whole_colony_extract: bool = False,
) -> pd.DataFrame:
    df = _load(path)
    species_col = _find_column(df, ["Species"])
    site_id_col = _find_column(df, ["SiteID", "Site ID", "Site code"])
    master_col = _find_column(df, ["MasterSite", "Master Site"])
    method_col = _find_column(df, ["Method"], required=False)
    unit_col = _find_column(df, ["Unit"])
    accuracy_col = _find_column(df, ["Accuracy"])
    estimate_col = _find_column(df, ["Estimate", "Estimate type"], required=False)
    comments_col = _find_column(df, ["Comments", "Comment"], required=False)
    plot_col = _find_column(df, ["Plot", "Plot site name", "Spatial level"], required=False)
    count_col = _find_column(df, ["Count"])
    year_col = _find_column(df, ["Year"], required=False)
    date_col = _find_column(df, ["Start date", "Date", "StartDate"], required=year_col is None)

    year = (
        df[year_col].map(_year_from_date)
        if year_col is not None
        else df[date_col].map(_year_from_date)
    )
    x = df.assign(_year=year)
    x = x[
        x["_year"].between(
            int(compatible_start_year),
            int(compatible_end_year),
            inclusive="both",
        )
    ].copy()

    direct = _direct_record_mask(x, accuracy_col, estimate_col)
    whole = _whole_colony_mask(x, plot_col, assume_whole_colony_extract)
    not_merged = _not_merged_mask(x, comments_col)
    x = x[direct & whole & not_merged].copy()

    x["_species"] = x[species_col].map(_norm)
    x["_master"] = x[master_col].map(lambda z: str(z).strip())
    x["_master_norm"] = x[master_col].map(_norm)
    x["_site_id"] = x[site_id_col].map(lambda z: str(z).strip())
    x["_unit"] = x[unit_col].map(lambda z: str(z).strip())
    x["_method"] = x[method_col].map(lambda z: str(z).strip()) if method_col else ""
    x["year"] = x["_year"].astype(int)
    x["state"] = x[count_col].map(lambda z: _count_state(str(z)))

    x = x[~x["_species"].isin(SENSITIVE)].copy()
    pilot = x["_species"].str.contains("kittiwake", regex=False) & (x["_master_norm"] == EXPOSED_MASTER)
    x = x[~pilot].copy()

    key = ["_species", "_master", "_unit", "_site_id", "year"]
    usable = x[x["state"].isin(["observed_positive", "explicit_zero"])].copy()
    dup = usable.groupby(key, dropna=False).size().rename("_n").reset_index()
    unique = dup[dup["_n"] == 1][key]
    x = x.merge(unique, on=key, how="inner")

    if method_col:
        method_n = (
            x[x["_method"].map(_norm) != ""]
            .groupby(["_species", "_master", "_unit", "_site_id"])["_method"]
            .nunique()
            .rename("_method_n")
            .reset_index()
        )
        x = x.merge(method_n, on=["_species", "_master", "_unit", "_site_id"], how="left")
        x["_method_n"] = x["_method_n"].fillna(0)
        x = x[x["_method_n"] <= 1].copy()

    return x[
        ["_species", "_master", "_master_norm", "_unit", "_site_id", "year", "state"]
    ].copy()


def completed_spells_for_site(years: list[int], states: list[str]) -> list[dict]:
    """Return completed positive -> zero...zero -> positive spells with no year gaps."""
    by = {int(y): str(s) for y, s in zip(years, states)}
    ordered = sorted(by)
    spells = []
    i = 0
    while i < len(ordered) - 1:
        y = ordered[i]
        y1 = ordered[i + 1]
        if y1 != y + 1 or by[y] != "observed_positive" or by[y1] != "explicit_zero":
            i += 1
            continue

        z = y1
        while (z + 1) in by and by[z + 1] == "explicit_zero":
            z += 1

        recol = z + 1
        if recol in by and by[recol] == "observed_positive":
            spells.append(
                {
                    "abandon_from": int(y),
                    "abandon_to": int(y1),
                    "recolonize_from": int(z),
                    "recolonize_to": int(recol),
                    "vacancy_years": int(recol - y1),
                }
            )
            i = ordered.index(recol)
        else:
            i += 1
    return spells


def consecutive_blocks(years: list[int]) -> list[list[int]]:
    vals = sorted({int(y) for y in years})
    if not vals:
        return []
    blocks = [[vals[0]]]
    for y in vals[1:]:
        if y == blocks[-1][-1] + 1:
            blocks[-1].append(y)
        else:
            blocks.append([y])
    return blocks


def containing_block(complete_years: list[int], spell: dict) -> list[int]:
    lo = int(spell["abandon_from"])
    hi = int(spell["recolonize_to"])
    for block in consecutive_blocks(complete_years):
        if lo >= block[0] and hi <= block[-1]:
            return block
    raise ValueError("completed spell not contained in a complete-year block")


def validate_zero_semantics(path: Path) -> dict:
    z = json.loads(path.read_text(encoding="utf-8"))
    required_true = (
        "row_with_direct_count_zero_is_surveyed_nil",
        "absent_site_year_row_is_not_zero",
        "estimated_or_imputed_zero_excluded_from_primary",
    )
    for key in required_true:
        if z.get(key) is not True:
            raise ValueError(f"zero-semantics confirmation failed: {key} must be true")
    source = str(z.get("confirmation_source", "")).strip()
    if not source:
        raise ValueError("zero-semantics confirmation_source must be non-empty")
    return {
        "row_with_direct_count_zero_is_surveyed_nil": True,
        "absent_site_year_row_is_not_zero": True,
        "estimated_or_imputed_zero_excluded_from_primary": True,
        "confirmation_source": source,
    }


def run(
    input_path: Path,
    support_json: Path,
    zero_semantics_json: Path,
    *,
    assume_whole_colony_extract: bool = False,
) -> dict:
    support = json.loads(support_json.read_text(encoding="utf-8"))
    if support.get("analysis_id") != "mina-smp-spatial-recovery-structure-v1":
        raise ValueError("Stage B requires the identity-resolved spatial-recovery structure output")
    if not support.get("decision", {}).get("structural_gate_passed"):
        raise ValueError("identity-resolved structural support gate did not pass")
    zero_semantics = validate_zero_semantics(zero_semantics_json)

    x = _state_frame(
        input_path,
        compatible_start_year=int(zero_semantics["compatible_start_year"]),
        compatible_end_year=int(zero_semantics["compatible_end_year"]),
        assume_whole_colony_extract=assume_whole_colony_extract,
    )
    raw_spells = []
    eligible_spells = []

    for panel in support["eligible_panels"]:
        species = str(panel["species"])
        master = str(panel["master_site"])
        unit = str(panel["unit"])
        roster = {str(v) for v in panel["retained_site_ids"]}
        years = [
            int(v)
            for v in panel["complete_years"]
            if int(zero_semantics["compatible_start_year"])
            <= int(v)
            <= int(zero_semantics["compatible_end_year"])
        ]
        if len(years) < 10:
            continue
        if max(years) - min(years) + 1 < 12:
            continue

        g = x[
            x["_species"].eq(species)
            & x["_master_norm"].eq(_norm(master))
            & x["_unit"].eq(unit)
            & x["_site_id"].isin(roster)
            & x["year"].isin(years)
        ].copy()

        observed_by_year = {
            int(y): set(v["_site_id"].astype(str))
            for y, v in g.groupby("year", sort=True)
        }
        state_complete_years = [
            int(y)
            for y in years
            if observed_by_year.get(int(y), set()) == roster
        ]
        if len(state_complete_years) < 10:
            continue
        if max(state_complete_years) - min(state_complete_years) + 1 < 12:
            continue

        g = g[g["year"].isin(state_complete_years)].copy()

        for site in sorted(roster):
            sg = g[g["_site_id"].eq(site)].sort_values("year")
            spells = completed_spells_for_site(
                sg["year"].astype(int).tolist(),
                sg["state"].astype(str).tolist(),
            )
            for k, sp in enumerate(spells, 1):
                block = containing_block(state_complete_years, sp)
                rec = {
                    "spell_id": f"{species}|{master}|{unit}|{site}|{k}",
                    "species": species,
                    "master_site": master,
                    "unit": unit,
                    "site_id": site,
                    **sp,
                    "state_complete_years": [int(v) for v in state_complete_years],
                    "n_state_complete_years": int(len(state_complete_years)),
                    "state_complete_span_years": int(max(state_complete_years) - min(state_complete_years) + 1),
                    "phase_block_start": int(block[0]),
                    "phase_block_end": int(block[-1]),
                    "phase_block_years": [int(v) for v in block],
                    "phase_block_length": int(len(block)),
                    "phase_null_eligible": bool(len(block) >= MIN_PHASE_BLOCK_YEARS),
                }
                raw_spells.append(rec)
                if rec["phase_null_eligible"]:
                    eligible_spells.append(rec)

    frame = pd.DataFrame(eligible_spells)
    n_spells = int(len(frame))
    n_sites = (
        int(frame[["species", "master_site", "site_id"]].drop_duplicates().shape[0])
        if n_spells else 0
    )
    n_masters = (
        int(frame[["species", "master_site"]].drop_duplicates().shape[0])
        if n_spells else 0
    )
    n_species = int(frame["species"].nunique()) if n_spells else 0
    sp_counts = Counter(frame["species"]) if n_spells else Counter()
    sp_masters = (
        frame.groupby("species")["master_site"].nunique().to_dict()
        if n_spells else {}
    )
    species_3 = sorted([sp for sp, n in sp_counts.items() if n >= 3])
    species_2masters = sorted([sp for sp, n in sp_masters.items() if int(n) >= 2])

    passed = bool(
        n_spells >= MIN_SPELLS
        and n_sites >= MIN_SITES
        and n_masters >= MIN_MASTERS
        and n_species >= MIN_SPECIES
        and len(species_3) >= MIN_SPECIES_3SPELLS
        and len(species_2masters) >= MIN_SPECIES_2MASTERS
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-smp-spatial-recovery-hysteresis-support-v1",
        "status": "provider_confirmed_state_only_completed_vacancy_spells_with_frozen_phase_blocks",
        "zero_semantics_confirmation": zero_semantics,
        "state_scan_scope": {
            "compatible_start_year": int(zero_semantics["compatible_start_year"]),
            "compatible_end_year": int(zero_semantics["compatible_end_year"]),
            "compatible_record_family_or_era": str(zero_semantics["compatible_record_family_or_era"]),
            "panel_year_rule": "Start from inherited Stage-A complete years inside the provider-confirmed zero-semantics interval, then retain only years with usable direct positive/explicit-zero state for every retained SiteID. Never add years and never convert missingness to zero."
        },
        "raw_completed_spell_count_before_phase_support": int(len(raw_spells)),
        "completed_spells": eligible_spells,
        "support": {
            "phase_eligible_completed_spells": n_spells,
            "distinct_siteids_with_spells": n_sites,
            "mastersites_with_spells": n_masters,
            "species_with_spells": n_species,
            "species_with_at_least_3_spells": species_3,
            "species_with_spells_in_at_least_2_mastersites": species_2masters,
        },
        "thresholds": {
            "minimum_phase_block_years_per_spell": MIN_PHASE_BLOCK_YEARS,
            "minimum_phase_eligible_completed_spells": MIN_SPELLS,
            "minimum_distinct_siteids_with_spells": MIN_SITES,
            "minimum_mastersites_with_spells": MIN_MASTERS,
            "minimum_species_with_spells": MIN_SPECIES,
            "minimum_species_with_at_least_3_spells": MIN_SPECIES_3SPELLS,
            "minimum_species_with_spells_in_at_least_2_mastersites": MIN_SPECIES_2MASTERS,
        },
        "decision": {
            "hysteresis_magnitude_execution_authorized": passed,
            "if_failed": (
                "Stop; do not lower support thresholds, phase-block support, "
                "or bridge missing years."
            ),
        },
        "forbidden_outputs_confirmed_absent": [
            "count magnitudes",
            "panel abundance totals",
            "abandonment abundance",
            "recolonization abundance",
            "hysteresis width H",
            "phase-null H values",
            "E",
            "kappa",
            "gamma",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--support-json", required=True, type=Path)
    p.add_argument("--zero-semantics-json", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()
    result = run(
        a.input,
        a.support_json,
        a.zero_semantics_json,
        assume_whole_colony_extract=a.assume_whole_colony_extract,
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "completed_spells"},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
