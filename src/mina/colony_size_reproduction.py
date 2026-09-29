"""Palmer Adelie colony size versus chick-production scaling."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows

N_DRAWS = 100_000
SEED = 20262929


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_chick_rows(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        raw = list(csv.DictReader(handle))
    out: list[dict[str, object]] = []
    seen: set[tuple[str, str, int]] = set()
    for row in raw:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        if not _finite(row.get("num_breeding_pairs")) or not _finite(
            row.get("num_chicks")
        ):
            continue
        pairs = float(row["num_breeding_pairs"])
        chicks = float(row["num_chicks"])
        if pairs <= 0 or chicks < 0:
            continue
        time = str(row.get("time", "")).strip()
        try:
            census_year = int(time[:4])
        except (TypeError, ValueError):
            continue
        season = census_year - 1
        code = str(row.get("colony_code", "")).strip()
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
                "pairs": pairs,
                "chicks": chicks,
                "census_time": str(row.get("census_time", "")).strip(),
            }
        )
    if not out:
        raise ValueError("no usable chick-production rows")
    return out


def build_island_season_sets(
    rows: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    minimum_pairs: float = 1.0,
) -> list[dict[str, object]]:
    allowed = set(allowed_islands)
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if str(row["island"]) not in allowed:
            continue
        if float(row["pairs"]) < minimum_pairs:
            continue
        groups[(str(row["island"]), int(row["season"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, season), local in sorted(groups.items()):
        if len(local) < 3:
            continue
        pairs = np.asarray([float(r["pairs"]) for r in local], dtype=float)
        chicks = np.asarray([float(r["chicks"]) for r in local], dtype=float)
        x = np.log(pairs)
        if float(np.std(x, ddof=1)) <= 0 or float(np.sum(chicks)) <= 0:
            continue
        out.append(
            {
                "island": island,
                "season": season,
                "rows": local,
                "pairs": pairs,
                "chicks": chicks,
                "x": x,
                "total_chicks": int(round(float(np.sum(chicks)))),
            }
        )
    if not out:
        raise ValueError("no eligible island-season chick sets")
    return out


def _set_moments(item: dict[str, object], beta: float) -> tuple[float, float, float]:
    x = np.asarray(item["x"], dtype=float)
    chicks = np.asarray(item["chicks"], dtype=float)
    c = float(np.sum(chicks))
    eta = beta * x
    eta = eta - float(np.max(eta))
    weight = np.exp(eta)
    prob = weight / float(np.sum(weight))
    mean_x = float(np.sum(prob * x))
    var_x = float(np.sum(prob * (x - mean_x) ** 2))
    score = float(np.sum(chicks * x) - c * mean_x)
    info = c * var_x
    return score, info, mean_x


def fit_beta(sets: list[dict[str, object]]) -> dict[str, float | int | bool | list[float]]:
    beta = 1.0
    converged = False
    iterations = 0
    for iterations in range(1, 101):
        score = 0.0
        info = 0.0
        for item in sets:
            local_score, local_info, _ = _set_moments(item, beta)
            score += local_score
            info += local_info
        if info <= 0:
            raise ValueError("non-positive conditional information")
        step = score / info
        beta += step
        if abs(step) < 1e-11:
            converged = True
            break

    info_hat = sum(_set_moments(item, beta)[1] for item in sets)
    se = math.sqrt(1.0 / info_hat)
    return {
        "beta_hat": float(beta),
        "se_observed_information": float(se),
        "wald_95ci": [float(beta - 1.96 * se), float(beta + 1.96 * se)],
        "iterations": iterations,
        "converged": converged,
    }


def score_at_one(sets: list[dict[str, object]]) -> float:
    return float(sum(_set_moments(item, 1.0)[0] for item in sets))


def conditional_multinomial_score_test(
    sets: list[dict[str, object]],
    *,
    n_draws: int = N_DRAWS,
    seed: int = SEED,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    observed = score_at_one(sets)
    null = np.zeros(n_draws, dtype=float)
    for item in sets:
        pairs = np.asarray(item["pairs"], dtype=float)
        x = np.asarray(item["x"], dtype=float)
        total = int(item["total_chicks"])
        prob = pairs / float(np.sum(pairs))
        mean_x = float(np.sum(prob * x))
        draws = rng.multinomial(total, prob, size=n_draws)
        null += draws @ x - total * mean_x
    p = (1 + int(np.sum(null >= observed))) / (n_draws + 1)
    return {
        "observed_score": float(observed),
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": float(p),
        "n_draws": n_draws,
        "seed": seed,
    }


def gamma_poisson_score_test(
    sets: list[dict[str, object]],
    *,
    cv: float,
    n_draws: int,
    seed: int,
) -> dict[str, object]:
    if cv <= 0:
        raise ValueError("cv must be positive")
    rng = np.random.default_rng(seed)
    observed = score_at_one(sets)
    null = np.zeros(n_draws, dtype=float)
    shape = 1.0 / (cv * cv)
    for item in sets:
        pairs = np.asarray(item["pairs"], dtype=float)
        x = np.asarray(item["x"], dtype=float)
        total = float(item["total_chicks"])
        prob = pairs / float(np.sum(pairs))
        mean_x = float(np.sum(prob * x))
        mu = total * prob
        scale = np.maximum(mu / shape, 1e-300)
        latent = rng.gamma(shape=shape, scale=scale, size=(n_draws, len(mu)))
        counts = rng.poisson(latent)
        sim_total = np.sum(counts, axis=1)
        null += counts @ x - sim_total * mean_x
    p = (1 + int(np.sum(null >= observed))) / (n_draws + 1)
    return {
        "cv": cv,
        "observed_score": float(observed),
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "one_sided_upper_p": float(p),
        "n_draws": n_draws,
        "seed": seed,
    }


def adult_overlap_diagnostic(
    chick_rows: list[dict[str, object]], adult_census: str | Path
) -> dict[str, object]:
    adult_rows = load_colony_rows(adult_census)
    lookup: dict[tuple[str, str, int], float] = {}
    for row in adult_rows:
        key = (
            str(row["island"]),
            str(row["colony_code"]),
            int(row["year"]),
        )
        if key in lookup:
            raise ValueError(f"duplicate adult overlap key: {key!r}")
        lookup[key] = float(row["breeding_pairs"])

    compared = 0
    exact = 0
    abs_diff: list[float] = []
    by_island = {island: {"compared": 0, "exact": 0} for island in ISLANDS}
    for row in chick_rows:
        key = (
            str(row["island"]),
            str(row["colony_code"]),
            int(row["season"]),
        )
        if key not in lookup:
            continue
        compared += 1
        by_island[key[0]]["compared"] += 1
        a = float(row["pairs"])
        b = float(lookup[key])
        if a == b:
            exact += 1
            by_island[key[0]]["exact"] += 1
        abs_diff.append(abs(a - b))
    return {
        "n_compared": compared,
        "n_exact": exact,
        "exact_fraction": exact / compared if compared else None,
        "median_absolute_difference": (
            float(np.median(abs_diff)) if abs_diff else None
        ),
        "by_island": {
            island: {
                **values,
                "exact_fraction": (
                    values["exact"] / values["compared"]
                    if values["compared"]
                    else None
                ),
            }
            for island, values in by_island.items()
        },
    }


def _summary(sets: list[dict[str, object]]) -> dict[str, object]:
    rows = [row for item in sets for row in item["rows"]]
    ratios = [float(r["chicks"]) / float(r["pairs"]) for r in rows]
    return {
        "n_island_seasons": len(sets),
        "n_colony_season_rows": len(rows),
        "season_range": [
            min(int(item["season"]) for item in sets),
            max(int(item["season"]) for item in sets),
        ],
        "total_chicks": int(sum(int(item["total_chicks"]) for item in sets)),
        "median_pairs": float(np.median([float(r["pairs"]) for r in rows])),
        "median_chicks_per_pair_descriptive": float(np.median(ratios)),
    }


def _fit_only(
    rows: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...],
    minimum_pairs: float,
) -> dict[str, object]:
    sets = build_island_season_sets(
        rows,
        allowed_islands=allowed_islands,
        minimum_pairs=minimum_pairs,
    )
    return {
        "summary": _summary(sets),
        "fit": fit_beta(sets),
        "score_at_beta1": score_at_one(sets),
    }


def analyze(
    chick_path: str | Path,
    adult_census: str | Path | None = None,
    *,
    n_draws: int = N_DRAWS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_draws < 999:
        raise ValueError("at least 999 null draws are required")
    rows = load_chick_rows(chick_path)
    sets = build_island_season_sets(rows)
    fit = fit_beta(sets)
    primary = conditional_multinomial_score_test(
        sets, n_draws=n_draws, seed=seed
    )

    leave_one_out = {}
    for island in ISLANDS:
        local = _fit_only(
            rows,
            allowed_islands=tuple(x for x in ISLANDS if x != island),
            minimum_pairs=1.0,
        )
        leave_one_out[island] = {
            "beta_hat": local["fit"]["beta_hat"],
            "score_at_beta1": local["score_at_beta1"],
        }

    exclude_lit_sets = build_island_season_sets(
        rows,
        allowed_islands=tuple(x for x in ISLANDS if x != "LIT"),
    )
    min2_sets = build_island_season_sets(rows, minimum_pairs=2.0)

    sensitivity = {
        "exclude_litchfield": {
            "fit": fit_beta(exclude_lit_sets),
            "score_test": conditional_multinomial_score_test(
                exclude_lit_sets, n_draws=n_draws, seed=seed + 1
            ),
        },
        "minimum_pairs_2": {
            "fit": fit_beta(min2_sets),
            "score_test": conditional_multinomial_score_test(
                min2_sets, n_draws=n_draws, seed=seed + 2
            ),
        },
        "leave_one_island_out": leave_one_out,
        "overdispersion_cv10": gamma_poisson_score_test(
            sets, cv=0.10, n_draws=n_draws, seed=seed + 10
        ),
        "overdispersion_cv20": gamma_poisson_score_test(
            sets, cv=0.20, n_draws=n_draws, seed=seed + 20
        ),
    }

    support = bool(
        float(fit["beta_hat"]) > 1.0
        and float(primary["one_sided_upper_p"]) <= 0.05
    )
    overlap = (
        adult_overlap_diagnostic(rows, adult_census)
        if adult_census is not None
        else None
    )
    source_bytes = Path(chick_path).read_bytes()
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-colony-size-reproduction-v1",
        "contract_id": "mina-palmer-colony-size-reproduction-v1",
        "source": {
            "dataset": "AdeliePenguinAdultandChickCounts",
            "doi": "10.6073/pasta/9bf4588c02d6caa12a68133134ed4489",
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "usable_rows": len(rows),
        },
        "primary_panel": _summary(sets),
        "primary_effect": fit,
        "primary_inference": primary,
        "sensitivities": sensitivity,
        "adult_denominator_overlap": overlap,
        "decision": {
            "superlinear_reproductive_scaling_supported": support,
            "direction": (
                "superlinear" if float(fit["beta_hat"]) > 1
                else "proportional_or_sublinear"
            ),
            "social_facilitation_mechanism_supported": support,
        },
        "interpretation_boundary": {
            "ratio_not_used_as_primary_response": True,
            "island_season_conditioned": True,
            "positive_result_not_specific_to_predation": True,
            "terrain_and_snow_confounding_remain_possible": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--adult-census", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--draws", type=int, default=N_DRAWS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(
        args.chicks,
        args.adult_census,
        n_draws=args.draws,
        seed=args.seed,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
