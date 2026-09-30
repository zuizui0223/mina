"""Mechanism diagnostic for persistence of Palmer colony performance state."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .performance_redistribution_lags import (
    ISLANDS,
    SEED_BASE as LAG_SEED_BASE,
    lag_panel,
    load_adult_rows,
    load_chick_rows,
    performance_rows,
)

N_PERMUTATIONS = 100_000
MEMORY_SEED_BASE = 20260950
BRIDGE_SEED = 20260960


def memory_panel(
    performance: list[dict[str, object]],
    lag: int,
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
) -> list[dict[str, object]]:
    lookup = {
        (str(r["island"]), str(r["colony"]), int(r["season"])): float(r["state"])
        for r in performance
        if str(r["island"]) in allowed_islands
    }
    out: list[dict[str, object]] = []
    for row in performance:
        island = str(row["island"])
        if island not in allowed_islands:
            continue
        future = (island, str(row["colony"]), int(row["season"]) + lag)
        if future not in lookup:
            continue
        out.append(
            {
                "island": island,
                "colony": str(row["colony"]),
                "season": int(row["season"]),
                "x": float(row["state"]),
                "y": lookup[future],
            }
        )
    return out


def bridge_panel(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    minimum_prior_size: float = 0.0,
) -> list[dict[str, object]]:
    lag2 = lag_panel(
        adults,
        performance,
        2,
        allowed_islands=allowed_islands,
        minimum_prior_size=minimum_prior_size,
    )
    future = {
        (str(r["island"]), str(r["colony"]), int(r["season"])): float(r["state"])
        for r in performance
        if str(r["island"]) in allowed_islands
    }
    out: list[dict[str, object]] = []
    for row in lag2:
        key = (
            str(row["island"]),
            str(row["colony"]),
            int(row["season"]) + 1,
        )
        if key not in future:
            continue
        out.append(
            {
                "island": str(row["island"]),
                "colony": str(row["colony"]),
                "season": int(row["season"]),
                "x": float(row["state"]),
                "y": float(row["relative_growth"]),
                "current_state": future[key],
                "zsize": float(row["zsize"]),
            }
        )
    return out


def _prepare_model(
    panel: list[dict[str, object]],
    *,
    extra_controls: tuple[str, ...] = (),
) -> dict[str, object]:
    colonies = sorted({f"{r['island']}:{r['colony']}" for r in panel})
    cmap = {name: idx for idx, name in enumerate(colonies)}
    n = len(panel)
    fe = np.zeros((n, len(colonies)), dtype=float)
    for idx, row in enumerate(panel):
        fe[idx, cmap[f"{row['island']}:{row['colony']}"]] = 1.0

    controls = fe
    if extra_controls:
        numerical = np.column_stack(
            [
                np.asarray([float(r[key]) for r in panel], dtype=float)
                for key in extra_controls
            ]
        )
        controls = np.column_stack([numerical, fe])

    x = np.asarray([float(r["x"]) for r in panel], dtype=float)
    y = np.asarray([float(r["y"]) for r in panel], dtype=float)
    inverse = np.linalg.pinv(controls.T @ controls)
    y_residual = y - controls @ (inverse @ (controls.T @ y))
    ztx = controls.T @ x
    denominator = float(x @ x - ztx @ (inverse @ ztx))
    if denominator <= 0:
        raise ValueError("non-positive residual predictor variance")
    observed = float((x @ y_residual) / denominator)

    groups: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, row in enumerate(panel):
        groups[(str(row["island"]), int(row["season"]))].append(idx)

    return {
        "panel": panel,
        "controls": controls,
        "inverse": inverse,
        "y_residual": y_residual,
        "observed": observed,
        "groups": groups,
        "x": x,
    }


def permutation_test(
    model: dict[str, object],
    *,
    permutations: int,
    seed: int,
    batch_size: int = 1000,
) -> dict[str, object]:
    panel = model["panel"]
    controls = np.asarray(model["controls"], dtype=float)
    inverse = np.asarray(model["inverse"], dtype=float)
    y_residual = np.asarray(model["y_residual"], dtype=float)
    original = np.asarray(model["x"], dtype=float)
    groups = model["groups"]
    observed = float(model["observed"])

    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=float)
    offset = 0
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        x = np.empty((batch, len(panel)), dtype=float)
        for indices in groups.values():
            idx = np.asarray(indices, dtype=int)
            values = original[idx]
            order = np.argsort(rng.random((batch, len(idx))), axis=1)
            x[:, idx] = values[order]
        ztx = x @ controls
        numerator = x @ y_residual
        denominator = np.sum(x * x, axis=1) - np.einsum(
            "bi,ij,bj->b", ztx, inverse, ztx, optimize=True
        )
        null[offset : offset + batch] = numerator / denominator
        offset += batch

    p = float((1 + int(np.sum(null >= observed))) / (permutations + 1))
    return {
        "n_rows": len(panel),
        "coefficient": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": p,
        "supported": bool(observed > 0 and p <= 0.05),
    }


def _primary_configuration(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    metric: str = "pearson",
    minimum_prior_size: float = 0.0,
    permutations: int = N_PERMUTATIONS,
    seed_offset: int = 0,
) -> dict[str, object]:
    performance = performance_rows(
        adults,
        chicks,
        allowed_islands=allowed_islands,
        metric=metric,
    )
    memory: dict[str, object] = {}
    for lag in (1, 2, 3):
        panel = memory_panel(
            performance,
            lag,
            allowed_islands=allowed_islands,
        )
        memory[str(lag)] = permutation_test(
            _prepare_model(panel),
            permutations=permutations,
            seed=MEMORY_SEED_BASE + seed_offset + lag - 1,
        )

    bridge = bridge_panel(
        adults,
        performance,
        allowed_islands=allowed_islands,
        minimum_prior_size=minimum_prior_size,
    )
    bridge_result = permutation_test(
        _prepare_model(
            bridge,
            extra_controls=("current_state", "zsize"),
        ),
        permutations=permutations,
        seed=BRIDGE_SEED + seed_offset,
    )
    return {
        "performance_rows": len(performance),
        "performance_island_seasons": len(
            {(str(r["island"]), int(r["season"])) for r in performance}
        ),
        "memory": memory,
        "bridge": bridge_result,
    }


def _observed_leave_one_out(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    excluded_island: str,
) -> dict[str, object]:
    allowed = tuple(x for x in ISLANDS if x != excluded_island)
    performance = performance_rows(
        adults, chicks, allowed_islands=allowed
    )
    memory = memory_panel(performance, 1, allowed_islands=allowed)
    rho1 = float(_prepare_model(memory)["observed"])
    bridge = bridge_panel(adults, performance, allowed_islands=allowed)
    delta = float(
        _prepare_model(
            bridge, extra_controls=("current_state", "zsize")
        )["observed"]
    )
    return {
        "memory_n": len(memory),
        "rho_1": rho1,
        "bridge_n": len(bridge),
        "delta_past": delta,
    }


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)

    primary = _primary_configuration(
        adults, chicks, permutations=permutations
    )
    no_lit = _primary_configuration(
        adults,
        chicks,
        allowed_islands=tuple(x for x in ISLANDS if x != "LIT"),
        permutations=permutations,
        seed_offset=100,
    )
    logratio = _primary_configuration(
        adults,
        chicks,
        metric="logratio",
        permutations=permutations,
        seed_offset=200,
    )
    performance_primary = performance_rows(adults, chicks)
    prior_ge2_panel = bridge_panel(
        adults,
        performance_primary,
        minimum_prior_size=2.0,
    )
    prior_ge2 = permutation_test(
        _prepare_model(
            prior_ge2_panel,
            extra_controls=("current_state", "zsize"),
        ),
        permutations=permutations,
        seed=20261001,
    )
    loo = {
        island: _observed_leave_one_out(adults, chicks, island)
        for island in ISLANDS
    }

    rho1 = primary["memory"]["1"]
    bridge = primary["bridge"]
    if rho1["supported"] and bridge["supported"]:
        pattern = "mixed_pattern"
    elif (not rho1["supported"]) and bridge["supported"]:
        pattern = "biological_memory_compatible_pattern"
    elif rho1["supported"] and (not bridge["supported"]):
        pattern = "persistent_state_pattern"
    else:
        pattern = "neither"

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-performance-memory-v1",
        "contract_id": "mina-palmer-performance-memory-v1",
        "source_counts": {
            "adult_rows": len(adults),
            "usable_chick_rows": len(chicks),
        },
        "primary": primary,
        "sensitivities": {
            "exclude_litchfield": no_lit,
            "alternate_logratio_metric": logratio,
            "minimum_prior_size_2": {
                "bridge": prior_ge2,
            },
            "leave_one_island_out_observed": loo,
        },
        "decision": {
            "pattern": pattern,
            "rho1_supported": bool(rho1["supported"]),
            "bridge_delta_past_supported": bool(bridge["supported"]),
        },
        "interpretation_boundary": {
            "causal_mediation_claim": False,
            "individual_movement_or_public_information_proven": False,
            "persistent_local_environment_excluded": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    args = parser.parse_args()
    result = analyze(
        args.adult_census,
        args.chicks,
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
