"""Validation of Palmer island coherence across colony-ID reporting regimes."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import load_colony_rows
from .island_partition import (
    N_SIZE_STRATA,
    _fisher_mean,
    _p_two_sided,
    _permute_labels_within_strata,
    _size_strata,
)

ALL_ISLANDS = ("CHR", "COR", "HUM", "LIT", "TOR")
EXTANT_ISLANDS = ("CHR", "COR", "HUM", "TOR")
PHASES = {
    "early_1991_2006": tuple(range(1991, 2007)),
    "late_2007_2017": tuple(range(2007, 2018)),
}
N_PERMUTATIONS = 20_000
SEED = 20260927
MIN_RETENTION_FRACTION = 0.75


def phase_panel(
    path: str | Path,
    years: tuple[int, ...],
    islands: tuple[str, ...],
) -> dict[str, object]:
    rows = load_colony_rows(path)
    by_unit_year: dict[tuple[str, str, int], float] = defaultdict(float)
    seen_codes: dict[str, set[str]] = {island: set() for island in islands}
    positive_codes: dict[str, set[str]] = {island: set() for island in islands}

    for row in rows:
        island = str(row["island"])
        year = int(row["year"])
        if island not in islands or year not in years:
            continue
        code = str(row["colony_code"])
        value = float(row["breeding_pairs"])
        by_unit_year[(island, code, year)] += value
        seen_codes[island].add(code)
        if value > 0:
            positive_codes[island].add(code)

    units: list[dict[str, object]] = []
    incomplete: dict[str, list[str]] = {island: [] for island in islands}
    zero_var: dict[str, list[str]] = {island: [] for island in islands}

    for island in islands:
        for code in sorted(positive_codes[island]):
            present = [year for year in years if (island, code, year) in by_unit_year]
            if len(present) != len(years):
                incomplete[island].append(code)
                continue
            counts = np.asarray(
                [by_unit_year[(island, code, year)] for year in years],
                dtype=float,
            )
            growth = np.diff(np.log1p(counts))
            if growth.size < 3 or float(np.std(growth, ddof=1)) <= 0:
                zero_var[island].append(code)
                continue
            units.append(
                {
                    "island": island,
                    "colony_code": code,
                    "counts": counts,
                    "mean_log1p_abundance": float(np.mean(np.log1p(counts))),
                }
            )

    eligible_sizes = {
        island: sum(str(unit["island"]) == island for unit in units)
        for island in islands
    }
    candidate_sizes = {
        island: len(positive_codes[island]) for island in islands
    }
    retention = {
        island: (
            eligible_sizes[island] / candidate_sizes[island]
            if candidate_sizes[island] > 0
            else 0.0
        )
        for island in islands
    }
    validity = bool(
        all(eligible_sizes[island] >= 2 for island in islands)
        and all(retention[island] >= MIN_RETENTION_FRACTION for island in islands)
    )

    return {
        "units": units,
        "candidate_positive_history_codes": candidate_sizes,
        "eligible_group_sizes": eligible_sizes,
        "retention_fraction": retention,
        "validity_pass": validity,
        "excluded_incomplete": incomplete,
        "excluded_zero_growth_variance": zero_var,
        "reported_but_never_positive_codes": {
            island: sorted(seen_codes[island] - positive_codes[island])
            for island in islands
        },
    }


def _partition_contrast(
    counts: np.ndarray,
    labels: np.ndarray,
) -> dict[str, float]:
    growth = np.diff(np.log1p(counts), axis=1)
    corr = np.corrcoef(growth)
    same = labels[:, None] == labels[None, :]
    upper = np.triu(np.ones_like(same, dtype=bool), k=1)
    within = _fisher_mean(corr[upper & same])
    between = _fisher_mean(corr[upper & ~same])
    return {
        "within_fisher_mean_r": within,
        "between_fisher_mean_r": between,
        "partition_contrast_r": within - between,
    }


def run_phase(
    path: str | Path,
    years: tuple[int, ...],
    islands: tuple[str, ...],
    n_permutations: int,
    seed: int,
) -> dict[str, object]:
    panel = phase_panel(path, years, islands)
    units = panel["units"]
    counts = np.vstack([np.asarray(unit["counts"], dtype=float) for unit in units])
    labels = np.asarray([str(unit["island"]) for unit in units], dtype=object)
    mean_size = np.asarray(
        [float(unit["mean_log1p_abundance"]) for unit in units],
        dtype=float,
    )
    strata = _size_strata(mean_size, N_SIZE_STRATA)
    observed = _partition_contrast(counts, labels)

    rng = np.random.default_rng(seed)
    null = np.empty(n_permutations, dtype=float)
    for index in range(n_permutations):
        perm = _permute_labels_within_strata(labels, strata, rng)
        null[index] = float(_partition_contrast(counts, perm)["partition_contrast_r"])

    p = _p_two_sided(null, float(observed["partition_contrast_r"]))
    supported = bool(
        panel["validity_pass"]
        and float(observed["partition_contrast_r"]) > 0
        and p <= 0.05
    )
    return {
        "years": list(years),
        "islands": list(islands),
        "n_eligible_units": len(units),
        "candidate_positive_history_codes": panel[
            "candidate_positive_history_codes"
        ],
        "eligible_group_sizes": panel["eligible_group_sizes"],
        "retention_fraction": panel["retention_fraction"],
        "validity_pass": panel["validity_pass"],
        "excluded_incomplete": panel["excluded_incomplete"],
        "excluded_zero_growth_variance": panel[
            "excluded_zero_growth_variance"
        ],
        "reported_but_never_positive_codes": panel[
            "reported_but_never_positive_codes"
        ],
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
        "supported": supported,
    }


def analyze(
    path: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 99:
        raise ValueError("at least 99 permutations are required")

    five: dict[str, object] = {}
    extant: dict[str, object] = {}
    for offset, (name, years) in enumerate(PHASES.items()):
        five[name] = run_phase(
            path, years, ALL_ISLANDS, n_permutations, seed + 10 * offset
        )
        extant[name] = run_phase(
            path, years, EXTANT_ISLANDS, n_permutations, seed + 10 * offset + 1
        )

    primary = bool(all(bool(five[name]["supported"]) for name in PHASES))
    no_litchfield = bool(all(bool(extant[name]["supported"]) for name in PHASES))
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-island-coherence-regime-validation-v1",
        "five_island_phase_replication": five,
        "four_extant_island_sensitivity": extant,
        "decision": {
            "island_coherence_replicated_across_id_regimes": primary,
            "not_litchfield_driven": no_litchfield,
            "strong_confirmation": bool(primary and no_litchfield),
        },
        "interpretation_boundary": {
            "original_primary_result_unchanged": True,
            "phase_boundary_fixed_from_id_audit": True,
            "positive_history_candidate_definition_frozen_pre_outcome": True,
            "no_imputation_or_code_merging": True,
            "does_not_test_distance_conditioned_coastline_effect": True,
            "does_not_retest_spatial_insurance": True,
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
