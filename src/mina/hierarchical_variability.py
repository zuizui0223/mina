"""Nested temporal-variability decomposition for the Palmer Adélie census."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows

STABLE_ROSTER_ISLANDS = ("COR", "HUM", "LIT")
PERSISTENT_STABLE_ROSTER_ISLANDS = ("COR", "HUM")
PERSISTENT_ISLANDS = ("CHR", "COR", "HUM", "TOR")
EXPECTED_YEARS = tuple(range(1991, 2018))
PRE_EXTINCTION_YEARS = tuple(range(1991, 2007))


def colony_roster_audit(rows: list[dict[str, object]]) -> dict[str, object]:
    by_island_year: dict[str, dict[int, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for row in rows:
        by_island_year[str(row["island"])][int(row["year"])].add(
            str(row["colony_code"])
        )

    out: dict[str, object] = {}
    for island in ISLANDS:
        by_year = by_island_year.get(island, {})
        years = sorted(by_year)
        rosters = [tuple(sorted(by_year[year])) for year in years]
        variants = sorted(set(rosters))
        change_years: list[int] = []
        previous: tuple[str, ...] | None = None
        for year, roster in zip(years, rosters):
            if previous is not None and roster != previous:
                change_years.append(year)
            previous = roster
        union = (
            sorted(set().union(*(by_year[year] for year in years)))
            if years
            else []
        )
        intersection = (
            sorted(set.intersection(*(by_year[year] for year in years)))
            if years
            else []
        )
        out[island] = {
            "n_years": len(years),
            "first_year": years[0] if years else None,
            "last_year": years[-1] if years else None,
            "roster_stable": len(variants) == 1,
            "roster_variant_count": len(variants),
            "roster_sizes": sorted({len(roster) for roster in rosters}),
            "union_code_count": len(union),
            "intersection_code_count": len(intersection),
            "union_codes": union,
            "intersection_codes": intersection,
            "change_years": change_years,
        }
    return out


def _matrix(
    series: dict[str, np.ndarray],
) -> tuple[list[str], np.ndarray]:
    if not series:
        raise ValueError("empty time-series collection")
    labels = sorted(series)
    arrays = [np.asarray(series[label], dtype=float) for label in labels]
    lengths = {array.size for array in arrays}
    if len(lengths) != 1 or next(iter(lengths)) < 3:
        raise ValueError("time series must share at least three observations")
    matrix = np.vstack(arrays)
    if not np.all(np.isfinite(matrix)):
        raise ValueError("non-finite time-series value")
    return labels, matrix


def wang_loreau_raw(
    series: dict[str, np.ndarray],
) -> dict[str, object]:
    """Squared-CV alpha/beta/gamma variability for additive raw abundance."""
    labels, matrix = _matrix(series)
    if np.any(matrix < 0):
        raise ValueError("Wang-Loreau raw abundance must be nonnegative")
    means = np.mean(matrix, axis=1)
    sds = np.std(matrix, axis=1, ddof=1)
    total_mean = float(np.sum(means))
    if total_mean <= 0:
        raise ValueError("nonpositive aggregate mean")
    alpha = float((np.sum(sds) / total_mean) ** 2)
    aggregate = np.sum(matrix, axis=0)
    gamma = float((np.std(aggregate, ddof=1) / total_mean) ** 2)
    if alpha <= 0 or gamma <= 0:
        raise ValueError("zero variability is not estimable for beta partition")
    beta = alpha / gamma
    phi = gamma / alpha
    return {
        "n_units": len(labels),
        "n_years": int(matrix.shape[1]),
        "total_mean_abundance": total_mean,
        "alpha_cv2": alpha,
        "gamma_cv2": gamma,
        "beta_spatial": beta,
        "phi_synchrony": phi,
        "identity_error_beta_phi": abs(beta * phi - 1.0),
    }


def covariance_synchrony(
    series: dict[str, np.ndarray],
) -> dict[str, object]:
    """Covariance synchrony for centered or otherwise nonpositive signals."""
    labels, matrix = _matrix(series)
    sds = np.std(matrix, axis=1, ddof=1)
    potential_variance = float(np.sum(sds) ** 2)
    aggregate_variance = float(
        np.var(np.sum(matrix, axis=0), ddof=1)
    )
    if potential_variance <= 0 or aggregate_variance <= 0:
        raise ValueError("zero variance is not estimable for synchrony")
    phi = aggregate_variance / potential_variance
    beta = 1.0 / phi
    return {
        "n_units": len(labels),
        "n_observations": int(matrix.shape[1]),
        "potential_aggregate_variance": potential_variance,
        "observed_aggregate_variance": aggregate_variance,
        "phi_synchrony": phi,
        "beta_spatial": beta,
        "identity_error_beta_phi": abs(beta * phi - 1.0),
    }


def _island_year_lookup(
    rows: list[dict[str, object]],
) -> dict[tuple[str, int], float]:
    lookup: dict[tuple[str, int], float] = defaultdict(float)
    for row in rows:
        lookup[(str(row["island"]), int(row["year"]))] += float(
            row["breeding_pairs"]
        )
    return dict(lookup)


def _colony_year_lookup(
    rows: list[dict[str, object]],
) -> dict[tuple[str, str, int], float]:
    return {
        (
            str(row["island"]),
            str(row["colony_code"]),
            int(row["year"]),
        ): float(row["breeding_pairs"])
        for row in rows
    }


def island_series(
    rows: list[dict[str, object]],
    islands: tuple[str, ...],
    years: tuple[int, ...],
) -> dict[str, np.ndarray]:
    lookup = _island_year_lookup(rows)
    series: dict[str, np.ndarray] = {}
    for island in islands:
        values = []
        for year in years:
            key = (island, year)
            if key not in lookup:
                raise ValueError(f"missing island-year total: {key}")
            values.append(lookup[key])
        series[island] = np.asarray(values, dtype=float)
    return series


def subcolony_series(
    rows: list[dict[str, object]],
    islands: tuple[str, ...],
    years: tuple[int, ...],
    audit: dict[str, object],
) -> dict[str, np.ndarray]:
    lookup = _colony_year_lookup(rows)
    out: dict[str, np.ndarray] = {}
    for island in islands:
        rec = audit[island]
        if not bool(rec["roster_stable"]):
            raise ValueError(f"nonstable colony-code roster: {island}")
        codes = list(rec["intersection_codes"])
        for code in codes:
            values = []
            for year in years:
                key = (island, str(code), year)
                if key not in lookup:
                    raise ValueError(f"missing colony census cell: {key}")
                values.append(lookup[key])
            out[f"{island}:{code}"] = np.asarray(values, dtype=float)
    return out


def nested_raw_decomposition(
    rows: list[dict[str, object]],
    islands: tuple[str, ...],
    years: tuple[int, ...],
    audit: dict[str, object],
) -> dict[str, object]:
    sub = subcolony_series(rows, islands, years, audit)
    isl = island_series(rows, islands, years)
    sub_stats = wang_loreau_raw(sub)
    island_stats = wang_loreau_raw(isl)

    alpha_sub = float(sub_stats["alpha_cv2"])
    alpha_island = float(island_stats["alpha_cv2"])
    gamma_archipelago = float(island_stats["gamma_cv2"])
    beta_within = alpha_sub / alpha_island
    beta_among = alpha_island / gamma_archipelago
    beta_total = alpha_sub / gamma_archipelago
    product = beta_within * beta_among

    if beta_total > 0 and not math.isclose(beta_total, 1.0):
        total_log = math.log(beta_total)
        within_log_share = math.log(beta_within) / total_log
        among_log_share = math.log(beta_among) / total_log
    else:
        within_log_share = None
        among_log_share = None

    per_island = {}
    for island in islands:
        prefix = f"{island}:"
        local = {
            key: value
            for key, value in sub.items()
            if key.startswith(prefix)
        }
        per_island[island] = wang_loreau_raw(local)

    return {
        "islands": list(islands),
        "first_year": years[0],
        "last_year": years[-1],
        "n_years": len(years),
        "n_subcolonies": len(sub),
        "alpha_subcolony_cv2": alpha_sub,
        "alpha_island_cv2": alpha_island,
        "gamma_archipelago_cv2": gamma_archipelago,
        "beta_within_islands": beta_within,
        "beta_among_islands": beta_among,
        "beta_total_subcolony_to_archipelago": beta_total,
        "multiplicative_identity_error": abs(beta_total - product),
        "log_beta_share_within_islands": within_log_share,
        "log_beta_share_among_islands": among_log_share,
        "per_island_subcolony_variability": per_island,
    }


def _linear_detrended_log1p(values: np.ndarray) -> np.ndarray:
    y = np.log1p(np.asarray(values, dtype=float))
    t = np.arange(y.size, dtype=float)
    x = np.column_stack([np.ones(y.size), t])
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank != x.shape[1]:
        raise ValueError("rank-deficient detrending design")
    return y - x @ beta


def _annual_log1p_growth(values: np.ndarray) -> np.ndarray:
    y = np.log1p(np.asarray(values, dtype=float))
    return np.diff(y)


def centered_signal_sensitivity(
    rows: list[dict[str, object]],
    islands: tuple[str, ...],
    years: tuple[int, ...],
    audit: dict[str, object],
    transform: str,
) -> dict[str, object]:
    raw_island = island_series(rows, islands, years)
    raw_sub = subcolony_series(rows, islands, years, audit)
    if transform == "linear_detrended_log1p":
        fn = _linear_detrended_log1p
    elif transform == "annual_log1p_growth":
        fn = _annual_log1p_growth
    else:
        raise ValueError(transform)

    island_transformed = {
        key: fn(value) for key, value in raw_island.items()
    }
    among = covariance_synchrony(island_transformed)
    within = {}
    for island in islands:
        prefix = f"{island}:"
        local = {
            key: fn(value)
            for key, value in raw_sub.items()
            if key.startswith(prefix)
        }
        within[island] = covariance_synchrony(local)
    within_beta = np.asarray(
        [
            float(within[island]["beta_spatial"])
            for island in islands
        ],
        dtype=float,
    )
    return {
        "transform": transform,
        "among_islands": among,
        "within_islands": within,
        "within_beta_summary": {
            "min": float(np.min(within_beta)),
            "median": float(np.median(within_beta)),
            "max": float(np.max(within_beta)),
        },
        "boundary": (
            "Non-additive log transforms are not used for an exact "
            "three-level alpha/gamma factorization."
        ),
    }


def analyze(path: str | Path) -> dict[str, object]:
    rows = load_colony_rows(path)
    audit = colony_roster_audit(rows)
    stable = tuple(
        island
        for island in ISLANDS
        if bool(audit[island]["roster_stable"])
    )
    if stable != STABLE_ROSTER_ISLANDS:
        raise ValueError(f"stable-roster island drift: {stable}")

    observed_years = tuple(sorted({int(row["year"]) for row in rows}))
    if observed_years != EXPECTED_YEARS:
        raise ValueError(
            "frozen synchronized-year drift: "
            f"{observed_years[0]}-{observed_years[-1]} "
            f"n={len(observed_years)}"
        )

    primary = nested_raw_decomposition(
        rows,
        STABLE_ROSTER_ISLANDS,
        EXPECTED_YEARS,
        audit,
    )
    pre_extinction = nested_raw_decomposition(
        rows,
        STABLE_ROSTER_ISLANDS,
        PRE_EXTINCTION_YEARS,
        audit,
    )
    persistent_stable = nested_raw_decomposition(
        rows,
        PERSISTENT_STABLE_ROSTER_ISLANDS,
        EXPECTED_YEARS,
        audit,
    )

    five_island = wang_loreau_raw(
        island_series(rows, ISLANDS, EXPECTED_YEARS)
    )
    four_persistent = wang_loreau_raw(
        island_series(rows, PERSISTENT_ISLANDS, EXPECTED_YEARS)
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

    primary_order = bool(
        primary["beta_within_islands"]
        > primary["beta_among_islands"]
    )
    pre_order = bool(
        pre_extinction["beta_within_islands"]
        > pre_extinction["beta_among_islands"]
    )
    persistent_order = bool(
        persistent_stable["beta_within_islands"]
        > persistent_stable["beta_among_islands"]
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-hierarchical-variability-v1",
        "status": "descriptive_hierarchical_variability_decomposition",
        "source_row_count": len(rows),
        "colony_roster_audit": audit,
        "stable_roster_islands": list(stable),
        "raw_abundance_primary": primary,
        "raw_abundance_context": {
            "five_island_archipelago": five_island,
            "four_persistent_islands": four_persistent,
        },
        "fixed_sensitivities": {
            "pre_litchfield_extinction_1991_2006": pre_extinction,
            "persistent_stable_roster_COR_HUM": persistent_stable,
        },
        "centered_signal_sensitivities": {
            "linear_detrended_log1p": detrended,
            "annual_log1p_growth": growth,
        },
        "decision": {
            "within_island_beta_exceeds_among_island_beta_primary": (
                primary_order
            ),
            "same_ordering_before_litchfield_extinction": pre_order,
            "same_ordering_without_litchfield": persistent_order,
            "hierarchy_ordering_retained_across_fixed_raw_sensitivities": bool(
                primary_order and pre_order and persistent_order
            ),
        },
        "interpretation_boundary": {
            "descriptive_not_confirmatory_p_value": True,
            "beta_asynchrony_not_causal_insurance_mechanism": True,
            "colony_codes_not_assumed_gis_polygons": True,
            "no_dispersal_inference": True,
            "raw_abundance_is_only_exact_three_level_alpha_beta_gamma_partition": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = analyze(args.census)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
