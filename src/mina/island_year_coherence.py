"""Missingness-robust test of island-level annual demographic coherence."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows

N_PERMUTATIONS = 20_000
SEED = 20260927
N_STRATA = 5
MIN_INFORMATIVE_TRANSITIONS = 3


def _build_colonies(
    path: str | Path,
    islands: tuple[str, ...],
) -> list[dict[str, object]]:
    rows = load_colony_rows(path)
    counts: dict[tuple[str, str, int], float] = defaultdict(float)
    codes: set[tuple[str, str]] = set()
    for row in rows:
        island = str(row["island"])
        if island not in islands:
            continue
        code = str(row["colony_code"])
        year = int(row["year"])
        counts[(island, code, year)] += float(row["breeding_pairs"])
        codes.add((island, code))

    colonies: list[dict[str, object]] = []
    for island, code in sorted(codes):
        years = sorted(
            year for ii, cc, year in counts
            if ii == island and cc == code
        )
        growth_rows: list[tuple[int, float]] = []
        for end_year in years:
            start_year = end_year - 1
            if (island, code, start_year) not in counts:
                continue
            start = float(counts[(island, code, start_year)])
            end = float(counts[(island, code, end_year)])
            if start == 0.0 and end == 0.0:
                continue
            growth_rows.append(
                (end_year, math.log1p(end) - math.log1p(start))
            )

        if len(growth_rows) < MIN_INFORMATIVE_TRANSITIONS:
            continue
        values = np.asarray([value for _, value in growth_rows], dtype=float)
        sd = float(np.std(values, ddof=1))
        if sd <= 0:
            continue
        mean = float(np.mean(values))
        standardized = [
            (year, (value - mean) / sd)
            for year, value in growth_rows
        ]
        reported_counts = np.asarray(
            [counts[(island, code, year)] for year in years],
            dtype=float,
        )
        colonies.append(
            {
                "island": island,
                "colony_code": code,
                "n_informative_transitions": len(growth_rows),
                "mean_log1p_abundance": float(
                    np.mean(np.log1p(reported_counts))
                ),
                "z_growth": standardized,
            }
        )
    return colonies


def _rank_strata(colonies: list[dict[str, object]]) -> np.ndarray:
    order = sorted(
        range(len(colonies)),
        key=lambda idx: (
            int(colonies[idx]["n_informative_transitions"]),
            float(colonies[idx]["mean_log1p_abundance"]),
            str(colonies[idx]["island"]),
            str(colonies[idx]["colony_code"]),
        ),
    )
    strata = np.empty(len(colonies), dtype=int)
    for rank, idx in enumerate(order):
        strata[idx] = min(N_STRATA - 1, rank * N_STRATA // len(colonies))
    return strata


def _regional_residuals(
    colonies: list[dict[str, object]],
) -> dict[tuple[int, int], float]:
    by_year: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for idx, colony in enumerate(colonies):
        for year, value in colony["z_growth"]:
            by_year[int(year)].append((idx, float(value)))

    out: dict[tuple[int, int], float] = {}
    for year, local in by_year.items():
        mean = float(np.mean([value for _, value in local]))
        for idx, value in local:
            out[(idx, year)] = value - mean
    return out


def _pair_aggregates(
    colonies: list[dict[str, object]],
    residuals: dict[tuple[int, int], float],
) -> dict[str, np.ndarray]:
    by_colony: dict[int, dict[int, float]] = defaultdict(dict)
    for (idx, year), value in residuals.items():
        by_colony[idx][year] = value

    pair_a: list[int] = []
    pair_b: list[int] = []
    sumprod: list[float] = []
    n_pairyears: list[int] = []
    early_sumprod: list[float] = []
    early_n: list[int] = []
    late_sumprod: list[float] = []
    late_n: list[int] = []

    for a, b in combinations(range(len(colonies)), 2):
        common = sorted(set(by_colony[a]) & set(by_colony[b]))
        if not common:
            continue
        products = np.asarray(
            [by_colony[a][year] * by_colony[b][year] for year in common],
            dtype=float,
        )
        early_mask = np.asarray([year <= 2006 for year in common], dtype=bool)
        late_mask = ~early_mask

        pair_a.append(a)
        pair_b.append(b)
        sumprod.append(float(np.sum(products)))
        n_pairyears.append(len(common))
        early_sumprod.append(float(np.sum(products[early_mask])))
        early_n.append(int(np.sum(early_mask)))
        late_sumprod.append(float(np.sum(products[late_mask])))
        late_n.append(int(np.sum(late_mask)))

    return {
        "a": np.asarray(pair_a, dtype=int),
        "b": np.asarray(pair_b, dtype=int),
        "sumprod": np.asarray(sumprod, dtype=float),
        "n": np.asarray(n_pairyears, dtype=float),
        "early_sumprod": np.asarray(early_sumprod, dtype=float),
        "early_n": np.asarray(early_n, dtype=float),
        "late_sumprod": np.asarray(late_sumprod, dtype=float),
        "late_n": np.asarray(late_n, dtype=float),
    }


def _contrast_from_labels(
    labels: np.ndarray,
    pairs: dict[str, np.ndarray],
    prefix: str = "",
) -> dict[str, float]:
    same = labels[pairs["a"]] == labels[pairs["b"]]
    sum_key = f"{prefix}sumprod"
    n_key = f"{prefix}n"
    sums = pairs[sum_key]
    weights = pairs[n_key]

    within_n = float(np.sum(weights[same]))
    between_n = float(np.sum(weights[~same]))
    if within_n <= 0 or between_n <= 0:
        raise ValueError("no within- or between-island pair-year support")
    within = float(np.sum(sums[same]) / within_n)
    between = float(np.sum(sums[~same]) / between_n)
    return {
        "within_mean_pairyear_product": within,
        "between_mean_pairyear_product": between,
        "island_year_covariance_contrast": within - between,
        "within_pairyears": int(within_n),
        "between_pairyears": int(between_n),
    }


def _p_two_sided(null: np.ndarray, observed: float) -> float:
    lower = (1 + int(np.sum(null <= observed))) / (null.size + 1)
    upper = (1 + int(np.sum(null >= observed))) / (null.size + 1)
    return float(min(1.0, 2.0 * min(lower, upper)))


def _permute_labels(
    labels: np.ndarray,
    strata: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    out = labels.copy()
    for stratum in sorted(set(strata.tolist())):
        idx = np.flatnonzero(strata == stratum)
        out[idx] = rng.permutation(out[idx])
    return out


def _run(
    path: str | Path,
    islands: tuple[str, ...],
    n_permutations: int,
    seed: int,
) -> dict[str, object]:
    colonies = _build_colonies(path, islands)
    if len(colonies) < 4:
        raise ValueError("too few eligible colonies")
    labels = np.asarray([str(c["island"]) for c in colonies], dtype=object)
    strata = _rank_strata(colonies)
    residuals = _regional_residuals(colonies)
    pairs = _pair_aggregates(colonies, residuals)
    observed = _contrast_from_labels(labels, pairs)

    rng = np.random.default_rng(seed)
    null = np.empty(n_permutations, dtype=float)
    for index in range(n_permutations):
        perm = _permute_labels(labels, strata, rng)
        null[index] = float(
            _contrast_from_labels(
                perm, pairs
            )["island_year_covariance_contrast"]
        )

    p = _p_two_sided(
        null, float(observed["island_year_covariance_contrast"])
    )
    supported = bool(
        observed["island_year_covariance_contrast"] > 0 and p <= 0.05
    )

    per_island: dict[str, object] = {}
    for island in islands:
        mask_label = labels == island
        same = (
            mask_label[pairs["a"]]
            & mask_label[pairs["b"]]
        )
        denom = float(np.sum(pairs["n"][same]))
        per_island[island] = {
            "n_eligible_colonies": int(np.sum(mask_label)),
            "n_informative_transitions": int(
                sum(
                    int(c["n_informative_transitions"])
                    for c in colonies
                    if c["island"] == island
                )
            ),
            "within_mean_pairyear_product": (
                float(np.sum(pairs["sumprod"][same]) / denom)
                if denom > 0 else None
            ),
            "within_pairyears": int(denom),
        }

    descriptive_periods = {}
    for name, prefix in (
        ("early_1991_2006", "early_"),
        ("late_2007_2017", "late_"),
    ):
        try:
            descriptive_periods[name] = _contrast_from_labels(
                labels, pairs, prefix=prefix
            )
        except ValueError:
            descriptive_periods[name] = None

    return {
        "islands": list(islands),
        "n_eligible_colonies": len(colonies),
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
        "per_island": per_island,
        "descriptive_periods": descriptive_periods,
        "eligibility": {
            "minimum_informative_transitions": MIN_INFORMATIVE_TRANSITIONS,
            "colony_records": [
                {
                    "island": str(c["island"]),
                    "colony_code": str(c["colony_code"]),
                    "n_informative_transitions": int(
                        c["n_informative_transitions"]
                    ),
                    "mean_log1p_abundance": float(
                        c["mean_log1p_abundance"]
                    ),
                    "stratum": int(strata[idx]),
                }
                for idx, c in enumerate(colonies)
            ],
        },
    }


def analyze(
    path: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 99:
        raise ValueError("at least 99 permutations are required")
    five = _run(path, ISLANDS, n_permutations, seed)
    four = _run(
        path,
        tuple(island for island in ISLANDS if island != "LIT"),
        n_permutations,
        seed + 1,
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-island-year-coherence-v1",
        "five_island_all_period": five,
        "four_island_no_litchfield": four,
        "decision": {
            "primary_supported": bool(five["supported"]),
            "not_litchfield_driven": bool(four["supported"]),
            "strong_confirmation": bool(
                five["supported"] and four["supported"]
            ),
        },
        "interpretation_boundary": {
            "post_primary_missingness_robust_validation": True,
            "does_not_test_distance_conditioned_coastline_effect": True,
            "does_not_identify_mechanism": True,
            "does_not_rescue_spatial_insurance": True,
            "no_imputation_or_code_merging": True,
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
