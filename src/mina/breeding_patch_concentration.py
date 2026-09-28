"""Breeding-patch concentration during Palmer Adélie decline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .hierarchical_variability import EXPECTED_YEARS, STABLE_ROSTER_ISLANDS
from .hierarchy_count_error import _draw_batch, _pooled_latent_state
from .lter import load_colony_rows
from .neff_coupling import ERROR_MODELS

SIMULATIONS = 100000
SEED = 20260928
BATCH_SIZE = 2000


def _effective_number_batch(matrix: np.ndarray) -> np.ndarray:
    """Effective colony number for [replicate, colony, year] count arrays."""
    total = np.sum(matrix, axis=1, dtype=float)
    squares = np.sum(np.asarray(matrix, dtype=float) ** 2, axis=1)
    out = np.full(total.shape, np.nan, dtype=float)
    valid = total > 0
    out[valid] = total[valid] ** 2 / squares[valid]
    return out


def _slope_batch(
    values: np.ndarray,
    years: np.ndarray,
) -> np.ndarray:
    if values.ndim != 2:
        raise ValueError("values must be replicate x time")
    if values.shape[1] != years.size:
        raise ValueError("time axis does not match years")
    x = np.asarray(years, dtype=float)
    centered = x - float(np.mean(x))
    denom = float(np.sum(centered**2))
    if denom <= 0:
        raise ValueError("zero time variance")
    centered_values = values - np.mean(values, axis=1, keepdims=True)
    return np.sum(centered_values * centered[None, :], axis=1) / denom


def _observed(
    state: dict[str, dict[str, object]],
) -> dict[str, dict[str, float | int]]:
    result: dict[str, dict[str, float | int]] = {}
    years = np.asarray(EXPECTED_YEARS, dtype=int)
    for island in STABLE_ROSTER_ISLANDS:
        matrix = np.asarray(state[island]["observed_matrix"], dtype=float)
        totals = np.asarray(state[island]["island_totals"], dtype=float)
        positive = totals > 0
        neff = _effective_number_batch(matrix[None, :, :])[0]
        local_years = years[positive]
        local_values = neff[positive]
        slope = float(_slope_batch(local_values[None, :], local_years)[0])
        first = float(local_values[0])
        last = float(local_values[-1])
        result[island] = {
            "positive_year_count": int(np.sum(positive)),
            "first_positive_year": int(local_years[0]),
            "last_positive_year": int(local_years[-1]),
            "first_neff": first,
            "last_neff": last,
            "fractional_change_first_to_last": float(last / first - 1.0),
            "neff_slope_per_year": slope,
        }
    return result


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)),
        "median": float(np.median(values)),
        "q_0_025": float(np.quantile(values, 0.025)),
        "q_0_05": float(np.quantile(values, 0.05)),
        "q_0_95": float(np.quantile(values, 0.95)),
        "q_0_975": float(np.quantile(values, 0.975)),
    }


def simulate(
    census_path: str | Path,
    simulations: int = SIMULATIONS,
    seed: int = SEED,
    batch_size: int = BATCH_SIZE,
) -> dict[str, object]:
    rows = load_colony_rows(census_path)
    state = _pooled_latent_state(rows)
    observed = _observed(state)

    years = np.asarray(EXPECTED_YEARS, dtype=int)
    rng = np.random.default_rng(seed)
    outputs: dict[str, object] = {}

    for model_name, cv in ERROR_MODELS:
        slope_chunks: dict[str, list[np.ndarray]] = {
            island: [] for island in STABLE_ROSTER_ISLANDS
        }
        completed = 0
        while completed < simulations:
            n = min(batch_size, simulations - completed)
            batch = _draw_batch(state, n, cv, rng)
            for island in STABLE_ROSTER_ISLANDS:
                totals = np.asarray(
                    state[island]["island_totals"], dtype=float
                )
                positive = totals > 0
                neff = _effective_number_batch(batch[island])
                slopes = _slope_batch(
                    neff[:, positive],
                    years[positive],
                )
                slope_chunks[island].append(slopes)
            completed += n

        slopes = {
            island: np.concatenate(slope_chunks[island])
            for island in STABLE_ROSTER_ISLANDS
        }

        island_results: dict[str, object] = {}
        joint = np.ones(simulations, dtype=bool)
        for island in STABLE_ROSTER_ISLANDS:
            values = slopes[island]
            obs = float(observed[island]["neff_slope_per_year"])
            exceed = int(np.sum(values <= obs))
            joint &= values <= obs
            island_results[island] = {
                **_summary(values),
                "observed_slope": obs,
                "simulated_slopes_le_observed": exceed,
                "one_sided_probability_le_observed": (
                    1.0 + exceed
                ) / (simulations + 1.0),
            }

        joint_count = int(np.sum(joint))
        outputs[model_name] = {
            "multiplicative_cv": cv,
            "island_slopes": island_results,
            "joint_all_three_as_or_more_negative_count": joint_count,
            "joint_all_three_as_or_more_negative_probability": (
                1.0 + joint_count
            ) / (simulations + 1.0),
        }

    support = True
    for name, _ in ERROR_MODELS:
        model = outputs[name]
        if float(
            model["joint_all_three_as_or_more_negative_probability"]
        ) > 0.05:
            support = False
        for island in STABLE_ROSTER_ISLANDS:
            if float(
                model["island_slopes"][island][
                    "one_sided_probability_le_observed"
                ]
            ) > 0.05:
                support = False

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-breeding-patch-concentration-v1",
        "status": "post_hoc_external_context_ecological_extension",
        "simulations_per_error_model": simulations,
        "seed": seed,
        "batch_size": batch_size,
        "eligible_islands": list(STABLE_ROSTER_ISLANDS),
        "null_composition": (
            "time-invariant cumulative colony-code shares within island"
        ),
        "observed": observed,
        "error_models": outputs,
        "decision": {
            "progressive_concentration_supported_under_all_frozen_error_models": bool(
                support
            ),
        },
        "interpretation_boundary": {
            "beyond_declining_total_and_independent_count_error": bool(
                support
            ),
            "physical_patch_identity_resolved": False,
            "habitat_mechanism_identified": False,
            "causal_spatial_insurance_claim": False,
            "external_torgersen_is_triangulation_only": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--simulations", type=int, default=SIMULATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    args = parser.parse_args()
    result = simulate(
        args.census,
        simulations=args.simulations,
        seed=args.seed,
        batch_size=args.batch_size,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
