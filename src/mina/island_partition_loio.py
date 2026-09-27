"""Leave-one-island-out robustness for the frozen overlap partition result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .island_partition_overlap import (
    ISLANDS,
    N_SIZE_STRATA,
    _p_two_sided,
    _permute_labels,
    _size_strata,
    contrast_for_labels,
    observed_units,
    pair_table,
)

N_PERMUTATIONS = 20_000
BASE_SEED = 20260927


def analyze_subset(
    units: list[dict[str, object]],
    omitted: str,
    n_permutations: int,
    seed: int,
) -> dict[str, object]:
    local = [unit for unit in units if str(unit["island"]) != omitted]
    labels = np.asarray([str(unit["island"]) for unit in local], dtype=object)
    pairs = pair_table(local)
    observed = contrast_for_labels(pairs, labels)
    sizes = np.asarray(
        [float(unit["mean_log1p_abundance"]) for unit in local],
        dtype=float,
    )
    strata = _size_strata(sizes, N_SIZE_STRATA)
    rng = np.random.default_rng(seed)
    null = np.empty(n_permutations, dtype=float)
    for index in range(n_permutations):
        permuted = _permute_labels(labels, strata, rng)
        null[index] = float(
            contrast_for_labels(pairs, permuted)["partition_contrast_r"]
        )
    contrast = float(observed["partition_contrast_r"])
    p = _p_two_sided(null, contrast)
    return {
        "omitted_island": omitted,
        "n_units": len(local),
        "n_informative_pairs": len(pairs),
        "observed": observed,
        "null": {
            "n_permutations": n_permutations,
            "seed": seed,
            "mean": float(np.mean(null)),
            "sd": float(np.std(null, ddof=1)),
            "q025": float(np.quantile(null, 0.025)),
            "q975": float(np.quantile(null, 0.975)),
            "two_sided_p": p,
        },
        "positive_contrast": bool(contrast > 0),
        "p_le_0_05": bool(p <= 0.05),
    }


def analyze(
    path: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    base_seed: int = BASE_SEED,
) -> dict[str, object]:
    units = observed_units(path)
    results = {}
    for index, island in enumerate(ISLANDS):
        results[island] = analyze_subset(
            units,
            island,
            n_permutations,
            base_seed + index,
        )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-island-partition-loio-v1",
        "results": results,
        "decision": {
            "directional_robustness": all(
                bool(results[island]["positive_contrast"])
                for island in ISLANDS
            ),
            "strong_permutation_robustness": all(
                bool(results[island]["p_le_0_05"])
                for island in ISLANDS
            ),
        },
        "interpretation_boundary": {
            "post_positive_diagnostic": True,
            "does_not_replace_primary_overlap_result": True,
            "no_selected_island_exclusions": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--base-seed", type=int, default=BASE_SEED)
    args = parser.parse_args()
    result = analyze(args.census, args.permutations, args.base_seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
