"""Durable colony-extinction hazard and neutral-thinning benchmarks."""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows

N_PERMUTATIONS = 100_000
PRIMARY_SEED = 20260929
WEIGHTED_SEED = 20260933


def _trajectories(path: str | Path) -> dict[tuple[str, str], dict[int, float]]:
    traj: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    for row in load_colony_rows(path):
        key = (str(row["island"]), str(row["colony_code"]))
        year = int(row["year"])
        if year in traj[key]:
            raise ValueError(f"duplicate island-colony-year: {key + (year,)!r}")
        traj[key][year] = float(row["breeding_pairs"])
    return traj


def _status(
    traj: dict[tuple[str, str], dict[int, float]],
    island: str,
    code: str,
    year: int,
    rule: str,
) -> int | None:
    m = traj[(island, code)]
    if year - 1 not in m or year not in m or m[year - 1] <= 0:
        return None
    if m[year] > 0:
        return 0
    if any(yy > year and count > 0 for yy, count in m.items()):
        return 0

    if rule == "primary":
        confirmed = (
            year + 1 in m
            and year + 2 in m
            and m[year + 1] == 0
            and m[year + 2] == 0
        )
    elif rule == "two_zero":
        confirmed = year + 1 in m and m[year + 1] == 0
    else:
        raise ValueError(f"unknown durable-extinction rule: {rule}")

    if confirmed and all(count == 0 for yy, count in m.items() if yy >= year):
        return 1
    return None


def risk_sets(
    path: str | Path,
    *,
    rule: str = "primary",
    islands: tuple[str, ...] = ISLANDS,
    prior_min: float = 0.0,
) -> dict[tuple[str, int], list[dict[str, object]]]:
    traj = _trajectories(path)
    out: dict[tuple[str, int], list[dict[str, object]]] = {}
    for island in islands:
        codes = sorted(code for i, code in traj if i == island)
        years = sorted({year for (i, _), m in traj.items() if i == island for year in m})
        for year in years:
            if year - 1 not in years:
                continue
            local: list[dict[str, object]] = []
            for code in codes:
                m = traj[(island, code)]
                if year - 1 not in m or year not in m or m[year - 1] <= prior_min:
                    continue
                status = _status(traj, island, code, year, rule)
                if status is None:
                    continue
                local.append(
                    {
                        "island": island,
                        "year": year,
                        "colony_code": code,
                        "prior_count": float(m[year - 1]),
                        "current_count": float(m[year]),
                        "event": bool(status),
                    }
                )
            if len(local) >= 2:
                out[(island, year)] = local
    return out


def _event_set_summaries(
    sets: dict[tuple[str, int], list[dict[str, object]]]
) -> tuple[list[dict[str, object]], float]:
    summaries: list[dict[str, object]] = []
    for (island, year), local in sorted(sets.items()):
        event = np.asarray([bool(row["event"]) for row in local], dtype=bool)
        if int(event.sum()) == 0 or int(event.sum()) == len(local):
            continue
        log_size = np.log1p(
            np.asarray([float(row["prior_count"]) for row in local], dtype=float)
        )
        sd = float(np.std(log_size, ddof=1))
        if sd <= 0:
            continue
        z = (log_size - float(np.mean(log_size))) / sd
        event_prior = np.asarray(
            [float(row["prior_count"]) for row in local if bool(row["event"])],
            dtype=float,
        )
        other_prior = np.asarray(
            [float(row["prior_count"]) for row in local if not bool(row["event"])],
            dtype=float,
        )
        summaries.append(
            {
                "island": island,
                "year": year,
                "n_at_risk": len(local),
                "n_events": int(event.sum()),
                "contrast": float(np.mean(z[event]) - np.mean(z[~event])),
                "event_mean_z": float(np.mean(z[event])),
                "non_event_mean_z": float(np.mean(z[~event])),
                "event_prior_mean": float(np.mean(event_prior)),
                "non_event_prior_mean": float(np.mean(other_prior)),
                "raw_mean_ratio": float(np.mean(event_prior) / np.mean(other_prior)),
            }
        )
    if not summaries:
        raise ValueError("no event-bearing risk sets")
    observed = float(np.mean([float(row["contrast"]) for row in summaries]))
    return summaries, observed


