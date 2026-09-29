"""Matched subcolony extinction-risk analysis for Palmer Adélie penguins."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows

STABLE_ISLANDS = ("COR", "HUM", "LIT")
N_PERMUTATIONS = 20_000
SEED = 20260929


def _raw_lookup(rows: list[dict[str, object]]):
    by_code: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    island_years: dict[str, set[int]] = defaultdict(set)
    island_year_codes: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    for row in rows:
        island = str(row["island"])
        code = str(row["colony_code"])
        year = int(row["year"])
        count = float(row["breeding_pairs"])
        by_code[(island, code)][year] = count
        island_years[island].add(year)
        island_year_codes[(island, year)][code] = count
    return by_code, island_years, island_year_codes


def transition_rows_from_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Construct positive colony-year risk intervals with adjacent t+1 census."""
    by_code, island_years, island_year_codes = _raw_lookup(rows)
    out: list[dict[str, object]] = []
    for (island, code), rec in sorted(by_code.items()):
        years_all = sorted(island_years[island])
        final_year = years_all[-1]
        for year in sorted(rec):
            count = float(rec[year])
            if count <= 0 or year + 1 not in rec:
                continue
            next_count = float(rec[year + 1])
            future_years = [y for y in years_all if y >= year + 1]
            complete_future = all(y in rec for y in future_years)
            durable = bool(
                next_count == 0
                and complete_future
                and all(float(rec[y]) == 0 for y in future_years)
            )
            total = float(sum(island_year_codes[(island, year)].values()))
            if total <= 0:
                continue
            out.append(
                {
                    "island": island,
                    "colony_code": code,
                    "start_year": year,
                    "end_year": year + 1,
                    "current_pairs": count,
                    "next_pairs": next_count,
                    "current_island_total": total,
                    "current_share": count / total,
                    "durable_extinction": durable,
                    "future_roster_complete": complete_future,
                    "island_final_year": final_year,
                }
            )
    return out


def transition_rows(path: str | Path) -> list[dict[str, object]]:
    return transition_rows_from_rows(load_colony_rows(path))


def _logsumexp(values: np.ndarray) -> float:
    vmax = float(np.max(values))
    return vmax + math.log(float(np.sum(np.exp(values - vmax))))


def _conditional_groups(
    rows: list[dict[str, object]], islands: tuple[str, ...]
) -> tuple[list[dict[str, object]], float, float]:
    local = [r for r in rows if str(r["island"]) in islands]
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in local:
        grouped[(str(row["island"]), int(row["start_year"]))].append(row)

    informative: list[tuple[tuple[str, int], list[dict[str, object]]]] = []
    for key, group in sorted(grouped.items()):
        m = sum(bool(r["durable_extinction"]) for r in group)
        if 0 < m < len(group):
            informative.append((key, group))
    if not informative:
        raise ValueError("no informative island-year extinction strata")

    raw_x = np.asarray(
        [math.log1p(float(r["current_pairs"])) for _, g in informative for r in g],
        dtype=float,
    )
    mean = float(np.mean(raw_x))
    sd = float(np.std(raw_x, ddof=1))
    if sd <= 0:
        raise ValueError("zero extinction-predictor variance")

    result: list[dict[str, object]] = []
    for (island, year), group in informative:
        x = np.asarray(
            [(math.log1p(float(r["current_pairs"])) - mean) / sd for r in group],
            dtype=float,
        )
        y = np.asarray([bool(r["durable_extinction"]) for r in group], dtype=bool)
        m = int(np.sum(y))
        subset_sums = np.asarray(
            [float(np.sum(x[list(idx)])) for idx in combinations(range(len(group)), m)],
            dtype=float,
        )
        result.append(
            {
                "island": island,
                "year": year,
                "x": x,
                "y": y,
                "m": m,
                "observed_sum": float(np.sum(x[y])),
                "subset_sums": subset_sums,
            }
        )
    return result, mean, sd


