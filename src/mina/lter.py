"""Palmer LTER five-island Adélie census synchrony analysis."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

ISLAND_NAMES = {
    "CHR": "Christine Island",
    "COR": "Cormorant Island",
    "HUM": "Humble Island",
    "LIT": "Litchfield Island",
    "TOR": "Torgersen Island",
}
ISLANDS = tuple(ISLAND_NAMES)


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_colony_rows(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    parsed: list[dict[str, object]] = []
    seen: set[tuple[str, int, str, str]] = set()
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        if not _finite(row.get("num_breeding_pairs")):
            # ERDDAP CSV includes a units row; other missing census values are
            # excluded rather than imputed.
            continue
        count = float(row["num_breeding_pairs"])
        if count < 0:
            raise ValueError("negative breeding-pair count")
        time = str(row.get("time", "")).strip()
        try:
            year = int(time[:4])
        except (TypeError, ValueError):
            continue
        study = str(row.get("study_name", "")).strip()
        colony = str(row.get("colony_code", "")).strip()
        key = (study, year, island, colony)
        if key in seen:
            raise ValueError(f"duplicate colony census key: {key!r}")
        seen.add(key)
        parsed.append(
            {
                "study_name": study,
                "year": year,
                "island": island,
                "colony_code": colony,
                "breeding_pairs": count,
            }
        )
    if not parsed:
        raise ValueError("no five-island census rows parsed")
    return parsed


def island_year_totals(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[int, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(int(row["year"]), str(row["island"]))].append(row)

    output: list[dict[str, object]] = []
    for (year, island), local in sorted(groups.items()):
        studies = sorted({str(row["study_name"]) for row in local})
        if len(studies) != 1:
            raise ValueError(
                f"multiple study names for {island} {year}: {studies}"
            )
        output.append(
            {
                "year": year,
                "study_name": studies[0],
                "island": island,
                "island_name": ISLAND_NAMES[island],
                "breeding_pairs": float(sum(float(row["breeding_pairs"]) for row in local)),
                "colony_count": len(local),
            }
        )
    return output


def synchronized_panel(
    totals: list[dict[str, object]],
) -> tuple[list[int], dict[str, np.ndarray], list[int]]:
    lookup = {
        (int(row["year"]), str(row["island"])): float(row["breeding_pairs"])
        for row in totals
    }
    years_all = sorted({int(row["year"]) for row in totals})
    years = [
        year
        for year in years_all
        if all((year, island) in lookup for island in ISLANDS)
    ]
    excluded = [year for year in years_all if year not in years]
    if len(years) < 3:
        raise ValueError("fewer than three synchronized five-island years")
    values = {
        island: np.asarray([lookup[(year, island)] for year in years], dtype=float)
        for island in ISLANDS
    }
    return years, values, excluded


def endpoint_summary(
    totals: list[dict[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for island in ISLANDS:
        rows = sorted(
            [row for row in totals if row["island"] == island],
            key=lambda row: int(row["year"]),
        )
        positive = [row for row in rows if float(row["breeding_pairs"]) > 0]
        first = positive[0] if positive else rows[0]
        last = rows[-1]
        first_count = float(first["breeding_pairs"])
        last_count = float(last["breeding_pairs"])
        result[island] = {
            "island_name": ISLAND_NAMES[island],
            "n_years": len(rows),
            "first_year": int(first["year"]),
            "first_count": first_count,
            "last_year": int(last["year"]),
            "last_count": last_count,
            "fraction_remaining": (
                last_count / first_count if first_count > 0 else None
            ),
            "zero_years": [
                int(row["year"])
                for row in rows
                if float(row["breeding_pairs"]) == 0.0
            ],
        }
    return result


def annual_growth(
    years: list[int],
    values: dict[str, np.ndarray],
) -> tuple[list[int], dict[str, np.ndarray]]:
    interval_end_years = [
        years[i]
        for i in range(1, len(years))
        if years[i] - years[i - 1] == 1
    ]
    indices = [
        i
        for i in range(1, len(years))
        if years[i] - years[i - 1] == 1
    ]
    growth = {
        island: np.asarray(
            [
                math.log1p(float(values[island][i]))
                - math.log1p(float(values[island][i - 1]))
                for i in indices
            ],
            dtype=float,
        )
        for island in ISLANDS
    }
    return interval_end_years, growth


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size != y.size or x.size < 3:
        return float("nan")
    sx = float(np.std(x, ddof=1))
    sy = float(np.std(y, ddof=1))
    if sx <= 0 or sy <= 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def growth_synchrony(growth: dict[str, np.ndarray]) -> dict[str, object]:
    pairs: dict[str, float] = {}
    finite_values: list[float] = []
    for a, b in combinations(ISLANDS, 2):
        r = _pearson(growth[a], growth[b])
        pairs[f"{a}__{b}"] = r
        if math.isfinite(r):
            finite_values.append(r)
    return {
        "pairwise_correlations": pairs,
        "median_pairwise_correlation": (
            float(np.median(finite_values)) if finite_values else None
        ),
        "mean_pairwise_correlation": (
            float(np.mean(finite_values)) if finite_values else None
        ),
    }


def common_component(
    years: list[int],
    values: dict[str, np.ndarray],
) -> dict[str, object]:
    matrix = np.column_stack(
        [np.log1p(values[island]) for island in ISLANDS]
    )
    mean = np.mean(matrix, axis=0)
    sd = np.std(matrix, axis=0, ddof=1)
    if np.any(sd <= 0):
        raise ValueError("zero variance island trajectory")
    z = (matrix - mean) / sd
    _, singular, vt = np.linalg.svd(z, full_matrices=False)
    variance = singular**2
    loading = vt[0].copy()
    if float(np.mean(loading)) < 0:
        loading *= -1
    return {
        "n_years": len(years),
        "pc1_variance_fraction": float(variance[0] / np.sum(variance)),
        "pc1_loadings": {
            island: float(loading[index])
            for index, island in enumerate(ISLANDS)
        },
    }


def _ols(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    if rank != x.shape[1]:
        raise ValueError("rank-deficient OLS design")
    residual = y - x @ beta
    return beta, float(residual @ residual)


def additive_decomposition(
    years: list[int],
    values: dict[str, np.ndarray],
) -> dict[str, float]:
    y: list[float] = []
    island_index: list[int] = []
    year_index: list[int] = []
    for j, year in enumerate(years):
        for i, island in enumerate(ISLANDS):
            y.append(math.log1p(float(values[island][j])))
            island_index.append(i)
            year_index.append(j)
    yy = np.asarray(y, dtype=float)
    n = yy.size
    intercept = np.ones((n, 1), dtype=float)

    island_dummy = np.zeros((n, len(ISLANDS) - 1), dtype=float)
    for row, idx in enumerate(island_index):
        if idx > 0:
            island_dummy[row, idx - 1] = 1.0

    year_dummy = np.zeros((n, len(years) - 1), dtype=float)
    for row, idx in enumerate(year_index):
        if idx > 0:
            year_dummy[row, idx - 1] = 1.0

    _, sse0 = _ols(intercept, yy)
    _, ssei = _ols(np.column_stack([intercept, island_dummy]), yy)
    _, ssey = _ols(np.column_stack([intercept, year_dummy]), yy)
    _, sseiy = _ols(
        np.column_stack([intercept, island_dummy, year_dummy]),
        yy,
    )
    if sse0 <= 0:
        raise ValueError("zero total variance")
    unique_year = (ssei - sseiy) / sse0
    unique_island = (ssey - sseiy) / sse0
    residual = sseiy / sse0
    additive_r2 = 1.0 - residual
    shared = additive_r2 - unique_year - unique_island
    return {
        "island_only_r2": 1.0 - ssei / sse0,
        "year_only_r2": 1.0 - ssey / sse0,
        "additive_r2": additive_r2,
        "unique_year_fraction": unique_year,
        "unique_island_fraction": unique_island,
        "shared_fraction": shared,
        "residual_fraction": residual,
    }


def common_growth_sensitivity(
    interval_years: list[int],
    growth: dict[str, np.ndarray],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for island in ISLANDS:
        others = [growth[x] for x in ISLANDS if x != island]
        common = np.mean(np.column_stack(others), axis=1)
        target = growth[island]
        x = np.column_stack([np.ones(target.size), common])
        beta, sse = _ols(x, target)
        tss = float(np.sum((target - np.mean(target)) ** 2))
        residual_sd = math.sqrt(sse / max(1, target.size - 2))
        result[island] = {
            "n_intervals": len(interval_years),
            "intercept": float(beta[0]),
            "common_growth_beta": float(beta[1]),
            "r2": (1.0 - sse / tss) if tss > 0 else None,
            "residual_sd": residual_sd,
        }
    return result


def trend_slopes(
    years: list[int],
    values: dict[str, np.ndarray],
) -> dict[str, object]:
    x_year = np.asarray(years, dtype=float)
    centered = x_year - np.mean(x_year)
    x = np.column_stack([np.ones(len(years)), centered])
    out: dict[str, object] = {}
    for island in ISLANDS:
        y = np.log1p(values[island])
        beta, sse = _ols(x, y)
        tss = float(np.sum((y - np.mean(y)) ** 2))
        slope = float(beta[1])
        out[island] = {
            "log1p_slope_per_year": slope,
            "multiplicative_change_per_year": math.exp(slope) - 1.0,
            "r2_linear_time": (1.0 - sse / tss) if tss > 0 else None,
        }
    return out


def analyze(path: str | Path) -> dict[str, object]:
    colony = load_colony_rows(path)
    totals = island_year_totals(colony)
    years, values, excluded = synchronized_panel(totals)
    interval_years, growth = annual_growth(years, values)
    if len(interval_years) < 5:
        raise ValueError("too few adjacent-year intervals for synchrony analysis")

    annual_dispersion = np.std(
        np.column_stack([growth[island] for island in ISLANDS]),
        axis=1,
        ddof=1,
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-lter-five-island-synchrony-v1",
        "source_row_count": len(colony),
        "island_year_totals": totals,
        "synchronized_panel": {
            "years": years,
            "n_years": len(years),
            "excluded_incomplete_years": excluded,
        },
        "endpoints": endpoint_summary(totals),
        "annual_growth": {
            "interval_end_years": interval_years,
            "values": {
                island: [float(x) for x in growth[island]]
                for island in ISLANDS
            },
            "mean_cross_island_dispersion": float(np.mean(annual_dispersion)),
        },
        "growth_synchrony": growth_synchrony(growth),
        "common_component": common_component(years, values),
        "common_growth_sensitivity": common_growth_sensitivity(
            interval_years, growth
        ),
        "trend_slopes": trend_slopes(years, values),
        "additive_decomposition": additive_decomposition(years, values),
        "interpretation_boundary": {
            "year_component_is_not_causal_sea_ice_effect": True,
            "island_residual_is_not_automatically_biotic_interaction": True,
            "no_interpolation": True,
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
