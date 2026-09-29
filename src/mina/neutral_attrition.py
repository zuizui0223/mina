"""Sequential neutral attrition null for Palmer breeding-patch concentration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .hierarchical_variability import EXPECTED_YEARS, STABLE_ROSTER_ISLANDS
from .lter import load_colony_rows

SIMULATIONS = 100_000
SEED = 20260930


def _matrix(rows, island):
    local = [r for r in rows if str(r["island"]) == island]
    codes = sorted({str(r["colony_code"]) for r in local})
    lookup = {
        (str(r["colony_code"]), int(r["year"])): float(r["breeding_pairs"])
        for r in local
    }
    matrix = np.asarray(
        [[lookup[(code, year)] for year in EXPECTED_YEARS] for code in codes],
        dtype=int,
    )
    return codes, matrix


def _neff(matrix):
    total = np.sum(matrix, axis=1, dtype=float)
    squares = np.sum(np.asarray(matrix, dtype=float) ** 2, axis=1)
    out = np.full(total.shape, np.nan, dtype=float)
    valid = total > 0
    out[valid] = total[valid] ** 2 / squares[valid]
    return out


def _slope_batch(values, years):
    x = np.asarray(years, dtype=float)
    centered = x - float(np.mean(x))
    denom = float(np.sum(centered**2))
    centered_values = values - np.mean(values, axis=1, keepdims=True)
    return np.sum(centered_values * centered[None, :], axis=1) / denom


def _multinomial_varying_probs(rng, total, probs):
    """Vectorized multinomial via sequential binomials for row-specific p."""
    probs = np.asarray(probs, dtype=float)
    n_rep, n_cat = probs.shape
    remaining_n = np.full(n_rep, int(total), dtype=int)
    remaining_p = np.ones(n_rep, dtype=float)
    out = np.zeros((n_rep, n_cat), dtype=int)
    for j in range(n_cat - 1):
        conditional = np.divide(
            probs[:, j],
            remaining_p,
            out=np.zeros(n_rep, dtype=float),
            where=remaining_p > 0,
        )
        conditional = np.clip(conditional, 0.0, 1.0)
        draw = rng.binomial(remaining_n, conditional)
        out[:, j] = draw
        remaining_n -= draw
        remaining_p = np.maximum(0.0, remaining_p - probs[:, j])
    out[:, -1] = remaining_n
    return out


def _simulate_island(matrix, simulations, rng):
    totals = np.sum(matrix, axis=0, dtype=int)
    years = np.asarray(EXPECTED_YEARS, dtype=int)
    positive = totals > 0
    observed_neff = _neff(matrix.T)
    observed_values = observed_neff[positive]
    observed_slope = float(_slope_batch(observed_values[None, :], years[positive])[0])
    observed_terminal = float(observed_values[-1])

    previous = np.broadcast_to(matrix[:, 0], (simulations, matrix.shape[0])).copy()
    neff = np.full((simulations, len(years)), np.nan, dtype=float)
    start_total = np.sum(previous, axis=1, dtype=float)
    neff[:, 0] = start_total**2 / np.sum(previous.astype(float) ** 2, axis=1)

    for t in range(1, len(years)):
        total = int(totals[t])
        if total <= 0:
            previous = np.zeros_like(previous)
            continue
        row_total = np.sum(previous, axis=1, dtype=float)
        probs = np.divide(
            previous,
            row_total[:, None],
            out=np.zeros_like(previous, dtype=float),
            where=row_total[:, None] > 0,
        )
        current = _multinomial_varying_probs(rng, total, probs)
        squares = np.sum(current.astype(float) ** 2, axis=1)
        neff[:, t] = total**2 / squares
        previous = current

    sim_values = neff[:, positive]
    slopes = _slope_batch(sim_values, years[positive])
    terminal = sim_values[:, -1]
    return {
        "observed_slope": observed_slope,
        "observed_terminal_neff": observed_terminal,
        "simulated_slopes": slopes,
        "simulated_terminal_neff": terminal,
        "positive_years": years[positive],
        "totals": totals,
    }


def _summary(values):
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)),
        "q025": float(np.quantile(values, 0.025)),
        "median": float(np.median(values)),
        "q975": float(np.quantile(values, 0.975)),
    }


def simulate(census_path, simulations=SIMULATIONS, seed=SEED):
    rows = load_colony_rows(census_path)
    rng = np.random.default_rng(seed)
    per_island = {}
    joint_flags = np.ones(simulations, dtype=bool)

    for island in STABLE_ROSTER_ISLANDS:
        codes, matrix = _matrix(rows, island)
        rec = _simulate_island(matrix, simulations, rng)
        slopes = rec["simulated_slopes"]
        terminal = rec["simulated_terminal_neff"]
        obs_slope = float(rec["observed_slope"])
        obs_terminal = float(rec["observed_terminal_neff"])
        slope_tail = (1 + int(np.sum(slopes <= obs_slope))) / (simulations + 1)
        terminal_tail = (1 + int(np.sum(terminal <= obs_terminal))) / (simulations + 1)
        joint_flags &= slopes <= obs_slope
        per_island[island] = {
            "colony_count": len(codes),
            "observed_slope": obs_slope,
            "neutral_slope": _summary(slopes),
            "one_sided_probability_slope_le_observed": float(slope_tail),
            "observed_terminal_neff": obs_terminal,
            "neutral_terminal_neff": _summary(terminal),
            "one_sided_probability_terminal_le_observed": float(terminal_tail),
            "first_year": int(rec["positive_years"][0]),
            "last_positive_year": int(rec["positive_years"][-1]),
        }

    joint_count = int(np.sum(joint_flags))
    joint_p = (1 + joint_count) / (simulations + 1)
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-neutral-attrition-v1",
        "contract_id": "mina-palmer-neutral-attrition-v1",
        "status": "post_hazard_sequential_neutral_drift_diagnostic",
        "simulations": simulations,
        "seed": seed,
        "eligible_islands": list(STABLE_ROSTER_ISLANDS),
        "per_island": per_island,
        "joint_all_three_slopes_le_observed": {
            "count": joint_count,
            "probability": float(joint_p),
        },
        "litchfield_forced_zero_note": {
            "observed_extinction_year": 2007,
            "fraction_complete_local_extinction_by_2007": 1.0,
            "reason": "The null conditions on the observed island total, which is exactly zero from 2007 onward; this output is structural rather than inferential.",
        },
        "decision": {
            "COR_more_concentrated_than_neutral": bool(
                per_island["COR"]["one_sided_probability_slope_le_observed"] <= 0.05
            ),
            "HUM_more_concentrated_than_neutral": bool(
                per_island["HUM"]["one_sided_probability_slope_le_observed"] <= 0.05
            ),
            "LIT_more_concentrated_than_neutral": bool(
                per_island["LIT"]["one_sided_probability_slope_le_observed"] <= 0.05
            ),
        },
        "interpretation_boundary": {
            "neutral_fit_does_not_prove_interactions_absent": True,
            "rejection_does_not_identify_predation_snow_or_habitat": True,
            "zero_is_absorbing_in_null": True,
            "observed_island_total_path_is_conditioned_on": True,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--simulations", type=int, default=SIMULATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = simulate(args.census, args.simulations, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
