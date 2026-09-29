"""Zero-boundary audit for Palmer durable colony extinction."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

from .colony_extinction_hazard import (
    _event_risk_sets,
    build_transitions,
    load_rows,
    standardize_risk_sets,
)

N = 100_000
SEED = 20260930
MODELS = {
    "poisson": 0.0,
    "gamma_poisson_cv10": 0.10,
    "gamma_poisson_cv20": 0.20,
}


def subset_dist(risk: dict[str, object], cv: float):
    k = int(risk["k"])
    z = np.asarray(risk["z"], dtype=float)
    prior = np.asarray(risk["prior"], dtype=float)
    nxt = np.asarray(risk["current"], dtype=float)
    m = len(prior)

    rate = float(nxt.sum() / prior.sum())
    mu = rate * prior
    if cv == 0:
        q = np.exp(-mu)
    else:
        shape = 1.0 / (cv * cv)
        q = np.power(shape / (shape + mu), shape)

    q = np.clip(q, 1e-300, 1 - 1e-15)
    logod = np.log(q) - np.log1p(-q)
    combos = list(itertools.combinations(range(m), k))
    logw = np.asarray([logod[list(combo)].sum() for combo in combos])
    weights = np.exp(logw - logw.max())
    weights /= weights.sum()

    values = []
    total = float(z.sum())
    for combo in combos:
        selected = z[list(combo)].sum()
        values.append(
            selected / k - (total - selected) / (m - k)
        )
    return np.asarray(values), weights, rate


def run(path: str | Path, n: int = N, seed: int = SEED) -> dict[str, object]:
    rows = load_rows(path)
    transitions = build_transitions(rows)
    standardized = standardize_risk_sets(transitions)
    risk_sets = _event_risk_sets(standardized)
    observed = float(
        np.mean([float(risk["observed_contrast"]) for risk in risk_sets])
    )

    models: dict[str, object] = {}
    for offset, (name, cv) in enumerate(MODELS.items()):
        rng = np.random.default_rng(seed + offset)
        null = np.zeros(n, dtype=float)
        rates = []
        for risk in risk_sets:
            values, weights, rate = subset_dist(risk, cv)
            rates.append(rate)
            null += values[rng.choice(len(values), size=n, p=weights)]
        null /= len(risk_sets)
        p = (1 + int(np.sum(null <= observed))) / (n + 1)
        models[name] = {
            "multiplicative_cv": cv,
            "observed_contrast": observed,
            "one_sided_lower_p": float(p),
            "null_mean": float(np.mean(null)),
            "null_sd": float(np.std(null, ddof=1)),
            "null_q025": float(np.quantile(null, 0.025)),
            "null_q50": float(np.quantile(null, 0.5)),
            "null_q975": float(np.quantile(null, 0.975)),
            "min_common_rate": float(np.min(rates)),
            "median_common_rate": float(np.median(rates)),
            "max_common_rate": float(np.max(rates)),
        }

    passed = all(
        float(result["one_sided_lower_p"]) <= 0.05
        for result in models.values()
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-colony-extinction-zero-boundary-audit-v1",
        "parent_primary_statistic": observed,
        "n_event_risk_sets": len(risk_sets),
        "simulations": n,
        "seed": seed,
        "models": models,
        "decision": {
            "exceeds_zero_boundary": passed,
            "size_selection_only": not passed,
        },
        "interpretation": {
            "small_colonies_disappear_first_descriptively": True,
            "size_ordering_stronger_than_proportional_zero_hitting": passed,
            "social_facilitation_supported_by_size_effect_alone": False,
            "next_question": (
                "Which colony-specific states make a colony small before "
                "it crosses the stochastic zero boundary?"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--simulations", type=int, default=N)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = run(args.census, args.simulations, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