def _fit_conditional_beta(groups: list[dict[str, object]]) -> dict[str, float]:
    beta = 0.0
    for _ in range(100):
        score = 0.0
        hess = 0.0
        for group in groups:
            sums = group["subset_sums"]
            eta = beta * sums
            vmax = float(np.max(eta))
            w = np.exp(eta - vmax)
            w /= float(np.sum(w))
            mean_sum = float(np.sum(w * sums))
            var_sum = float(np.sum(w * (sums - mean_sum) ** 2))
            score += float(group["observed_sum"]) - mean_sum
            hess -= var_sum
        if hess >= 0 or not math.isfinite(hess):
            raise ValueError("invalid conditional-logit Hessian")
        step = score / hess
        beta_new = float(np.clip(beta - step, -25.0, 25.0))
        if abs(beta_new - beta) < 1e-10:
            beta = beta_new
            break
        beta = beta_new

    score = 0.0
    hess = 0.0
    loglik = 0.0
    for group in groups:
        sums = group["subset_sums"]
        eta = beta * sums
        lse = _logsumexp(eta)
        w = np.exp(eta - lse)
        mean_sum = float(np.sum(w * sums))
        var_sum = float(np.sum(w * (sums - mean_sum) ** 2))
        score += float(group["observed_sum"]) - mean_sum
        hess -= var_sum
        loglik += beta * float(group["observed_sum"]) - lse
    if hess >= 0:
        raise ValueError("non-negative final Hessian")
    se = math.sqrt(-1.0 / hess)
    return {
        "beta_per_sd_log1p_pairs": beta,
        "se": se,
        "ci95_low": beta - 1.96 * se,
        "ci95_high": beta + 1.96 * se,
        "odds_ratio_per_sd": math.exp(beta),
        "odds_ratio_ci95_low": math.exp(beta - 1.96 * se),
        "odds_ratio_ci95_high": math.exp(beta + 1.96 * se),
        "log_likelihood": loglik,
        "score_at_solution": score,
    }