def exchangeability_test(
    sets: dict[tuple[str, int], list[dict[str, object]]],
    *,
    permutations: int = N_PERMUTATIONS,
    seed: int = PRIMARY_SEED,
) -> dict[str, object]:
    summaries, observed = _event_set_summaries(sets)
    rng = np.random.default_rng(seed)
    null = np.zeros(permutations, dtype=float)
    used = 0
    for _, local in sorted(sets.items()):
        event = np.asarray([bool(row["event"]) for row in local], dtype=bool)
        m = int(event.sum())
        n = len(local)
        if m == 0 or m == n:
            continue
        z = np.log1p(
            np.asarray([float(row["prior_count"]) for row in local], dtype=float)
        )
        z = (z - float(np.mean(z))) / float(np.std(z, ddof=1))
        uniforms = rng.random((permutations, n))
        chosen = np.argpartition(uniforms, m - 1, axis=1)[:, :m]
        event_sum = z[chosen].sum(axis=1)
        null += event_sum / m - (float(np.sum(z)) - event_sum) / (n - m)
        used += 1
    null /= used
    return {
        "observed_contrast": observed,
        "n_event_risk_sets": len(summaries),
        "n_events": int(sum(int(row["n_events"]) for row in summaries)),
        "permutations": permutations,
        "seed": seed,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": float((1 + int(np.sum(null <= observed))) / (permutations + 1)),
        "risk_set_summaries": summaries,
    }


def _log_zero_odds(lam: float) -> float:
    # q = exp(-lam); return log(q / (1-q)) stably.
    if lam <= 0:
        return 1e300
    if lam > 50:
        return -lam
    q = math.exp(-lam)
    return -lam - math.log1p(-q)


def neutral_thinning_test(
    sets: dict[tuple[str, int], list[dict[str, object]]],
    *,
    permutations: int = N_PERMUTATIONS,
    seed: int = WEIGHTED_SEED,
) -> dict[str, object]:
    summaries, observed = _event_set_summaries(sets)
    rng = np.random.default_rng(seed)
    null = np.zeros(permutations, dtype=float)
    used = 0
    diagnostic: list[dict[str, object]] = []

    for (island, year), local in sorted(sets.items()):
        event = np.asarray([bool(row["event"]) for row in local], dtype=bool)
        m = int(event.sum())
        n = len(local)
        if m == 0 or m == n:
            continue

        prior = np.asarray([float(row["prior_count"]) for row in local], dtype=float)
        current = np.asarray([float(row["current_count"]) for row in local], dtype=float)
        log_size = np.log1p(prior)
        z = (log_size - float(np.mean(log_size))) / float(np.std(log_size, ddof=1))

        multiplier = float(np.sum(current) / np.sum(prior))
        log_odds = np.asarray(
            [_log_zero_odds(multiplier * value) for value in prior], dtype=float
        )
        subsets = np.asarray(list(itertools.combinations(range(n), m)), dtype=int)
        log_weights = np.asarray(
            [float(np.sum(log_odds[list(subset)])) for subset in subsets],
            dtype=float,
        )
        log_weights -= float(np.max(log_weights))
        weights = np.exp(log_weights)
        weights /= float(np.sum(weights))
        selected = subsets[
            rng.choice(len(subsets), size=permutations, replace=True, p=weights)
        ]
        event_sum = z[selected].sum(axis=1)
        part = event_sum / m - (float(np.sum(z)) - event_sum) / (n - m)
        null += part
        used += 1

        diagnostic.append(
            {
                "island": island,
                "year": year,
                "n_at_risk": n,
                "n_events": m,
                "shared_growth_multiplier": multiplier,
                "observed_contrast": float(np.mean(z[event]) - np.mean(z[~event])),
                "weighted_null_mean_contrast": float(np.mean(part)),
            }
        )

    null /= used
    return {
        "observed_contrast": observed,
        "n_event_risk_sets": len(summaries),
        "n_events": int(sum(int(row["n_events"]) for row in summaries)),
        "permutations": permutations,
        "seed": seed,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": float((1 + int(np.sum(null <= observed))) / (permutations + 1)),
        "risk_set_diagnostic": diagnostic,
    }


def logistic_effect(
    sets: dict[tuple[str, int], list[dict[str, object]]]
) -> dict[str, object]:
    response: list[float] = []
    z_size: list[float] = []
    years: list[float] = []
    islands: list[str] = []
    for (island, year), local in sorted(sets.items()):
        values = np.log1p(
            np.asarray([float(row["prior_count"]) for row in local], dtype=float)
        )
        sd = float(np.std(values, ddof=1))
        if sd <= 0:
            continue
        z = (values - float(np.mean(values))) / sd
        for row, zz in zip(local, z):
            response.append(float(bool(row["event"])))
            z_size.append(float(zz))
            years.append(float(year))
            islands.append(island)

    y = np.asarray(response, dtype=float)
    centered_year = np.asarray(years, dtype=float) - float(np.mean(years))
    columns = [
        np.ones(len(y), dtype=float),
        np.asarray(z_size, dtype=float),
        centered_year,
    ]
    for island in ISLANDS[1:]:
        columns.append(
            np.asarray([1.0 if value == island else 0.0 for value in islands])
        )
    x = np.column_stack(columns)
    beta = np.zeros(x.shape[1], dtype=float)
    converged = False
    for iteration in range(100):
        eta = np.clip(x @ beta, -30.0, 30.0)
        p = 1.0 / (1.0 + np.exp(-eta))
        w = p * (1.0 - p)
        information = x.T @ (w[:, None] * x)
        score = x.T @ (y - p)
        step = np.linalg.solve(information, score)
        beta = beta + step
        if float(np.max(np.abs(step))) < 1e-10:
            converged = True
            break
    eta = np.clip(x @ beta, -30.0, 30.0)
    p = 1.0 / (1.0 + np.exp(-eta))
    w = p * (1.0 - p)
    cov = np.linalg.inv(x.T @ (w[:, None] * x))
    se = np.sqrt(np.diag(cov))
    lo = float(beta[1] - 1.96 * se[1])
    hi = float(beta[1] + 1.96 * se[1])
    return {
        "n_rows": len(y),
        "n_events": int(np.sum(y)),
        "converged": converged,
        "iterations": iteration + 1,
        "size_coefficient": float(beta[1]),
        "size_se": float(se[1]),
        "size_odds_ratio_per_within_riskset_sd": float(math.exp(beta[1])),
        "size_or_95ci": [float(math.exp(lo)), float(math.exp(hi))],
        "model": "event ~ within-risk-set z(log1p prior size) + island indicators + centered year",
    }


