"""Test whether small Palmer Adelie breeding groups have reduced per-pair chick output."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ISLANDS = ("CHR", "COR", "HUM", "LIT", "TOR")
N_DRAWS = 100_000
SEED = 20260929
MIN_COLONIES = 4


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_rows(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        raw = list(csv.DictReader(handle))
    candidates: dict[tuple[str, str, int], list[dict[str, object]]] = defaultdict(list)
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
        candidates[key].append(
            {
                "study_name": str(row.get("study_name", "")).strip(),
                "time": time,
                "season": season,
                "island": island,
                "colony_code": code,
                "pairs": pairs,
                "chicks": chicks,
                "chicks_per_pair": chicks / pairs,
                "census_time": str(row.get("census_time", "")).strip(),
            }
        )

    out: list[dict[str, object]] = []
    for key, local in sorted(candidates.items()):
        chosen = sorted(
            local,
            key=lambda r: (
                -float(r["chicks"]),
                -float(r["pairs"]),
                str(r["census_time"]),
            ),
        )[0]
        chosen = dict(chosen)
        chosen["source_duplicate_count"] = len(local)
        out.append(chosen)
    if not out:
        raise ValueError("no usable chick-production rows")
    return out


def build_groups(
    rows: list[dict[str, object]],
    *,
    islands: tuple[str, ...] = ISLANDS,
    min_pairs: float = 1.0,
    exclude_duplicate_keys: bool = False,
) -> list[dict[str, object]]:
    allowed = set(islands)
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if str(row["island"]) not in allowed:
            continue
        if exclude_duplicate_keys and int(row.get("source_duplicate_count", 1)) > 1:
            continue
        if float(row["pairs"]) < min_pairs:
            continue
        grouped[(str(row["island"]), int(row["season"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, season), local in sorted(grouped.items()):
        if len(local) < MIN_COLONIES:
            continue
        pairs = np.asarray([float(r["pairs"]) for r in local], dtype=float)
        chicks = np.asarray([float(r["chicks"]) for r in local], dtype=float)
        total_chicks_float = float(np.sum(chicks))
        total_chicks = int(round(total_chicks_float))
        if not math.isclose(total_chicks_float, total_chicks, abs_tol=1e-9):
            raise ValueError("non-integer chick count encountered")
        if total_chicks < 1:
            continue
        x_raw = np.log1p(pairs)
        sd = float(np.std(x_raw, ddof=1))
        if sd <= 0 or not math.isfinite(sd):
            continue
        x = (x_raw - float(np.mean(x_raw))) / sd
        p = pairs / float(np.sum(pairs))
        mu_x = float(np.sum(p * x))
        var_x = float(np.sum(p * (x - mu_x) ** 2))
        information = total_chicks * var_x
        if information <= 0 or not math.isfinite(information):
            continue
        score = float(np.sum(chicks * x) - total_chicks * mu_x)
        out.append(
            {
                "key": f"{island}:{season}",
                "island": island,
                "season": season,
                "n_colonies": len(local),
                "pairs": pairs,
                "chicks": chicks,
                "x": x,
                "p": p,
                "total_pairs": float(np.sum(pairs)),
                "total_chicks": total_chicks,
                "score": score,
                "information": information,
                "mean_chicks_per_pair": total_chicks / float(np.sum(pairs)),
            }
        )
    if not out:
        raise ValueError("no eligible island-season groups")
    return out


def observed_score(groups: list[dict[str, object]]) -> dict[str, float]:
    score = float(np.sum([float(g["score"]) for g in groups]))
    information = float(np.sum([float(g["information"]) for g in groups]))
    if information <= 0:
        raise ValueError("non-positive total information")
    return {
        "score": score,
        "information": information,
        "z": score / math.sqrt(information),
    }


def simulate_multinomial_contributions(
    groups: list[dict[str, object]],
    *,
    n_draws: int,
    seed: int,
) -> dict[str, np.ndarray]:
    if n_draws < 999:
        raise ValueError("at least 999 Monte Carlo draws are required")
    rng = np.random.default_rng(seed)
    out: dict[str, np.ndarray] = {}
    for group in groups:
        p = np.asarray(group["p"], dtype=float)
        x = np.asarray(group["x"], dtype=float)
        c = int(group["total_chicks"])
        mu_x = float(np.sum(p * x))
        sim = rng.multinomial(c, p, size=n_draws)
        out[str(group["key"])] = sim @ x - c * mu_x
    return out


def combine_test(
    groups: list[dict[str, object]],
    contributions: dict[str, np.ndarray],
) -> dict[str, object]:
    observed = observed_score(groups)
    null_score: np.ndarray | None = None
    for group in groups:
        key = str(group["key"])
        values = contributions[key]
        null_score = values.copy() if null_score is None else null_score + values
    if null_score is None:
        raise ValueError("empty null contribution set")
    denom = math.sqrt(float(observed["information"]))
    null_z = null_score / denom
    z = float(observed["z"])
    p = float((1 + int(np.sum(null_z >= z))) / (null_z.size + 1))
    return {
        "n_groups": len(groups),
        "n_colony_rows": int(sum(int(g["n_colonies"]) for g in groups)),
        "observed_score": float(observed["score"]),
        "observed_information": float(observed["information"]),
        "observed_z": z,
        "null_mean_z": float(np.mean(null_z)),
        "null_sd_z": float(np.std(null_z, ddof=1)),
        "null_q025_z": float(np.quantile(null_z, 0.025)),
        "null_q975_z": float(np.quantile(null_z, 0.975)),
        "one_sided_upper_p": p,
        "supported": bool(z > 0 and p <= 0.05),
    }


def multinomial_test(
    groups: list[dict[str, object]],
    *,
    n_draws: int,
    seed: int,
) -> tuple[dict[str, object], dict[str, np.ndarray]]:
    contributions = simulate_multinomial_contributions(
        groups, n_draws=n_draws, seed=seed
    )
    return combine_test(groups, contributions), contributions


def conditional_size_effect(groups: list[dict[str, object]]) -> dict[str, object]:
    beta = 0.0
    iterations = 0
    for iterations in range(1, 101):
        score = 0.0
        info = 0.0
        for group in groups:
            pairs = np.asarray(group["pairs"], dtype=float)
            x = np.asarray(group["x"], dtype=float)
            chicks = np.asarray(group["chicks"], dtype=float)
            c = float(group["total_chicks"])
            eta = np.clip(beta * x, -30.0, 30.0)
            w = pairs * np.exp(eta)
            p = w / float(np.sum(w))
            mu = float(np.sum(p * x))
            var = float(np.sum(p * (x - mu) ** 2))
            score += float(np.sum(chicks * x) - c * mu)
            info += c * var
        if info <= 0:
            raise ValueError("non-positive information in size-effect model")
        step = score / info
        beta += step
        if abs(step) < 1e-10:
            break
    se = 1.0 / math.sqrt(info)
    return {
        "beta_per_within_group_sd_log1p_pairs": beta,
        "naive_information_se": se,
        "multiplicative_per_pair_success_per_1sd_larger_group": math.exp(beta),
        "wald_95ci_beta": [beta - 1.96 * se, beta + 1.96 * se],
        "iterations": iterations,
        "role": "descriptive effect size; Monte Carlo score test is primary",
    }


def _sample_dirichlet_multinomial_scores(
    group: dict[str, object],
    *,
    concentration: float,
    n_draws: int,
    rng: np.random.Generator,
) -> np.ndarray:
    p = np.asarray(group["p"], dtype=float)
    x = np.asarray(group["x"], dtype=float)
    c = int(group["total_chicks"])
    alpha = concentration * p
    gamma = rng.gamma(shape=alpha, scale=1.0, size=(n_draws, p.size))
    q = gamma / np.sum(gamma, axis=1, keepdims=True)

    remaining_count = np.full(n_draws, c, dtype=np.int64)
    remaining_prob = np.ones(n_draws, dtype=float)
    weighted = np.zeros(n_draws, dtype=float)
    for idx in range(p.size - 1):
        cond = np.divide(
            q[:, idx],
            remaining_prob,
            out=np.zeros_like(remaining_prob),
            where=remaining_prob > 0,
        )
        cond = np.clip(cond, 0.0, 1.0)
        draw = rng.binomial(remaining_count, cond)
        weighted += draw * x[idx]
        remaining_count -= draw
        remaining_prob -= q[:, idx]
        remaining_prob = np.clip(remaining_prob, 0.0, 1.0)
    weighted += remaining_count * x[-1]
    null_mu = c * float(np.sum(p * x))
    return weighted - null_mu


def dirichlet_multinomial_test(
    groups: list[dict[str, object]],
    *,
    concentration: float,
    n_draws: int,
    seed: int,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    null_score = np.zeros(n_draws, dtype=float)
    for group in groups:
        null_score += _sample_dirichlet_multinomial_scores(
            group,
            concentration=concentration,
            n_draws=n_draws,
            rng=rng,
        )
    observed = observed_score(groups)
    denom = math.sqrt(float(observed["information"]))
    null_z = null_score / denom
    z = float(observed["z"])
    p = float((1 + int(np.sum(null_z >= z))) / (n_draws + 1))
    return {
        "concentration": concentration,
        "n_groups": len(groups),
        "observed_z": z,
        "null_mean_z": float(np.mean(null_z)),
        "null_sd_z": float(np.std(null_z, ddof=1)),
        "null_q025_z": float(np.quantile(null_z, 0.025)),
        "null_q975_z": float(np.quantile(null_z, 0.975)),
        "one_sided_upper_p": p,
        "supported": bool(z > 0 and p <= 0.05),
    }


def _group_summary(groups: list[dict[str, object]]) -> dict[str, object]:
    by_island: dict[str, dict[str, float | int]] = {}
    for island in ISLANDS:
        local = [g for g in groups if str(g["island"]) == island]
        if not local:
            continue
        by_island[island] = {
            "n_groups": len(local),
            "n_colony_rows": int(sum(int(g["n_colonies"]) for g in local)),
            "total_pairs": float(sum(float(g["total_pairs"]) for g in local)),
            "total_chicks": int(sum(int(g["total_chicks"]) for g in local)),
        }
    seasons = sorted({int(g["season"]) for g in groups})
    return {
        "n_groups": len(groups),
        "season_range": [min(seasons), max(seasons)],
        "n_seasons": len(seasons),
        "by_island": by_island,
    }


def analyze(
    path: str | Path,
    *,
    n_draws: int = N_DRAWS,
    seed: int = SEED,
) -> dict[str, object]:
    rows = load_rows(path)
    groups = build_groups(rows)
    primary, contributions = multinomial_test(
        groups, n_draws=n_draws, seed=seed
    )

    loo: dict[str, object] = {}
    for island in ISLANDS:
        local = [g for g in groups if str(g["island"]) != island]
        loo[island] = combine_test(local, contributions)

    no_duplicate_groups = build_groups(rows, exclude_duplicate_keys=True)
    no_duplicate, _ = multinomial_test(
        no_duplicate_groups, n_draws=n_draws, seed=seed + 19
    )

    threshold2_groups = build_groups(rows, min_pairs=2.0)
    threshold2, _ = multinomial_test(
        threshold2_groups, n_draws=n_draws, seed=seed + 20
    )
    threshold5_groups = build_groups(rows, min_pairs=5.0)
    threshold5, _ = multinomial_test(
        threshold5_groups, n_draws=n_draws, seed=seed + 21
    )

    dm10 = dirichlet_multinomial_test(
        groups,
        concentration=100.0,
        n_draws=n_draws,
        seed=seed + 30,
    )
    dm20 = dirichlet_multinomial_test(
        groups,
        concentration=25.0,
        n_draws=n_draws,
        seed=seed + 31,
    )

    effect = conditional_size_effect(groups)
    positive_loo = all(float(v["observed_z"]) > 0 for v in loo.values())
    stronger = bool(
        primary["supported"]
        and positive_loo
        and float(threshold2["observed_z"]) > 0
        and float(threshold5["observed_z"]) > 0
    )

    source_bytes = Path(path).read_bytes()
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-small-group-reproductive-success-v1",
        "contract_id": "mina-palmer-small-group-reproductive-success-v1",
        "source": {
            "dataset": "AdeliePenguinAdultandChickCounts",
            "doi": "10.6073/pasta/9bf4588c02d6caa12a68133134ed4489",
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "usable_rows": len(rows),
            "duplicate_key_count": int(sum(int(r.get("source_duplicate_count", 1)) > 1 for r in rows)),
            "duplicate_keys": [
                f"{r['island']}:{r['colony_code']}:{r['season']}"
                for r in rows
                if int(r.get("source_duplicate_count", 1)) > 1
            ],
        },
        "analysis_frame": _group_summary(groups),
        "primary_equal_per_pair_null": primary,
        "effect_size": effect,
        "sensitivities": {
            "exclude_litchfield": loo["LIT"],
            "leave_one_island_out": loo,
            "exclude_duplicate_keys": no_duplicate,
            "pairs_at_least_2": threshold2,
            "pairs_at_least_5": threshold5,
            "dirichlet_multinomial_A100": dm10,
            "dirichlet_multinomial_A25": dm20,
        },
        "decision": {
            "small_group_reproductive_disadvantage_supported": bool(
                primary["supported"]
            ),
            "stronger_pattern": stronger,
            "positive_all_leave_one_island_out": positive_loo,
            "robust_to_dirichlet_multinomial_A100": bool(dm10["supported"]),
            "robust_to_dirichlet_multinomial_A25": bool(dm20["supported"]),
        },
        "interpretation_boundary": {
            "does_not_identify_predation": True,
            "does_not_prove_social_facilitation": True,
            "colony_code_not_assumed_physical_polygon": True,
            "extinction_order_not_used_as_independent_allee_evidence": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--draws", type=int, default=N_DRAWS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(args.chicks, n_draws=args.draws, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
