#!/usr/bin/env python3
"""Outcome-blind synthetic recovery for the Paper 2 A x H coupling hypothesis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _parse_seasons(value) -> list[int]:
    return [int(v) for v in str(value).split(";") if str(v).strip()]


def oracle_crossover_estimate(
    frame: pd.DataFrame,
    *,
    gamma: np.ndarray,
    seed: int,
    forcing_sd: float,
    site_loading_sd: float,
    process_sd: float,
    observation_sd: float,
) -> dict:
    """Recover coupling-trait effects when synthetic shared forcing is known.

    This is deliberately an oracle-forcing upper-bound test. It validates the
    interaction design conditional on recovery of the shared factor; it does
    not claim to validate the later latent-factor state-space fit.
    """
    rng = np.random.default_rng(seed)
    local = frame.reset_index(drop=True).copy()
    traits = local[["A", "H", "R", "AH"]].to_numpy(float)
    groups = sorted(local["forcing_group"].astype(str).unique())
    group_index = {g: i for i, g in enumerate(groups)}
    n_sites = len(local)
    n_groups = len(groups)
    years = np.arange(1980, 2025)

    site_loading = (
        1.0
        + traits @ np.asarray(gamma, dtype=float)
        + rng.normal(0.0, site_loading_sd, n_sites)
    )
    site_mu = -0.015 + rng.normal(0.0, 0.01, n_sites)
    forcing = rng.normal(0.0, forcing_sd, (n_groups, len(years)))

    observed: list[dict[int, float]] = []
    for i, row in local.iterrows():
        group = group_index[str(row["forcing_group"])]
        state = np.empty(46, dtype=float)
        state[0] = 7.0 + rng.normal(0.0, 0.4)
        increments = (
            site_mu[i]
            + site_loading[i] * forcing[group]
            + rng.normal(0.0, process_sd, len(years))
        )
        state[1:] = state[0] + np.cumsum(increments)
        seasons = _parse_seasons(row["seasons"])
        observed.append(
            {
                season: float(
                    state[season - 1980]
                    + rng.normal(0.0, observation_sd)
                )
                for season in seasons
                if 1980 <= season <= 2025
            }
        )

    interval_rows = []
    for i, row in local.iterrows():
        seasons = sorted(observed[i])
        for s0, s1 in zip(seasons[:-1], seasons[1:]):
            if s1 <= s0:
                continue
            group = group_index[str(row["forcing_group"])]
            integrated_forcing = float(
                forcing[group, s0 - 1980 : s1 - 1980].sum()
            )
            interval_rows.append(
                (
                    i,
                    group,
                    s1 - s0,
                    integrated_forcing,
                    observed[i][s1] - observed[i][s0],
                )
            )
    if not interval_rows:
        raise ValueError("no observation intervals available")

    site_idx = np.asarray([r[0] for r in interval_rows], dtype=int)
    group_idx = np.asarray([r[1] for r in interval_rows], dtype=int)
    dt = np.asarray([r[2] for r in interval_rows], dtype=float)
    fsum = np.asarray([r[3] for r in interval_rows], dtype=float)
    response = np.asarray([r[4] for r in interval_rows], dtype=float)

    # Joint linear recovery conditional on the known synthetic forcing:
    # site-specific mu + group loading baseline + common A/H/R/AH effects.
    p = n_sites + n_groups + 4
    X = np.zeros((len(interval_rows), p), dtype=float)
    rr = np.arange(len(interval_rows))
    X[rr, site_idx] = dt
    X[rr, n_sites + group_idx] = fsum
    X[:, n_sites + n_groups :] = fsum[:, None] * traits[site_idx]

    beta = np.linalg.lstsq(X, response, rcond=None)[0]
    return {
        "gamma_hat": [float(v) for v in beta[-4:]],
        "n_intervals": int(len(interval_rows)),
        "design_rank": int(np.linalg.matrix_rank(X)),
        "design_columns": int(X.shape[1]),
    }


def empirical_recovery(
    frame: pd.DataFrame,
    *,
    gamma_ah: float,
    n_replicates: int,
    seed: int,
    forcing_sd: float,
    site_loading_sd: float,
    process_sd: float,
    observation_sd: float,
) -> np.ndarray:
    estimates = []
    gamma = np.array([-0.15, 0.0, -0.10, gamma_ah], dtype=float)
    for rep in range(n_replicates):
        result = oracle_crossover_estimate(
            frame,
            gamma=gamma,
            seed=seed + rep,
            forcing_sd=forcing_sd,
            site_loading_sd=site_loading_sd,
            process_sd=process_sd,
            observation_sd=observation_sd,
        )
        estimates.append(result["gamma_hat"][3])
    return np.asarray(estimates, dtype=float)


def run_recovery_grid(
    frame: pd.DataFrame,
    *,
    n_replicates: int = 200,
) -> dict:
    """Run a predeclared oracle-forcing power/stress grid by species."""
    scenarios = {
        "low_noise": {"process_sd": 0.03, "observation_sd": 0.05},
        "base_noise": {"process_sd": 0.05, "observation_sd": 0.08},
        "high_noise": {"process_sd": 0.10, "observation_sd": 0.15},
    }
    base_effects = (0.0, -0.20, -0.35, -0.50)
    out = {}
    for species_offset, (species_id, local) in enumerate(
        frame.groupby("species_id", sort=True)
    ):
        species = {}
        base_values = {}
        for effect_index, effect in enumerate(base_effects):
            base_values[effect] = empirical_recovery(
                local,
                gamma_ah=effect,
                n_replicates=n_replicates,
                seed=100_000 + species_offset * 100_000 + effect_index * 10_000,
                forcing_sd=0.08,
                site_loading_sd=0.12,
                process_sd=scenarios["base_noise"]["process_sd"],
                observation_sd=scenarios["base_noise"]["observation_sd"],
            )
        null_threshold = float(np.quantile(base_values[0.0], 0.05))
        base_summary = {}
        for effect, values in base_values.items():
            base_summary[str(effect)] = {
                "mean_estimate": float(values.mean()),
                "sd_estimate": float(values.std(ddof=1)),
                "negative_fraction": float((values < 0).mean()),
                "empirical_one_sided_detection": float(
                    (values < null_threshold).mean()
                ),
                "q05": float(np.quantile(values, 0.05)),
                "q50": float(np.quantile(values, 0.50)),
                "q95": float(np.quantile(values, 0.95)),
            }
        species["base_noise_power_curve"] = {
            "null_5pct_threshold": null_threshold,
            "effects": base_summary,
        }

        stress = {}
        for scenario_index, scenario_name in enumerate(("low_noise", "high_noise")):
            params = scenarios[scenario_name]
            null = empirical_recovery(
                local,
                gamma_ah=0.0,
                n_replicates=n_replicates,
                seed=500_000 + species_offset * 100_000 + scenario_index * 20_000,
                forcing_sd=0.08,
                site_loading_sd=0.12,
                process_sd=params["process_sd"],
                observation_sd=params["observation_sd"],
            )
            alt = empirical_recovery(
                local,
                gamma_ah=-0.35,
                n_replicates=n_replicates,
                seed=510_000 + species_offset * 100_000 + scenario_index * 20_000,
                forcing_sd=0.08,
                site_loading_sd=0.12,
                process_sd=params["process_sd"],
                observation_sd=params["observation_sd"],
            )
            threshold = float(np.quantile(null, 0.05))
            stress[scenario_name] = {
                **params,
                "null_5pct_threshold": threshold,
                "interaction": -0.35,
                "mean_estimate": float(alt.mean()),
                "sign_recovery": float((alt < 0).mean()),
                "empirical_one_sided_detection": float((alt < threshold).mean()),
                "q05": float(np.quantile(alt, 0.05)),
                "q95": float(np.quantile(alt, 0.95)),
            }
        species["noise_stress_at_minus_0.35"] = stress
        out[str(species_id)] = species
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--frame", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--replicates", type=int, default=200)
    a = p.parse_args()
    frame = pd.read_csv(a.frame)
    result = {
        "schema_version": 1,
        "simulation_id": "mina-paper2-crossover-oracle-recovery-v1",
        "estimand": "gamma_AH effect on shared-forcing loading lambda",
        "forcing_status": (
            "oracle synthetic forcing is supplied to the recovery fit; "
            "this is an upper-bound interaction-identifiability test, not "
            "a validation of latent-factor estimation"
        ),
        "n_replicates": int(a.replicates),
        "fixed_simulation_parameters": {
            "forcing_sd": 0.08,
            "site_loading_sd": 0.12,
            "gamma_A": -0.15,
            "gamma_H": 0.0,
            "gamma_R": -0.10,
            "base_gamma_AH_grid": [0.0, -0.20, -0.35, -0.50],
            "noise_scenarios": {
                "low_noise": {"process_sd": 0.03, "observation_sd": 0.05},
                "base_noise": {"process_sd": 0.05, "observation_sd": 0.08},
                "high_noise": {"process_sd": 0.10, "observation_sd": 0.15},
            },
        },
        "species": run_recovery_grid(frame, n_replicates=a.replicates),
        "no_demographic_outcomes_opened": True,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
