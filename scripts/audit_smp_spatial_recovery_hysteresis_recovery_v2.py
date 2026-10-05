#!/usr/bin/env python3
"""Synthetic recovery audit for SMP spatial-recovery hysteresis V2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.finalize_smp_spatial_recovery_hysteresis_support_v2 import (
    common_noncircular_shifts,
)
from scripts.run_smp_spatial_recovery_hysteresis_v1 import (
    H_from_years,
    hierarchical_means,
    sign_flip_test,
)
from scripts.run_smp_spatial_recovery_hysteresis_v2 import (
    noncircular_common_shift_null,
)


SEED = 20261005
YEARS = list(range(2000, 2016))
N_SPECIES = 5
MASTERS_PER_SPECIES = 2
SITES_PER_MASTER = 3
DATASETS = 60
SHIFT_B = 1999


def ar1_noise(rng: np.random.Generator, n: int, phi: float = 0.5, sd: float = 0.025):
    out = np.zeros(n, float)
    eps = rng.normal(0.0, sd, size=n)
    out[0] = eps[0]
    for i in range(1, n):
        out[i] = phi * out[i - 1] + eps[i]
    return out


def first_completed_spell(states: list[int]) -> dict:
    for i in range(len(states) - 1):
        if states[i] == 1 and states[i + 1] == 0:
            j = i + 1
            while j + 1 < len(states) and states[j + 1] == 0:
                j += 1
            if j + 1 < len(states) and states[j + 1] == 1:
                return {
                    "abandon_from": YEARS[i],
                    "abandon_to": YEARS[i + 1],
                    "recolonize_from": YEARS[j],
                    "recolonize_to": YEARS[j + 1],
                }
    raise ValueError("synthetic trajectory did not produce a completed spell")


def threshold_states(parent_log: np.ndarray, abandon: float, recolonize: float) -> list[int]:
    state = 1
    out = [1]
    for value in parent_log[1:]:
        if state == 1 and value < abandon:
            state = 0
        elif state == 0 and value > recolonize:
            state = 1
        out.append(state)
    return out


def make_parent_and_event(rng: np.random.Generator, scenario: str):
    n = len(YEARS)
    t = np.arange(n, dtype=float)
    noise = ar1_noise(rng, n)

    if scenario == "stationary_exogenous_events":
        parent_log = 5.0 + noise
        event = {
            "abandon_from": 2002,
            "abandon_to": 2003,
            "recolonize_from": 2007,
            "recolonize_to": 2008,
        }
        return parent_log, event

    if scenario == "monotonic_drift_exogenous_events":
        parent_log = 4.4 + np.linspace(0.0, 1.6, n) + noise
        event = {
            "abandon_from": 2002,
            "abandon_to": 2003,
            "recolonize_from": 2007,
            "recolonize_to": 2008,
        }
        return parent_log, event

    # Symmetric decline-recovery path, with a little autocorrelated noise.
    parent_log = 4.15 + 0.19 * np.abs(t - 7.5) + noise

    if scenario == "reversible_threshold_cycle":
        states = threshold_states(parent_log, abandon=4.82, recolonize=4.82)
    elif scenario == "hysteresis_threshold_moderate":
        states = threshold_states(parent_log, abandon=4.72, recolonize=5.00)
    elif scenario == "hysteresis_threshold_strong":
        states = threshold_states(parent_log, abandon=4.62, recolonize=5.18)
    else:
        raise ValueError(scenario)

    return parent_log, first_completed_spell(states)


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
            parent_log, event = make_parent_and_event(rng, scenario)
            parent = np.maximum(np.expm1(parent_log), 0.0)

            data = {"background": parent}
            for j in range(SITES_PER_MASTER):
                data[f"S{j}"] = np.full(len(YEARS), 2.0)
            mat = pd.DataFrame(data, index=YEARS)
            cache[(species, master.casefold(), unit)] = mat

            local = []
            for j in range(SITES_PER_MASTER):
                site = f"S{j}"
                sp = {
                    "species": species,
                    "master_site": master,
                    "master_site_key": master,
                    "unit": unit,
                    "site_id": site,
                    **event,
                    "phase_block_start": YEARS[0],
                    "phase_block_end": YEARS[-1],
                    "phase_block_years": YEARS,
                    "state_complete_years": YEARS,
                }
                local.append(sp)

            shifts = common_noncircular_shifts(local)
            if len(shifts) < 3:
                raise ValueError(f"synthetic shift support too small: {scenario} {master} {shifts}")
            gid = f"{master}|{YEARS[0]}|{YEARS[-1]}"
            for sp in local:
                sp = {
                    **sp,
                    "shift_group_id": gid,
                    "eligible_common_shifts": shifts,
                    "n_common_shifts": len(shifts),
                }
                spells.append(sp)
                years = [
                    int(sp["abandon_from"]),
                    int(sp["abandon_to"]),
                    int(sp["recolonize_from"]),
                    int(sp["recolonize_to"]),
                ]
                H = H_from_years(mat, str(sp["site_id"]), *years)
                observed_rows.append({
                    **sp,
                    "H": float(H),
                })

    return pd.DataFrame(observed_rows), spells, cache


def evaluate_dataset(seed: int, scenario: str) -> dict:
    observed, spells, cache = build_dataset(seed, scenario)
    hier = hierarchical_means(observed)
    vals = hier["species"]["species_mean_H"].to_numpy(float)
    sign = sign_flip_test(vals)
    shift = noncircular_common_shift_null(
        observed,
        spells,
        cache,
        B=SHIFT_B,
        seed=seed + 1000003,
    )
    T = float(hier["T"])
    supported = bool(
        T > 0
        and sign["one_sided_p"] <= 0.05
        and shift["delta_shift_observed_minus_median"] > 0
        and shift["upper_tail_p"] <= 0.05
    )
    return {
        "T": T,
        "sign_p": float(sign["one_sided_p"]),
        "shift_p": float(shift["upper_tail_p"]),
        "delta_shift": float(shift["delta_shift_observed_minus_median"]),
        "supported": supported,
    }


def run() -> dict:
    scenarios = [
        "stationary_exogenous_events",
        "monotonic_drift_exogenous_events",
        "reversible_threshold_cycle",
        "hysteresis_threshold_moderate",
        "hysteresis_threshold_strong",
    ]
    out = {}
    for k, scenario in enumerate(scenarios):
        rows = [
            evaluate_dataset(SEED + k * 100000 + r * 997, scenario)
            for r in range(DATASETS)
        ]
        out[scenario] = {
            "datasets": DATASETS,
            "support_rate": float(np.mean([r["supported"] for r in rows])),
            "median_T": float(np.median([r["T"] for r in rows])),
            "median_sign_p": float(np.median([r["sign_p"] for r in rows])),
            "median_shift_p": float(np.median([r["shift_p"] for r in rows])),
            "median_delta_shift": float(np.median([r["delta_shift"] for r in rows])),
        }

    passed = bool(
        out["stationary_exogenous_events"]["support_rate"] <= 0.15
        and out["monotonic_drift_exogenous_events"]["support_rate"] <= 0.15
        and out["reversible_threshold_cycle"]["support_rate"] <= 0.15
        and out["hysteresis_threshold_strong"]["support_rate"] >= 0.70
    )
    return {
        "schema_version": 2,
        "result_id": "mina-smp-spatial-recovery-hysteresis-recovery-audit-v2",
        "synthetic_design": {
            "species": N_SPECIES,
            "physical_master_sites": N_SPECIES * MASTERS_PER_SPECIES,
            "spells": N_SPECIES * MASTERS_PER_SPECIES * SITES_PER_MASTER,
            "years": [YEARS[0], YEARS[-1]],
            "datasets_per_scenario": DATASETS,
            "shift_null_resamples_per_dataset": SHIFT_B,
            "seed": SEED,
        },
        "scenarios": out,
        "decision": {
            "recovery_audit_passed": passed,
            "thresholds": {
                "max_stationary_false_positive": 0.15,
                "max_monotonic_drift_false_positive": 0.15,
                "max_reversible_threshold_false_positive": 0.15,
                "min_strong_hysteresis_recovery": 0.70,
            },
        },
        "boundary": [
            "Synthetic design audit only; no SMP biological outcome was used.",
            "Synthetic threshold gaps are calibration scenarios, not biological effect-size priors.",
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
    return 0 if result["decision"]["recovery_audit_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
