"""Autocorrelation-preserving circular-shift null for the N_eff coefficient."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

from .colony_network import full_coefficient, loyo, transition_rows
from .lter import ISLANDS
from .neff_permutation import _fast_permutation_statistics

EXPECTED_ROWS = 120
EXPECTED_END_YEARS = 26
EXPECTED_BETA = 0.11679896749684501
EXPECTED_GAIN = 0.0010288409158503153
PERSISTENT_ISLANDS = ("CHR", "COR", "HUM", "TOR")


def island_sequences(
    rows: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for island in ISLANDS:
        indexed = [
            (idx, row)
            for idx, row in enumerate(rows)
            if str(row["island"]) == island
        ]
        indexed.sort(key=lambda item: int(item[1]["start_year"]))
        if not indexed:
            continue
        indices = np.asarray([idx for idx, _ in indexed], dtype=int)
        years = np.asarray(
            [int(row["start_year"]) for _, row in indexed], dtype=int
        )
        values = np.asarray(
            [
                math.log1p(float(row["effective_colony_number"]))
                for _, row in indexed
            ],
            dtype=float,
        )
        if len(years) >= 2 and not np.all(np.diff(years) == 1):
            raise ValueError(
                f"non-contiguous transition years for {island}: {years.tolist()}"
            )
        out[island] = {
            "indices": indices,
            "years": years,
            "values": values,
        }
    return out


def _shifted_values(values: np.ndarray, shifts: np.ndarray) -> np.ndarray:
    """Return columns containing circularly shifted copies of one series."""
    n = int(values.size)
    if n < 2:
        raise ValueError("circular shift requires at least two observations")
    positions = np.arange(n, dtype=int)[:, None]
    donor_index = (positions - shifts[None, :]) % n
    return values[donor_index]


def independent_shift_matrix(
    rows: list[dict[str, object]],
    simulations: int,
    seed: int,
) -> tuple[np.ndarray, dict[str, object]]:
    seq = island_sequences(rows)
    if set(seq) != set(ISLANDS):
        raise ValueError(f"missing island sequence: {sorted(set(ISLANDS)-set(seq))}")

    rng = np.random.default_rng(seed)
    shift_rows = {
        island: rng.integers(
            low=0,
            high=len(seq[island]["values"]),
            size=simulations,
            dtype=np.int64,
        )
        for island in ISLANDS
    }

    # Reject the single global identity transformation if it happens to be drawn.
    identity = np.ones(simulations, dtype=bool)
    for island in ISLANDS:
        identity &= shift_rows[island] == 0
    rejected = int(np.sum(identity))
    while np.any(identity):
        columns = np.flatnonzero(identity)
        for island in ISLANDS:
            shift_rows[island][columns] = rng.integers(
                low=0,
                high=len(seq[island]["values"]),
                size=len(columns),
                dtype=np.int64,
            )
        identity = np.ones(simulations, dtype=bool)
        for island in ISLANDS:
            identity &= shift_rows[island] == 0

    matrix = np.empty((len(rows), simulations), dtype=float)
    frequency: dict[str, dict[str, int]] = {}
    for island in ISLANDS:
        indices = seq[island]["indices"]
        values = seq[island]["values"]
        shifts = shift_rows[island]
        matrix[indices, :] = _shifted_values(values, shifts)
        counts = Counter(int(x) for x in shifts.tolist())
        frequency[island] = {
            str(lag): int(counts.get(lag, 0))
            for lag in range(len(values))
        }

    diagnostic = {
        "global_identity_draws_rejected": rejected,
        "sequence_lengths": {
            island: int(len(seq[island]["values"])) for island in ISLANDS
        },
        "year_ranges": {
            island: [
                int(seq[island]["years"][0]),
                int(seq[island]["years"][-1]),
            ]
            for island in ISLANDS
        },
        "shift_frequencies": frequency,
    }
    return matrix, diagnostic


def joint_shift_matrix(
    rows: list[dict[str, object]],
) -> tuple[np.ndarray, list[dict[str, int]]]:
    """Exact 26 x 16 sensitivity preserving covariance among four extant islands."""
    seq = island_sequences(rows)
    lengths = {island: len(seq[island]["values"]) for island in ISLANDS}
    persistent_lengths = {lengths[island] for island in PERSISTENT_ISLANDS}
    if persistent_lengths != {26}:
        raise ValueError(
            f"expected 26 transitions for persistent islands, got {lengths}"
        )
    if lengths["LIT"] != 16:
        raise ValueError(f"expected 16 LIT transitions, got {lengths['LIT']}")

    combos = [
        {"persistent_lag": persistent_lag, "lit_lag": lit_lag}
        for persistent_lag in range(26)
        for lit_lag in range(16)
    ]
    matrix = np.empty((len(rows), len(combos)), dtype=float)

    persistent_shifts = np.asarray(
        [combo["persistent_lag"] for combo in combos], dtype=int
    )
    lit_shifts = np.asarray(
        [combo["lit_lag"] for combo in combos], dtype=int
    )

    for island in PERSISTENT_ISLANDS:
        indices = seq[island]["indices"]
        matrix[indices, :] = _shifted_values(
            seq[island]["values"], persistent_shifts
        )
    matrix[seq["LIT"]["indices"], :] = _shifted_values(
        seq["LIT"]["values"], lit_shifts
    )
    return matrix, combos


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)),
        "q_0_025": float(np.quantile(values, 0.025)),
        "q_0_05": float(np.quantile(values, 0.05)),
        "q_0_50": float(np.quantile(values, 0.50)),
        "q_0_95": float(np.quantile(values, 0.95)),
        "q_0_975": float(np.quantile(values, 0.975)),
        "q_0_99": float(np.quantile(values, 0.99)),
    }


def _monte_carlo_p(
    values: np.ndarray,
    observed: float,
) -> dict[str, float | int]:
    exceed = int(np.sum(values >= observed))
    p_one = (1.0 + exceed) / (len(values) + 1.0)
    exceed_two = int(np.sum(np.abs(values) >= abs(observed)))
    p_two = (1.0 + exceed_two) / (len(values) + 1.0)
    se = math.sqrt(p_one * (1.0 - p_one) / (len(values) + 1.0))
    return {
        "exceedances_ge_observed": exceed,
        "one_sided_p": p_one,
        "monte_carlo_se": se,
        "two_sided_abs_p": p_two,
        "two_sided_abs_exceedances": exceed_two,
    }


def diagnose(
    census_path: str | Path,
    simulations: int = 100000,
    seed: int = 20260927,
) -> dict[str, object]:
    rows = transition_rows(census_path)
    observed = loyo(rows, "effective")
    observed_beta = full_coefficient(rows, "effective")
    observed_gain = float(observed["mse_gain_C0_minus_C1"])

    if len(rows) != EXPECTED_ROWS or int(observed["n_years"]) != EXPECTED_END_YEARS:
        raise ValueError(
            f"frozen sample drift: rows={len(rows)}, "
            f"years={observed['n_years']}"
        )
    if not math.isclose(
        observed_beta, EXPECTED_BETA, rel_tol=0.0, abs_tol=1e-12
    ):
        raise ValueError(
            f"frozen beta drift: {observed_beta} != {EXPECTED_BETA}"
        )
    if not math.isclose(
        observed_gain, EXPECTED_GAIN, rel_tol=0.0, abs_tol=1e-12
    ):
        raise ValueError(
            f"frozen gain drift: {observed_gain} != {EXPECTED_GAIN}"
        )

    independent_matrix, shift_diag = independent_shift_matrix(
        rows, simulations=simulations, seed=seed
    )
    independent_gains, independent_betas = _fast_permutation_statistics(
        rows, independent_matrix
    )
    primary_p = _monte_carlo_p(independent_betas, observed_beta)
    gain_p = _monte_carlo_p(independent_gains, observed_gain)

    joint_matrix, joint_combos = joint_shift_matrix(rows)
    joint_gains, joint_betas = _fast_permutation_statistics(rows, joint_matrix)
    # The identity transformation is part of the exact randomization group and
    # must count as at least one statistic as extreme as observed. Numerical
    # re-expression through FWL can differ from the direct fit at roundoff scale,
    # so use the same strict 1e-10 identity tolerance for exact tail membership.
    tolerance = 1e-10
    joint_ge = int(np.sum(joint_betas >= observed_beta - tolerance))
    joint_abs = int(
        np.sum(np.abs(joint_betas) >= abs(observed_beta) - tolerance)
    )
    joint_one = joint_ge / len(joint_betas)
    joint_two = joint_abs / len(joint_betas)

    # Identity must reproduce the observed coefficient and gain exactly.
    identity_index = next(
        i for i, combo in enumerate(joint_combos)
        if combo["persistent_lag"] == 0 and combo["lit_lag"] == 0
    )
    if not math.isclose(
        float(joint_betas[identity_index]),
        observed_beta,
        rel_tol=0.0,
        abs_tol=1e-10,
    ):
        raise ValueError("joint-shift identity beta does not reproduce observed")
    if not math.isclose(
        float(joint_gains[identity_index]),
        observed_gain,
        rel_tol=0.0,
        abs_tol=1e-10,
    ):
        raise ValueError("joint-shift identity gain does not reproduce observed")

    primary_survives = bool(float(primary_p["one_sided_p"]) <= 0.05)
    joint_survives = bool(joint_one <= 0.05)
    retained = bool(primary_survives and joint_survives)

    return {
        "schema_version": 1,
        "analysis_id": "mina-neff-circular-shift-v1",
        "status": "serial_structure_preserving_null_diagnostic",
        "simulations": simulations,
        "seed": seed,
        "observed": {
            "n_rows": len(rows),
            "n_end_years": int(observed["n_years"]),
            "standardized_beta": observed_beta,
            "held_out_mse_gain": observed_gain,
        },
        "primary_independent_island_shift": {
            "coefficient_null": {
                **_summary(independent_betas),
                "proportion_positive": float(np.mean(independent_betas > 0)),
                **primary_p,
            },
            "held_out_gain_secondary": {
                **_summary(independent_gains),
                "proportion_positive": float(np.mean(independent_gains > 0)),
                **gain_p,
            },
            "shift_diagnostics": shift_diag,
        },
        "joint_persistent_island_shift_sensitivity": {
            "n_exact_combinations": len(joint_combos),
            "coefficient_null": {
                **_summary(joint_betas),
                "proportion_positive": float(np.mean(joint_betas > 0)),
                "exceedances_ge_observed": joint_ge,
                "exact_one_sided_p": joint_one,
                "two_sided_abs_exceedances": joint_abs,
                "exact_two_sided_abs_p": joint_two,
            },
            "held_out_gain_secondary": {
                **_summary(joint_gains),
                "proportion_positive": float(np.mean(joint_gains > 0)),
            },
            "identity_reproduces_observed": True,
        },
        "decision": {
            "primary_independent_shift_p_le_0_05": primary_survives,
            "joint_shift_p_le_0_05": joint_survives,
            "association_retained_against_both_structured_nulls": retained,
        },
        "interpretation_boundary": {
            "null_correction_not_new_endpoint": True,
            "circular_wraparound_is_structured_surrogate": True,
            "held_out_prediction_remains_unsupported_from_prior_block_test": True,
            "causal_inference": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--simulations", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=20260927)
    args = parser.parse_args()
    result = diagnose(
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
