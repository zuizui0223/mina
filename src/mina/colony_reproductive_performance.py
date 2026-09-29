"""Palmer Adelie colony size and reproductive-performance analysis."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from .colony_extinction_hazard import build_transitions, load_rows as load_adult_rows
from .lter import ISLANDS

N_SIMULATIONS = 100_000
SEED = 20260930
MIN_PRIMARY_GROUPS = 15
MIN_PRIMARY_ROWS = 60
MIN_COLONY_SEASONS_FE = 5
MIN_H3_RISKSETS = 5
MIN_H3_EVENTS = 8


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _integer_count(value: str | float | int, name: str) -> int:
    number = float(value)
    rounded = round(number)
    if not math.isclose(number, rounded, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(f"{name} is not integer-valued: {number}")
    return int(rounded)


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

        pairs = _integer_count(row["num_breeding_pairs"], "num_breeding_pairs")
        chicks = _integer_count(row["num_chicks"], "num_chicks")
        if pairs <= 0 or chicks < 0:
            continue
        if chicks > 2 * pairs:
            raise ValueError(
                f"chick count exceeds two-slot biological cap: {island} "
                f"{row.get('colony_code')} pairs={pairs} chicks={chicks}"
            )

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
                "season_start_year": season,
                "island": island,
                "colony_code": code,
                "pairs": pairs,
                "chicks": chicks,
                "chicks_per_pair": chicks / pairs,
                "census_time": str(row.get("census_time", "")).strip(),
            }
        )

    if not out:
        raise ValueError("no usable Palmer chick-production rows")
    return out


def _group_rows(
    rows: list[dict[str, object]],
    *,
    minimum_colonies: int = 3,
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["island"]), int(row["season_start_year"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, season), local in sorted(grouped.items()):
        if len(local) < minimum_colonies:
            continue
        pairs = np.asarray([int(row["pairs"]) for row in local], dtype=int)
        chicks = np.asarray([int(row["chicks"]) for row in local], dtype=int)
        if int(chicks.sum()) <= 0:
            continue
        x = np.log1p(pairs.astype(float))
        sd = float(np.std(x, ddof=1))
        if sd <= 0:
            continue
        z = (x - float(np.mean(x))) / sd
        success = chicks / pairs
        slope = float(np.dot(z, success) / np.dot(z, z))
        out.append(
            {
                "island": island,
                "season_start_year": season,
                "rows": local,
                "pairs": pairs,
                "chicks": chicks,
                "z_log_pairs": z,
                "observed_slope": slope,
            }
        )
    return out


def _simulate_allocations(
    rng: np.random.Generator,
    pairs: np.ndarray,
    total_chicks: int,
    size: int,
) -> np.ndarray:
    capacities = (2 * pairs).astype(np.int64)
    if total_chicks > int(capacities.sum()):
        raise ValueError("total chicks exceed total two-slot capacity")
    return rng.multivariate_hypergeometric(
        capacities,
        int(total_chicks),
        size=size,
    )


def primary_size_productivity(
    rows: list[dict[str, object]],
    *,
    n_simulations: int = N_SIMULATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    groups = _group_rows(rows, minimum_colonies=3)
    n_rows = int(sum(len(group["rows"]) for group in groups))
    if len(groups) < MIN_PRIMARY_GROUPS or n_rows < MIN_PRIMARY_ROWS:
        return {
            "estimable": False,
            "n_groups": len(groups),
            "n_rows": n_rows,
            "reason": "failed_frozen_estimability_gate",
        }

    observed = float(np.mean([float(group["observed_slope"]) for group in groups]))
    rng = np.random.default_rng(seed)
    null = np.zeros(n_simulations, dtype=float)
    for group in groups:
        pairs = np.asarray(group["pairs"], dtype=int)
        z = np.asarray(group["z_log_pairs"], dtype=float)
        draws = _simulate_allocations(
            rng,
            pairs,
            int(np.sum(group["chicks"])),
            n_simulations,
        )
        success = draws / pairs[None, :]
        slopes = (success @ z) / float(np.dot(z, z))
        null += slopes
    null /= len(groups)
    p = (1 + int(np.sum(null >= observed))) / (n_simulations + 1)

    per_island: dict[str, object] = {}
    for island in ISLANDS:
        local = [
            float(group["observed_slope"])
            for group in groups
            if str(group["island"]) == island
        ]
        per_island[island] = {
            "n_groups": len(local),
            "mean_slope": float(np.mean(local)) if local else None,
            "median_slope": float(np.median(local)) if local else None,
        }

    return {
        "estimable": True,
        "n_groups": len(groups),
        "n_rows": n_rows,
        "observed_mean_slope": observed,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q50": float(np.quantile(null, 0.5)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": float(p),
        "supported": bool(observed > 0 and p <= 0.05),
        "per_island": per_island,
        "group_slopes": [
            {
                "island": str(group["island"]),
                "season_start_year": int(group["season_start_year"]),
                "n_colonies": len(group["rows"]),
                "slope": float(group["observed_slope"]),
            }
            for group in groups
        ],
    }


def _two_way_fe_design(rows: list[dict[str, object]]) -> tuple[
    list[dict[str, object]], np.ndarray, np.ndarray, list[tuple[str, int]]
]:
    colony_counts = Counter(
        (str(row["island"]), str(row["colony_code"])) for row in rows
    )
    retained = [
        row
        for row in rows
        if colony_counts[(str(row["island"]), str(row["colony_code"]))]
        >= MIN_COLONY_SEASONS_FE
    ]
    by_group: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in retained:
        by_group[(str(row["island"]), int(row["season_start_year"]))].append(row)
    retained = [
        row
        for key, local in by_group.items()
        if len(local) >= 2
        for row in local
    ]
    if not retained:
        raise ValueError("no rows for two-way fixed-effect analysis")

    colony_levels = sorted(
        {(str(row["island"]), str(row["colony_code"])) for row in retained}
    )
    group_levels = sorted(
        {(str(row["island"]), int(row["season_start_year"])) for row in retained}
    )
    colony_index = {key: idx for idx, key in enumerate(colony_levels)}
    group_index = {key: idx for idx, key in enumerate(group_levels)}

    n = len(retained)
    columns = [np.ones(n, dtype=float)]
    for level in colony_levels[1:]:
        columns.append(
            np.asarray(
                [
                    1.0
                    if (str(row["island"]), str(row["colony_code"])) == level
                    else 0.0
                    for row in retained
                ]
            )
        )
    for level in group_levels[1:]:
        columns.append(
            np.asarray(
                [
                    1.0
                    if (str(row["island"]), int(row["season_start_year"])) == level
                    else 0.0
                    for row in retained
                ]
            )
        )
    fe = np.column_stack(columns)
    x = np.log1p(
        np.asarray([int(row["pairs"]) for row in retained], dtype=float)
    )
    coef, _, _, _ = np.linalg.lstsq(fe, x, rcond=None)
    x_resid = x - fe @ coef
    denom = float(np.dot(x_resid, x_resid))
    if denom <= 1e-12:
        raise ValueError("two-way FE size effect is not estimable")
    return retained, x_resid, fe, group_levels


def two_way_fixed_effect(
    rows: list[dict[str, object]],
    *,
    n_simulations: int = N_SIMULATIONS,
    seed: int = SEED + 1,
) -> dict[str, object]:
    retained, x_resid, _, group_levels = _two_way_fe_design(rows)
    success = np.asarray(
        [float(row["chicks_per_pair"]) for row in retained], dtype=float
    )
    denom = float(np.dot(x_resid, x_resid))
    observed = float(np.dot(x_resid, success) / denom)

    row_indices: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, row in enumerate(retained):
        row_indices[
            (str(row["island"]), int(row["season_start_year"]))
        ].append(idx)

    rng = np.random.default_rng(seed)
    null_numerator = np.zeros(n_simulations, dtype=float)
    for key in group_levels:
        idx = row_indices.get(key, [])
        if len(idx) < 2:
            continue
        pairs = np.asarray([int(retained[i]["pairs"]) for i in idx], dtype=int)
        chicks = np.asarray([int(retained[i]["chicks"]) for i in idx], dtype=int)
        if int(chicks.sum()) <= 0:
            simulated_success = np.zeros((n_simulations, len(idx)), dtype=float)
        else:
            draws = _simulate_allocations(
                rng,
                pairs,
                int(chicks.sum()),
                n_simulations,
            )
            simulated_success = draws / pairs[None, :]
        null_numerator += simulated_success @ x_resid[np.asarray(idx, dtype=int)]

    null = null_numerator / denom
    p = (1 + int(np.sum(null >= observed))) / (n_simulations + 1)
    return {
        "estimable": True,
        "n_rows": len(retained),
        "n_colonies": len(
            {
                (str(row["island"]), str(row["colony_code"]))
                for row in retained
            }
        ),
        "n_island_seasons": len(group_levels),
        "observed_log_size_coefficient": observed,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q50": float(np.quantile(null, 0.5)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": float(p),
        "supported": bool(observed > 0 and p <= 0.05),
    }


def pre_extinction_performance(
    chick_rows: list[dict[str, object]],
    adult_census: str | Path,
    *,
    n_simulations: int = N_SIMULATIONS,
    seed: int = SEED + 2,
) -> dict[str, object]:
    adult_rows = load_adult_rows(adult_census)
    transitions = build_transitions(adult_rows)

    transition_groups: dict[
        tuple[str, int], list[dict[str, object]]
    ] = defaultdict(list)
    for row in transitions:
        transition_groups[
            (str(row["island"]), int(row["start_year"]))
        ].append(row)

    chick_lookup = {
        (
            str(row["island"]),
            str(row["colony_code"]),
            int(row["season_start_year"]),
        ): row
        for row in chick_rows
    }

    groups: list[dict[str, object]] = []
    joined_event_count = 0
    joined_transition_count = 0
    for (island, year), local in sorted(transition_groups.items()):
        joined = []
        for transition in local:
            key = (
                island,
                str(transition["colony_code"]),
                year,
            )
            chick = chick_lookup.get(key)
            if chick is None:
                continue
            joined_transition_count += 1
            joined.append(
                {
                    "event": int(transition["event"]),
                    "pairs": int(chick["pairs"]),
                    "chicks": int(chick["chicks"]),
                    "success": float(chick["chicks_per_pair"]),
                    "colony_code": str(chick["colony_code"]),
                }
            )
        n_event = sum(item["event"] for item in joined)
        joined_event_count += n_event
        if n_event <= 0 or n_event >= len(joined):
            continue
        pairs = np.asarray([item["pairs"] for item in joined], dtype=int)
        chicks = np.asarray([item["chicks"] for item in joined], dtype=int)
        event = np.asarray([item["event"] for item in joined], dtype=int)
        success = chicks / pairs
        contrast = float(
            np.mean(success[event == 1]) - np.mean(success[event == 0])
        )
        groups.append(
            {
                "island": island,
                "start_year": year,
                "joined": joined,
                "pairs": pairs,
                "chicks": chicks,
                "event": event,
                "observed_contrast": contrast,
            }
        )

    informative_events = int(
        sum(int(np.sum(group["event"])) for group in groups)
    )
    if len(groups) < MIN_H3_RISKSETS or informative_events < MIN_H3_EVENTS:
        return {
            "estimable": False,
            "n_informative_risk_sets": len(groups),
            "n_informative_events": informative_events,
            "n_joined_transitions": joined_transition_count,
            "n_joined_events_all": joined_event_count,
            "reason": "failed_frozen_estimability_gate",
        }

    observed = float(
        np.mean([float(group["observed_contrast"]) for group in groups])
    )
    rng = np.random.default_rng(seed)
    null = np.zeros(n_simulations, dtype=float)
    for group in groups:
        pairs = np.asarray(group["pairs"], dtype=int)
        event = np.asarray(group["event"], dtype=int)
        draws = _simulate_allocations(
            rng,
            pairs,
            int(np.sum(group["chicks"])),
            n_simulations,
        )
        success = draws / pairs[None, :]
        event_mean = success[:, event == 1].mean(axis=1)
        survivor_mean = success[:, event == 0].mean(axis=1)
        null += event_mean - survivor_mean
    null /= len(groups)
    p = (1 + int(np.sum(null <= observed))) / (n_simulations + 1)

    return {
        "estimable": True,
        "n_informative_risk_sets": len(groups),
        "n_informative_events": informative_events,
        "n_joined_transitions": joined_transition_count,
        "n_joined_events_all": joined_event_count,
        "observed_event_minus_survivor_success": observed,
        "null_mean": float(np.mean(null)),
        "null_sd": float(np.std(null, ddof=1)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q50": float(np.quantile(null, 0.5)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": float(p),
        "supported": bool(observed < 0 and p <= 0.05),
        "risk_sets": [
            {
                "island": str(group["island"]),
                "start_year": int(group["start_year"]),
                "n_colonies": len(group["joined"]),
                "n_events": int(np.sum(group["event"])),
                "contrast": float(group["observed_contrast"]),
            }
            for group in groups
        ],
    }


def analyze(
    chick_path: str | Path,
    adult_census: str | Path,
    *,
    n_simulations: int = N_SIMULATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    if n_simulations < 999:
        raise ValueError("at least 999 simulations are required")
    rows = load_chick_rows(chick_path)
    h1 = primary_size_productivity(
        rows,
        n_simulations=n_simulations,
        seed=seed,
    )
    h2 = two_way_fixed_effect(
        rows,
        n_simulations=n_simulations,
        seed=seed + 1,
    )
    h3 = pre_extinction_performance(
        rows,
        adult_census,
        n_simulations=n_simulations,
        seed=seed + 2,
    )

    source_bytes = Path(chick_path).read_bytes()
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-colony-reproductive-performance-v1",
        "contract_id": "mina-palmer-colony-reproductive-performance-v1",
        "source": {
            "dataset_id": "AdeliePenguinAdultandChickCounts",
            "doi": "10.6073/pasta/9bf4588c02d6caa12a68133134ed4489",
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "n_usable_rows": len(rows),
            "season_range": [
                min(int(row["season_start_year"]) for row in rows),
                max(int(row["season_start_year"]) for row in rows),
            ],
        },
        "H1_size_productivity": h1,
        "H2_two_way_fixed_effect": h2,
        "H3_pre_extinction_performance": h3,
        "decision": {
            "H1_support": bool(h1.get("supported", False)),
            "strong_density_dependence": bool(
                h1.get("supported", False) and h2.get("supported", False)
            ),
            "pre_extinction_performance_penalty": bool(
                h3.get("supported", False)
            ),
            "allee_like_reproductive_signature": bool(
                h1.get("supported", False) and h2.get("supported", False)
            ),
        },
        "interpretation_boundary": {
            "does_not_uniquely_identify_social_facilitation": True,
            "does_not_uniquely_identify_skua_predation": True,
            "stable_colony_quality_addressed_by_fixed_effects": True,
            "primary_inference_uses_chick_slot_null": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--simulations", type=int, default=N_SIMULATIONS
    )
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = analyze(
        args.chicks,
        args.adult_census,
        n_simulations=args.simulations,
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
