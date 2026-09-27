"""Missingness-aware Palmer colony covariance test for the island partition."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows

YEARS = tuple(range(1991, 2018))
N_PERMUTATIONS = 20_000
SEED = 20260927
N_SIZE_STRATA = 5
MIN_SHARED_GROWTH_INTERVALS = 4


def observed_units(path: str | Path) -> list[dict[str, object]]:
    rows = load_colony_rows(path)
    values: dict[tuple[str, str, int], float] = defaultdict(float)
    codes: dict[str, set[str]] = {island: set() for island in ISLANDS}
    for row in rows:
        year = int(row["year"])
        if year not in YEARS:
            continue
        island = str(row["island"])
        code = str(row["colony_code"])
        values[(island, code, year)] += float(row["breeding_pairs"])
        codes[island].add(code)

    units: list[dict[str, object]] = []
    for island in ISLANDS:
        for code in sorted(codes[island]):
            reported = {
                year: values[(island, code, year)]
                for year in YEARS
                if (island, code, year) in values
            }
            if not any(count > 0 for count in reported.values()):
                continue
            growth: dict[int, float] = {}
            for year in YEARS[1:]:
                if year in reported and year - 1 in reported:
                    growth[year] = math.log1p(reported[year]) - math.log1p(
                        reported[year - 1]
                    )
            units.append(
                {
                    "island": island,
                    "colony_code": code,
                    "n_reported_years": len(reported),
                    "n_growth_intervals": len(growth),
                    "mean_log1p_abundance": float(
                        np.mean([math.log1p(x) for x in reported.values()])
                    ),
                    "growth": growth,
                }
            )
    return units


def _pair_record(a: dict[str, object], b: dict[str, object]) -> dict[str, object] | None:
    ga = a["growth"]
    gb = b["growth"]
    shared = sorted(set(ga) & set(gb))
    if len(shared) < MIN_SHARED_GROWTH_INTERVALS:
        return None
    xa = np.asarray([float(ga[year]) for year in shared], dtype=float)
    xb = np.asarray([float(gb[year]) for year in shared], dtype=float)
    if float(np.std(xa, ddof=1)) <= 0 or float(np.std(xb, ddof=1)) <= 0:
        return None
    r = float(np.corrcoef(xa, xb)[0, 1])
    r = float(np.clip(r, -0.999999, 0.999999))
    return {
        "z": float(np.arctanh(r)),
        "weight": float(len(shared) - 3),
        "r": r,
        "n_shared": len(shared),
    }


def pair_table(units: list[dict[str, object]]) -> list[dict[str, object]]:
    pairs: list[dict[str, object]] = []
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            record = _pair_record(units[i], units[j])
            if record is None:
                continue
            pairs.append(
                {
                    "i": i,
                    "j": j,
                    **record,
                }
            )
    if not pairs:
        raise ValueError("no informative colony pairs")
    return pairs


def _weighted_fisher_mean(pairs: list[dict[str, object]], mask: np.ndarray) -> tuple[float, float, int]:
    selected = [pair for pair, keep in zip(pairs, mask.tolist()) if keep]
    if not selected:
        raise ValueError("empty pair class")
    weights = np.asarray([float(pair["weight"]) for pair in selected], dtype=float)
    z = np.asarray([float(pair["z"]) for pair in selected], dtype=float)
    weight_sum = float(np.sum(weights))
    if weight_sum <= 0:
        raise ValueError("non-positive Fisher information")
    return float(np.tanh(np.sum(weights * z) / weight_sum)), weight_sum, len(selected)


def contrast_for_labels(
    pairs: list[dict[str, object]],
    labels: np.ndarray,
) -> dict[str, float | int]:
    same = np.asarray(
        [labels[int(pair["i"])] == labels[int(pair["j"])] for pair in pairs],
        dtype=bool,
    )
    within, within_weight, n_within = _weighted_fisher_mean(pairs, same)
    between, between_weight, n_between = _weighted_fisher_mean(pairs, ~same)
    return {
        "within_fisher_mean_r": within,
        "between_fisher_mean_r": between,
        "partition_contrast_r": within - between,
        "within_information_weight": within_weight,
        "between_information_weight": between_weight,
        "n_within_pairs": n_within,
        "n_between_pairs": n_between,
    }


def _size_strata(values: np.ndarray, n_strata: int = N_SIZE_STRATA) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    strata = np.empty(values.size, dtype=int)
    for rank, idx in enumerate(order):
        strata[idx] = min(n_strata - 1, (rank * n_strata) // values.size)
    return strata


def _permute_labels(
    labels: np.ndarray,
    strata: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    out = labels.copy()
    for stratum in sorted(set(int(value) for value in strata)):
        idx = np.flatnonzero(strata == stratum)
        out[idx] = rng.permutation(out[idx])
    return out


def _p_two_sided(null: np.ndarray, observed: float) -> float:
    upper = (1 + int(np.sum(null >= observed))) / (null.size + 1)
    lower = (1 + int(np.sum(null <= observed))) / (null.size + 1)
    return float(min(1.0, 2.0 * min(upper, lower)))


def analyze(
    path: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 99:
        raise ValueError("at least 99 permutations are required")
    units = observed_units(path)
    labels = np.asarray([str(unit["island"]) for unit in units], dtype=object)
    group_sizes = {
        island: int(np.sum(labels == island))
        for island in ISLANDS
    }
    validity_groups = all(group_sizes[island] >= 2 for island in ISLANDS)
    pairs = pair_table(units)
    observed = contrast_for_labels(pairs, labels)
    validity_information = bool(
        float(observed["within_information_weight"]) > 0
        and float(observed["between_information_weight"]) > 0
    )
    validity_pass = bool(validity_groups and validity_information)

    sizes = np.asarray(
        [float(unit["mean_log1p_abundance"]) for unit in units], dtype=float
    )
    strata = _size_strata(sizes)
    rng = np.random.default_rng(seed)
    null = np.empty(n_permutations, dtype=float)
    for k in range(n_permutations):
        permuted = _permute_labels(labels, strata, rng)
        null[k] = float(
            contrast_for_labels(pairs, permuted)["partition_contrast_r"]
        )

    observed_contrast = float(observed["partition_contrast_r"])
    p = _p_two_sided(null, observed_contrast)
    included_codes = {
        island: [
            str(unit["colony_code"])
            for unit in units
            if str(unit["island"]) == island
        ]
        for island in ISLANDS
    }
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-island-partition-overlap-v1",
        "years": list(YEARS),
        "n_units": len(units),
        "group_sizes": group_sizes,
        "included_codes": included_codes,
        "n_informative_pairs": len(pairs),
        "validity_pass": validity_pass,
        "observed": observed,
        "null": {
            "type": (
                "island labels permuted within five fixed mean-log1p-abundance "
                "rank strata; trajectories and missingness remain attached to units"
            ),
            "n_size_strata": N_SIZE_STRATA,
            "n_permutations": n_permutations,
            "seed": seed,
            "mean": float(np.mean(null)),
            "sd": float(np.std(null, ddof=1)),
            "q025": float(np.quantile(null, 0.025)),
            "q975": float(np.quantile(null, 0.975)),
            "two_sided_p": p,
        },
        "decision": {
            "island_partition_supported": bool(validity_pass and p <= 0.05),
            "direction": (
                "within_island_more_synchronous"
                if observed_contrast > 0
                else "within_island_less_synchronous"
                if observed_contrast < 0
                else "no_contrast"
            ),
        },
        "interpretation_boundary": {
            "v1_complete_case_gate_remains_failed": True,
            "no_missing_as_zero": True,
            "no_colony_id_merging": True,
            "no_distance_adjustment": True,
            "no_dispersal_inference": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(args.census, args.permutations, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
