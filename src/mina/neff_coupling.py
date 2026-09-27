"""Mechanical-coupling diagnostic for the N_eff coefficient."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .colony_network import transition_rows
from .lter import ISLANDS, load_colony_rows
from .neff_permutation import availability_strata

OBSERVED_BETA = 0.11679896749684507
ERROR_MODELS = (
    ("poisson", 0.0),
    ("gamma_poisson_cv10", 0.10),
    ("gamma_poisson_cv20", 0.20),
)


def _state_compositions(
    census_path: str | Path,
) -> dict[tuple[int, str], dict[str, object]]:
    groups: dict[tuple[int, str], list[float]] = defaultdict(list)
    for row in load_colony_rows(census_path):
        groups[(int(row["year"]), str(row["island"]))].append(
            float(row["breeding_pairs"])
        )

    states: dict[tuple[int, str], dict[str, object]] = {}
    for key, counts in groups.items():
        positive = np.asarray([value for value in counts if value > 0], dtype=float)
        total = float(np.sum(counts))
        if total > 0:
            shares = positive / total
        else:
            shares = np.asarray([], dtype=float)
        states[key] = {"total": total, "shares": shares}
    return states


def _stratified_schedule(
    rows: list[dict[str, object]],
    rng: np.random.Generator,
) -> dict[int, int]:
    schedule: dict[int, int] = {}
    for _, years in availability_strata(rows).items():
        donors = rng.permutation(np.asarray(years, dtype=int)).tolist()
        schedule.update(
            {target: int(donor) for target, donor in zip(years, donors)}
        )
    return schedule


def _draw_counts(
    total: float,
    shares: np.ndarray,
    rng: np.random.Generator,
    multiplicative_cv: float,
) -> np.ndarray:
    if total <= 0:
        return np.zeros(0, dtype=float)
    if shares.size == 0:
        raise ValueError("positive state has no positive colony shares")

    base = total * shares
    while True:
        means = base.copy()
        if multiplicative_cv > 0:
            shape = 1.0 / (multiplicative_cv**2)
            factors = rng.gamma(
                shape=shape,
                scale=1.0 / shape,
                size=means.size,
            )
            means = means * factors
        counts = rng.poisson(means).astype(float)
        # Occupancy is known from the frozen census. Condition error draws on
        # retaining at least one detected breeding pair for known-positive states.
        if float(np.sum(counts)) > 0:
            return counts


def _effective(counts: np.ndarray) -> float:
    total = float(np.sum(counts))
    if total <= 0:
        raise ValueError("effective colony number undefined for zero total")
    positive = counts[counts > 0]
    shares = positive / total
    return float(1.0 / np.sum(shares**2))


def _fit_beta(
    islands: list[str],
    start_year: np.ndarray,
    current_total: np.ndarray,
    next_total: np.ndarray,
    effective: np.ndarray,
) -> float:
    levels = tuple(island for island in ISLANDS if island in set(islands))
    lookup = {island: index for index, island in enumerate(levels)}
    x = np.zeros((len(islands), len(levels)), dtype=float)
    for row_index, island in enumerate(islands):
        x[row_index, lookup[island]] = 1.0

    abundance = np.log1p(current_total)
    abundance = (abundance - float(np.mean(abundance))) / float(
        np.std(abundance, ddof=1)
    )
    year = (start_year - float(np.mean(start_year))) / float(
        np.std(start_year, ddof=1)
    )
    topology = np.log1p(effective)
    topology = (topology - float(np.mean(topology))) / float(
        np.std(topology, ddof=1)
    )
    design = np.column_stack([x, abundance, year, topology])
    growth = np.log1p(next_total) - np.log1p(current_total)
    beta, _, rank, _ = np.linalg.lstsq(design, growth, rcond=None)
    if rank != design.shape[1]:
        raise ValueError("rank deficient mechanical-coupling model")
    return float(beta[-1])


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)),
        "median": float(np.median(values)),
        "q_0_025": float(np.quantile(values, 0.025)),
        "q_0_05": float(np.quantile(values, 0.05)),
        "q_0_95": float(np.quantile(values, 0.95)),
        "q_0_975": float(np.quantile(values, 0.975)),
        "proportion_positive": float(np.mean(values > 0)),
    }


def simulate(
    census_path: str | Path,
    simulations: int = 10000,
    seed: int = 20260927,
) -> dict[str, object]:
    transitions = transition_rows(census_path)
    states = _state_compositions(census_path)

    islands = [str(row["island"]) for row in transitions]
    start_year = np.asarray(
        [float(row["start_year"]) for row in transitions], dtype=float
    )
    current_keys = [
        (int(row["start_year"]), str(row["island"])) for row in transitions
    ]
    next_keys = [
        (int(row["end_year"]), str(row["island"])) for row in transitions
    ]

    rng = np.random.default_rng(seed)
    outputs: dict[str, object] = {}

    for model_name, cv in ERROR_MODELS:
        coupled = np.empty(simulations, dtype=float)
        decoupled = np.empty(simulations, dtype=float)

        for replicate in range(simulations):
            schedule = _stratified_schedule(transitions, rng)
            predictor_counts: dict[tuple[int, str], np.ndarray] = {}
            independent_counts: dict[tuple[int, str], np.ndarray] = {}

            # Draw every island-year state needed by a transition. Start-year
            # composition is block-permuted; 2017 uses its observed composition
            # because it contributes only a next-year total, not N_eff.
            needed = sorted(set(current_keys) | set(next_keys))
            for year, island in needed:
                target = states[(year, island)]
                if float(target["total"]) <= 0:
                    predictor_counts[(year, island)] = np.zeros(0, dtype=float)
                    independent_counts[(year, island)] = np.zeros(0, dtype=float)
                    continue

                donor_year = schedule.get(year, year)
                donor = states[(donor_year, island)]
                shares = np.asarray(donor["shares"], dtype=float)
                predictor_counts[(year, island)] = _draw_counts(
                    float(target["total"]), shares, rng, cv
                )
                independent_counts[(year, island)] = _draw_counts(
                    float(target["total"]), shares, rng, cv
                )

            effective = np.asarray(
                [_effective(predictor_counts[key]) for key in current_keys],
                dtype=float,
            )
            current_coupled = np.asarray(
                [float(np.sum(predictor_counts[key])) for key in current_keys],
                dtype=float,
            )
            current_decoupled = np.asarray(
                [float(np.sum(independent_counts[key])) for key in current_keys],
                dtype=float,
            )
            next_independent = np.asarray(
                [float(np.sum(independent_counts[key])) for key in next_keys],
                dtype=float,
            )

            coupled[replicate] = _fit_beta(
                islands,
                start_year,
                current_coupled,
                next_independent,
                effective,
            )
            decoupled[replicate] = _fit_beta(
                islands,
                start_year,
                current_decoupled,
                next_independent,
                effective,
            )

        bias = coupled - decoupled
        exceed_coupled = int(np.sum(coupled >= OBSERVED_BETA))
        exceed_decoupled = int(np.sum(decoupled >= OBSERVED_BETA))
        outputs[model_name] = {
            "multiplicative_cv": cv,
            "coupled_beta": {
                **_summary(coupled),
                "exceedances_ge_observed": exceed_coupled,
                "one_sided_probability_ge_observed": (
                    1.0 + exceed_coupled
                ) / (simulations + 1.0),
            },
            "decoupled_beta": {
                **_summary(decoupled),
                "exceedances_ge_observed": exceed_decoupled,
                "one_sided_probability_ge_observed": (
                    1.0 + exceed_decoupled
                ) / (simulations + 1.0),
            },
            "paired_coupling_bias": {
                **_summary(bias),
                "median_fraction_of_observed_beta": float(
                    np.median(bias) / OBSERVED_BETA
                ),
                "mean_fraction_of_observed_beta": float(
                    np.mean(bias) / OBSERVED_BETA
                ),
            },
        }

    survives = all(
        float(outputs[name]["coupled_beta"]["one_sided_probability_ge_observed"])
        <= 0.05
        for name, _ in ERROR_MODELS
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-neff-mechanical-coupling-v1",
        "status": "post_positive_same_census_error_diagnostic",
        "simulations_per_error_model": simulations,
        "seed": seed,
        "observed_standardized_beta": OBSERVED_BETA,
        "transition_row_count": len(transitions),
        "end_year_count": len({int(row["end_year"]) for row in transitions}),
        "error_models": outputs,
        "decision": {
            "observed_beta_unusual_under_all_coupled_nulls": bool(survives),
        },
        "boundary": {
            "stylized_error_not_calibrated_observer_uncertainty": True,
            "year_block_latent_topology_alignment_destroyed": True,
            "held_out_predictive_gain_already_failed_permutation": True,
            "causal_habitat_claim": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260927)
    args = parser.parse_args()
    result = simulate(args.census, args.simulations, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