def descriptive_outputs(
    sets: dict[tuple[str, int], list[dict[str, object]]]
) -> dict[str, object]:
    summaries, _ = _event_set_summaries(sets)
    event_values: list[float] = []
    other_values: list[float] = []
    transitions: list[tuple[float, int]] = []
    for _, local in sorted(sets.items()):
        for row in local:
            prior = float(row["prior_count"])
            event = int(bool(row["event"]))
            transitions.append((prior, event))
        if any(bool(row["event"]) for row in local) and not all(
            bool(row["event"]) for row in local
        ):
            for row in local:
                target = event_values if bool(row["event"]) else other_values
                target.append(float(row["prior_count"]))

    prior = np.asarray([v for v, _ in transitions], dtype=float)
    event = np.asarray([e for _, e in transitions], dtype=int)
    edges = np.quantile(prior, [0.25, 0.5, 0.75])
    bins = np.digitize(prior, edges, right=True)
    quartiles = []
    for idx in range(4):
        mask = bins == idx
        quartiles.append(
            {
                "quartile": idx + 1,
                "n": int(np.sum(mask)),
                "events": int(np.sum(event[mask])),
                "event_rate": float(np.mean(event[mask])) if np.any(mask) else None,
                "prior_min": float(np.min(prior[mask])) if np.any(mask) else None,
                "prior_max": float(np.max(prior[mask])) if np.any(mask) else None,
            }
        )
    return {
        "event_prior_count_median": float(np.median(event_values)),
        "event_prior_count_mean": float(np.mean(event_values)),
        "non_event_prior_count_median": float(np.median(other_values)),
        "non_event_prior_count_mean": float(np.mean(other_values)),
        "median_event_to_non_event_raw_mean_ratio_by_risk_set": float(
            np.median([float(row["raw_mean_ratio"]) for row in summaries])
        ),
        "pooled_prior_size_quartiles": quartiles,
    }


def analyze(
    path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    primary_sets = risk_sets(path)
    exchange = exchangeability_test(
        primary_sets, permutations=permutations, seed=PRIMARY_SEED
    )
    weighted = neutral_thinning_test(
        primary_sets, permutations=permutations, seed=WEIGHTED_SEED
    )

    sensitivity_specs = {
        "exclude_litchfield": (
            risk_sets(path, islands=tuple(i for i in ISLANDS if i != "LIT")),
            20260934,
        ),
        "prior_count_ge2": (risk_sets(path, prior_min=1.0), 20260935),
        "two_zero_endpoint": (risk_sets(path, rule="two_zero"), 20260936),
    }
    weighted_sensitivities = {
        name: neutral_thinning_test(sets, permutations=permutations, seed=seed)
        for name, (sets, seed) in sensitivity_specs.items()
    }

    loo: dict[str, float] = {}
    for island in ISLANDS:
        local = risk_sets(path, islands=tuple(i for i in ISLANDS if i != island))
        _, contrast = _event_set_summaries(local)
        loo[island] = contrast

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-colony-extinction-hazard-v1",
        "primary_exchangeability": exchange,
        "neutral_thinning": weighted,
        "neutral_thinning_sensitivities": weighted_sensitivities,
        "leave_one_island_out_contrast": loo,
        "secondary_logistic": logistic_effect(primary_sets),
        "descriptive": descriptive_outputs(primary_sets),
        "decision": {
            "small_group_disappearance_under_exchangeability": bool(
                exchange["observed_contrast"] < 0
                and exchange["one_sided_lower_p"] <= 0.05
            ),
            "excess_small_group_extinction_beyond_neutral_thinning": bool(
                weighted["observed_contrast"] < 0
                and weighted["one_sided_lower_p"] <= 0.05
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    args = parser.parse_args()
    result = analyze(args.census, permutations=args.permutations)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
