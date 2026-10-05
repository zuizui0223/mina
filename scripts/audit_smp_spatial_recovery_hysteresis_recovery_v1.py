#!/usr/bin/env python3
"""Synthetic recovery audit for the frozen SMP hysteresis dual gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.run_smp_spatial_recovery_hysteresis_v1 import (
    hierarchical_means,
    physical_master_site_sign_flip_test,
    sign_flip_test,
    spell_effect,
    structured_linear_shift_null,
)


SEED = 20261005
N_SPECIES = 5
MASTERS_PER_SPECIES = 2
SITES_PER_MASTER = 3
YEARS = list(range(2000, 2010))
EVENT = {
    "abandon_from": 2001,
    "abandon_to": 2002,
    "recolonize_from": 2004,
    "recolonize_to": 2005,
    "shift_block_start": 2000,
    "shift_block_end": 2009,
    "shift_block_years": YEARS,
    "common_offset_values": [-1, 0, 1, 2, 3, 4],
    "n_common_offsets": 6,
    "linear_shift_null_eligible": True,
}
DATASETS = 40
LINEAR_B = 999


def ar1_noise(rng: np.random.Generator, n: int, phi: float = 0.55, sd: float = 0.08):
    z = np.zeros(n, float)
    eps = rng.normal(0.0, sd, size=n)
    z[0] = eps[0]
    for i in range(1, n):
        z[i] = phi * z[i - 1] + eps[i]
    return z


def make_parent_log(
    rng: np.random.Generator,
    scenario: str,
) -> np.ndarray:
    n = len(YEARS)
    base = 5.0 + ar1_noise(rng, n)

    if scenario == "reversible_stationary":
        return base
    if scenario == "monotonic_drift":
        return base + np.linspace(0.0, 1.5, n)
    if scenario == "aligned_signal_moderate":
        x = base.copy()
        # Recolonization transition is 2004->2005. Put the pulse on both sides
        # of that transition so H reflects a genuine event-aligned state shift.
        x[4:6] += 0.5
        return x
    if scenario == "aligned_signal_strong":
        x = base.copy()
        x[4:6] += 1.0
        return x
    raise ValueError(scenario)


def build_dataset(seed: int, scenario: str):
    rng = np.random.default_rng(seed)
    cache = {}
    spells = []
    observed_rows = []

    for s in range(N_SPECIES):
        species = f"sp{s}"
        for m in range(MASTERS_PER_SPECIES):
            master = f"M{s}-{m}"
            unit = "AON"
            parent_log = make_parent_log(rng, scenario)
            parent = np.maximum(np.expm1(parent_log), 0.0)

            # Three focal SiteIDs share one physical MasterSite trajectory.
            # Each focal count is small relative to the background, so
            # leave-one-site-out parent state is dominated by the shared path.
            data = {"background": parent}
            for j in range(SITES_PER_MASTER):
                data[f"S{j}"] = np.full(len(YEARS), 2.0)
            mat = pd.DataFrame(data, index=YEARS)
            cache[(species, master.casefold(), unit)] = mat

            for j in range(SITES_PER_MASTER):
                site = f"S{j}"
                sp = {
                    "species": species,
                    "master_site": master,
                    "master_site_key": master,
                    "unit": unit,
                    "site_id": site,
                    **EVENT,
                }
                spells.append(sp)
                observed_rows.append({
                    "species": species,
                    "master_site": master,
                    "master_site_key": master,
                    "site_id": site,
                    "H": spell_effect(mat, site, sp)["H"],
                })

    return pd.DataFrame(observed_rows), spells, cache


def evaluate_dataset(seed: int, scenario: str) -> dict:
    observed, spells, cache = build_dataset(seed, scenario)
    hier = hierarchical_means(observed)
    vals = hier["species"]["species_mean_H"].to_numpy(float)
    sign = sign_flip_test(vals)
    master_sign = physical_master_site_sign_flip_test(observed, spells, seed=seed)
    linear = structured_linear_shift_null(
        observed,
        spells,
        cache,
        B=LINEAR_B,
        seed=seed + 1000003,
    )
    T = float(hier["T"])
    supported = bool(
        T > 0
        and sign["one_sided_p"] <= 0.05
        and master_sign["one_sided_p"] <= 0.05
        and linear["delta_linear_observed_minus_median"] > 0
        and linear["upper_tail_p"] <= 0.05
    )
    return {
        "T": T,
        "sign_p": float(sign["one_sided_p"]),
        "master_sign_p": float(master_sign["one_sided_p"]),
        "linear_p": float(linear["upper_tail_p"]),
        "delta_linear": float(linear["delta_linear_observed_minus_median"]),
        "supported": supported,
    }


def run() -> dict:
    scenarios = [
        "reversible_stationary",
        "monotonic_drift",
        "aligned_signal_moderate",
        "aligned_signal_strong",
    ]
    out = {}
    for k, scenario in enumerate(scenarios):
        rows = [
            evaluate_dataset(SEED + k * 100000 + r * 997, scenario)
            for r in range(DATASETS)
        ]
        support_rate = float(np.mean([r["supported"] for r in rows]))
        out[scenario] = {
            "datasets": DATASETS,
            "support_rate": support_rate,
            "median_T": float(np.median([r["T"] for r in rows])),
            "median_sign_p": float(np.median([r["sign_p"] for r in rows])),
            "median_master_sign_p": float(np.median([r["master_sign_p"] for r in rows])),
            "median_linear_p": float(np.median([r["linear_p"] for r in rows])),
            "median_delta_linear": float(np.median([r["delta_linear"] for r in rows])),
        }

    passed = bool(
        out["reversible_stationary"]["support_rate"] <= 0.15
        and out["monotonic_drift"]["support_rate"] <= 0.15
        and out["aligned_signal_strong"]["support_rate"] >= 0.70
    )
    return {
        "schema_version": 1,
        "result_id": "mina-smp-spatial-recovery-hysteresis-recovery-audit-v1",
        "synthetic_design": {
            "species": N_SPECIES,
            "physical_master_sites": N_SPECIES * MASTERS_PER_SPECIES,
            "spells": N_SPECIES * MASTERS_PER_SPECIES * SITES_PER_MASTER,
            "years_per_shift_block": len(YEARS),
            "common_offsets": [-1, 0, 1, 2, 3, 4],
            "datasets_per_scenario": DATASETS,
            "linear_shift_null_resamples_per_dataset": LINEAR_B,
            "seed": SEED,
        },
        "scenarios": out,
        "decision": {
            "recovery_audit_passed": passed,
            "thresholds": {
                "max_stationary_false_positive": 0.15,
                "max_monotonic_drift_false_positive": 0.15,
                "min_strong_signal_recovery": 0.70,
            },
        },
        "boundary": [
            "Synthetic calibration only; not biological effect-size prior.",
            "No SMP outcome data were used.",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()
    result = run()
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["decision"]["recovery_audit_passed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
