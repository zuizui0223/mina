#!/usr/bin/env python3
"""Frozen Stage-C paired abandonment/recolonization hysteresis test.

Primary support requires both:
1. positive species-balanced hysteresis under a species sign-flip test;
2. observed hysteresis exceeding a structured common-phase null that preserves
   each MasterSite block's multivariate abundance trajectory.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

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


SEED = 20261005
BOOT_B = 9999
RANDOM_SIGN_B = 100000
PHASE_B = 9999


def prepare_count_frame(
    path: Path,
    *,
    assume_whole_colony_extract: bool = False,
) -> pd.DataFrame:
    """Apply the frozen SMP direct-count filters without any trend calculation."""
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
    x = x[x["_year"].between(1986, 2024, inclusive="both")].copy()

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
    x["_count"] = pd.to_numeric(x[count_col], errors="coerce")

    x = x[~x["_species"].isin(SENSITIVE)].copy()
    pilot = x["_species"].str.contains("kittiwake", regex=False) & (
        x["_master_norm"] == EXPOSED_MASTER
    )
    x = x[~pilot].copy()

    if x["_count"].isna().any():
        raise ValueError("Non-numeric or missing direct Count in Stage-C input")
    if (x["_count"] < 0).any():
        raise ValueError("Negative Count values are not allowed")

    key = ["_species", "_master", "_unit", "_site_id", "year"]
    dup_n = x.groupby(key, dropna=False).size().rename("_n").reset_index()
    unique_keys = dup_n[dup_n["_n"] == 1][key]
    x = x.merge(unique_keys, on=key, how="inner")

    if method_col:
        method_n = (
            x[x["_method"].map(_norm) != ""]
            .groupby(["_species", "_master", "_unit", "_site_id"])["_method"]
            .nunique()
            .rename("_method_n")
            .reset_index()
        )
        x = x.merge(
            method_n,
            on=["_species", "_master", "_unit", "_site_id"],
            how="left",
        )
        x["_method_n"] = x["_method_n"].fillna(0)
        x = x[x["_method_n"] <= 1].copy()

    return x[
        ["_species", "_master", "_master_norm", "_unit", "_site_id", "year", "_count"]
    ].copy()



def transition_midpoint(parent_excl_a: float, parent_excl_b: float) -> float:
    return float(0.5 * (np.log1p(parent_excl_a) + np.log1p(parent_excl_b)))


def parent_excluding_site(matrix: pd.DataFrame, site: str, year: int) -> float:
    row = matrix.loc[int(year)].astype(float)
    value = float(row.sum() - float(row.loc[site]))
    if value < 0:
        raise ValueError("negative leave-one-site-out parent abundance")
    return value


def H_from_years(
    matrix: pd.DataFrame,
    site: str,
    abandon_from: int,
    abandon_to: int,
    recolonize_from: int,
    recolonize_to: int,
) -> float:
    ae = transition_midpoint(
        parent_excluding_site(matrix, site, abandon_from),
        parent_excluding_site(matrix, site, abandon_to),
    )
    ac = transition_midpoint(
        parent_excluding_site(matrix, site, recolonize_from),
        parent_excluding_site(matrix, site, recolonize_to),
    )
    return float(ac - ae)


def spell_effect(matrix: pd.DataFrame, site: str, spell: dict) -> dict:
    years = [
        int(spell["abandon_from"]),
        int(spell["abandon_to"]),
        int(spell["recolonize_from"]),
        int(spell["recolonize_to"]),
    ]
    for year in years:
        if year not in matrix.index:
            raise ValueError(f"spell year {year} missing from matrix")
    if site not in matrix.columns:
        raise ValueError(f"spell site {site} missing from matrix")

    ae = transition_midpoint(
        parent_excluding_site(matrix, site, years[0]),
        parent_excluding_site(matrix, site, years[1]),
    )
    ac = transition_midpoint(
        parent_excluding_site(matrix, site, years[2]),
        parent_excluding_site(matrix, site, years[3]),
    )
    return {
        "abandon_state": float(ae),
        "recolonize_state": float(ac),
        "H": float(ac - ae),
    }


def hierarchical_means(frame: pd.DataFrame) -> dict:
    site = (
        frame.groupby(["species", "master_site", "site_id"], as_index=False)["H"]
        .mean()
        .rename(columns={"H": "site_mean_H"})
    )
    master = (
        site.groupby(["species", "master_site"], as_index=False)["site_mean_H"]
        .mean()
        .rename(columns={"site_mean_H": "master_mean_H"})
    )
    species = (
        master.groupby("species", as_index=False)["master_mean_H"]
        .mean()
        .rename(columns={"master_mean_H": "species_mean_H"})
    )
    return {
        "T": float(species["species_mean_H"].mean()),
        "site": site,
        "master": master,
        "species": species,
    }


def sign_flip_test(species_values: np.ndarray) -> dict:
    vals = np.asarray(species_values, float)
    T = float(vals.mean())
    s = len(vals)
    if s <= 20:
        stats = np.asarray(
            [
                float(np.mean(vals * np.asarray(signs, float)))
                for signs in itertools.product((-1.0, 1.0), repeat=s)
            ],
            float,
        )
        p = float(np.sum(stats >= T) / len(stats))
        mode = "exact"
        n = int(len(stats))
    else:
        rng = np.random.default_rng(SEED)
        stats = np.empty(RANDOM_SIGN_B, float)
        for i in range(RANDOM_SIGN_B):
            signs = rng.choice(np.array([-1.0, 1.0]), size=s, replace=True)
            stats[i] = float(np.mean(vals * signs))
        p = float((1 + np.sum(stats >= T)) / (RANDOM_SIGN_B + 1))
        mode = "monte_carlo"
        n = RANDOM_SIGN_B
    return {"mode": mode, "replicates_or_exact_states": n, "one_sided_p": p}


def species_bootstrap(species_values: np.ndarray) -> list[float]:
    vals = np.asarray(species_values, float)
    rng = np.random.default_rng(SEED + 17)
    boot = np.empty(BOOT_B, float)
    for i in range(BOOT_B):
        boot[i] = float(np.mean(rng.choice(vals, size=len(vals), replace=True)))
    return [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]


def build_panel_cache(
    x: pd.DataFrame,
    structural: dict,
    spells: list[dict],
) -> dict:
    panel_map = {
        (str(p["species"]), _norm(p["master_site"]), str(p["unit"])): p
        for p in structural["eligible_panels"]
    }
    needed = {
        (str(sp["species"]), _norm(sp["master_site"]), str(sp["unit"]))
        for sp in spells
    }
    cache = {}
    for key in sorted(needed):
        if key not in panel_map:
            raise ValueError(f"cycle panel not in frozen roster: {key}")
        panel = panel_map[key]
        roster = [str(v) for v in panel["retained_site_ids"]]
        years = [int(v) for v in panel["complete_years"]]
        g = x[
            x["_species"].eq(key[0])
            & x["_master_norm"].eq(key[1])
            & x["_unit"].eq(key[2])
            & x["_site_id"].isin(roster)
            & x["year"].isin(years)
        ].copy()
        mat = (
            g.pivot(index="year", columns="_site_id", values="_count")
            .reindex(index=years, columns=roster)
        )
        if mat.isna().any().any():
            raise ValueError(f"count matrix drift: {key}")
        cache[key] = mat.astype(float)
    return cache


def _shift_year(year: int, block_years: list[int], shift: int) -> int:
    block = [int(v) for v in block_years]
    index = {y: i for i, y in enumerate(block)}
    if int(year) not in index:
        raise ValueError(f"event year {year} outside frozen phase block")
    return int(block[(index[int(year)] + int(shift)) % len(block)])


def shifted_spell_H(
    matrix: pd.DataFrame,
    site: str,
    spell: dict,
    shift: int,
) -> float:
    block = [int(v) for v in spell["phase_block_years"]]
    if len(block) < 6:
        raise ValueError("phase-null spell has block shorter than frozen 6-year minimum")
    years = [
        _shift_year(int(spell["abandon_from"]), block, shift),
        _shift_year(int(spell["abandon_to"]), block, shift),
        _shift_year(int(spell["recolonize_from"]), block, shift),
        _shift_year(int(spell["recolonize_to"]), block, shift),
    ]
    return H_from_years(matrix, site, *years)


def structured_phase_null(
    observed_rows: pd.DataFrame,
    spells: list[dict],
    cache: dict,
    *,
    B: int = PHASE_B,
    seed: int = SEED,
) -> dict:
    rng = np.random.default_rng(int(seed))
    T_obs = hierarchical_means(observed_rows)["T"]

    block_specs = {}
    for sp in spells:
        key = (
            str(sp["species"]),
            _norm(sp["master_site"]),
            str(sp["unit"]),
            int(sp["phase_block_start"]),
            int(sp["phase_block_end"]),
        )
        years = tuple(int(v) for v in sp["phase_block_years"])
        if key in block_specs and block_specs[key] != years:
            raise ValueError("inconsistent frozen phase block metadata")
        block_specs[key] = years

    T_null = np.empty(int(B), float)
    for r in range(int(B)):
        shifts = {
            key: int(rng.integers(0, len(years)))
            for key, years in block_specs.items()
        }
        sim_rows = []
        for sp in spells:
            panel_key = (
                str(sp["species"]),
                _norm(sp["master_site"]),
                str(sp["unit"]),
            )
            block_key = (
                panel_key[0],
                panel_key[1],
                panel_key[2],
                int(sp["phase_block_start"]),
                int(sp["phase_block_end"]),
            )
            H = shifted_spell_H(
                cache[panel_key],
                str(sp["site_id"]),
                sp,
                shifts[block_key],
            )
            sim_rows.append(
                {
                    "species": str(sp["species"]),
                    "master_site": str(sp["master_site"]),
                    "site_id": str(sp["site_id"]),
                    "H": float(H),
                }
            )
        T_null[r] = hierarchical_means(pd.DataFrame(sim_rows))["T"]

    median = float(np.median(T_null))
    p = float((1 + np.sum(T_null >= T_obs)) / (len(T_null) + 1))
    return {
        "resamples": int(B),
        "seed": int(seed),
        "distinct_phase_blocks": int(len(block_specs)),
        "median_T": median,
        "q025": float(np.quantile(T_null, 0.025)),
        "q975": float(np.quantile(T_null, 0.975)),
        "delta_phase_observed_minus_median": float(T_obs - median),
        "upper_tail_p": p,
    }


def run(
    input_path: Path,
    structural_json: Path,
    cycle_json: Path,
    *,
    assume_whole_colony_extract: bool = False,
) -> tuple[dict, pd.DataFrame]:
    structural = json.loads(structural_json.read_text(encoding="utf-8"))
    cycles = json.loads(cycle_json.read_text(encoding="utf-8"))
    if structural.get("analysis_id") != "mina-smp-spatial-recovery-structure-v1":
        raise ValueError("Stage C requires the identity-resolved spatial-recovery structure output")
    if not structural.get("decision", {}).get("structural_gate_passed"):
        raise ValueError("identity-resolved structural gate did not pass")
    zero = cycles.get("zero_semantics_confirmation", {})
    required_zero = (
        "row_with_direct_count_zero_is_surveyed_nil",
        "absent_site_year_row_is_not_zero",
        "estimated_or_imputed_zero_excluded_from_primary",
    )
    if not all(zero.get(k) is True for k in required_zero):
        raise ValueError("Stage C requires provider-confirmed zero semantics from Stage B")
    if not str(zero.get("confirmation_source", "")).strip():
        raise ValueError("Stage C zero-semantics confirmation_source is missing")
    if not cycles.get("decision", {}).get("hysteresis_magnitude_execution_authorized"):
        raise ValueError("state-only hysteresis support gate did not pass")

    spells = list(cycles["completed_spells"])
    x = prepare_count_frame(
        input_path,
        assume_whole_colony_extract=assume_whole_colony_extract,
    )
    cache = build_panel_cache(x, structural, spells)

    rows = []
    for sp in spells:
        key = (str(sp["species"]), _norm(sp["master_site"]), str(sp["unit"]))
        eff = spell_effect(cache[key], str(sp["site_id"]), sp)
        rows.append({**sp, **eff})

    frame = pd.DataFrame(rows)
    hier = hierarchical_means(frame)
    vals = hier["species"]["species_mean_H"].to_numpy(float)
    sign = sign_flip_test(vals)
    ci = species_bootstrap(vals)
    phase = structured_phase_null(frame, spells, cache)

    T = float(hier["T"])
    supported = bool(
        T > 0
        and sign["one_sided_p"] <= 0.05
        and phase["delta_phase_observed_minus_median"] > 0
        and phase["upper_tail_p"] <= 0.05
    )

    result = {
        "schema_version": 1,
        "analysis_id": "mina-smp-spatial-recovery-hysteresis-effect-v1",
        "status": "first_and_only_frozen_magnitude_execution",
        "spell_count": int(len(frame)),
        "macro": {
            "primary_T_species_balanced_mean_H": T,
            "species_count": int(len(vals)),
            "species_positive_H": int(np.sum(vals > 0)),
            "species_sign_flip": sign,
            "species_bootstrap_95": ci,
            "structured_phase_null": phase,
            "supported": supported,
            "site_means": hier["site"].to_dict(orient="records"),
            "master_means": hier["master"].to_dict(orient="records"),
            "species_means": hier["species"].to_dict(orient="records"),
        },
        "decision": {
            "spatial_recovery_hysteresis_supported": supported,
            "requires_species_sign_flip_and_structured_phase_null": True,
        },
        "boundary": [
            "A supported result demonstrates asymmetric spatial recovery at retained SiteIDs, not a unique social mechanism.",
            "The focal SiteID is excluded from surrounding population abundance at observed and shifted transitions.",
            "The structured phase null preserves each block's multivariate abundance trajectory and cross-site covariance while breaking alignment with frozen event dates.",
            "Stable site pairing does not remove time-varying habitat, predator, disturbance, or management confounding.",
            "No first-colonization events enter the primary paired test.",
        ],
    }
    return result, frame


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--structural-json", required=True, type=Path)
    p.add_argument("--cycle-json", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-spells-csv", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()
    result, frame = run(
        a.input,
        a.structural_json,
        a.cycle_json,
        assume_whole_colony_extract=a.assume_whole_colony_extract,
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    frame.to_csv(a.out_spells_csv, index=False)
    print(
        json.dumps(
            {
                "spell_count": result["spell_count"],
                "decision": result["decision"],
                "macro": {
                    k: v
                    for k, v in result["macro"].items()
                    if k not in {"site_means", "master_means", "species_means"}
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
