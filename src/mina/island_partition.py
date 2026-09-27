"""Test whether Palmer colony dynamics respect the observed island partition."""
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
MIN_RETENTION_FRACTION = 0.75


def complete_colony_panel(path: str | Path) -> dict[str, object]:
    """Return complete, temporally variable colony units over the frozen 1991-2017 panel."""
    rows = load_colony_rows(path)
    by_unit_year: dict[tuple[str, str, int], float] = defaultdict(float)
    all_codes: dict[str, set[str]] = {island: set() for island in ISLANDS}
    for row in rows:
        island = str(row["island"])
        colony = str(row["colony_code"])
        year = int(row["year"])
        if year not in YEARS:
            continue
        by_unit_year[(island, colony, year)] += float(row["breeding_pairs"])
        all_codes[island].add(colony)

    units: list[dict[str, object]] = []
    excluded_incomplete: dict[str, list[str]] = {island: [] for island in ISLANDS}
    excluded_zero_growth_variance: dict[str, list[str]] = {
        island: [] for island in ISLANDS
    }

    for island in ISLANDS:
        for colony in sorted(all_codes[island]):
            present = [year for year in YEARS if (island, colony, year) in by_unit_year]
            if len(present) != len(YEARS):
                excluded_incomplete[island].append(colony)
                continue
            counts = np.asarray(
                [by_unit_year[(island, colony, year)] for year in YEARS], dtype=float
            )
            growth = np.diff(np.log1p(counts))
            if float(np.std(growth, ddof=1)) <= 0:
                excluded_zero_growth_variance[island].append(colony)
                continue
            units.append(
                {
                    "island": island,
                    "colony_code": colony,
                    "counts": counts,
                    "mean_log1p_abundance": float(np.mean(np.log1p(counts))),
                }
            )

    eligible_sizes = {
        island: sum(str(unit["island"]) == island for unit in units)
        for island in ISLANDS
    }
    total_codes = {island: len(all_codes[island]) for island in ISLANDS}
    retention = {
        island: (
            eligible_sizes[island] / total_codes[island]
            if total_codes[island] > 0
            else 0.0
        )
        for island in ISLANDS
    }
    validity_pass = bool(
        all(eligible_sizes[island] >= 2 for island in ISLANDS)
        and all(retention[island] >= MIN_RETENTION_FRACTION for island in ISLANDS)
    )
    if any(eligible_sizes[island] < 2 for island in ISLANDS):
        raise ValueError(
            f"fewer than two eligible complete colony units: {eligible_sizes}"
        )

    return {
        "units": units,
        "eligible_group_sizes": eligible_sizes,
        "total_unique_codes": total_codes,
        "retention_fraction": retention,
        "validity_pass": validity_pass,
        "excluded_incomplete": excluded_incomplete,
        "excluded_zero_growth_variance": excluded_zero_growth_variance,
    }


