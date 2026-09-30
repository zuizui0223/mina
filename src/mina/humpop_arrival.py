"""Humble Island colony-level arrival timing test."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np

from .performance_redistribution_lags import (
    _adult_lookup,
    _study_season,
    load_adult_rows,
    load_chick_rows,
    performance_rows,
)

N_PERMUTATIONS = 100_000
SEED = 20260980


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_humpop(
    path: str | Path,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected = ["studyName", "Date", "Island", "Colony", "Adults"]
    if not rows:
        raise ValueError("HUMPOP table contains no data rows")

    parsed: list[tuple[tuple[int, str, str], dict[str, object]]] = []
    key_counts: dict[tuple[int, str, str], int] = defaultdict(int)
    for row in rows:
        if list(row) != expected:
            raise ValueError(f"unexpected HUMPOP columns: {list(row)!r}")
        if str(row["Island"]).strip() != "HUM":
            continue
        if not _finite(row["Adults"]):
            continue
        adults = float(row["Adults"])
        if adults < 0:
            raise ValueError("negative HUMPOP adult count")
        season = _study_season(str(row["studyName"]).strip())
        observed = date.fromisoformat(str(row["Date"]).strip())
        colony = str(row["Colony"]).strip()
        key = (season, colony, observed.isoformat())
        record = {
            "season": season,
            "date": observed,
            "colony": colony,
            "adults": adults,
        }
        parsed.append((key, record))
        key_counts[key] += 1

    duplicate_keys = {key for key, count in key_counts.items() if count > 1}
    out = [record for key, record in parsed if key not in duplicate_keys]
    if not out:
        raise ValueError("no usable HUMPOP rows after duplicate-key exclusion")
    return out, {
        "raw_numeric_humble_rows": len(parsed),
        "duplicate_keys_excluded": len(duplicate_keys),
        "rows_excluded_by_duplicate_rule": sum(
            count for key, count in key_counts.items() if key in duplicate_keys
        ),
        "usable_rows_after_duplicate_rule": len(out),
    }

def arrival_endpoints(
    rows: list[dict[str, object]],
    *,
    threshold: float = 0.5,
    minimum_observations: int = 0,
) -> list[dict[str, object]]:
    if not (0.0 < threshold < 1.0):
        raise ValueError("threshold must be between 0 and 1")
    groups: dict[tuple[int, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(int(row["season"]), str(row["colony"]))].append(row)

    out: list[dict[str, object]] = []
    for (season, colony), local in sorted(groups.items()):
        local = sorted(local, key=lambda r: r["date"])
        if len(local) < max(2, minimum_observations):
            continue
        values = np.asarray([float(r["adults"]) for r in local], dtype=float)
        maximum = float(np.max(values))
        if maximum <= 0:
            continue
        normalized = values / maximum
        crossing: float | None = None
        origin = date(season, 10, 1)
        for idx in range(1, len(local)):
            before = float(normalized[idx - 1])
            after = float(normalized[idx])
            if before < threshold <= after:
                d0 = (local[idx - 1]["date"] - origin).days
                d1 = (local[idx]["date"] - origin).days
                fraction = (threshold - before) / (after - before)
                crossing = float(d0 + fraction * (d1 - d0))
                break
        if crossing is None:
            continue
        out.append(
            {
                "arrival_season": season,
                "colony": colony,
                "threshold": threshold,
                "arrival_day": crossing,
                "n_observations": len(local),
                "season_max_adults": maximum,
                "first_date": local[0]["date"].isoformat(),
                "last_date": local[-1]["date"].isoformat(),
            }
        )
    return out


def matched_panel(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    endpoints: list[dict[str, object]],
    *,
    minimum_prior_size: float = 0.0,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    adult_lookup = _adult_lookup(adults)
    perf_lookup = {
        (str(r["colony"]), int(r["season"])): float(r["state"])
        for r in performance
        if str(r["island"]) == "HUM"
    }
    perf_codes = sorted(
        {str(r["colony"]) for r in performance if str(r["island"]) == "HUM"}
    )
    arrival_codes = sorted({str(r["colony"]) for r in endpoints})
    exact_codes = sorted(set(perf_codes) & set(arrival_codes))

    raw: list[dict[str, object]] = []
    for endpoint in endpoints:
        arrival_season = int(endpoint["arrival_season"])
        predictor_season = arrival_season - 1
        colony = str(endpoint["colony"])
        pkey = (colony, predictor_season)
        akey = ("HUM", colony, predictor_season)
        if pkey not in perf_lookup or akey not in adult_lookup:
            continue
        prior_size = float(adult_lookup[akey])
        if prior_size < minimum_prior_size:
            continue
        raw.append(
            {
                **endpoint,
                "predictor_season": predictor_season,
                "state": float(perf_lookup[pkey]),
                "prior_size": prior_size,
            }
        )

    by_season: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in raw:
        by_season[int(row["predictor_season"])].append(row)

    panel: list[dict[str, object]] = []
    dropped_small_sets: list[int] = []
    for season, local in sorted(by_season.items()):
        if len(local) < 3:
            dropped_small_sets.append(season)
            continue
        size = np.log1p(
            np.asarray([float(r["prior_size"]) for r in local], dtype=float)
        )
        sd = float(np.std(size, ddof=1))
        if sd <= 0:
            z = np.zeros_like(size)
        else:
            z = (size - float(np.mean(size))) / sd
        for row, value in zip(local, z):
            panel.append({**row, "z_prior_size": float(value)})

    diagnostic = {
        "performance_colony_codes": perf_codes,
        "arrival_endpoint_colony_codes": arrival_codes,
        "exact_code_overlap": exact_codes,
        "n_raw_matches": len(raw),
        "n_panel_rows": len(panel),
        "n_predictor_seasons": len(
            {int(r["predictor_season"]) for r in panel}
        ),
        "dropped_predictor_seasons_with_lt3_colonies": dropped_small_sets,
    }
    return panel, diagnostic


def _dummy_matrix(
    rows: list[dict[str, object]],
    field: str,
) -> np.ndarray:
    levels = sorted({str(r[field]) for r in rows})
    lookup = {level: idx for idx, level in enumerate(levels)}
    matrix = np.zeros((len(rows), len(levels)), dtype=float)
    for idx, row in enumerate(rows):
        matrix[idx, lookup[str(row[field])]] = 1.0
    return matrix


def _prepare_model(
    panel: list[dict[str, object]],
    performance: list[dict[str, object]],
) -> dict[str, object]:
    if len(panel) < 100:
        raise ValueError("fewer than 100 matched colony-seasons")
    seasons = {int(r["predictor_season"]) for r in panel}
    if len(seasons) < 10:
        raise ValueError("fewer than 10 matched predictor seasons")

    y = np.asarray([float(r["arrival_day"]) for r in panel], dtype=float)
    state = np.asarray([float(r["state"]) for r in panel], dtype=float)
    zsize = np.asarray([float(r["z_prior_size"]) for r in panel], dtype=float)
    colony_fe = _dummy_matrix(panel, "colony")
    arrival_fe = _dummy_matrix(panel, "arrival_season")
    controls = np.column_stack([zsize, colony_fe, arrival_fe])
    gram_inv = np.linalg.pinv(controls.T @ controls)
    y_resid = y - controls @ (gram_inv @ (controls.T @ y))
    ctx = controls.T @ state
    denominator = float(state @ state - ctx @ (gram_inv @ ctx))
    if denominator <= 0:
        raise ValueError("zero residual performance variance")
    observed = float((state @ y_resid) / denominator)

    perf_groups: dict[int, tuple[list[str], np.ndarray]] = {}
    grouped: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        if str(row["island"]) == "HUM":
            grouped[int(row["season"])].append(row)
    for season, local in grouped.items():
        local = sorted(local, key=lambda r: str(r["colony"]))
        perf_groups[season] = (
            [str(r["colony"]) for r in local],
            np.asarray([float(r["state"]) for r in local], dtype=float),
        )

    group_rows: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    by_panel: dict[int, list[int]] = defaultdict(list)
    for idx, row in enumerate(panel):
        by_panel[int(row["predictor_season"])].append(idx)
    for season, indices in by_panel.items():
        if season not in perf_groups:
            raise ValueError(f"predictor season absent from performance groups: {season}")
        colonies, _ = perf_groups[season]
        positions = {name: idx for idx, name in enumerate(colonies)}
        row_indices = np.asarray(indices, dtype=int)
        source_positions = np.asarray(
            [positions[str(panel[idx]["colony"])] for idx in indices],
            dtype=int,
        )
        group_rows[season] = (row_indices, source_positions)

    return {
        "panel": panel,
        "controls": controls,
        "gram_inv": gram_inv,
        "y_resid": y_resid,
        "observed": observed,
        "perf_groups": perf_groups,
        "group_rows": group_rows,
    }


def permutation_test(
    model: dict[str, object],
    *,
    permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
    batch_size: int = 1000,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    panel = model["panel"]
    controls = np.asarray(model["controls"], dtype=float)
    gram_inv = np.asarray(model["gram_inv"], dtype=float)
    y_resid = np.asarray(model["y_resid"], dtype=float)
    null = np.empty(permutations, dtype=float)

    offset = 0
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        x = np.empty((batch, len(panel)), dtype=float)
        for season in sorted(model["group_rows"]):
            _, values = model["perf_groups"][season]
            order = np.argsort(rng.random((batch, len(values))), axis=1)
            assigned = values[order]
            row_indices, source_positions = model["group_rows"][season]
            x[:, row_indices] = assigned[:, source_positions]
        ctx = x @ controls
        numerator = x @ y_resid
        denominator = np.sum(x * x, axis=1) - np.einsum(
            "bi,ij,bj->b", ctx, gram_inv, ctx, optimize=True
        )
        null[offset : offset + batch] = numerator / denominator
        offset += batch

    observed = float(model["observed"])
    p = float((1 + int(np.sum(null <= observed))) / (permutations + 1))
    return {
        "n_rows": len(panel),
        "n_predictor_seasons": len(
            {int(r["predictor_season"]) for r in panel}
        ),
        "beta": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_lower_p": p,
        "supported": bool(observed < 0 and p <= 0.05),
    }


def observed_beta(
    panel: list[dict[str, object]],
    performance: list[dict[str, object]],
) -> float:
    return float(_prepare_model(panel, performance)["observed"])


def run_endpoint(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    humpop: list[dict[str, object]],
    *,
    threshold: float,
    minimum_observations: int = 0,
    minimum_prior_size: float = 0.0,
    permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    endpoints = arrival_endpoints(
        humpop,
        threshold=threshold,
        minimum_observations=minimum_observations,
    )
    panel, diagnostic = matched_panel(
        adults,
        performance,
        endpoints,
        minimum_prior_size=minimum_prior_size,
    )
    model = _prepare_model(panel, performance)
    test = permutation_test(model, permutations=permutations, seed=seed)
    return {
        "threshold": threshold,
        "n_arrival_endpoints": len(endpoints),
        "matching": diagnostic,
        "test": test,
    }


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    humpop_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)
    performance = performance_rows(
        adults,
        chicks,
        allowed_islands=("HUM",),
    )
    humpop, humpop_audit = load_humpop(humpop_path)

    primary = run_endpoint(
        adults,
        performance,
        humpop,
        threshold=0.5,
        permutations=permutations,
        seed=SEED,
    )
    q25 = run_endpoint(
        adults,
        performance,
        humpop,
        threshold=0.25,
        permutations=permutations,
        seed=SEED + 1,
    )
    q75 = run_endpoint(
        adults,
        performance,
        humpop,
        threshold=0.75,
        permutations=permutations,
        seed=SEED + 2,
    )
    obs4 = run_endpoint(
        adults,
        performance,
        humpop,
        threshold=0.5,
        minimum_observations=4,
        permutations=permutations,
        seed=SEED + 3,
    )
    ge2 = run_endpoint(
        adults,
        performance,
        humpop,
        threshold=0.5,
        minimum_prior_size=2.0,
        permutations=permutations,
        seed=SEED + 4,
    )

    primary_endpoints = arrival_endpoints(humpop, threshold=0.5)
    primary_panel, _ = matched_panel(adults, performance, primary_endpoints)
    loo: dict[str, float | None] = {}
    for colony in sorted({str(r["colony"]) for r in primary_panel}):
        local = [r for r in primary_panel if str(r["colony"]) != colony]
        if (
            len(local) < 100
            or len({int(r["predictor_season"]) for r in local}) < 10
        ):
            loo[colony] = None
        else:
            loo[colony] = observed_beta(local, performance)

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-humpop-arrival-v1",
        "gate_id": "mina-palmer-humpop-arrival-schema-gate-v1",
        "source_counts": {
            "adult_rows": len(adults),
            "usable_chick_rows": len(chicks),
            "humble_performance_rows": len(performance),
            "humpop_rows": len(humpop),
            "humpop_duplicate_audit": humpop_audit,
        },
        "primary_midpoint_50": primary,
        "sensitivities": {
            "crossing_25": q25,
            "crossing_75": q75,
            "minimum_four_arrival_observations": obs4,
            "minimum_prior_size_2": ge2,
            "leave_one_colony_out_observed_beta": loo,
        },
        "decision": {
            "arrival_process_supported": bool(primary["test"]["supported"]),
            "individual_movement_identified": False,
        },
        "interpretation_boundary": {
            "arrival_timing_identifies_returning_vs_immigrant": False,
            "individual_band_resight_gate_remains_blocked": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--humpop", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    args = parser.parse_args()
    result = analyze(
        args.adult_census,
        args.chicks,
        args.humpop,
        permutations=args.permutations,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
