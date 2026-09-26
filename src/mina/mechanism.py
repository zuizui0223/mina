"""Regional-local mechanism utilities for the frozen Palmer five-island result."""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np

ISLANDS = ("CHR", "COR", "HUM", "LIT", "TOR")
SUBOPTIMAL_HABITAT = {
    "LIT": 89.5,
    "COR": 63.0,
    "CHR": 46.8,
    "TOR": 44.3,
    "HUM": 44.2,
}


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size != y.size or x.size < 3:
        raise ValueError("correlation requires paired values")
    sx = float(np.std(x, ddof=1))
    sy = float(np.std(y, ddof=1))
    if sx <= 0 or sy <= 0:
        raise ValueError("zero variance")
    return float(np.corrcoef(x, y)[0, 1])


def _rank_no_ties(x: np.ndarray) -> np.ndarray:
    if len(set(float(v) for v in x)) != x.size:
        raise ValueError("exact rank helper assumes no ties")
    order = np.argsort(x)
    ranks = np.empty(x.size, dtype=float)
    ranks[order] = np.arange(x.size, dtype=float)
    return ranks


def _spearman(x: np.ndarray, y: np.ndarray) -> float:
    return _pearson(_rank_no_ties(x), _rank_no_ties(y))


def _exact_permutation_p(
    x: np.ndarray,
    y: np.ndarray,
    statistic,
) -> float:
    observed = abs(float(statistic(x, y)))
    exceed = 0
    total = 0
    for perm in itertools.permutations(y.tolist()):
        value = abs(float(statistic(x, np.asarray(perm, dtype=float))))
        exceed += int(value >= observed - 1e-12)
        total += 1
    return exceed / total


def static_habitat_validation(receipt: dict[str, object]) -> dict[str, object]:
    trend = receipt["trend_slopes_annual_multiplicative_change"]
    x = np.asarray([SUBOPTIMAL_HABITAT[i] for i in ISLANDS], dtype=float)
    y = np.asarray([float(trend[i]) for i in ISLANDS], dtype=float)

    pearson = _pearson(x, y)
    spearman = _spearman(x, y)
    design = np.column_stack([np.ones(x.size), x])
    beta, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if rank != 2:
        raise ValueError("rank-deficient habitat regression")
    fitted = design @ beta
    residual = y - fitted
    tss = float(np.sum((y - np.mean(y)) ** 2))
    sse = float(residual @ residual)

    return {
        "source": {
            "citation": "Fraser et al. 2013 Oceanography 26(3):207-209",
            "doi": "10.5670/oceanog.2013.64",
            "role": "published external predictor / updated-series replication",
        },
        "suboptimal_habitat_percent": SUBOPTIMAL_HABITAT,
        "frozen_1991_2017_annual_multiplicative_change": {
            island: float(trend[island]) for island in ISLANDS
        },
        "pearson_r": pearson,
        "pearson_exact_permutation_p_two_sided": _exact_permutation_p(
            x, y, _pearson
        ),
        "spearman_rho": spearman,
        "spearman_exact_permutation_p_two_sided": _exact_permutation_p(
            x, y, _spearman
        ),
        "ols_change_per_1pct_suboptimal_habitat": float(beta[1]),
        "ols_intercept": float(beta[0]),
        "ols_r2": 1.0 - sse / tss if tss > 0 else None,
        "interpretation_boundary": {
            "n_islands": 5,
            "external_relation_was_published_before_mina": True,
            "use_effect_size_not_binary_significance": True,
            "not_a_fresh_discovery_test": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lter-receipt", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    receipt = json.loads(args.lter_receipt.read_text(encoding="utf-8"))
    result = {
        "schema_version": 1,
        "analysis_id": "mina-palmer-static-habitat-validation-v1",
        "static_habitat": static_habitat_validation(receipt),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
