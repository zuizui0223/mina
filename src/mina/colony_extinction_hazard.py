"""Palmer Adelie colony-code durable-extinction hazard analysis."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ISLANDS = ("CHR", "COR", "HUM", "LIT", "TOR")
N_PERMUTATIONS = 100_000
SEED = 20260929
MAX_SUBSETS = 100_000


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
    out: list[dict[str, object]] = []
    seen: set[tuple[str, int, str, str]] = set()
    for row in raw:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS or not _finite(row.get("num_breeding_pairs")):
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
        code = str(row.get("colony_code", "")).strip()
        key = (study, year, island, code)
        if key in seen:
            raise ValueError(f"duplicate census key: {key!r}")
        seen.add(key)
        out.append(
            {
                "study_name": study,
                "year": year,
                "island": island,
                "colony_code": code,
                "count": count,
            }
        )
    if not out:
        raise ValueError("no Palmer colony rows parsed")
    return out


def _island_totals(rows: list[dict[str, object]]) -> dict[tuple[str, int], float]:
    out: dict[tuple[str, int], float] = defaultdict(float)
    for row in rows:
        out[(str(row["island"]), int(row["year"]))] += float(row["count"])
    return dict(out)


def build_transitions(
    rows: list[dict[str, object]],
    *,
    followup_zero_years: int = 2,
    allowed_islands: tuple[str, ...] = ISLANDS,
    minimum_prior_count: float = 1.0,
) -> list[dict[str, object]]:
    if followup_zero_years < 1:
        raise ValueError("followup_zero_years must be >= 1")
    allowed = set(allowed_islands)
    local_rows = [r for r in rows if str(r["island"]) in allowed]
    totals = _island_totals(local_rows)
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in local_rows:
        groups[(str(row["island"]), str(row["colony_code"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, code), local in sorted(groups.items()):
        by_year = {int(r["year"]): float(r["count"]) for r in local}
        years = sorted(by_year)
        positives = [year for year in years if by_year[year] > 0]
        if not positives:
            continue
        first_positive = min(positives)
        for end_year in years:
            start_year = end_year - 1
            if end_year <= first_positive or start_year not in by_year:
                continue
            prior = float(by_year[start_year])
            current = float(by_year[end_year])
            if prior < minimum_prior_count:
                continue

            event = 0
            if current == 0.0:
                if any(by_year[year] > 0 for year in years if year > end_year):
                    event = 0
                else:
                    required = [
                        end_year + offset
                        for offset in range(1, followup_zero_years + 1)
                    ]
                    if any(year not in by_year for year in required):
                        continue
                    if any(by_year[year] != 0.0 for year in required):
                        event = 0
                    else:
                        event = 1

            total_prior = float(totals[(island, start_year)])
            if total_prior <= 0:
                raise ValueError("positive colony count with non-positive island total")
            out.append(
                {
                    "island": island,
                    "colony_code": code,
                    "start_year": start_year,
                    "end_year": end_year,
                    "prior_count": prior,
                    "current_count": current,
                    "event": event,
                    "island_total_prior": total_prior,
                    "prior_share": prior / total_prior,
                    "log1p_prior": math.log1p(prior),
                }
            )
    return out


def standardize_risk_sets(
    transitions: list[dict[str, object]],
) -> list[dict[str, object]]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in transitions:
        groups[(str(row["island"]), int(row["end_year"]))].append(row)

    out: list[dict[str, object]] = []
    for _, local in sorted(groups.items()):
        if len(local) < 2:
            continue
        x = np.asarray([float(r["log1p_prior"]) for r in local], dtype=float)
        sd = float(np.std(x, ddof=1))
        if not math.isfinite(sd) or sd <= 0:
            continue
        mean = float(np.mean(x))
        for row in local:
            enriched = dict(row)
            enriched["risk_set_size"] = len(local)
            enriched["z_log1p_prior"] = (
                float(row["log1p_prior"]) - mean
            ) / sd
            out.append(enriched)
    return out


def _event_risk_sets(
    standardized: list[dict[str, object]],
) -> list[dict[str, object]]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in standardized:
        groups[(str(row["island"]), int(row["end_year"]))].append(row)
    out: list[dict[str, object]] = []
    for (island, year), local in sorted(groups.items()):
        events = np.asarray([int(r["event"]) for r in local], dtype=int)
        k = int(np.sum(events))
        if k <= 0 or k >= len(local):
            continue
        z = np.asarray(
            [float(r["z_log1p_prior"]) for r in local], dtype=float
        )
        prior = np.asarray(
            [float(r["prior_count"]) for r in local], dtype=float
        )
        current = np.asarray(
            [float(r["current_count"]) for r in local], dtype=float
        )
        contrast = float(
            np.mean(z[events == 1]) - np.mean(z[events == 0])
        )
        ratio = float(
            np.mean(prior[events == 1]) / np.mean(prior[events == 0])
        )
        out.append(
            {
                "island": island,
                "end_year": year,
                "n": len(local),
                "k": k,
                "z": z,
                "prior": prior,
                "current": current,
                "events": events,
                "observed_contrast": contrast,
                "event_to_non_event_mean_count_ratio": ratio,
            }
        )
    return out


def exchangeable_test(
    standardized: list[dict[str, object]],
    *,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    sets = _event_risk_sets(standardized)
    if len(sets) < 3:
        raise ValueError("fewer than three informative event-bearing risk sets")
    observed = float(
        np.mean([float(s["observed_contrast"]) for s in sets])
    )
    rng = np.random.default_rng(seed)
    null = np.zeros(n_permutations, dtype=float)
    for risk in sets:
        z = np.asarray(risk["z"], dtype=float)
        n = z.size
        k = int(risk["k"])
        random_scores = rng.random((n_permutations, n))
        idx = np.argpartition(random_scores, k - 1, axis=1)[:, :k]
        event_sum = z[idx].sum(axis=1)
        event_mean = event_sum / k
        non_event_mean = (float(np.sum(z)) - event_sum) / (n - k)
        null += event_mean - non_event_mean
    null /= len(sets)
    p = float(
        (1 + int(np.sum(null <= observed))) / (n_permutations + 1)
    )
    ratios = [
        float(s["event_to_non_event_mean_count_ratio"]) for s in sets
    ]
    return {
        "n_event_risk_sets": len(sets),
        "observed_contrast": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": p,
        "supported": bool(observed < 0 and p <= 0.05),
        "median_event_to_non_event_mean_count_ratio": float(
            np.median(ratios)
        ),
        "mean_event_to_non_event_mean_count_ratio": float(
            np.mean(ratios)
        ),
    }


def _subset_distribution(
    z: np.ndarray,
    q: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray]:
    n = int(z.size)
    n_subsets = math.comb(n, k)
    if n_subsets > MAX_SUBSETS:
        raise ValueError(
            f"risk set requires {n_subsets} subsets; exceeds frozen cap"
        )
    values: list[float] = []
    log_weights: list[float] = []
    eps = 1e-300
    for combo in itertools.combinations(range(n), k):
        mask = np.zeros(n, dtype=bool)
        mask[list(combo)] = True
        values.append(
            float(np.mean(z[mask]) - np.mean(z[~mask]))
        )
        event_log = np.log(np.clip(q[mask], eps, 1.0))
        nonevent_log = np.log(
            np.clip(1.0 - q[~mask], eps, 1.0)
        )
        log_weights.append(
            float(np.sum(event_log) + np.sum(nonevent_log))
        )
    logw = np.asarray(log_weights, dtype=float)
    shifted = logw - float(np.max(logw))
    weights = np.exp(shifted)
    weights /= float(np.sum(weights))
    return np.asarray(values, dtype=float), weights


def _neutral_q(
    risk: dict[str, object],
    family: str,
    cv: float | None = None,
) -> np.ndarray:
    prior = np.asarray(risk["prior"], dtype=float)
    current = np.asarray(risk["current"], dtype=float)
    n_total = float(np.sum(prior))
    m_total = float(np.sum(current))
    if n_total <= 0:
        raise ValueError("non-positive prior risk-set total")
    if family == "binomial":
        if m_total > n_total:
            raise ValueError(
                "binomial thinning requested for a growing risk set"
            )
        survival = m_total / n_total
        return np.power(max(0.0, 1.0 - survival), prior)
    lam = m_total * prior / n_total
    if family == "poisson":
        return np.exp(-lam)
    if family == "gamma_poisson":
        if cv is None or cv <= 0:
            raise ValueError(
                "positive cv required for gamma-Poisson null"
            )
        cv2 = cv * cv
        return np.power(
            1.0 + cv2 * lam, -1.0 / cv2
        )
    raise ValueError(f"unknown neutral family: {family}")


def size_conditioned_neutral_test(
    standardized: list[dict[str, object]],
    *,
    family: str = "poisson",
    cv: float | None = None,
    decline_only: bool = False,
    n_draws: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    raw_sets = _event_risk_sets(standardized)
    sets: list[dict[str, object]] = []
    for risk in raw_sets:
        prior = np.asarray(risk["prior"], dtype=float)
        current = np.asarray(risk["current"], dtype=float)
        if (
            decline_only
            and float(np.sum(current)) > float(np.sum(prior))
        ):
            continue
        q = _neutral_q(risk, family, cv)
        values, weights = _subset_distribution(
            np.asarray(risk["z"], dtype=float),
            q,
            int(risk["k"]),
        )
        enriched = dict(risk)
        enriched["null_values"] = values
        enriched["null_weights"] = weights
        sets.append(enriched)
    if len(sets) < 3:
        raise ValueError(
            "too few risk sets for size-conditioned neutral test"
        )

    observed = float(
        np.mean([float(s["observed_contrast"]) for s in sets])
    )
    rng = np.random.default_rng(seed)
    null = np.zeros(n_draws, dtype=float)
    for risk in sets:
        values = np.asarray(
            risk["null_values"], dtype=float
        )
        weights = np.asarray(
            risk["null_weights"], dtype=float
        )
        choice = rng.choice(
            values.size, size=n_draws, p=weights
        )
        null += values[choice]
    null /= len(sets)
    null_mean = float(np.mean(null))
    p = float(
        (1 + int(np.sum(null <= observed))) / (n_draws + 1)
    )
    return {
        "family": family,
        "cv": cv,
        "decline_only": decline_only,
        "n_event_risk_sets": len(sets),
        "observed_contrast": observed,
        "null_mean": null_mean,
        "observed_minus_null_mean": observed - null_mean,
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": p,
        "mechanism_gate_pass": bool(
            observed < null_mean and p <= 0.05
        ),
    }


def _logistic_fit(
    standardized: list[dict[str, object]],
) -> dict[str, object]:
    if not standardized:
        raise ValueError("empty standardized transition panel")
    island_values = [
        str(r["island"]) for r in standardized
    ]
    years = np.asarray(
        [float(r["end_year"]) for r in standardized],
        dtype=float,
    )
    year_sd = float(np.std(years, ddof=1))
    if year_sd <= 0:
        raise ValueError("zero year variance")
    year_z = (
        years - float(np.mean(years))
    ) / year_sd
    columns = [
        np.ones(len(standardized), dtype=float),
        np.asarray(
            [
                float(r["z_log1p_prior"])
                for r in standardized
            ],
            dtype=float,
        ),
    ]
    labels = ["intercept", "z_log1p_prior"]
    for island in ISLANDS[1:]:
        columns.append(
            np.asarray(
                [
                    1.0 if x == island else 0.0
                    for x in island_values
                ]
            )
        )
        labels.append(f"island_{island}")
    columns.append(year_z)
    labels.append("year_z")
    x = np.column_stack(columns)
    y = np.asarray(
        [float(r["event"]) for r in standardized],
        dtype=float,
    )

    beta = np.zeros(x.shape[1], dtype=float)
    ridge = 1e-8
    iterations = 0
    for iterations in range(1, 101):
        eta = x @ beta
        prob = 1.0 / (
            1.0 + np.exp(-np.clip(eta, -30.0, 30.0))
        )
        weight = prob * (1.0 - prob)
        gradient = x.T @ (y - prob) - ridge * beta
        information = (
            x.T @ (weight[:, None] * x)
            + ridge * np.eye(x.shape[1])
        )
        step = np.linalg.solve(information, gradient)
        beta = beta + step
        if float(np.max(np.abs(step))) < 1e-10:
            break
    eta = x @ beta
    prob = 1.0 / (
        1.0 + np.exp(-np.clip(eta, -30.0, 30.0))
    )
    weight = prob * (1.0 - prob)
    information = (
        x.T @ (weight[:, None] * x)
        + ridge * np.eye(x.shape[1])
    )
    covariance = np.linalg.inv(information)
    se = np.sqrt(np.diag(covariance))
    idx = labels.index("z_log1p_prior")
    coef = float(beta[idx])
    coef_se = float(se[idx])
    return {
        "n_rows": len(standardized),
        "n_events": int(np.sum(y)),
        "iterations": iterations,
        "size_coefficient": coef,
        "naive_hessian_se": coef_se,
        "odds_ratio_per_1sd_larger_prior_size": math.exp(coef),
        "wald_95ci_coefficient": [
            coef - 1.96 * coef_se,
            coef + 1.96 * coef_se,
        ],
        "role": (
            "descriptive effect-size summary; "
            "primary inference is permutation-based"
        ),
    }


def _quartiles(
    standardized: list[dict[str, object]],
) -> list[dict[str, object]]:
    ordered = sorted(
        standardized,
        key=lambda r: (
            float(r["prior_count"]),
            str(r["island"]),
            int(r["end_year"]),
            str(r["colony_code"]),
        ),
    )
    n = len(ordered)
    buckets: list[list[dict[str, object]]] = [
        [] for _ in range(4)
    ]
    for rank, row in enumerate(ordered):
        bucket = min(3, rank * 4 // n)
        buckets[bucket].append(row)
    out: list[dict[str, object]] = []
    for idx, local in enumerate(buckets, start=1):
        counts = [
            float(r["prior_count"]) for r in local
        ]
        events = int(
            sum(int(r["event"]) for r in local)
        )
        out.append(
            {
                "quartile": idx,
                "n": len(local),
                "events": events,
                "event_rate": (
                    events / len(local)
                    if local
                    else None
                ),
                "min_prior_count": (
                    min(counts) if counts else None
                ),
                "max_prior_count": (
                    max(counts) if counts else None
                ),
            }
        )
    return out


def _run_exchangeable_sensitivity(
    rows: list[dict[str, object]],
    *,
    followup_zero_years: int,
    allowed_islands: tuple[str, ...],
    minimum_prior_count: float,
    n_permutations: int,
    seed: int,
) -> dict[str, object]:
    transitions = build_transitions(
        rows,
        followup_zero_years=followup_zero_years,
        allowed_islands=allowed_islands,
        minimum_prior_count=minimum_prior_count,
    )
    standardized = standardize_risk_sets(transitions)
    result = exchangeable_test(
        standardized,
        n_permutations=n_permutations,
        seed=seed,
    )
    result["raw_transition_rows"] = len(transitions)
    result["raw_durable_events"] = int(
        sum(int(r["event"]) for r in transitions)
    )
    result["eligible_risk_set_rows"] = len(standardized)
    result["eligible_events"] = int(
        sum(int(r["event"]) for r in standardized)
    )
    return result


def analyze(
    path: str | Path,
    *,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 999:
        raise ValueError(
            "at least 999 permutations/draws are required"
        )
    rows = load_rows(path)
    transitions = build_transitions(rows)
    standardized = standardize_risk_sets(transitions)
    primary = exchangeable_test(
        standardized,
        n_permutations=n_permutations,
        seed=seed,
    )
    primary.update(
        {
            "raw_transition_rows": len(transitions),
            "raw_durable_events": int(
                sum(int(r["event"]) for r in transitions)
            ),
            "eligible_risk_set_rows": len(standardized),
            "eligible_events": int(
                sum(int(r["event"]) for r in standardized)
            ),
        }
    )

    event_counts = [
        float(r["prior_count"])
        for r in standardized
        if int(r["event"]) == 1
    ]
    survivor_counts = [
        float(r["prior_count"])
        for r in standardized
        if int(r["event"]) == 0
    ]

    neutral = size_conditioned_neutral_test(
        standardized,
        family="poisson",
        n_draws=n_permutations,
        seed=seed,
    )
    neutral_cv10 = size_conditioned_neutral_test(
        standardized,
        family="gamma_poisson",
        cv=0.10,
        n_draws=n_permutations,
        seed=seed,
    )
    neutral_cv20 = size_conditioned_neutral_test(
        standardized,
        family="gamma_poisson",
        cv=0.20,
        n_draws=n_permutations,
        seed=seed,
    )
    neutral_binomial = size_conditioned_neutral_test(
        standardized,
        family="binomial",
        decline_only=True,
        n_draws=n_permutations,
        seed=seed,
    )

    leave_one_out: dict[str, object] = {}
    for index, island in enumerate(ISLANDS):
        allowed = tuple(
            x for x in ISLANDS if x != island
        )
        leave_one_out[island] = (
            _run_exchangeable_sensitivity(
                rows,
                followup_zero_years=2,
                allowed_islands=allowed,
                minimum_prior_count=1.0,
                n_permutations=n_permutations,
                seed=seed + 10 + index,
            )
        )

    source_bytes = Path(path).read_bytes()
    strong_exchangeable = bool(
        primary["supported"]
        and all(
            float(v["observed_contrast"]) < 0
            for v in leave_one_out.values()
        )
    )
    neutral_sensitivity_excess = all(
        float(x["observed_minus_null_mean"]) < 0
        for x in (
            neutral,
            neutral_cv10,
            neutral_cv20,
            neutral_binomial,
        )
    )
    return {
        "schema_version": 1,
        "analysis_id": (
            "mina-palmer-colony-extinction-hazard-v1"
        ),
        "contracts": [
            "mina-palmer-colony-extinction-hazard-v1",
            "mina-palmer-colony-extinction-neutral-null-v1",
        ],
        "source": {
            "dataset": "Palmer LTER AdeliePenguinCensus",
            "doi": (
                "10.6073/pasta/"
                "89dd52217ca37e3a72a67f7a9bc3c82e"
            ),
            "sha256": hashlib.sha256(
                source_bytes
            ).hexdigest(),
            "parsed_rows": len(rows),
        },
        "primary_exchangeable_risk_set_test": primary,
        "prior_size_descriptives": {
            "event_median_pairs": float(
                np.median(event_counts)
            ),
            "event_mean_pairs": float(
                np.mean(event_counts)
            ),
            "non_event_median_pairs": float(
                np.median(survivor_counts)
            ),
            "non_event_mean_pairs": float(
                np.mean(survivor_counts)
            ),
            "pooled_rank_quartiles": _quartiles(
                standardized
            ),
        },
        "secondary_discrete_time_logistic": (
            _logistic_fit(standardized)
        ),
        "exchangeable_sensitivities": {
            "two_zero_rule": (
                _run_exchangeable_sensitivity(
                    rows,
                    followup_zero_years=1,
                    allowed_islands=ISLANDS,
                    minimum_prior_count=1.0,
                    n_permutations=n_permutations,
                    seed=seed + 1,
                )
            ),
            "exclude_litchfield": (
                _run_exchangeable_sensitivity(
                    rows,
                    followup_zero_years=2,
                    allowed_islands=tuple(
                        x for x in ISLANDS
                        if x != "LIT"
                    ),
                    minimum_prior_count=1.0,
                    n_permutations=n_permutations,
                    seed=seed + 2,
                )
            ),
            "leave_one_island_out": leave_one_out,
            "prior_count_at_least_2": (
                _run_exchangeable_sensitivity(
                    rows,
                    followup_zero_years=2,
                    allowed_islands=ISLANDS,
                    minimum_prior_count=2.0,
                    n_permutations=n_permutations,
                    seed=seed + 20,
                )
            ),
        },
        "size_conditioned_neutral_gate": {
            "poisson_primary": neutral,
            "gamma_poisson_cv10": neutral_cv10,
            "gamma_poisson_cv20": neutral_cv20,
            "decline_only_binomial": neutral_binomial,
        },
        "decision": {
            "exchangeable_small_group_pattern_supported": bool(
                primary["supported"]
            ),
            "exchangeable_pattern_leave_one_out_stable": (
                strong_exchangeable
            ),
            "supra_proportional_small_group_vulnerability_supported": bool(
                neutral["mechanism_gate_pass"]
            ),
            "excess_vulnerability_direction_stable_across_neutral_sensitivities": (
                neutral_sensitivity_excess
            ),
            "social_facilitation_or_predation_mechanism_supported": False,
        },
        "interpretation": {
            "supported": (
                "Durable colony-code losses are strongly "
                "concentrated among groups that were already "
                "small relative to contemporaneous groups on "
                "the same island."
            ),
            "mechanism_gate": (
                "The size-conditioned proportional demographic "
                "null must be passed before this ordering can be "
                "interpreted as supra-proportional small-group "
                "vulnerability."
            ),
            "boundary": (
                "Colony-code counts do not identify predation, "
                "social facilitation, snow, habitat quality or "
                "mapped patch causality."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--census", required=True, type=Path
    )
    parser.add_argument(
        "--out", required=True, type=Path
    )
    parser.add_argument(
        "--permutations",
        type=int,
        default=N_PERMUTATIONS,
    )
    parser.add_argument(
        "--seed", type=int, default=SEED
    )
    args = parser.parse_args()
    result = analyze(
        args.census,
        n_permutations=args.permutations,
        seed=args.seed,
    )
    args.out.parent.mkdir(
        parents=True, exist_ok=True
    )
    args.out.write_text(
        json.dumps(
            result, indent=2, sort_keys=True
        ) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
