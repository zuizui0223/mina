"""Prospective matched-risk-set analysis of Palmer Adélie colony disappearance."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .lter import ISLANDS, load_colony_rows

N_PERMUTATIONS = 100_000
SEED = 20260929


def colony_series(path: str | Path) -> dict[tuple[str, str], dict[int, float]]:
    rows = load_colony_rows(path)
    out: dict[tuple[str, str], dict[int, float]] = defaultdict(dict)
    for row in rows:
        key = (str(row["island"]), str(row["colony_code"]))
        year = int(row["year"])
        if year in out[key]:
            raise ValueError(f"duplicate colony-year: {key!r} {year}")
        out[key][year] = float(row["breeding_pairs"])
    return dict(out)


def durable_extinctions(
    series: dict[tuple[str, str], dict[int, float]],
    *,
    min_later_censuses: int = 2,
) -> dict[tuple[str, str], int]:
    """First zero after presence that never reappears and has required follow-up."""
    events: dict[tuple[str, str], int] = {}
    for key, values in series.items():
        years = sorted(values)
        positive = [y for y in years if values[y] > 0]
        if not positive:
            continue
        first_positive = min(positive)
        for year in years:
            if year <= first_positive or values[year] != 0:
                continue
            later = [y for y in years if y > year]
            if (
                len(later) >= min_later_censuses
                and all(values[y] == 0 for y in later)
            ):
                events[key] = year
                break
    return events


def build_risk_rows(
    series: dict[tuple[str, str], dict[int, float]],
    events: dict[tuple[str, str], int],
    *,
    islands: tuple[str, ...] = ISLANDS,
    min_prior_count: float = 0.0,
) -> list[dict[str, object]]:
    """Build adjacent-year risk sets and standardize prior size within each set."""
    by_island_year: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    for (island, code), values in series.items():
        if island not in islands:
            continue
        for year, count in values.items():
            by_island_year[(island, year)][code] = count

    rows: list[dict[str, object]] = []
    years_by_island = {
        island: sorted(y for i, y in by_island_year if i == island)
        for island in islands
    }
    for island in islands:
        years = years_by_island[island]
        year_set = set(years)
        for end_year in years:
            start_year = end_year - 1
            if start_year not in year_set:
                continue
            previous = by_island_year[(island, start_year)]
            current = by_island_year[(island, end_year)]
            codes = [
                code
                for code, count in previous.items()
                if count > 0
                and count >= min_prior_count
                and code in current
            ]
            if len(codes) < 2:
                continue
            log_size = np.asarray(
                [math.log1p(previous[code]) for code in codes], dtype=float
            )
            sd = float(np.std(log_size, ddof=1))
            if not math.isfinite(sd) or sd <= 0:
                continue
            z = (log_size - float(np.mean(log_size))) / sd
            island_total = float(sum(previous.values()))
            for code, z_value in zip(codes, z):
                rows.append(
                    {
                        "island": island,
                        "start_year": start_year,
                        "end_year": end_year,
                        "colony_code": code,
                        "prior_count": float(previous[code]),
                        "prior_island_share": (
                            float(previous[code]) / island_total
                            if island_total > 0
                            else None
                        ),
                        "size_z": float(z_value),
                        "event": int(events.get((island, code)) == end_year),
                    }
                )
    return rows


def event_bearing_risk_sets(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["island"]), int(row["end_year"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, year), local in sorted(grouped.items()):
        n_event = sum(int(row["event"]) for row in local)
        if n_event <= 0 or n_event >= len(local):
            continue
        event_z = np.asarray(
            [float(row["size_z"]) for row in local if int(row["event"]) == 1]
        )
        survivor_z = np.asarray(
            [float(row["size_z"]) for row in local if int(row["event"]) == 0]
        )
        event_count = np.asarray(
            [float(row["prior_count"]) for row in local if int(row["event"]) == 1]
        )
        survivor_count = np.asarray(
            [float(row["prior_count"]) for row in local if int(row["event"]) == 0]
        )
        out.append(
            {
                "island": island,
                "end_year": year,
                "n_at_risk": len(local),
                "n_events": n_event,
                "contrast": float(np.mean(event_z) - np.mean(survivor_z)),
                "event_prior_mean": float(np.mean(event_count)),
                "survivor_prior_mean": float(np.mean(survivor_count)),
                "mean_size_ratio": float(
                    np.mean(event_count) / np.mean(survivor_count)
                ),
                "z": [float(row["size_z"]) for row in local],
            }
        )
    return out


def primary_statistic(risk_sets: list[dict[str, object]]) -> float:
    if not risk_sets:
        raise ValueError("no event-bearing risk sets")
    return float(np.mean([float(group["contrast"]) for group in risk_sets]))


def permutation_test(
    risk_sets: list[dict[str, object]],
    *,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_permutations < 99:
        raise ValueError("at least 99 permutations are required")
    observed = primary_statistic(risk_sets)
    rng = np.random.default_rng(seed)
    null = np.zeros(n_permutations, dtype=float)
    for group in risk_sets:
        z = np.asarray(group["z"], dtype=float)
        n = z.size
        k = int(group["n_events"])
        random_scores = rng.random((n_permutations, n))
        selected = np.argpartition(random_scores, k - 1, axis=1)[:, :k]
        selected_sum = z[selected].sum(axis=1)
        # z is centered within each risk set. This equals
        # mean(z_event) - mean(z_non_event).
        null += selected_sum * n / (k * (n - k))
    null /= len(risk_sets)
    p = (1 + int(np.sum(null <= observed))) / (n_permutations + 1)
    return {
        "observed_contrast": observed,
        "n_permutations": n_permutations,
        "seed": seed,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": float(p),
    }


def _logistic_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    """IRLS logistic effect-size model: event ~ size_z + year + island."""
    island_levels = [island for island in ISLANDS if any(r["island"] == island for r in rows)]
    baseline = island_levels[0]
    years = np.asarray([float(r["end_year"]) for r in rows], dtype=float)
    year_center = float(np.mean(years))
    columns = ["intercept", "size_z", "year_centered"] + [
        f"island_{island}" for island in island_levels[1:]
    ]
    x_rows = []
    for row in rows:
        island = str(row["island"])
        x_rows.append(
            [1.0, float(row["size_z"]), float(row["end_year"]) - year_center]
            + [1.0 if island == level else 0.0 for level in island_levels[1:]]
        )
    x = np.asarray(x_rows, dtype=float)
    y = np.asarray([float(r["event"]) for r in rows], dtype=float)
    beta = np.zeros(x.shape[1], dtype=float)
    for _ in range(100):
        eta = np.clip(x @ beta, -30.0, 30.0)
        p = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(p * (1.0 - p), 1e-9, None)
        working = eta + (y - p) / w
        xw = x * np.sqrt(w)[:, None]
        zw = working * np.sqrt(w)
        new_beta, _, rank, _ = np.linalg.lstsq(xw, zw, rcond=None)
        if rank != x.shape[1]:
            raise ValueError("rank-deficient logistic design")
        if float(np.max(np.abs(new_beta - beta))) < 1e-10:
            beta = new_beta
            break
        beta = new_beta
    eta = np.clip(x @ beta, -30.0, 30.0)
    p = 1.0 / (1.0 + np.exp(-eta))
    w = np.clip(p * (1.0 - p), 1e-9, None)
    info = x.T @ (w[:, None] * x)
    covariance = np.linalg.inv(info)
    se = np.sqrt(np.diag(covariance))
    idx = columns.index("size_z")
    return {
        "columns": columns,
        "coefficients": {name: float(beta[i]) for i, name in enumerate(columns)},
        "standard_errors": {name: float(se[i]) for i, name in enumerate(columns)},
        "baseline_island": baseline,
        "year_center": year_center,
        "size_z_coefficient": float(beta[idx]),
        "size_z_se": float(se[idx]),
        "odds_ratio_per_1sd_larger_prior_size": float(math.exp(beta[idx])),
    }


def _descriptives(
    rows: list[dict[str, object]],
    risk_sets: list[dict[str, object]],
) -> dict[str, object]:
    event = np.asarray(
        [float(r["prior_count"]) for r in rows if int(r["event"]) == 1], dtype=float
    )
    non_event = np.asarray(
        [float(r["prior_count"]) for r in rows if int(r["event"]) == 0], dtype=float
    )
    ratios = np.asarray([float(g["mean_size_ratio"]) for g in risk_sets], dtype=float)

    counts = np.asarray([float(r["prior_count"]) for r in rows], dtype=float)
    edges = np.quantile(counts, [0.0, 0.25, 0.5, 0.75, 1.0])
    quartiles: list[dict[str, object]] = []
    for q in range(4):
        lower, upper = float(edges[q]), float(edges[q + 1])
        selected = []
        for row in rows:
            value = float(row["prior_count"])
            in_bin = value >= lower and (value <= upper if q == 3 else value < upper)
            if in_bin:
                selected.append(row)
        quartiles.append(
            {
                "quartile": q + 1,
                "lower": lower,
                "upper": upper,
                "n": len(selected),
                "events": int(sum(int(r["event"]) for r in selected)),
                "event_rate": (
                    float(np.mean([int(r["event"]) for r in selected]))
                    if selected
                    else None
                ),
            }
        )
    return {
        "event_prior_count": {
            "n": int(event.size),
            "median": float(np.median(event)),
            "mean": float(np.mean(event)),
        },
        "all_non_event_prior_count": {
            "n": int(non_event.size),
            "median": float(np.median(non_event)),
            "mean": float(np.mean(non_event)),
        },
        "matched_risk_set_mean_size_ratio": {
            "median": float(np.median(ratios)),
            "mean": float(np.mean(ratios)),
            "q25": float(np.quantile(ratios, 0.25)),
            "q75": float(np.quantile(ratios, 0.75)),
        },
        "prior_size_quartiles": quartiles,
    }


def _one_analysis(
    series: dict[tuple[str, str], dict[int, float]],
    *,
    min_later_censuses: int,
    islands: tuple[str, ...],
    min_prior_count: float,
    n_permutations: int,
    seed: int,
) -> dict[str, object]:
    events = durable_extinctions(series, min_later_censuses=min_later_censuses)
    rows = build_risk_rows(
        series,
        events,
        islands=islands,
        min_prior_count=min_prior_count,
    )
    risk_sets = event_bearing_risk_sets(rows)
    test = permutation_test(
        risk_sets,
        n_permutations=n_permutations,
        seed=seed,
    )
    return {
        "n_risk_rows": len(rows),
        "n_events_in_risk_rows": int(sum(int(r["event"]) for r in rows)),
        "n_event_bearing_risk_sets": len(risk_sets),
        "n_events_in_primary_risk_sets": int(
            sum(int(g["n_events"]) for g in risk_sets)
        ),
        "test": test,
        "descriptives": _descriptives(rows, risk_sets),
        "risk_set_summaries": [
            {k: v for k, v in group.items() if k != "z"} for group in risk_sets
        ],
        "logistic_effect_size": _logistic_summary(rows),
    }


def analyze(
    census_path: str | Path,
    *,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    series = colony_series(census_path)
    primary = _one_analysis(
        series,
        min_later_censuses=2,
        islands=ISLANDS,
        min_prior_count=0.0,
        n_permutations=n_permutations,
        seed=seed,
    )
    two_zero = _one_analysis(
        series,
        min_later_censuses=1,
        islands=ISLANDS,
        min_prior_count=0.0,
        n_permutations=n_permutations,
        seed=seed + 1,
    )
    no_litchfield = _one_analysis(
        series,
        min_later_censuses=2,
        islands=tuple(i for i in ISLANDS if i != "LIT"),
        min_prior_count=0.0,
        n_permutations=n_permutations,
        seed=seed + 2,
    )
    threshold2 = _one_analysis(
        series,
        min_later_censuses=2,
        islands=ISLANDS,
        min_prior_count=2.0,
        n_permutations=n_permutations,
        seed=seed + 3,
    )
    loo: dict[str, object] = {}
    for index, excluded in enumerate(ISLANDS):
        loo[excluded] = _one_analysis(
            series,
            min_later_censuses=2,
            islands=tuple(i for i in ISLANDS if i != excluded),
            min_prior_count=0.0,
            n_permutations=n_permutations,
            seed=seed + 10 + index,
        )

    p = float(primary["test"]["one_sided_lower_p"])
    contrast = float(primary["test"]["observed_contrast"])
    loo_negative = sum(
        float(value["test"]["observed_contrast"]) < 0 for value in loo.values()
    )
    stronger = bool(
        contrast < 0
        and p <= 0.05
        and loo_negative >= 4
        and float(two_zero["test"]["observed_contrast"]) < 0
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-colony-extinction-hazard-v1",
        "contract_id": "mina-palmer-colony-extinction-hazard-v1",
        "primary": primary,
        "sensitivities": {
            "two_zero_rule": two_zero,
            "exclude_litchfield": no_litchfield,
            "prior_count_at_least_2": threshold2,
            "leave_one_island_out": loo,
        },
        "decision": {
            "small_group_vulnerability_supported": bool(
                contrast < 0 and p <= 0.05
            ),
            "stronger_mechanistic_pattern": stronger,
            "negative_leave_one_island_out": loo_negative,
        },
        "interpretation_boundary": {
            "size_selective_disappearance_not_causal_mechanism": True,
            "does_not_identify_predation_or_social_facilitation": True,
            "colony_code_not_assumed_physical_polygon": True,
            "same_census_previously_analyzed_so_not_fully_outcome_blind": True,
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
