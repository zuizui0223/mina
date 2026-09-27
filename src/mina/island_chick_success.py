"""Independent life-stage validation using colony-specific chick production."""
from __future__ import annotations

import argparse
import csv
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
MIN_SEASONS = 5


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_chick_rows(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out: list[dict[str, object]] = []
    seen: set[tuple[str, str, int]] = set()
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        if not _finite(row.get("num_breeding_pairs")) or not _finite(
            row.get("num_chicks")
        ):
            continue
        adult = float(row["num_breeding_pairs"])
        chicks = float(row["num_chicks"])
        if adult < 0 or chicks < 0:
            raise ValueError("negative adult/chick count")
        time = str(row.get("time", "")).strip()
        try:
            census_year = int(time[:4])
        except (TypeError, ValueError):
            continue
        season = census_year - 1
        code = str(row.get("colony_code", "")).strip()
        if adult <= 0:
            continue
        key = (island, code, season)
        if key in seen:
            raise ValueError(f"duplicate usable chick row: {key!r}")
        seen.add(key)
        out.append(
            {
                "study_name": str(row.get("study_name", "")).strip(),
                "time": time,
                "season": season,
                "island": island,
                "colony_code": code,
                "adult_pairs": adult,
                "chicks": chicks,
                "chicks_per_pair": chicks / adult,
                "census_time": str(row.get("census_time", "")).strip(),
            }
        )
    if not out:
        raise ValueError("no usable chick-production rows")
    return out


def _eligible_colonies(
    rows: list[dict[str, object]], islands: tuple[str, ...]
) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if str(row["island"]) in islands:
            groups[(str(row["island"]), str(row["colony_code"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, code), local in sorted(groups.items()):
        local = sorted(local, key=lambda r: int(r["season"]))
        if len(local) < MIN_SEASONS:
            continue
        values = np.asarray(
            [float(r["chicks_per_pair"]) for r in local], dtype=float
        )
        sd = float(np.std(values, ddof=1))
        if sd <= 0:
            continue
        mean = float(np.mean(values))
        out.append(
            {
                "island": island,
                "colony_code": code,
                "n_seasons": len(local),
                "mean_log1p_adults": float(
                    np.mean(
                        [
                            math.log1p(float(r["adult_pairs"]))
                            for r in local
                        ]
                    )
                ),
                "z_success": [
                    (int(r["season"]), (float(r["chicks_per_pair"]) - mean) / sd)
                    for r in local
                ],
            }
        )
    return out


def _rank_strata(colonies: list[dict[str, object]]) -> np.ndarray:
    order = sorted(
        range(len(colonies)),
        key=lambda idx: (
            int(colonies[idx]["n_seasons"]),
            float(colonies[idx]["mean_log1p_adults"]),
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
    by_season: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for idx, colony in enumerate(colonies):
        for season, value in colony["z_success"]:
            by_season[int(season)].append((idx, float(value)))
    out: dict[tuple[int, int], float] = {}
    for season, local in by_season.items():
        mean = float(np.mean([v for _, v in local]))
        for idx, value in local:
            out[(idx, season)] = value - mean
    return out


def _pair_aggregates(
    colonies: list[dict[str, object]],
    residuals: dict[tuple[int, int], float],
) -> dict[str, np.ndarray]:
    by_colony: dict[int, dict[int, float]] = defaultdict(dict)
    for (idx, season), value in residuals.items():
        by_colony[idx][season] = value
    aa: list[int] = []
    bb: list[int] = []
    sums: list[float] = []
    nn: list[int] = []
    for a, b in combinations(range(len(colonies)), 2):
        common = sorted(set(by_colony[a]) & set(by_colony[b]))
        if not common:
            continue
        products = [
            by_colony[a][season] * by_colony[b][season]
            for season in common
        ]
        aa.append(a)
        bb.append(b)
        sums.append(float(np.sum(products)))
        nn.append(len(products))
    return {
        "a": np.asarray(aa, dtype=int),
        "b": np.asarray(bb, dtype=int),
        "sumprod": np.asarray(sums, dtype=float),
        "n": np.asarray(nn, dtype=float),
    }


def _contrast(
    labels: np.ndarray, pairs: dict[str, np.ndarray]
) -> dict[str, float | int]:
    same = labels[pairs["a"]] == labels[pairs["b"]]
    wn = float(np.sum(pairs["n"][same]))
    bn = float(np.sum(pairs["n"][~same]))
    if wn <= 0 or bn <= 0:
        raise ValueError("empty within/between pair-season class")
    within = float(np.sum(pairs["sumprod"][same]) / wn)
    between = float(np.sum(pairs["sumprod"][~same]) / bn)
    return {
        "within_mean_pairseason_product": within,
        "between_mean_pairseason_product": between,
        "island_success_covariance_contrast": within - between,
        "within_pairseasons": int(wn),
        "between_pairseasons": int(bn),
    }


def _permute(
    labels: np.ndarray, strata: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    out = labels.copy()
    for stratum in sorted(set(strata.tolist())):
        idx = np.flatnonzero(strata == stratum)
        out[idx] = rng.permutation(out[idx])
    return out


def _p_two_sided(null: np.ndarray, observed: float) -> float:
    lower = (1 + int(np.sum(null <= observed))) / (null.size + 1)
    upper = (1 + int(np.sum(null >= observed))) / (null.size + 1)
    return float(min(1.0, 2.0 * min(lower, upper)))


def _run(
    rows: list[dict[str, object]],
    islands: tuple[str, ...],
    n_permutations: int,
    seed: int,
) -> dict[str, object]:
    colonies = _eligible_colonies(rows, islands)
    if len(colonies) < 4:
        raise ValueError("too few eligible chick-success colonies")
    labels = np.asarray([str(c["island"]) for c in colonies], dtype=object)
    strata = _rank_strata(colonies)
    residuals = _regional_residuals(colonies)
    pairs = _pair_aggregates(colonies, residuals)
    observed = _contrast(labels, pairs)

    rng = np.random.default_rng(seed)
    null = np.empty(n_permutations, dtype=float)
    for idx in range(n_permutations):
        perm = _permute(labels, strata, rng)
        null[idx] = float(
            _contrast(perm, pairs)["island_success_covariance_contrast"]
        )
    target = float(observed["island_success_covariance_contrast"])
    p = _p_two_sided(null, target)

    per_island: dict[str, object] = {}
    for island in islands:
        mask = labels == island
        same = mask[pairs["a"]] & mask[pairs["b"]]
        denom = float(np.sum(pairs["n"][same]))
        per_island[island] = {
            "n_eligible_colonies": int(np.sum(mask)),
            "within_mean_pairseason_product": (
                float(np.sum(pairs["sumprod"][same]) / denom)
                if denom > 0
                else None
            ),
            "within_pairseasons": int(denom),
        }

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
        "supported": bool(target > 0 and p <= 0.05),
        "per_island": per_island,
        "eligibility": {
            "minimum_seasons": MIN_SEASONS,
            "colonies": [
                {
                    "island": str(c["island"]),
                    "colony_code": str(c["colony_code"]),
                    "n_seasons": int(c["n_seasons"]),
                    "mean_log1p_adults": float(c["mean_log1p_adults"]),
                    "stratum": int(strata[idx]),
                }
                for idx, c in enumerate(colonies)
            ],
        },
    }


def adult_overlap_diagnostic(
    chick_rows: list[dict[str, object]], adult_census: str | Path
) -> dict[str, object]:
    adult_rows = load_colony_rows(adult_census)
    lookup: dict[tuple[str, str, int], float] = defaultdict(float)
    for row in adult_rows:
        lookup[
            (
                str(row["island"]),
                str(row["colony_code"]),
                int(row["year"]),
            )
        ] += float(row["breeding_pairs"])

    compared = 0
    exact = 0
    abs_diff: list[float] = []
    rel_diff: list[float] = []
    by_island: dict[str, dict[str, int]] = {
        island: {"compared": 0, "exact": 0} for island in ISLANDS
    }
    for row in chick_rows:
        key = (
            str(row["island"]),
            str(row["colony_code"]),
            int(row["season"]),
        )
        if key not in lookup:
            continue
        a = float(row["adult_pairs"])
        b = float(lookup[key])
        compared += 1
        by_island[key[0]]["compared"] += 1
        if a == b:
            exact += 1
            by_island[key[0]]["exact"] += 1
        abs_diff.append(abs(a - b))
        if b > 0:
            rel_diff.append(abs(a - b) / b)
    return {
        "n_compared": compared,
        "n_exact": exact,
        "exact_fraction": exact / compared if compared else None,
        "median_absolute_difference": (
            float(np.median(abs_diff)) if abs_diff else None
        ),
        "median_relative_difference": (
            float(np.median(rel_diff)) if rel_diff else None
        ),
        "by_island": {
            island: {
                **v,
                "exact_fraction": (
                    v["exact"] / v["compared"] if v["compared"] else None
                ),
            }
            for island, v in by_island.items()
        },
    }


def analyze(
    chick_path: str | Path,
    adult_census: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 99:
        raise ValueError("at least 99 permutations are required")
    rows = load_chick_rows(chick_path)
    five = _run(rows, ISLANDS, n_permutations, seed)
    four_islands = tuple(i for i in ISLANDS if i != "LIT")
    four = _run(rows, four_islands, n_permutations, seed + 1)
    overlap = adult_overlap_diagnostic(rows, adult_census)
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-island-chick-success-coherence-v1",
        "n_usable_chick_rows": len(rows),
        "season_range": [
            min(int(r["season"]) for r in rows),
            max(int(r["season"]) for r in rows),
        ],
        "five_island_primary": five,
        "four_island_no_litchfield": four,
        "adult_denominator_overlap": overlap,
        "decision": {
            "primary_supported": bool(five["supported"]),
            "not_litchfield_driven": bool(four["supported"]),
            "strong_independent_validation": bool(
                five["supported"] and four["supported"]
            ),
        },
        "interpretation_boundary": {
            "different_life_stage_endpoint": True,
            "adult_denominator_overlap_reported": True,
            "does_not_identify_coastline_causality": True,
            "no_imputation_or_code_merging": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(
        args.chicks,
        args.adult_census,
        args.permutations,
        args.seed,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