def synchrony_phi(matrix: np.ndarray) -> float:
    """Loreau-de Mazancourt/Wang-Loreau synchrony on centered temporal fluctuations."""
    x = np.asarray(matrix, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 3:
        raise ValueError("synchrony requires >=2 units and >=3 time points")
    cov = np.cov(x, rowvar=True, ddof=1)
    sd = np.sqrt(np.clip(np.diag(cov), 0.0, None))
    if np.any(sd <= 0):
        raise ValueError("zero temporal variance in synchrony input")
    phi = float(np.sum(cov) / (np.sum(sd) ** 2))
    return float(np.clip(phi, 0.0, 1.0))


def wang_loreau_variability(count_matrix: np.ndarray) -> dict[str, float]:
    """Alpha, gamma and multiplicative beta variability for nonnegative counts."""
    x = np.asarray(count_matrix, dtype=float)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 3:
        raise ValueError("variability requires >=2 units and >=3 years")
    means = np.mean(x, axis=1)
    total_mean = float(np.sum(means))
    if total_mean <= 0:
        raise ValueError("zero aggregate mean")
    cov = np.cov(x, rowvar=True, ddof=1)
    sd = np.sqrt(np.clip(np.diag(cov), 0.0, None))
    alpha = float((np.sum(sd) / total_mean) ** 2)
    gamma = float(np.sum(cov) / (total_mean**2))
    phi = float(gamma / alpha) if alpha > 0 else float("nan")
    beta = float(1.0 / phi) if phi > 0 else float("inf")
    return {
        "alpha_cv2": alpha,
        "gamma_cv2": gamma,
        "phi": phi,
        "beta": beta,
    }


def _fisher_mean(values: np.ndarray) -> float:
    vals = np.asarray(values, dtype=float)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        raise ValueError("no finite pairwise correlations")
    vals = np.clip(vals, -0.999999, 0.999999)
    return float(np.tanh(np.mean(np.arctanh(vals))))


def _partition_core(
    counts: np.ndarray,
    growth: np.ndarray,
    corr: np.ndarray,
    labels: np.ndarray,
) -> dict[str, object]:
    same = labels[:, None] == labels[None, :]
    upper = np.triu(np.ones_like(same, dtype=bool), k=1)
    within_r = _fisher_mean(corr[upper & same])
    between_r = _fisher_mean(corr[upper & ~same])

    within_phi: dict[str, float] = {}
    aggregate_growth: list[np.ndarray] = []
    for group in ISLANDS:
        idx = np.flatnonzero(labels == group)
        if idx.size < 2:
            raise ValueError(f"group {group} has fewer than two units")
        within_phi[group] = synchrony_phi(growth[idx, :])
        totals = np.sum(counts[idx, :], axis=0)
        aggregate_growth.append(np.diff(np.log1p(totals)))

    mean_within_phi = float(np.mean(list(within_phi.values())))
    among_group_phi = synchrony_phi(np.vstack(aggregate_growth))
    return {
        "within_fisher_mean_r": within_r,
        "between_fisher_mean_r": between_r,
        "partition_contrast_r": within_r - between_r,
        "mean_within_growth_phi": mean_within_phi,
        "among_group_total_growth_phi": among_group_phi,
        "hierarchy_gap_phi": among_group_phi - mean_within_phi,
        "within_growth_phi_by_group": within_phi,
    }


def partition_metrics(counts: np.ndarray, labels: np.ndarray) -> dict[str, object]:
    growth = np.diff(np.log1p(counts), axis=1)
    corr = np.corrcoef(growth)
    core = _partition_core(counts, growth, corr, labels)
    core["wang_loreau_by_group"] = {
        group: wang_loreau_variability(counts[np.flatnonzero(labels == group), :])
        for group in ISLANDS
    }
    return core


def _size_strata(
    values: np.ndarray, n_strata: int = N_SIZE_STRATA
) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    strata = np.empty(values.size, dtype=int)
    for rank, idx in enumerate(order):
        strata[idx] = min(n_strata - 1, (rank * n_strata) // values.size)
    return strata


def _permute_labels_within_strata(
    labels: np.ndarray,
    strata: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    out = labels.copy()
    for stratum in sorted(set(int(value) for value in strata)):
        idx = np.flatnonzero(strata == stratum)
        out[idx] = rng.permutation(out[idx])
    return out


def _p_upper(null: np.ndarray, observed: float) -> float:
    return float((1 + np.sum(null >= observed)) / (null.size + 1))


def _p_lower(null: np.ndarray, observed: float) -> float:
    return float((1 + np.sum(null <= observed)) / (null.size + 1))


def _p_two_sided(null: np.ndarray, observed: float) -> float:
    lower = _p_lower(null, observed)
    upper = _p_upper(null, observed)
    return float(min(1.0, 2.0 * min(lower, upper)))


def analyze(
    path: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 99:
        raise ValueError("at least 99 permutations are required")

    panel = complete_colony_panel(path)
    units = panel["units"]
    counts = np.vstack(
        [np.asarray(unit["counts"], dtype=float) for unit in units]
    )
    labels = np.asarray(
        [str(unit["island"]) for unit in units], dtype=object
    )
    mean_size = np.asarray(
        [float(unit["mean_log1p_abundance"]) for unit in units], dtype=float
    )
    strata = _size_strata(mean_size)
    growth = np.diff(np.log1p(counts), axis=1)
    corr = np.corrcoef(growth)

    observed = _partition_core(counts, growth, corr, labels)
    observed["wang_loreau_by_group"] = {
        group: wang_loreau_variability(
            counts[np.flatnonzero(labels == group), :]
        )
        for group in ISLANDS
    }

    rng = np.random.default_rng(seed)
    null_contrast = np.empty(n_permutations, dtype=float)
    null_gap = np.empty(n_permutations, dtype=float)
    null_within_phi = np.empty(n_permutations, dtype=float)

    for index in range(n_permutations):
        permuted = _permute_labels_within_strata(labels, strata, rng)
        metrics = _partition_core(counts, growth, corr, permuted)
        null_contrast[index] = float(metrics["partition_contrast_r"])
        null_gap[index] = float(metrics["hierarchy_gap_phi"])
        null_within_phi[index] = float(metrics["mean_within_growth_phi"])

    contrast = float(observed["partition_contrast_r"])
    gap = float(observed["hierarchy_gap_phi"])
    within_phi = float(observed["mean_within_growth_phi"])
    p_boundary = _p_two_sided(null_contrast, contrast)
    p_gap = _p_upper(null_gap, gap)
    p_within = _p_lower(null_within_phi, within_phi)
    validity_pass = bool(panel["validity_pass"])

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-island-partition-v1",
        "years": list(YEARS),
        "n_eligible_units": len(units),
        "eligible_group_sizes": panel["eligible_group_sizes"],
        "total_unique_codes": panel["total_unique_codes"],
        "retention_fraction": panel["retention_fraction"],
        "validity_pass": validity_pass,
        "excluded_incomplete": panel["excluded_incomplete"],
        "excluded_zero_growth_variance": panel[
            "excluded_zero_growth_variance"
        ],
        "observed": observed,
        "null": {
            "type": (
                "island labels permuted within five predeclared "
                "mean-log1p-abundance rank strata"
            ),
            "n_size_strata": N_SIZE_STRATA,
            "n_permutations": n_permutations,
            "seed": seed,
            "partition_contrast_r": {
                "mean": float(np.mean(null_contrast)),
                "sd": float(np.std(null_contrast, ddof=1)),
                "q025": float(np.quantile(null_contrast, 0.025)),
                "q975": float(np.quantile(null_contrast, 0.975)),
                "two_sided_p": p_boundary,
            },
            "hierarchy_gap_phi": {
                "mean": float(np.mean(null_gap)),
                "sd": float(np.std(null_gap, ddof=1)),
                "q95": float(np.quantile(null_gap, 0.95)),
                "upper_p": p_gap,
            },
            "mean_within_growth_phi": {
                "mean": float(np.mean(null_within_phi)),
                "sd": float(np.std(null_within_phi, ddof=1)),
                "q05": float(np.quantile(null_within_phi, 0.05)),
                "lower_p": p_within,
            },
        },
        "decision": {
            "island_partition_detected": bool(
                validity_pass and p_boundary <= 0.05
            ),
            "within_island_spatial_insurance_supported": bool(
                validity_pass and gap > 0 and p_gap <= 0.05
            ),
            "pairwise_direction": (
                "within_island_more_synchronous"
                if contrast > 0
                else "within_island_less_synchronous"
                if contrast < 0
                else "no_contrast"
            ),
        },
        "interpretation_boundary": {
            "tests_island_partition_not_coastline_effect_beyond_distance": True,
            "colony_coordinates_not_used": True,
            "no_migration_inference_from_covariance_alone": True,
            "complete_case_colony_units_only": True,
            "distance_conditioned_test_requires_colony_gis_crosswalk": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--permutations", type=int, default=N_PERMUTATIONS
    )
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
