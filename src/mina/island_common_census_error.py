"""Shared island-year census-error sensitivity for the frozen coherence signal."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .island_year_coherence import (
    _build_colonies,
    _rank_strata,
)
from .lter import ISLANDS, load_colony_rows

CV_GRID = (0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50)
N_REPLICATES = 20_000
SEED = 20260927
OBSERVED_FIVE = 0.09279582032316958
OBSERVED_FOUR = 0.08571095302780918
BATCH_SIZE = 500


def _transition_arrays(
    path: str | Path,
    islands: tuple[str, ...],
) -> dict[str, object]:
    colonies = _build_colonies(path, islands)
    strata = _rank_strata(colonies)
    label_lookup = {island: idx for idx, island in enumerate(islands)}
    base_labels = np.asarray(
        [label_lookup[str(c["island"])] for c in colonies], dtype=int
    )

    eligible = {
        (str(c["island"]), str(c["colony_code"])): idx
        for idx, c in enumerate(colonies)
    }
    rows = load_colony_rows(path)
    counts: dict[tuple[str, str, int], float] = defaultdict(float)
    for row in rows:
        key = (str(row["island"]), str(row["colony_code"]))
        if key not in eligible:
            continue
        counts[(key[0], key[1], int(row["year"]))] += float(
            row["breeding_pairs"]
        )

    years = sorted({year for _, _, year in counts})
    year_lookup = {year: idx for idx, year in enumerate(years)}

    col_idx: list[int] = []
    start_count: list[float] = []
    end_count: list[float] = []
    start_yidx: list[int] = []
    end_yidx: list[int] = []

    by_colony_q: list[list[int]] = [[] for _ in colonies]
    by_year_q: list[list[int]] = [[] for _ in years]

    for (island, code), idx in sorted(eligible.items(), key=lambda kv: kv[1]):
        local_years = sorted(
            year
            for ii, cc, year in counts
            if ii == island and cc == code
        )
        for end_year in local_years:
            start_year = end_year - 1
            if (island, code, start_year) not in counts:
                continue
            start = float(counts[(island, code, start_year)])
            end = float(counts[(island, code, end_year)])
            if start == 0.0 and end == 0.0:
                continue
            q = len(col_idx)
            col_idx.append(idx)
            start_count.append(start)
            end_count.append(end)
            start_yidx.append(year_lookup[start_year])
            end_yidx.append(year_lookup[end_year])
            by_colony_q[idx].append(q)
            by_year_q[year_lookup[end_year]].append(q)

    expected = [
        int(c["n_informative_transitions"]) for c in colonies
    ]
    observed = [len(x) for x in by_colony_q]
    if observed != expected:
        raise ValueError("transition reconstruction drifted from frozen analysis")

    return {
        "colonies": colonies,
        "strata": np.asarray(strata, dtype=int),
        "base_labels": base_labels,
        "n_labels": len(islands),
        "years": years,
        "col_idx": np.asarray(col_idx, dtype=int),
        "start_count": np.asarray(start_count, dtype=float),
        "end_count": np.asarray(end_count, dtype=float),
        "start_yidx": np.asarray(start_yidx, dtype=int),
        "end_yidx": np.asarray(end_yidx, dtype=int),
        "by_colony_q": [np.asarray(x, dtype=int) for x in by_colony_q],
        "by_year_q": [np.asarray(x, dtype=int) for x in by_year_q],
    }


def _permuted_label_batch(
    base_labels: np.ndarray,
    strata: np.ndarray,
    batch: int,
    rng: np.random.Generator,
) -> np.ndarray:
    out = np.empty((batch, base_labels.size), dtype=int)
    for stratum in sorted(set(strata.tolist())):
        idx = np.flatnonzero(strata == stratum)
        source = base_labels[idx]
        # Random-key sorting gives independent uniform permutations per row.
        order = np.argsort(rng.random((batch, idx.size)), axis=1)
        out[:, idx] = source[order]
    return out


def _batch_contrast(
    data: dict[str, object],
    labels: np.ndarray,
    cv: float,
    rng: np.random.Generator,
) -> np.ndarray:
    batch = labels.shape[0]
    n_labels = int(data["n_labels"])
    n_years = len(data["years"])
    col_idx = data["col_idx"]
    start_count = data["start_count"]
    end_count = data["end_count"]
    start_yidx = data["start_yidx"]
    end_yidx = data["end_yidx"]

    if cv == 0.0:
        factors = np.ones((batch, n_labels, n_years), dtype=float)
    else:
        sigma2 = math.log1p(cv * cv)
        log_factors = rng.normal(
            loc=-0.5 * sigma2,
            scale=math.sqrt(sigma2),
            size=(batch, n_labels, n_years),
        )
        factors = np.exp(log_factors)

    row = np.arange(batch)[:, None]
    q_labels = labels[:, col_idx]
    start_factor = factors[
        row, q_labels, start_yidx[None, :]
    ]
    end_factor = factors[
        row, q_labels, end_yidx[None, :]
    ]
    growth = (
        np.log1p(end_count[None, :] * end_factor)
        - np.log1p(start_count[None, :] * start_factor)
    )

    z = np.empty_like(growth)
    for qidx in data["by_colony_q"]:
        local = growth[:, qidx]
        mean = np.mean(local, axis=1)
        sd = np.std(local, axis=1, ddof=1)
        if np.any(sd <= 0):
            raise ValueError("simulated zero within-colony growth variance")
        z[:, qidx] = (local - mean[:, None]) / sd[:, None]

    residual = z.copy()
    for qidx in data["by_year_q"]:
        if qidx.size == 0:
            continue
        mean = np.mean(z[:, qidx], axis=1)
        residual[:, qidx] -= mean[:, None]

    within_sum = np.zeros(batch, dtype=float)
    between_sum = np.zeros(batch, dtype=float)
    within_n = np.zeros(batch, dtype=float)
    between_n = np.zeros(batch, dtype=float)

    for qidx in data["by_year_q"]:
        if qidx.size < 2:
            continue
        rv = residual[:, qidx]
        cols = col_idx[qidx]
        labs = labels[:, cols]

        total_sum = (
            np.sum(rv, axis=1) ** 2 - np.sum(rv * rv, axis=1)
        ) / 2.0
        total_n = qidx.size * (qidx.size - 1) / 2.0

        same_sum = np.zeros(batch, dtype=float)
        same_n = np.zeros(batch, dtype=float)
        for group in range(n_labels):
            mask = labs == group
            ng = np.sum(mask, axis=1)
            sumg = np.sum(rv * mask, axis=1)
            sumsqg = np.sum(rv * rv * mask, axis=1)
            same_sum += (sumg * sumg - sumsqg) / 2.0
            same_n += ng * (ng - 1) / 2.0

        within_sum += same_sum
        within_n += same_n
        between_sum += total_sum - same_sum
        between_n += total_n - same_n

    if np.any(within_n <= 0) or np.any(between_n <= 0):
        raise ValueError("simulated labels produced empty pair-year class")
    return within_sum / within_n - between_sum / between_n


def _simulate_cv(
    data: dict[str, object],
    cv: float,
    n_replicates: int,
    seed_sequence: np.random.SeedSequence,
) -> np.ndarray:
    rng = np.random.default_rng(seed_sequence)
    chunks: list[np.ndarray] = []
    remaining = n_replicates
    while remaining:
        batch = min(BATCH_SIZE, remaining)
        labels = _permuted_label_batch(
            data["base_labels"], data["strata"], batch, rng
        )
        chunks.append(_batch_contrast(data, labels, cv, rng))
        remaining -= batch
    return np.concatenate(chunks)


def _run_grid(
    path: str | Path,
    islands: tuple[str, ...],
    observed_target: float,
    n_replicates: int,
    seed: int,
    analysis_index: int,
) -> dict[str, object]:
    data = _transition_arrays(path, islands)
    rows = {}
    for cv_index, cv in enumerate(CV_GRID):
        ss = np.random.SeedSequence([seed, analysis_index, cv_index])
        values = _simulate_cv(data, cv, n_replicates, ss)
        exceed = int(np.sum(values >= observed_target))
        p_upper = float((1 + exceed) / (n_replicates + 1))
        rows[f"{cv:.2f}"] = {
            "cv": cv,
            "mean": float(np.mean(values)),
            "sd": float(np.std(values, ddof=1)),
            "q95": float(np.quantile(values, 0.95)),
            "q99": float(np.quantile(values, 0.99)),
            "exceedances": exceed,
            "upper_p": p_upper,
        }
    return {
        "islands": list(islands),
        "n_eligible_colonies": len(data["colonies"]),
        "n_informative_transitions": int(len(data["col_idx"])),
        "observed_target": observed_target,
        "grid": rows,
    }


def analyze(
    path: str | Path,
    n_replicates: int = N_REPLICATES,
    seed: int = SEED,
) -> dict[str, object]:
    if n_replicates < 99:
        raise ValueError("at least 99 replicates are required")

    five = _run_grid(
        path, ISLANDS, OBSERVED_FIVE, n_replicates, seed, 0
    )
    four_islands = tuple(i for i in ISLANDS if i != "LIT")
    four = _run_grid(
        path, four_islands, OBSERVED_FOUR, n_replicates, seed, 1
    )

    primary_grid = five["grid"]
    through_10 = [
        primary_grid[f"{cv:.2f}"]["upper_p"]
        for cv in CV_GRID
        if cv <= 0.10
    ]
    through_20 = [
        primary_grid[f"{cv:.2f}"]["upper_p"]
        for cv in CV_GRID
        if cv <= 0.20
    ]
    if all(float(p) <= 0.05 for p in through_20):
        classification = "strong_robustness"
    elif all(float(p) <= 0.05 for p in through_10):
        classification = "moderate_robustness"
    else:
        classification = "fragile_to_shared_error"

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-island-common-census-error-v1",
        "measurement_error": {
            "family": "fully shared island-year mean-one lognormal multiplier",
            "cv_grid": list(CV_GRID),
            "replicates_per_cv": n_replicates,
            "seed": seed,
        },
        "five_island_primary": five,
        "four_island_no_litchfield_sensitivity": four,
        "decision": {
            "classification": classification,
            "robust_through_cv_10pct": bool(
                all(float(p) <= 0.05 for p in through_10)
            ),
            "robust_through_cv_20pct": bool(
                all(float(p) <= 0.05 for p in through_20)
            ),
        },
        "interpretation_boundary": {
            "cv_grid_is_sensitivity_not_empirical_error_estimate": True,
            "fully_shared_multiplier_favors_observer_error_alternative": True,
            "does_not_rule_out_all_spatial_observation_bias": True,
            "does_not_identify_biological_mechanism": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--replicates", type=int, default=N_REPLICATES)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(args.census, args.replicates, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
