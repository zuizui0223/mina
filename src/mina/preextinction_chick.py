"""Pre-extinction chick-production test for Palmer Adelie colony codes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .colony_extinction_hazard import (
    ISLANDS,
    build_transitions,
    load_rows,
    standardize_risk_sets,
)

N_SIMULATIONS = 100_000
SEED = 20260930
BATCH_SIZE = 2_000


def _finite(value: str | None) -> bool:
    if value in {None, "", "NULL", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_chicks(path: str | Path) -> tuple[dict[tuple[str, str, int], float], dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    grouped: dict[tuple[str, str, int], list[float]] = defaultdict(list)
    usable_rows = 0
    for row in rows:
        island = str(row.get("Island", "")).strip()
        code = str(row.get("Colony", "")).strip()
        date = str(row.get("Date GMT", "")).strip()
        if island not in ISLANDS or not code or not _finite(row.get("Chicks")):
            continue
        chicks = float(row["Chicks"])
        if chicks < 0:
            raise ValueError("negative chick count")
        try:
            season = int(date[:4]) - 1
        except (TypeError, ValueError):
            continue
        grouped[(island, code, season)].append(chicks)
        usable_rows += 1

    cleaned: dict[tuple[str, str, int], float] = {}
    ambiguous: list[dict[str, object]] = []
    identical_duplicates = 0
    for key, values in sorted(grouped.items()):
        unique = sorted(set(values))
        if len(unique) == 1:
            cleaned[key] = float(unique[0])
            if len(values) > 1:
                identical_duplicates += 1
        else:
            ambiguous.append(
                {
                    "island": key[0],
                    "colony_code": key[1],
                    "season": key[2],
                    "values": unique,
                    "n_rows": len(values),
                }
            )
    inventory = {
        "raw_rows": len(rows),
        "usable_nonnegative_chick_rows": usable_rows,
        "unique_cleaned_keys": len(cleaned),
        "identical_duplicate_keys_collapsed": identical_duplicates,
        "ambiguous_duplicate_keys_excluded": len(ambiguous),
        "ambiguous_duplicate_details": ambiguous,
        "season_range": [
            min(key[2] for key in cleaned),
            max(key[2] for key in cleaned),
        ] if cleaned else None,
    }
    if not cleaned:
        raise ValueError("no cleaned chick counts")
    return cleaned, inventory


def build_joined_risk_sets(
    adult_census: str | Path,
    chick_path: str | Path,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    adults = load_rows(adult_census)
    transitions = build_transitions(adults)
    standardized = standardize_risk_sets(transitions)
    chicks, inventory = load_chicks(chick_path)

    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    matched = 0
    matched_events = 0
    for row in standardized:
        key = (
            str(row["island"]),
            str(row["colony_code"]),
            int(row["start_year"]),
        )
        if key not in chicks:
            continue
        enriched = dict(row)
        enriched["chicks"] = float(chicks[key])
        groups[(str(row["island"]), int(row["start_year"]))].append(enriched)
        matched += 1
        matched_events += int(row["event"])

    risk_sets: list[dict[str, object]] = []
    for (island, season), local in sorted(groups.items()):
        events = np.asarray([int(row["event"]) for row in local], dtype=int)
        if len(local) < 2 or int(events.sum()) <= 0 or int(events.sum()) >= len(local):
            continue
        prior = np.asarray([float(row["prior_count"]) for row in local], dtype=float)
        chicks_obs = np.asarray([float(row["chicks"]) for row in local], dtype=float)
        total_prior = float(prior.sum())
        if total_prior <= 0:
            raise ValueError("non-positive joined prior total")
        total_chicks = int(round(float(chicks_obs.sum())))
        if not np.allclose(chicks_obs, np.round(chicks_obs)):
            raise ValueError("non-integer chick count in snapshot")
        probs = prior / total_prior
        expected = total_chicks * probs
        residual = (chicks_obs - expected) / np.sqrt(np.maximum(expected, 1e-12))
        observed_contrast = float(
            np.mean(residual[events == 1]) - np.mean(residual[events == 0])
        )
        risk_sets.append(
            {
                "island": island,
                "season": season,
                "rows": local,
                "event": events,
                "prior": prior,
                "chicks": chicks_obs,
                "total_chicks": total_chicks,
                "probs": probs,
                "expected": expected,
                "pearson_residual": residual,
                "observed_contrast": observed_contrast,
            }
        )

    join_info = {
        **inventory,
        "adult_standardized_transition_rows": len(standardized),
        "matched_colony_season_rows": matched,
        "matched_durable_events": matched_events,
        "informative_risk_sets": len(risk_sets),
        "informative_matched_events": int(
            sum(int(np.sum(risk["event"])) for risk in risk_sets)
        ),
    }
    return risk_sets, join_info


def _deviance_residual(obs: np.ndarray, expected: np.ndarray) -> np.ndarray:
    out = np.empty_like(expected, dtype=float)
    positive = obs > 0
    term = np.empty_like(expected, dtype=float)
    term[positive] = (
        obs[positive] * np.log(obs[positive] / np.maximum(expected[positive], 1e-12))
        - (obs[positive] - expected[positive])
    )
    term[~positive] = expected[~positive]
    out[:] = np.sign(obs - expected) * np.sqrt(np.maximum(2.0 * term, 0.0))
    return out


def _observed_summary(risk_sets: list[dict[str, object]]) -> dict[str, object]:
    if not risk_sets:
        raise ValueError("no informative chick-performance risk sets")
    contrasts = [float(risk["observed_contrast"]) for risk in risk_sets]
    event_residuals: list[float] = []
    non_event_residuals: list[float] = []
    event_chicks: list[float] = []
    non_event_chicks: list[float] = []
    deviance_contrasts: list[float] = []
    per_set: list[dict[str, object]] = []
    for risk in risk_sets:
        e = np.asarray(risk["event"], dtype=int)
        r = np.asarray(risk["pearson_residual"], dtype=float)
        y = np.asarray(risk["chicks"], dtype=float)
        mu = np.asarray(risk["expected"], dtype=float)
        dr = _deviance_residual(y, mu)
        event_residuals.extend(r[e == 1].tolist())
        non_event_residuals.extend(r[e == 0].tolist())
        event_chicks.extend(y[e == 1].tolist())
        non_event_chicks.extend(y[e == 0].tolist())
        dev = float(np.mean(dr[e == 1]) - np.mean(dr[e == 0]))
        deviance_contrasts.append(dev)
        per_set.append(
            {
                "island": risk["island"],
                "season": int(risk["season"]),
                "n_joined": len(e),
                "n_events": int(e.sum()),
                "total_chicks": int(risk["total_chicks"]),
                "pearson_contrast": float(risk["observed_contrast"]),
                "deviance_contrast": dev,
            }
        )
    return {
        "cross_risk_set_pearson_contrast": float(np.mean(contrasts)),
        "event_mean_pearson_residual": float(np.mean(event_residuals)),
        "event_median_pearson_residual": float(np.median(event_residuals)),
        "non_event_mean_pearson_residual": float(np.mean(non_event_residuals)),
        "non_event_median_pearson_residual": float(np.median(non_event_residuals)),
        "event_mean_chicks": float(np.mean(event_chicks)),
        "event_median_chicks": float(np.median(event_chicks)),
        "non_event_mean_chicks": float(np.mean(non_event_chicks)),
        "non_event_median_chicks": float(np.median(non_event_chicks)),
        "cross_risk_set_deviance_contrast": float(np.mean(deviance_contrasts)),
        "risk_sets": per_set,
    }


def simulate_null(
    risk_sets: list[dict[str, object]],
    *,
    simulations: int = N_SIMULATIONS,
    seed: int = SEED,
    batch_size: int = BATCH_SIZE,
) -> dict[str, object]:
    if len(risk_sets) < 1:
        raise ValueError("no risk sets for chick-performance null")
    observed = float(
        np.mean([float(risk["observed_contrast"]) for risk in risk_sets])
    )
    rng = np.random.default_rng(seed)
    draws: list[np.ndarray] = []
    completed = 0
    while completed < simulations:
        b = min(batch_size, simulations - completed)
        statistic = np.zeros(b, dtype=float)
        for risk in risk_sets:
            total = int(risk["total_chicks"])
            probs = np.asarray(risk["probs"], dtype=float)
            expected = np.asarray(risk["expected"], dtype=float)
            event = np.asarray(risk["event"], dtype=int)
            simulated = rng.multinomial(total, probs, size=b).astype(float)
            residual = (
                simulated - expected[None, :]
            ) / np.sqrt(np.maximum(expected[None, :], 1e-12))
            statistic += (
                np.mean(residual[:, event == 1], axis=1)
                - np.mean(residual[:, event == 0], axis=1)
            )
        statistic /= len(risk_sets)
        draws.append(statistic)
        completed += b
    null = np.concatenate(draws)
    p = (1 + int(np.sum(null <= observed))) / (simulations + 1)
    return {
        "n_risk_sets": len(risk_sets),
        "observed_contrast": observed,
        "simulations": simulations,
        "seed": seed,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q50": float(np.quantile(null, 0.5)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": float(p),
        "supported": bool(observed < 0 and p <= 0.05),
    }


def analyze(
    adult_census: str | Path,
    chick_path: str | Path,
    *,
    simulations: int = N_SIMULATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    risk_sets, join_info = build_joined_risk_sets(adult_census, chick_path)
    if len(risk_sets) < 5:
        raise ValueError(
            f"only {len(risk_sets)} informative risk sets; contract requires >=5"
        )
    observed = _observed_summary(risk_sets)
    primary = simulate_null(
        risk_sets,
        simulations=simulations,
        seed=seed,
    )

    high_chick_sets = [
        risk for risk in risk_sets if int(risk["total_chicks"]) >= 10
    ]
    high_chick = (
        simulate_null(
            high_chick_sets,
            simulations=simulations,
            seed=seed + 1,
        )
        if high_chick_sets
        else None
    )

    loo: dict[str, object] = {}
    negative_loo = 0
    estimable_loo = 0
    for index, island in enumerate(ISLANDS):
        local = [risk for risk in risk_sets if risk["island"] != island]
        if len(local) < 3:
            loo[island] = {"estimable": False, "n_risk_sets": len(local)}
            continue
        result = simulate_null(
            local,
            simulations=simulations,
            seed=seed + 10 + index,
        )
        result["estimable"] = True
        loo[island] = result
        estimable_loo += 1
        negative_loo += int(float(result["observed_contrast"]) < 0)

    source_hash = hashlib.sha256(Path(chick_path).read_bytes()).hexdigest()
    strong = bool(
        primary["supported"]
        and estimable_loo >= 4
        and negative_loo >= 4
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-preextinction-chick-performance-v1",
        "contract_id": "mina-palmer-preextinction-chick-performance-v1",
        "source": {
            "chick_snapshot_sha256": source_hash,
            "adult_census_sha256": hashlib.sha256(
                Path(adult_census).read_bytes()
            ).hexdigest(),
        },
        "join_inventory": join_info,
        "observed": observed,
        "primary_multinomial_null": primary,
        "sensitivities": {
            "exclude_total_chicks_lt_10": high_chick,
            "leave_one_island_out": loo,
            "deviance_residual_observed_contrast": observed[
                "cross_risk_set_deviance_contrast"
            ],
        },
        "decision": {
            "preextinction_reproductive_penalty_supported": bool(
                primary["supported"]
            ),
            "strong_leave_one_island_out_support": strong,
        },
        "interpretation_boundary": {
            "not_a_next_year_recruitment_causal_claim": True,
            "not_an_allee_effect_test": True,
            "not_specific_to_snow_predation_food_or_disturbance": True,
            "size_conditioned_within_island_season": True,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--adult-census", required=True, type=Path)
    p.add_argument("--chicks", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--simulations", type=int, default=N_SIMULATIONS)
    p.add_argument("--seed", type=int, default=SEED)
    a = p.parse_args()
    result = analyze(
        a.adult_census,
        a.chicks,
        simulations=a.simulations,
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
