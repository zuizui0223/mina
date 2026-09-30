"""Performance-memory mechanism diagnostics for Palmer Adelie colonies."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .performance_redistribution_lags import (
    ISLANDS,
    load_adult_rows,
    load_chick_rows,
    performance_rows,
    lag_panel,
)

N_PERMUTATIONS = 100_000
MEMORY_SEED_BASE = 20260950
BRIDGE_SEED = 20260960


def _colony_fixed_effects(rows: list[dict[str, object]]) -> np.ndarray:
    colonies = sorted({f"{r['island']}:{r['colony']}" for r in rows})
    cmap = {name: idx for idx, name in enumerate(colonies)}
    fe = np.zeros((len(rows), len(colonies)), dtype=float)
    for idx, row in enumerate(rows):
        fe[idx, cmap[f"{row['island']}:{row['colony']}"]] = 1.0
    return fe


def memory_panel(
    performance: list[dict[str, object]],
    lag: int,
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
) -> list[dict[str, object]]:
    if lag < 1:
        raise ValueError("memory lag must be >= 1")
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
        season = int(row["season"])
        future_key = (island, str(row["colony"]), season + lag)
        if future_key not in lookup:
            continue
        out.append(
            {
                "island": island,
                "colony": str(row["colony"]),
                "season": season,
                "past": float(row["state"]),
                "future": float(lookup[future_key]),
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
    state_lookup = {
        (str(r["island"]), str(r["colony"]), int(r["season"])): float(r["state"])
        for r in performance
        if str(r["island"]) in allowed_islands
    }
    lag2 = lag_panel(
        adults,
        performance,
        2,
        allowed_islands=allowed_islands,
        minimum_prior_size=minimum_prior_size,
    )
    out: list[dict[str, object]] = []
    for row in lag2:
        current_key = (
            str(row["island"]),
            str(row["colony"]),
            int(row["season"]) + 1,
        )
        if current_key not in state_lookup:
            continue
        out.append(
            {
                **row,
                "past": float(row["state"]),
                "current": float(state_lookup[current_key]),
                "outcome": float(row["relative_growth"]),
            }
        )
    return out


def _performance_groups(
    performance: list[dict[str, object]],
) -> dict[tuple[str, int], tuple[list[str], np.ndarray]]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        groups[(str(row["island"]), int(row["season"]))].append(row)
    out: dict[tuple[str, int], tuple[list[str], np.ndarray]] = {}
    for key, local in groups.items():
        local = sorted(local, key=lambda r: str(r["colony"]))
        out[key] = (
            [str(r["colony"]) for r in local],
            np.asarray([float(r["state"]) for r in local], dtype=float),
        )
    return out


def _prepare_permutation_model(
    panel: list[dict[str, object]],
    performance: list[dict[str, object]],
    *,
    x_field: str,
    y_field: str,
    controls: np.ndarray,
) -> dict[str, object]:
    x = np.asarray([float(r[x_field]) for r in panel], dtype=float)
    y = np.asarray([float(r[y_field]) for r in panel], dtype=float)
    gram_inv = np.linalg.pinv(controls.T @ controls)
    y_residual = y - controls @ (gram_inv @ (controls.T @ y))
    ctx = controls.T @ x
    denominator = float(x @ x - ctx @ (gram_inv @ ctx))
    if denominator <= 0:
        raise ValueError("zero residual predictor variance")
    observed = float((x @ y_residual) / denominator)

    perf_groups = _performance_groups(performance)
    by_panel: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, row in enumerate(panel):
        by_panel[(str(row["island"]), int(row["season"]))].append(idx)

    group_rows: dict[tuple[str, int], tuple[np.ndarray, np.ndarray]] = {}
    for key, indices in by_panel.items():
        if key not in perf_groups:
            raise ValueError(f"panel predictor group absent from performance table: {key!r}")
        colonies, _ = perf_groups[key]
        positions = {name: idx for idx, name in enumerate(colonies)}
        row_indices = np.asarray(indices, dtype=int)
        source_positions = np.asarray(
            [positions[str(panel[idx]["colony"])] for idx in indices],
            dtype=int,
        )
        group_rows[key] = (row_indices, source_positions)

    return {
        "panel": panel,
        "controls": controls,
        "gram_inv": gram_inv,
        "y_residual": y_residual,
        "observed": observed,
        "performance_groups": perf_groups,
        "group_rows": group_rows,
    }


def _permutation_test(
    model: dict[str, object],
    *,
    permutations: int,
    seed: int,
    batch_size: int = 1000,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    n = len(model["panel"])
    controls = np.asarray(model["controls"], dtype=float)
    gram_inv = np.asarray(model["gram_inv"], dtype=float)
    y_residual = np.asarray(model["y_residual"], dtype=float)
    groups = model["performance_groups"]
    group_rows = model["group_rows"]

    null = np.empty(permutations, dtype=float)
    offset = 0
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        x = np.empty((batch, n), dtype=float)
        for key in sorted(group_rows):
            _, values = groups[key]
            order = np.argsort(rng.random((batch, len(values))), axis=1)
            assigned = values[order]
            row_indices, source_positions = group_rows[key]
            x[:, row_indices] = assigned[:, source_positions]

        ctx = x @ controls
        numerator = x @ y_residual
        denominator = np.sum(x * x, axis=1) - np.einsum(
            "bi,ij,bj->b", ctx, gram_inv, ctx, optimize=True
        )
        null[offset : offset + batch] = numerator / denominator
        offset += batch

    observed = float(model["observed"])
    p_value = float(
        (1 + int(np.sum(null >= observed))) / (permutations + 1)
    )
    return {
        "n_rows": n,
        "coefficient": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": p_value,
        "supported": bool(observed > 0 and p_value <= 0.05),
    }


def memory_test(
    performance: list[dict[str, object]],
    lag: int,
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    permutations: int = N_PERMUTATIONS,
    seed: int = MEMORY_SEED_BASE,
) -> dict[str, object]:
    panel = memory_panel(
        performance, lag, allowed_islands=allowed_islands
    )
    model = _prepare_permutation_model(
        panel,
        performance,
        x_field="past",
        y_field="future",
        controls=_colony_fixed_effects(panel),
    )
    result = _permutation_test(
        model, permutations=permutations, seed=seed
    )
    result["lag"] = lag
    return result


def _bridge_controls(panel: list[dict[str, object]]) -> np.ndarray:
    fe = _colony_fixed_effects(panel)
    current = np.asarray([float(r["current"]) for r in panel], dtype=float)
    zsize = np.asarray([float(r["zsize"]) for r in panel], dtype=float)
    return np.column_stack([current, zsize, fe])


def _current_coefficient(panel: list[dict[str, object]]) -> float:
    fe = _colony_fixed_effects(panel)
    past = np.asarray([float(r["past"]) for r in panel], dtype=float)
    current = np.asarray([float(r["current"]) for r in panel], dtype=float)
    zsize = np.asarray([float(r["zsize"]) for r in panel], dtype=float)
    y = np.asarray([float(r["outcome"]) for r in panel], dtype=float)
    x = np.column_stack([past, current, zsize, fe])
    beta, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    return float(beta[1])


def bridge_test(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    minimum_prior_size: float = 0.0,
    permutations: int = N_PERMUTATIONS,
    seed: int = BRIDGE_SEED,
) -> dict[str, object]:
    panel = bridge_panel(
        adults,
        performance,
        allowed_islands=allowed_islands,
        minimum_prior_size=minimum_prior_size,
    )
    model = _prepare_permutation_model(
        panel,
        performance,
        x_field="past",
        y_field="outcome",
        controls=_bridge_controls(panel),
    )
    result = _permutation_test(
        model, permutations=permutations, seed=seed
    )
    result["delta_past"] = result.pop("coefficient")
    result["delta_current_descriptive"] = _current_coefficient(panel)
    return result


def _observed_memory(
    performance: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...],
) -> float:
    panel = memory_panel(performance, 1, allowed_islands=allowed_islands)
    model = _prepare_permutation_model(
        panel,
        performance,
        x_field="past",
        y_field="future",
        controls=_colony_fixed_effects(panel),
    )
    return float(model["observed"])


def _observed_bridge(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...],
) -> float:
    panel = bridge_panel(
        adults, performance, allowed_islands=allowed_islands
    )
    model = _prepare_permutation_model(
        panel,
        performance,
        x_field="past",
        y_field="outcome",
        controls=_bridge_controls(panel),
    )
    return float(model["observed"])


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)
    primary_perf = performance_rows(adults, chicks)

    memory = {
        str(lag): memory_test(
            primary_perf,
            lag,
            permutations=permutations,
            seed=MEMORY_SEED_BASE + lag - 1,
        )
        for lag in (1, 2, 3)
    }
    bridge = bridge_test(
        adults,
        primary_perf,
        permutations=permutations,
        seed=BRIDGE_SEED,
    )

    no_lit = tuple(x for x in ISLANDS if x != "LIT")
    no_lit_perf = performance_rows(
        adults, chicks, allowed_islands=no_lit
    )
    no_lit_result = {
        "memory_lag1": memory_test(
            no_lit_perf,
            1,
            allowed_islands=no_lit,
            permutations=permutations,
            seed=20260972,
        ),
        "bridge": bridge_test(
            adults,
            no_lit_perf,
            allowed_islands=no_lit,
            permutations=permutations,
            seed=20260973,
        ),
    }

    logratio_perf = performance_rows(adults, chicks, metric="logratio")
    logratio_result = {
        "memory_lag1": memory_test(
            logratio_perf,
            1,
            permutations=permutations,
            seed=20260970,
        ),
        "bridge": bridge_test(
            adults,
            logratio_perf,
            permutations=permutations,
            seed=20260971,
        ),
    }

    prior_ge2 = bridge_test(
        adults,
        primary_perf,
        minimum_prior_size=2.0,
        permutations=permutations,
        seed=20260974,
    )

    leave_one_out: dict[str, object] = {}
    for island in ISLANDS:
        allowed = tuple(x for x in ISLANDS if x != island)
        local_perf = performance_rows(
            adults, chicks, allowed_islands=allowed
        )
        leave_one_out[island] = {
            "rho_1": _observed_memory(
                local_perf, allowed_islands=allowed
            ),
            "delta_past": _observed_bridge(
                adults, local_perf, allowed_islands=allowed
            ),
        }

    rho1_supported = bool(memory["1"]["supported"])
    delta_supported = bool(bridge["supported"])
    if rho1_supported and delta_supported:
        pattern = "mixed_pattern"
    elif rho1_supported:
        pattern = "persistent_state_pattern"
    elif delta_supported:
        pattern = "biological_memory_compatible_pattern"
    else:
        pattern = "neither"

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-performance-memory-v1",
        "contract_id": "mina-palmer-performance-memory-v1",
        "source_counts": {
            "adult_rows": len(adults),
            "usable_chick_rows": len(chicks),
            "performance_rows": len(primary_perf),
        },
        "P3_performance_memory": memory,
        "P4_bridge": bridge,
        "sensitivities": {
            "exclude_litchfield": no_lit_result,
            "alternate_logratio_metric": logratio_result,
            "minimum_prior_size_2_bridge": prior_ge2,
            "leave_one_island_out_observed": leave_one_out,
        },
        "decision": {
            "rho_1_supported": rho1_supported,
            "delta_past_supported": delta_supported,
            "pattern": pattern,
            "individual_public_information_use_identified": False,
        },
        "interpretation_boundary": {
            "bridge_is_causal_mediation": False,
            "null_memory_would_rule_out_environment": False,
            "colony_counts_identify_movement_process": False,
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
