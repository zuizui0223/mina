"""Independent count-error null for the Palmer hierarchy result."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from .hierarchical_variability import (
    EXPECTED_YEARS,
    STABLE_ROSTER_ISLANDS,
    colony_roster_audit,
    nested_raw_decomposition,
    centered_signal_sensitivity,
)
from .lter import load_colony_rows
from .neff_coupling import ERROR_MODELS

SIMULATIONS = 100000
SEED = 20260928
BATCH_SIZE = 2000


def _pooled_latent_state(
    rows: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    audit = colony_roster_audit(rows)
    state: dict[str, dict[str, object]] = {}
    for island in STABLE_ROSTER_ISLANDS:
        rec = audit[island]
        if not bool(rec["roster_stable"]):
            raise ValueError(f"nonstable roster in error null: {island}")
        codes = [str(x) for x in rec["intersection_codes"]]
        lookup = {
            (str(row["colony_code"]), int(row["year"])): float(
                row["breeding_pairs"]
            )
            for row in rows
            if str(row["island"]) == island
        }
        matrix = np.asarray(
            [
                [lookup[(code, year)] for year in EXPECTED_YEARS]
                for code in codes
            ],
            dtype=float,
        )
        totals = np.sum(matrix, axis=0)
        cumulative = np.sum(matrix, axis=1)
        if float(np.sum(cumulative)) <= 0:
            raise ValueError(f"zero cumulative abundance: {island}")
        shares = cumulative / float(np.sum(cumulative))
        latent = shares[:, None] * totals[None, :]
        state[island] = {
            "codes": codes,
            "observed_matrix": matrix,
            "island_totals": totals,
            "pooled_shares": shares,
            "latent_means": latent,
        }
    return state


def _alpha_cv2(matrix: np.ndarray) -> np.ndarray:
    means = np.mean(matrix, axis=2)
    sds = np.std(matrix, axis=2, ddof=1)
    total_mean = np.sum(means, axis=1)
    if np.any(total_mean <= 0):
        raise ValueError("nonpositive simulated aggregate mean")
    return (np.sum(sds, axis=1) / total_mean) ** 2


def _raw_batch(
    counts: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sub = np.concatenate(
        [counts[island] for island in STABLE_ROSTER_ISLANDS],
        axis=1,
    )
    islands = np.stack(
        [
            np.sum(counts[island], axis=1)
            for island in STABLE_ROSTER_ISLANDS
        ],
        axis=1,
    )
    alpha_sub = _alpha_cv2(sub)
    alpha_island = _alpha_cv2(islands)
    archipelago = np.sum(islands, axis=1)
    total_mean = np.sum(np.mean(islands, axis=2), axis=1)
    gamma = (
        np.std(archipelago, axis=1, ddof=1) / total_mean
    ) ** 2
    if np.any(gamma <= 0):
        raise ValueError("zero simulated archipelago variability")
    beta_within = alpha_sub / alpha_island
    beta_among = alpha_island / gamma
    contrast = np.log(beta_within / beta_among)
    return beta_within, beta_among, contrast


def _detrended_log1p(matrix: np.ndarray) -> np.ndarray:
    y = np.log1p(matrix)
    t = np.arange(y.shape[2], dtype=float)
    centered = t - float(np.mean(t))
    denominator = float(np.sum(centered**2))
    mean = np.mean(y, axis=2, keepdims=True)
    slope = np.sum(
        (y - mean) * centered[None, None, :],
        axis=2,
        keepdims=True,
    ) / denominator
    return y - mean - slope * centered[None, None, :]


def _annual_log1p_growth(matrix: np.ndarray) -> np.ndarray:
    return np.diff(np.log1p(matrix), axis=2)


def _covariance_beta(matrix: np.ndarray) -> np.ndarray:
    sds = np.std(matrix, axis=2, ddof=1)
    potential = np.sum(sds, axis=1) ** 2
    aggregate = np.sum(matrix, axis=1)
    observed = np.var(aggregate, axis=1, ddof=1)
    if np.any(observed <= 0):
        raise ValueError("zero simulated aggregate variance")
    return potential / observed


def _centered_ratio_batch(
    counts: dict[str, np.ndarray],
    transform: str,
) -> tuple[np.ndarray, np.ndarray]:
    if transform == "linear_detrended_log1p":
        fn = _detrended_log1p
    elif transform == "annual_log1p_growth":
        fn = _annual_log1p_growth
    else:
        raise ValueError(transform)

    islands = np.stack(
        [
            np.sum(counts[island], axis=1)
            for island in STABLE_ROSTER_ISLANDS
        ],
        axis=1,
    )
    among = _covariance_beta(fn(islands))
    within = np.stack(
        [
            _covariance_beta(fn(counts[island]))
            for island in STABLE_ROSTER_ISLANDS
        ],
        axis=1,
    )
    ratio = np.median(within, axis=1) / among
    all_within_exceed = np.all(within > among[:, None], axis=1)
    return ratio, all_within_exceed


def _draw_batch(
    state: dict[str, dict[str, object]],
    simulations: int,
    multiplicative_cv: float,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    counts: dict[str, np.ndarray] = {}
    for island in STABLE_ROSTER_ISLANDS:
        latent = np.asarray(state[island]["latent_means"], dtype=float)
        if multiplicative_cv > 0:
            shape = 1.0 / (multiplicative_cv**2)
            factors = rng.gamma(
                shape=shape,
                scale=1.0 / shape,
                size=(simulations,) + latent.shape,
            )
            means = factors * latent[None, :, :]
        else:
            means = np.broadcast_to(
                latent,
                (simulations,) + latent.shape,
            )
        counts[island] = rng.poisson(means).astype(float)
    return counts


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


def _tail(values: np.ndarray, observed: float) -> dict[str, object]:
    exceedances = int(np.sum(values >= observed))
    return {
        **_summary(values),
        "observed": observed,
        "exceedances_ge_observed": exceedances,
        "one_sided_probability_ge_observed": (
            1.0 + exceedances
        ) / (len(values) + 1.0),
    }


def _observed_statistics(
    rows: list[dict[str, object]],
) -> dict[str, float]:
    audit = colony_roster_audit(rows)
    raw = nested_raw_decomposition(
        rows,
        STABLE_ROSTER_ISLANDS,
        EXPECTED_YEARS,
        audit,
    )
    detrended = centered_signal_sensitivity(
        rows,
        STABLE_ROSTER_ISLANDS,
        EXPECTED_YEARS,
        audit,
        "linear_detrended_log1p",
    )
    growth = centered_signal_sensitivity(
        rows,
        STABLE_ROSTER_ISLANDS,
        EXPECTED_YEARS,
        audit,
        "annual_log1p_growth",
    )
    beta_within = float(raw["beta_within_islands"])
    beta_among = float(raw["beta_among_islands"])
    return {
        "raw_beta_within": beta_within,
        "raw_beta_among": beta_among,
        "raw_log_beta_contrast": math.log(beta_within / beta_among),
        "detrended_median_within_to_among_ratio": float(
            detrended["within_beta_summary"]["median_ratio_to_among_beta"]
        ),
        "growth_median_within_to_among_ratio": float(
            growth["within_beta_summary"]["median_ratio_to_among_beta"]
        ),
    }


def simulate(
    census_path: str | Path,
    simulations: int = SIMULATIONS,
    seed: int = SEED,
    batch_size: int = BATCH_SIZE,
) -> dict[str, object]:
    rows = load_colony_rows(census_path)
    state = _pooled_latent_state(rows)
    observed = _observed_statistics(rows)

    rng = np.random.default_rng(seed)
    outputs: dict[str, object] = {}

    for model_name, cv in ERROR_MODELS:
        raw_within: list[np.ndarray] = []
        raw_among: list[np.ndarray] = []
        raw_contrast: list[np.ndarray] = []
        detrended_ratio: list[np.ndarray] = []
        growth_ratio: list[np.ndarray] = []
        detrended_all: list[np.ndarray] = []
        growth_all: list[np.ndarray] = []

        completed = 0
        while completed < simulations:
            n = min(batch_size, simulations - completed)
            batch = _draw_batch(state, n, cv, rng)
            beta_within, beta_among, contrast = _raw_batch(batch)
            detrended, detrended_gt = _centered_ratio_batch(
                batch,
                "linear_detrended_log1p",
            )
            growth, growth_gt = _centered_ratio_batch(
                batch,
                "annual_log1p_growth",
            )
            raw_within.append(beta_within)
            raw_among.append(beta_among)
            raw_contrast.append(contrast)
            detrended_ratio.append(detrended)
            growth_ratio.append(growth)
            detrended_all.append(detrended_gt)
            growth_all.append(growth_gt)
            completed += n

        bw = np.concatenate(raw_within)
        ba = np.concatenate(raw_among)
        contrast = np.concatenate(raw_contrast)
        detrended = np.concatenate(detrended_ratio)
        growth = np.concatenate(growth_ratio)
        detrended_gt = np.concatenate(detrended_all)
        growth_gt = np.concatenate(growth_all)

        outputs[model_name] = {
            "multiplicative_cv": cv,
            "raw_beta_within": _tail(
                bw,
                observed["raw_beta_within"],
            ),
            "raw_beta_among": {
                **_summary(ba),
                "observed": observed["raw_beta_among"],
            },
            "raw_log_beta_contrast": _tail(
                contrast,
                observed["raw_log_beta_contrast"],
            ),
            "raw_probability_beta_within_exceeds_beta_among": float(
                np.mean(bw > ba)
            ),
            "linear_detrended_log1p": {
                "median_within_to_among_ratio": _tail(
                    detrended,
                    observed[
                        "detrended_median_within_to_among_ratio"
                    ],
                ),
                "probability_all_three_within_beta_exceed_among": float(
                    np.mean(detrended_gt)
                ),
            },
            "annual_log1p_growth": {
                "median_within_to_among_ratio": _tail(
                    growth,
                    observed["growth_median_within_to_among_ratio"],
                ),
                "probability_all_three_within_beta_exceed_among": float(
                    np.mean(growth_gt)
                ),
            },
        }

    raw_p = {
        name: float(
            outputs[name]["raw_log_beta_contrast"][
                "one_sided_probability_ge_observed"
            ]
        )
        for name, _ in ERROR_MODELS
    }
    raw_robust_all = all(value <= 0.05 for value in raw_p.values())
    raw_robust_low_error = all(
        raw_p[name] <= 0.05
        for name in ("poisson", "gamma_poisson_cv10")
    )

    latent_summary = {
        island: {
            "colony_count": len(state[island]["codes"]),
            "pooled_shares": {
                code: float(value)
                for code, value in zip(
                    state[island]["codes"],
                    np.asarray(
                        state[island]["pooled_shares"],
                        dtype=float,
                    ),
                )
            },
            "latent_within_island_beta": 1.0,
        }
        for island in STABLE_ROSTER_ISLANDS
    }

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-hierarchy-count-error-null-v1",
        "status": "post_hoc_measurement_error_robustness_diagnostic",
        "simulations_per_error_model": simulations,
        "seed": seed,
        "batch_size": batch_size,
        "observed_statistics": observed,
        "latent_complete_synchrony_state": latent_summary,
        "error_models": outputs,
        "decision": {
            "raw_hierarchy_unusual_under_all_error_models": bool(
                raw_robust_all
            ),
            "raw_hierarchy_unusual_under_poisson_and_cv10": bool(
                raw_robust_low_error
            ),
            "raw_hierarchy_measurement_error_robust": bool(
                raw_robust_all
            ),
        },
        "interpretation_boundary": {
            "stylized_error_not_empirically_calibrated_for_palmer": True,
            "failure_does_not_prove_count_error_explanation": True,
            "success_does_not_estimate_actual_observer_error": True,
            "centered_log_signals_are_not_exact_wang_loreau_partitions": True,
            "no_new_error_models_without_external_calibration": True,
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
