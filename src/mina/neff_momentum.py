"""Demographic-momentum sensitivity for the Palmer N_eff association."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from .colony_network import (
    full_coefficient as original_full_coefficient,
    loyo as original_loyo,
    transition_rows,
)
from .lter import ISLANDS
from .neff_circular_shift import independent_shift_matrix, joint_shift_matrix

EXPECTED_BASE_BETA = 0.11679896749684501
EXPECTED_LAG1_BETA = 0.11849651213599004
EXPECTED_LAG1_GAIN = 0.0009286183774917245
SIMULATIONS = 100000
SEED = 20260927


def enrich_lags(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    previous_growth = {
        (str(row["island"]), int(row["start_year"])): row["previous_growth"]
        for row in rows
    }
    out: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        island = str(row["island"])
        year = int(row["start_year"])
        enriched = dict(row)
        enriched["_full_index"] = index
        enriched["lag1_growth"] = row["previous_growth"]
        enriched["lag2_growth"] = previous_growth.get((island, year - 1))
        out.append(enriched)
    return out


def complete_cases(
    rows: list[dict[str, object]],
    lag_fields: tuple[str, ...],
) -> list[dict[str, object]]:
    return [
        row
        for row in rows
        if all(row.get(field) is not None for field in lag_fields)
    ]


def _levels(rows: list[dict[str, object]]) -> tuple[str, ...]:
    present = {str(row["island"]) for row in rows}
    return tuple(island for island in ISLANDS if island in present)


def _island_matrix(
    rows: list[dict[str, object]],
    levels: tuple[str, ...],
) -> np.ndarray:
    lookup = {island: index for index, island in enumerate(levels)}
    matrix = np.zeros((len(rows), len(levels)), dtype=float)
    for row_index, row in enumerate(rows):
        matrix[row_index, lookup[str(row["island"])]] = 1.0
    return matrix


def _standardize(
    train: np.ndarray,
    test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mean = float(np.mean(train))
    sd = float(np.std(train, ddof=1))
    if sd <= 0:
        raise ValueError("zero predictor variance")
    return (train - mean) / sd, (test - mean) / sd


def _design(
    train: list[dict[str, object]],
    test: list[dict[str, object]],
    lag_fields: tuple[str, ...],
    topology: bool,
) -> tuple[np.ndarray, np.ndarray]:
    levels = _levels(train)
    if any(str(row["island"]) not in levels for row in test):
        raise ValueError("test island absent from training")

    x_train = _island_matrix(train, levels)
    x_test = _island_matrix(test, levels)

    pairs: list[tuple[np.ndarray, np.ndarray]] = [
        (
            np.asarray(
                [math.log1p(float(row["current_total"])) for row in train],
                dtype=float,
            ),
            np.asarray(
                [math.log1p(float(row["current_total"])) for row in test],
                dtype=float,
            ),
        ),
        (
            np.asarray([float(row["start_year"]) for row in train], dtype=float),
            np.asarray([float(row["start_year"]) for row in test], dtype=float),
        ),
    ]
    if topology:
        pairs.append(
            (
                np.asarray(
                    [
                        math.log1p(float(row["effective_colony_number"]))
                        for row in train
                    ],
                    dtype=float,
                ),
                np.asarray(
                    [
                        math.log1p(float(row["effective_colony_number"]))
                        for row in test
                    ],
                    dtype=float,
                ),
            )
        )
    for field in lag_fields:
        pairs.append(
            (
                np.asarray([float(row[field]) for row in train], dtype=float),
                np.asarray([float(row[field]) for row in test], dtype=float),
            )
        )

    for train_values, test_values in pairs:
        z_train, z_test = _standardize(train_values, test_values)
        x_train = np.column_stack([x_train, z_train])
        x_test = np.column_stack([x_test, z_test])
    return x_train, x_test


def _ols(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank != x.shape[1]:
        raise ValueError("rank-deficient momentum model")
    return beta


def full_coefficient(
    rows: list[dict[str, object]],
    lag_fields: tuple[str, ...],
) -> float:
    local = complete_cases(rows, lag_fields)
    x, _ = _design(local, local, lag_fields, topology=True)
    y = np.asarray([float(row["next_growth"]) for row in local], dtype=float)
    beta = _ols(x, y)
    topology_index = len(_levels(local)) + 2
    return float(beta[topology_index])


def loyo(
    rows: list[dict[str, object]],
    lag_fields: tuple[str, ...],
) -> dict[str, object]:
    local = complete_cases(rows, lag_fields)
    years = sorted({int(row["end_year"]) for row in local})
    errors = {"C0": [], "C1": []}

    for held in years:
        train = [row for row in local if int(row["end_year"]) != held]
        test = [row for row in local if int(row["end_year"]) == held]
        y_train = np.asarray(
            [float(row["next_growth"]) for row in train], dtype=float
        )
        y_test = np.asarray(
            [float(row["next_growth"]) for row in test], dtype=float
        )
        for model, topology in (("C0", False), ("C1", True)):
            x_train, x_test = _design(
                train,
                test,
                lag_fields,
                topology=topology,
            )
            beta = _ols(x_train, y_train)
            residual = y_test - x_test @ beta
            errors[model].extend((residual**2).tolist())

    mse = {key: float(np.mean(values)) for key, values in errors.items()}
    return {
        "n_rows": len(local),
        "n_end_years": len(years),
        "mse": mse,
        "mse_gain_C0_minus_C1": mse["C0"] - mse["C1"],
    }


def _baseline_residuals(
    rows: list[dict[str, object]],
    lag_fields: tuple[str, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    local = complete_cases(rows, lag_fields)
    levels = _levels(local)
    x = _island_matrix(local, levels)
    continuous = [
        np.asarray(
            [math.log1p(float(row["current_total"])) for row in local],
            dtype=float,
        ),
        np.asarray([float(row["start_year"]) for row in local], dtype=float),
    ]
    continuous.extend(
        np.asarray([float(row[field]) for row in local], dtype=float)
        for field in lag_fields
    )
    x = np.column_stack([x, *continuous])
    if np.linalg.matrix_rank(x) != x.shape[1]:
        raise ValueError("rank-deficient structured-null baseline")
    q, _ = np.linalg.qr(x, mode="reduced")
    y = np.asarray([float(row["next_growth"]) for row in local], dtype=float)
    y_residual = y - q @ (q.T @ y)
    indices = np.asarray(
        [int(row["_full_index"]) for row in local], dtype=int
    )
    return indices, q, y_residual


def shifted_coefficients(
    rows: list[dict[str, object]],
    lag_fields: tuple[str, ...],
    full_shift_matrix: np.ndarray,
) -> np.ndarray:
    indices, q, y_residual = _baseline_residuals(rows, lag_fields)
    topology = np.asarray(full_shift_matrix[indices, :], dtype=float)
    means = np.mean(topology, axis=0)
    sds = np.std(topology, axis=0, ddof=1)
    if np.any(sds <= 0):
        raise ValueError("zero shifted topology variance")
    topology = (topology - means) / sds
    topology_residual = topology - q @ (q.T @ topology)
    denominator = np.sum(topology_residual**2, axis=0)
    if np.any(denominator <= 0):
        raise ValueError("zero residual topology variance")
    return (topology_residual.T @ y_residual) / denominator


def _monte_carlo_p(
    values: np.ndarray,
    observed: float,
) -> dict[str, float | int]:
    exceedances = int(np.sum(values >= observed))
    return {
        "exceedances_ge_observed": exceedances,
        "one_sided_p": (1.0 + exceedances) / (len(values) + 1.0),
        "null_q_0_95": float(np.quantile(values, 0.95)),
        "null_q_0_975": float(np.quantile(values, 0.975)),
        "null_q_0_99": float(np.quantile(values, 0.99)),
    }


def analyze(
    census_path: str | Path,
    simulations: int = SIMULATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    original = transition_rows(census_path)
    rows = enrich_lags(original)

    base_beta = original_full_coefficient(original, "effective")
    base_loyo = original_loyo(original, "effective")
    if not math.isclose(
        base_beta, EXPECTED_BASE_BETA, rel_tol=0.0, abs_tol=1e-12
    ):
        raise ValueError(f"base beta drift: {base_beta}")
    if not math.isclose(
        full_coefficient(rows, ("lag1_growth",)),
        EXPECTED_LAG1_BETA,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("lag1 coefficient no longer matches frozen sensitivity")
    lag1_loyo_check = loyo(rows, ("lag1_growth",))
    if not math.isclose(
        float(lag1_loyo_check["mse_gain_C0_minus_C1"]),
        EXPECTED_LAG1_GAIN,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("lag1 LOYO gain no longer matches frozen sensitivity")

    specs = {
        "lag1": ("lag1_growth",),
        "lag1_lag2": ("lag1_growth", "lag2_growth"),
    }
    observed: dict[str, dict[str, object]] = {}
    for name, fields in specs.items():
        local = complete_cases(rows, fields)
        observed[name] = {
            "n_rows": len(local),
            "n_end_years": len({int(row["end_year"]) for row in local}),
            "standardized_neff_beta": full_coefficient(rows, fields),
            "loyo": loyo(rows, fields),
        }

    independent_matrix, shift_diagnostics = independent_shift_matrix(
        original,
        simulations=simulations,
        seed=seed,
    )
    joint_matrix, joint_combos = joint_shift_matrix(original)

    structured: dict[str, dict[str, object]] = {}
    tolerance = 1e-10
    for name, fields in specs.items():
        obs = float(observed[name]["standardized_neff_beta"])
        independent_betas = shifted_coefficients(
            rows, fields, independent_matrix
        )
        joint_betas = shifted_coefficients(rows, fields, joint_matrix)
        identity_index = next(
            index
            for index, combo in enumerate(joint_combos)
            if combo["persistent_lag"] == 0 and combo["lit_lag"] == 0
        )
        if not math.isclose(
            float(joint_betas[identity_index]),
            obs,
            rel_tol=0.0,
            abs_tol=tolerance,
        ):
            raise ValueError(f"{name} joint identity does not reproduce observed")
        joint_exceedances = int(
            np.sum(joint_betas >= obs - tolerance)
        )
        structured[name] = {
            "independent_full_series_circular_shift": {
                **_monte_carlo_p(independent_betas, obs),
                "simulations": simulations,
                "seed": seed,
            },
            "joint_full_series_exact_shift": {
                "n_exact_combinations": len(joint_betas),
                "exceedances_ge_observed": joint_exceedances,
                "exact_one_sided_p": joint_exceedances / len(joint_betas),
                "identity_reproduces_observed": True,
            },
        }

    lag2_beta = float(observed["lag1_lag2"]["standardized_neff_beta"])
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-neff-demographic-momentum-v1",
        "status": "demographic_momentum_confound_sensitivity",
        "simulations": simulations,
        "seed": seed,
        "original_model": {
            "n_rows": len(original),
            "standardized_neff_beta": base_beta,
            "loyo_mse_gain": float(base_loyo["mse_gain_C0_minus_C1"]),
        },
        "momentum_models": observed,
        "structured_null_reuse": structured,
        "effect_retention": {
            "lag1_lag2_beta_fraction_of_original": lag2_beta / base_beta,
            "lag1_lag2_beta_absolute_change": lag2_beta - base_beta,
            "lag1_lag2_gain_fraction_of_original": (
                float(
                    observed["lag1_lag2"]["loyo"]["mse_gain_C0_minus_C1"]
                )
                / float(base_loyo["mse_gain_C0_minus_C1"])
            ),
        },
        "shift_diagnostics": shift_diagnostics,
        "interpretation_boundary": {
            "new_null_family_introduced": False,
            "robust_predictor_claim": False,
            "causal_claim": False,
            "early_warning_claim": False,
            "association_not_explained_away_by_two_year_momentum_controls": True,
            "incremental_held_out_gain_remains_small": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--simulations", type=int, default=SIMULATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(
        args.census,
        simulations=args.simulations,
        seed=args.seed,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