def matched_hazard(
    rows: list[dict[str, object]],
    islands: tuple[str, ...],
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 99:
        raise ValueError("at least 99 permutations are required")
    groups, mean, sd = _conditional_groups(rows, islands)
    fit = _fit_conditional_beta(groups)
    observed = float(sum(float(g["observed_sum"]) for g in groups))

    rng = np.random.default_rng(seed)
    null = np.zeros(n_permutations, dtype=float)
    for group in groups:
        sums = group["subset_sums"]
        null += rng.choice(sums, size=n_permutations, replace=True)
    lower = (1 + int(np.sum(null <= observed))) / (n_permutations + 1)
    upper = (1 + int(np.sum(null >= observed))) / (n_permutations + 1)
    p_two = float(min(1.0, 2.0 * min(lower, upper)))

    n_rows = int(sum(len(g["x"]) for g in groups))
    n_events = int(sum(int(g["m"]) for g in groups))

    informative_keys = {(str(g["island"]), int(g["year"])) for g in groups}
    informative_rows = [
        r
        for r in rows
        if str(r["island"]) in islands
        and (str(r["island"]), int(r["start_year"])) in informative_keys
    ]
    event_rows = [r for r in informative_rows if bool(r["durable_extinction"])]
    survivor_rows = [r for r in informative_rows if not bool(r["durable_extinction"])]

    def _summary(local: list[dict[str, object]]) -> dict[str, float | int | None]:
        if not local:
            return {"n": 0, "median_pairs": None, "median_share": None}
        pairs = np.asarray([float(r["current_pairs"]) for r in local], dtype=float)
        shares = np.asarray([float(r["current_share"]) for r in local], dtype=float)
        return {
            "n": len(local),
            "median_pairs": float(np.median(pairs)),
            "mean_pairs": float(np.mean(pairs)),
            "q25_pairs": float(np.quantile(pairs, 0.25)),
            "q75_pairs": float(np.quantile(pairs, 0.75)),
            "median_share": float(np.median(shares)),
            "mean_share": float(np.mean(shares)),
        }

    return {
        "islands": list(islands),
        "n_informative_strata": len(groups),
        "n_risk_rows": n_rows,
        "n_durable_extinctions": n_events,
        "predictor": "z(log1p breeding pairs at t) within analysis scope",
        "conditioning": (
            "island x start-year; strata without both event and survivor are non-informative"
        ),
        "standardization": {"raw_log1p_mean": mean, "raw_log1p_sd": sd},
        "conditional_logit": fit,
        "descriptive_risk_set_comparison": {
            "durable_extinction_events": _summary(event_rows),
            "same_stratum_survivors": _summary(survivor_rows),
            "share_role": (
                "descriptive only: island total is fixed within island-year strata, so current "
                "group size and within-island share encode nearly the same ordering and are not "
                "treated as independent causal predictors"
            ),
        },
        "permutation": {
            "statistic": (
                "sum standardized log1p pairs among observed durable-extinction events"
            ),
            "observed": observed,
            "null_mean": float(np.mean(null)),
            "null_sd": float(np.std(null, ddof=1)),
            "q025": float(np.quantile(null, 0.025)),
            "q975": float(np.quantile(null, 0.975)),
            "two_sided_p": p_two,
            "n_permutations": n_permutations,
            "seed": seed,
        },
        "supported": bool(
            fit["beta_per_sd_log1p_pairs"] < 0.0 and p_two <= 0.05
        ),
    }


def proportional_thinning_null(
    raw_rows: list[dict[str, object]],
    islands: tuple[str, ...],
    n_simulations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_simulations < 99:
        raise ValueError("at least 99 simulations are required")
    _, island_years, island_year_codes = _raw_lookup(raw_rows)
    groups: list[dict[str, object]] = []
    skipped_missing_next = 0

    for island in islands:
        years = sorted(island_years.get(island, set()))
        for year in years:
            if year + 1 not in island_years.get(island, set()):
                continue
            current = island_year_codes[(island, year)]
            nxt = island_year_codes[(island, year + 1)]
            active_codes = sorted(code for code, count in current.items() if count > 0)
            if not active_codes:
                continue
            if any(code not in nxt for code in active_codes):
                skipped_missing_next += 1
                continue
            counts = np.asarray(
                [float(current[code]) for code in active_codes], dtype=float
            )
            probs = counts / float(np.sum(counts))
            next_active_mass = int(
                round(sum(float(nxt[code]) for code in active_codes))
            )
            observed_zero = int(
                sum(float(nxt[code]) == 0.0 for code in active_codes)
            )
            groups.append(
                {
                    "island": island,
                    "year": year,
                    "active_codes": active_codes,
                    "probs": probs,
                    "next_active_mass": next_active_mass,
                    "observed_zero": observed_zero,
                }
            )

    if not groups:
        raise ValueError("no proportional-thinning transition groups")

    observed = int(sum(int(g["observed_zero"]) for g in groups))
    rng = np.random.default_rng(seed)
    null = np.zeros(n_simulations, dtype=int)
    for group in groups:
        draws = rng.multinomial(
            int(group["next_active_mass"]),
            group["probs"],
            size=n_simulations,
        )
        null += np.sum(draws == 0, axis=1)
    p_upper = (1 + int(np.sum(null >= observed))) / (n_simulations + 1)
    return {
        "islands": list(islands),
        "n_island_year_transitions": len(groups),
        "skipped_for_missing_next_code": skipped_missing_next,
        "observed_next_year_zero_transitions": observed,
        "null": {
            "description": (
                "Within each island-year, retain the observed next-year breeding-pair mass "
                "assigned to colony codes active at t and allocate it multinomially among "
                "those codes in proportion to their t shares. New/reappearing-code mass is "
                "conditioned out rather than reassigned."
            ),
            "mean_zero_transitions": float(np.mean(null)),
            "sd_zero_transitions": float(np.std(null, ddof=1)),
            "q025": float(np.quantile(null, 0.025)),
            "q975": float(np.quantile(null, 0.975)),
            "max_simulated": int(np.max(null)),
            "upper_tail_p": float(p_upper),
            "n_simulations": n_simulations,
            "seed": seed,
        },
        "excess_zero_supported": bool(
            observed > float(np.quantile(null, 0.975)) and p_upper <= 0.05
        ),
    }


def analyze(
    census: str | Path,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    raw = load_colony_rows(census)
    transitions = transition_rows_from_rows(raw)
    primary_hazard = matched_hazard(
        transitions,
        STABLE_ISLANDS,
        n_permutations=n_permutations,
        seed=seed,
    )
    all5_hazard = matched_hazard(
        transitions,
        ISLANDS,
        n_permutations=n_permutations,
        seed=seed + 1,
    )
    primary_thinning = proportional_thinning_null(
        raw,
        STABLE_ISLANDS,
        n_simulations=n_permutations,
        seed=seed + 2,
    )
    all5_thinning = proportional_thinning_null(
        raw,
        ISLANDS,
        n_simulations=n_permutations,
        seed=seed + 3,
    )
    overall = bool(
        primary_hazard["supported"]
        and primary_thinning["excess_zero_supported"]
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-subcolony-extinction-hazard-v1",
        "inference_status": "post_outcome_exploratory_frozen_for_reproducibility",
        "source_row_count": len(raw),
        "n_positive_adjacent_risk_rows": len(transitions),
        "primary_stable_roster": {
            "islands": list(STABLE_ISLANDS),
            "matched_hazard": primary_hazard,
            "proportional_thinning_null": primary_thinning,
        },
        "five_island_sensitivity": {
            "islands": list(ISLANDS),
            "matched_hazard": all5_hazard,
            "proportional_thinning_null": all5_thinning,
        },
        "decision": {
            "ordered_small_group_attrition_beyond_simple_proportional_thinning": overall,
            "requires_both_primary_tests": True,
        },
        "interpretation_boundary": {
            "colony_codes_are_not_assumed_physical_polygons": True,
            "predation_or_social_facilitation_not_identified": True,
            "snow_or_terrain_mechanism_not_identified": True,
            "multinomial_null_is_not_a_full_demographic_process_model": True,
            "terminal_positive_rows_are_right_censored": True,
            "pre_entry_zero_rows_do_not_enter_risk_sets": True,
            "durable_extinction_requires_continuous_future_zero_observation": True,
            "size_and_share_not_separately_identified_within_island_year": True,
            "analysis_not_claimed_as_preregistered_or_confirmatory": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(
        args.census,
        n_permutations=args.permutations,
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
