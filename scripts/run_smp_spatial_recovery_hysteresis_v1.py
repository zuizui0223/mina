#!/usr/bin/env python3
"""Frozen Stage-C paired abandonment/recolonization hysteresis test.

Primary support requires both:
1. positive species-balanced observed hysteresis under a species sign-flip test;
2. observed hysteresis exceeding an elapsed-time-matched trajectory-drift null.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.gate_smp_trend_balance_v1 import _prepare_raw
from scripts.gate_smp_master_site_support_v1 import _norm


SEED = 20261005
BOOT_B = 9999
RANDOM_SIGN_B = 100000
DRIFT_B = 20000


def transition_midpoint(parent_excl_a: float, parent_excl_b: float) -> float:
    return float(0.5 * (np.log1p(parent_excl_a) + np.log1p(parent_excl_b)))


def parent_excluding_site(matrix: pd.DataFrame, site: str, year: int) -> float:
    row = matrix.loc[int(year)].astype(float)
    value = float(row.sum() - float(row.loc[site]))
    if value < 0:
        raise ValueError("negative leave-one-site-out parent abundance")
    return value


def H_at_start(matrix: pd.DataFrame, site: str, start: int, gap: int) -> float:
    a0, a1 = int(start), int(start) + 1
    c0, c1 = int(start) + int(gap), int(start) + int(gap) + 1
    for year in (a0, a1, c0, c1):
        if year not in matrix.index:
            raise ValueError(f"pseudo/observed transition year {year} missing")
    ae = transition_midpoint(
        parent_excluding_site(matrix, site, a0),
        parent_excluding_site(matrix, site, a1),
    )
    ac = transition_midpoint(
        parent_excluding_site(matrix, site, c0),
        parent_excluding_site(matrix, site, c1),
    )
    return float(ac - ae)


def spell_effect(matrix: pd.DataFrame, site: str, spell: dict) -> dict:
    start = int(spell["abandon_from"])
    gap = int(spell["transition_gap_years"])
    observed_H = H_at_start(matrix, site, start, gap)
    ae = transition_midpoint(
        parent_excluding_site(matrix, site, int(spell["abandon_from"])),
        parent_excluding_site(matrix, site, int(spell["abandon_to"])),
    )
    ac = transition_midpoint(
        parent_excluding_site(matrix, site, int(spell["recolonize_from"])),
        parent_excluding_site(matrix, site, int(spell["recolonize_to"])),
    )
    if not np.isclose(observed_H, ac - ae):
        raise AssertionError("observed H mismatch")
    return {
        "abandon_state": float(ae),
        "recolonize_state": float(ac),
        "H": float(observed_H),
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


def trajectory_drift_null(
    observed_rows: pd.DataFrame,
    spells: list[dict],
    cache: dict,
    *,
    B: int = DRIFT_B,
    seed: int = SEED,
) -> dict:
    rng = np.random.default_rng(int(seed))
    T_null = np.empty(int(B), float)

    for r in range(int(B)):
        sim_rows = []
        for sp in spells:
            starts = [int(v) for v in sp["pseudo_start_years"]]
            if len(starts) < 3:
                raise ValueError("spell entered Stage C without >=3 frozen pseudo placements")
            start = int(rng.choice(starts))
            key = (str(sp["species"]), _norm(sp["master_site"]), str(sp["unit"]))
            H = H_at_start(
                cache[key],
                str(sp["site_id"]),
                start,
                int(sp["transition_gap_years"]),
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

    T_obs = hierarchical_means(observed_rows)["T"]
    median = float(np.median(T_null))
    p = float((1 + np.sum(T_null >= T_obs)) / (len(T_null) + 1))
    return {
        "simulations": int(B),
        "seed": int(seed),
        "median_T": median,
        "q025": float(np.quantile(T_null, 0.025)),
        "q975": float(np.quantile(T_null, 0.975)),
        "delta_T_observed_minus_median": float(T_obs - median),
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
    if not structural.get("decision", {}).get("structural_gate_passed"):
        raise ValueError("structural gate did not pass")
    if not cycles.get("decision", {}).get("hysteresis_magnitude_execution_authorized"):
        raise ValueError("state-only hysteresis support gate did not pass")

    spells = list(cycles["completed_spells"])
    x = _prepare_raw(
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
    drift = trajectory_drift_null(frame, spells, cache)

    T = float(hier["T"])
    supported = bool(
        T > 0
        and sign["one_sided_p"] <= 0.05
        and drift["delta_T_observed_minus_median"] > 0
        and drift["upper_tail_p"] <= 0.05
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
            "sign_flip": sign,
            "species_bootstrap_95": ci,
            "trajectory_drift_null": drift,
            "supported": supported,
            "site_means": hier["site"].to_dict(orient="records"),
            "master_means": hier["master"].to_dict(orient="records"),
            "species_means": hier["species"].to_dict(orient="records"),
        },
        "decision": {
            "spatial_recovery_hysteresis_supported": supported,
            "requires_both_sign_flip_and_trajectory_drift_null": True,
        },
        "boundary": [
            "A supported result demonstrates history-dependent spatial recovery at retained SiteIDs, not a unique social mechanism.",
            "The focal SiteID is excluded from parent abundance at all observed and pseudo transitions.",
            "The elapsed-time-matched null controls generic parent-abundance drift over the observed vacancy duration.",
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
