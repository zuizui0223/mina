"""Source-paired Palmer Adélie group-size / reproductive-success analysis v2.

Chick counts come from the January chick census. Breeding-pair denominators come
from the independent November breeding census matched by study_name, island and
colony_code. The legacy chick-table num_breeding_pairs field is deliberately
not used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows

N_DRAWS = 100_000
SEED = 20260930
MIN_COLONIES = 4
_STUDY_RE = re.compile(r"^PAL(\d{2})(\d{2})$")


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def study_start_year(study_name: str) -> int | None:
    m = _STUDY_RE.match(study_name.strip())
    if m is None:
        return None
    yy = int(m.group(1))
    return 1900 + yy if yy >= 50 else 2000 + yy


def load_adult_pairs(path: str | Path) -> dict[tuple[str, str, str], float]:
    rows = load_colony_rows(path)
    out: dict[tuple[str, str, str], float] = {}
    for row in rows:
        key = (
            str(row["study_name"]).strip(),
            str(row["island"]).strip(),
            str(row["colony_code"]).strip(),
        )
        if key in out:
            raise ValueError(f"duplicate adult study/island/colony key: {key!r}")
        value = float(row["breeding_pairs"])
        if value < 0:
            raise ValueError("negative breeding-pair count")
        out[key] = value
    if not out:
        raise ValueError("no adult breeding-pair rows")
    return out


def load_chick_candidates(
    path: str | Path,
) -> dict[tuple[str, str, str], list[dict[str, object]]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        raw = list(csv.DictReader(handle))
    out: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in raw:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        if not _finite(row.get("num_chicks")):
            continue
        chicks = float(row["num_chicks"])
        if chicks < 0:
            raise ValueError("negative chick count")
        study = str(row.get("study_name", "")).strip()
        code = str(row.get("colony_code", "")).strip()
        if not study or not code:
            continue
        time = str(row.get("time", "")).strip()
        calendar_season: int | None = None
        try:
            calendar_season = int(time[:4]) - 1
        except (TypeError, ValueError):
            pass
        encoded = study_start_year(study)
        out[(study, island, code)].append(
            {
                "study_name": study,
                "island": island,
                "colony_code": code,
                "chicks": chicks,
                "time": time,
                "census_time": str(row.get("census_time", "")).strip(),
                "study_start_year": encoded,
                "calendar_derived_season": calendar_season,
                "date_conflict": bool(
                    encoded is not None
                    and calendar_season is not None
                    and encoded != calendar_season
                ),
            }
        )
    if not out:
        raise ValueError("no usable chick rows")
    return dict(out)


def choose_chick_rows(
    candidates: dict[tuple[str, str, str], list[dict[str, object]]]
) -> tuple[dict[tuple[str, str, str], dict[str, object]], dict[str, object]]:
    chosen: dict[tuple[str, str, str], dict[str, object]] = {}
    duplicate_keys: list[str] = []
    for key, local in sorted(candidates.items()):
        if len(local) > 1:
            duplicate_keys.append("|".join(key))
        selected = sorted(
            local,
            key=lambda r: (
                -float(r["chicks"]),
                str(r["time"]),
                str(r["census_time"]),
            ),
        )[0]
        x = dict(selected)
        x["source_duplicate_count"] = len(local)
        chosen[key] = x
    return chosen, {
        "candidate_key_count": len(candidates),
        "duplicate_key_count": len(duplicate_keys),
        "duplicate_keys": duplicate_keys,
    }


def source_paired_rows(
    chick_path: str | Path,
    adult_path: str | Path,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    adult = load_adult_pairs(adult_path)
    candidates = load_chick_candidates(chick_path)
    chicks, duplicate_diag = choose_chick_rows(candidates)

    chick_keys = set(chicks)
    adult_keys = set(adult)
    matched = sorted(chick_keys & adult_keys)
    rows: list[dict[str, object]] = []
    matched_zero_pairs = 0
    for key in matched:
        pairs = float(adult[key])
        if pairs <= 0:
            matched_zero_pairs += 1
            continue
        chick = chicks[key]
        count = float(chick["chicks"])
        rows.append(
            {
                **chick,
                "pairs": pairs,
                "chicks_per_pair": count / pairs,
                "biologically_inconsistent_ratio": bool(count > 2.0 * pairs),
            }
        )
    if not rows:
        raise ValueError("no positive-pair source-matched rows")

    ratios = np.asarray([float(r["chicks_per_pair"]) for r in rows], dtype=float)
    conflicts = [r for r in rows if bool(r["date_conflict"])]
    inconsistent = [r for r in rows if bool(r["biologically_inconsistent_ratio"])]
    diag = {
        **duplicate_diag,
        "adult_key_count": len(adult_keys),
        "chick_key_count": len(chick_keys),
        "matched_key_count_before_positive_pair_filter": len(matched),
        "matched_positive_pair_rows": len(rows),
        "matched_zero_pair_keys": matched_zero_pairs,
        "unmatched_chick_keys": len(chick_keys - adult_keys),
        "unmatched_adult_keys": len(adult_keys - chick_keys),
        "date_conflict_rows": len(conflicts),
        "date_conflict_keys": [
            f"{r['study_name']}|{r['island']}|{r['colony_code']}" for r in conflicts
        ],
        "chicks_gt_2x_pairs_rows": len(inconsistent),
        "chicks_gt_2x_pairs_keys": [
            f"{r['study_name']}|{r['island']}|{r['colony_code']}" for r in inconsistent
        ],
        "ratio_quantiles": {
            "q00": float(np.quantile(ratios, 0.00)),
            "q01": float(np.quantile(ratios, 0.01)),
            "q05": float(np.quantile(ratios, 0.05)),
            "q50": float(np.quantile(ratios, 0.50)),
            "q95": float(np.quantile(ratios, 0.95)),
            "q99": float(np.quantile(ratios, 0.99)),
            "q100": float(np.quantile(ratios, 1.00)),
        },
    }
    return rows, diag


def build_groups(
    rows: list[dict[str, object]],
    *,
    islands: tuple[str, ...] = ISLANDS,
    min_pairs: float = 1.0,
    exclude_inconsistent_ratio: bool = False,
    exclude_date_conflict: bool = False,
) -> list[dict[str, object]]:
    allowed = set(islands)
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if str(row["island"]) not in allowed:
            continue
        if float(row["pairs"]) < min_pairs:
            continue
        if exclude_inconsistent_ratio and bool(row["biologically_inconsistent_ratio"]):
            continue
        if exclude_date_conflict and bool(row["date_conflict"]):
            continue
        grouped[(str(row["island"]), str(row["study_name"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, study), local in sorted(grouped.items()):
        if len(local) < MIN_COLONIES:
            continue
        pairs = np.asarray([float(r["pairs"]) for r in local], dtype=float)
        chicks_float = np.asarray([float(r["chicks"]) for r in local], dtype=float)
        if np.any(pairs <= 0) or np.any(chicks_float < 0):
            raise ValueError("invalid paired counts")
        if not np.allclose(chicks_float, np.rint(chicks_float), atol=1e-9):
            raise ValueError("non-integer chick count encountered")
        chicks = np.rint(chicks_float).astype(np.int64)
        total_chicks = int(np.sum(chicks))
        if total_chicks < 1:
            continue

        xraw = np.log1p(pairs)
        sd = float(np.std(xraw, ddof=0))
        if not math.isfinite(sd) or sd <= 0:
            continue
        x = (xraw - float(np.mean(xraw))) / sd
        p = pairs / float(np.sum(pairs))
        mu_x = float(np.sum(p * x))
        var_x = float(np.sum(p * (x - mu_x) ** 2))
        info = total_chicks * var_x
        if info <= 0 or not math.isfinite(info):
            continue
        score = float(np.sum(chicks * x) - total_chicks * mu_x)
        out.append(
            {
                "key": f"{island}:{study}",
                "island": island,
                "study_name": study,
                "study_start_year": study_start_year(study),
                "n_colonies": len(local),
                "pairs": pairs,
                "chicks": chicks,
                "x": x,
                "p": p,
                "total_pairs": float(np.sum(pairs)),
                "total_chicks": total_chicks,
                "score": score,
                "information": info,
                "mean_chicks_per_pair": total_chicks / float(np.sum(pairs)),
            }
        )
    if not out:
        raise ValueError("no eligible island-season groups")
    return out


def observed_score(groups: list[dict[str, object]]) -> dict[str, float]:
    score = float(sum(float(g["score"]) for g in groups))
    info = float(sum(float(g["information"]) for g in groups))
    if info <= 0:
        raise ValueError("non-positive total information")
    return {"score": score, "information": info, "z": score / math.sqrt(info)}


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
    obs = observed_score(groups)
    null_score: np.ndarray | None = None
    for group in groups:
        vals = contributions[str(group["key"])]
        null_score = vals.copy() if null_score is None else null_score + vals
    if null_score is None:
        raise ValueError("empty null contribution set")
    denom = math.sqrt(float(obs["information"]))
    null_z = null_score / denom
    z = float(obs["z"])
    p = float((1 + int(np.sum(null_z >= z))) / (null_z.size + 1))
    return {
        "n_groups": len(groups),
        "n_colony_rows": int(sum(int(g["n_colonies"]) for g in groups)),
        "observed_score": float(obs["score"]),
        "observed_information": float(obs["information"]),
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
    info = float("nan")
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
            raise ValueError("non-positive information in effect-size model")
        step = score / info
        beta += step
        if abs(step) < 1e-10:
            break
    se = 1.0 / math.sqrt(info)
    return {
        "beta_per_within_group_sd_log1p_pairs": float(beta),
        "naive_information_se": float(se),
        "multiplicative_per_pair_success_per_1sd_larger_group": float(math.exp(beta)),
        "wald_95ci_beta": [float(beta - 1.96 * se), float(beta + 1.96 * se)],
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
        remaining_prob = np.clip(remaining_prob - q[:, idx], 0.0, 1.0)
    weighted += remaining_count * x[-1]
    return weighted - c * float(np.sum(p * x))


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
    obs = observed_score(groups)
    denom = math.sqrt(float(obs["information"]))
    null_z = null_score / denom
    z = float(obs["z"])
    p = float((1 + int(np.sum(null_z >= z))) / (n_draws + 1))
    return {
        "concentration": float(concentration),
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
    years = [
        int(g["study_start_year"])
        for g in groups
        if g["study_start_year"] is not None
    ]
    by_island: dict[str, object] = {}
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
    return {
        "n_groups": len(groups),
        "n_colony_rows": int(sum(int(g["n_colonies"]) for g in groups)),
        "season_range": [min(years), max(years)] if years else None,
        "n_seasons": len(set(years)),
        "by_island": by_island,
    }


def _run_variant(
    rows: list[dict[str, object]],
    *,
    islands: tuple[str, ...] = ISLANDS,
    min_pairs: float = 1.0,
    exclude_inconsistent_ratio: bool = False,
    exclude_date_conflict: bool = False,
    n_draws: int,
    seed: int,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    groups = build_groups(
        rows,
        islands=islands,
        min_pairs=min_pairs,
        exclude_inconsistent_ratio=exclude_inconsistent_ratio,
        exclude_date_conflict=exclude_date_conflict,
    )
    result, _ = multinomial_test(groups, n_draws=n_draws, seed=seed)
    return groups, result


def analyze(
    chick_path: str | Path,
    adult_path: str | Path,
    *,
    n_draws: int = N_DRAWS,
    seed: int = SEED,
) -> dict[str, object]:
    rows, pairing = source_paired_rows(chick_path, adult_path)
    groups = build_groups(rows)
    primary, contributions = multinomial_test(
        groups, n_draws=n_draws, seed=seed
    )
    effect = conditional_size_effect(groups)

    loo: dict[str, object] = {}
    for island in ISLANDS:
        local = [g for g in groups if str(g["island"]) != island]
        loo[island] = combine_test(local, contributions)

    _, no_lit = _run_variant(
        rows,
        islands=tuple(i for i in ISLANDS if i != "LIT"),
        n_draws=n_draws,
        seed=seed + 10,
    )
    _, p2 = _run_variant(
        rows, min_pairs=2.0, n_draws=n_draws, seed=seed + 20
    )
    _, p5 = _run_variant(
        rows, min_pairs=5.0, n_draws=n_draws, seed=seed + 21
    )
    _, consistent = _run_variant(
        rows,
        exclude_inconsistent_ratio=True,
        n_draws=n_draws,
        seed=seed + 22,
    )
    _, date_clean = _run_variant(
        rows,
        exclude_date_conflict=True,
        n_draws=n_draws,
        seed=seed + 23,
    )
    dm100 = dirichlet_multinomial_test(
        groups, concentration=100.0, n_draws=n_draws, seed=seed + 30
    )
    dm25 = dirichlet_multinomial_test(
        groups, concentration=25.0, n_draws=n_draws, seed=seed + 31
    )

    source_robust = bool(
        primary["supported"]
        and consistent["supported"]
        and date_clean["supported"]
    )
    positive_loo = all(float(v["observed_z"]) > 0 for v in loo.values())
    stronger = bool(
        source_robust
        and positive_loo
        and float(p2["observed_z"]) > 0
        and float(p5["observed_z"]) > 0
    )

    return {
        "schema_version": 2,
        "analysis_id": "mina-palmer-small-group-reproductive-success-v2",
        "contract_id": "mina-palmer-small-group-reproductive-success-v2",
        "source": {
            "chick_dataset": "AdeliePenguinAdultandChickCounts",
            "chick_doi": "10.6073/pasta/9bf4588c02d6caa12a68133134ed4489",
            "chick_sha256": hashlib.sha256(Path(chick_path).read_bytes()).hexdigest(),
            "adult_dataset": "AdeliePenguinCensus",
            "adult_doi": "10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e",
            "adult_sha256": hashlib.sha256(Path(adult_path).read_bytes()).hexdigest(),
        },
        "pairing_diagnostics": pairing,
        "analysis_frame": _group_summary(groups),
        "primary_equal_per_pair_null": primary,
        "effect_size": effect,
        "sensitivities": {
            "exclude_litchfield": no_lit,
            "leave_one_island_out": loo,
            "pairs_at_least_2": p2,
            "pairs_at_least_5": p5,
            "exclude_chicks_gt_2x_pairs": consistent,
            "exclude_legacy_date_conflicts": date_clean,
            "dirichlet_multinomial_A100": dm100,
            "dirichlet_multinomial_A25": dm25,
        },
        "decision": {
            "primary_supported": bool(primary["supported"]),
            "source_robust_support": source_robust,
            "positive_all_leave_one_island_out": positive_loo,
            "stronger_pattern": stronger,
            "robust_to_dirichlet_multinomial_A100": bool(dm100["supported"]),
            "robust_to_dirichlet_multinomial_A25": bool(dm25["supported"]),
        },
        "interpretation_boundary": {
            "legacy_chick_pair_field_not_used": True,
            "study_name_is_primary_season_key": True,
            "does_not_identify_predation": True,
            "does_not_prove_social_facilitation_or_allee_effect": True,
            "colony_code_not_assumed_physical_polygon": True,
            "v1_is_superseded_not_replication": True,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--chicks", required=True, type=Path)
    p.add_argument("--adult-census", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--draws", type=int, default=N_DRAWS)
    p.add_argument("--seed", type=int, default=SEED)
    a = p.parse_args()
    result = analyze(
        a.chicks,
        a.adult_census,
        n_draws=a.draws,
        seed=a.seed,
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
