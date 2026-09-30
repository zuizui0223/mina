"""Independent nest-level reproductive-success validation of Palmer colony redistribution."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .performance_redistribution_lags import (
    ISLANDS,
    _adult_lookup,
    _study_season,
    load_adult_rows,
    load_chick_rows,
    performance_rows,
)

N_PERMUTATIONS = 100_000
SEED = 20260990
MIN_NESTS = 5
MIN_ROWS = 50
MIN_GROUPS = 10


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan", "NULL", "null"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _positive_event(value: str | None) -> int:
    """Frozen semantic repair: only a positive numeric creche date is success."""
    if not _finite(value):
        return 0
    return int(float(value) > 0.0)


def load_repro(path: str | Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []
    expected = [
        "studyName", "Island", "Colony", "Site Number", "Nest Number",
        "Egg 1 Lay Date", "Egg 2 Lay Date", "Egg 1 Loss Date", "Egg 2 Loss Date",
        "Chick 1 Hatch Date", "Chick 2 Hatch Date",
        "Chick 1 Loss Date", "Chick 2 Loss Date",
        "Chick 1 Creche Date", "Chick 2 Creche Date", "Notes",
    ]
    if fields != expected:
        raise ValueError(f"unexpected REPRO columns: {fields!r}")

    parsed: list[tuple[tuple[str, str, str, str, str], dict[str, object]]] = []
    key_count: dict[tuple[str, str, str, str, str], int] = defaultdict(int)
    for row in rows:
        island = str(row["Island"]).strip()
        if island not in ISLANDS:
            continue
        study = str(row["studyName"]).strip()
        season = _study_season(study)
        colony = str(row["Colony"]).strip()
        site = str(row["Site Number"]).strip()
        nest = str(row["Nest Number"]).strip()
        key = (study, island, colony, site, nest)
        record = {
            "study_name": study,
            "season": season,
            "island": island,
            "colony": colony,
            "site": site,
            "nest": nest,
            "creched_chicks": (
                _positive_event(row["Chick 1 Creche Date"])
                + _positive_event(row["Chick 2 Creche Date"])
            ),
        }
        parsed.append((key, record))
        key_count[key] += 1

    duplicated = {key for key, count in key_count.items() if count > 1}
    usable = [record for key, record in parsed if key not in duplicated]
    return usable, {
        "raw_rows": len(rows),
        "parsed_focal_rows": len(parsed),
        "duplicate_nest_keys": len(duplicated),
        "rows_excluded_by_duplicate_rule": sum(
            count for key, count in key_count.items() if key in duplicated
        ),
        "usable_nest_rows": len(usable),
    }


def repro_states(
    rows: list[dict[str, object]],
    *,
    minimum_nests: int = MIN_NESTS,
    binary_any_creche: bool = False,
    allowed_islands: tuple[str, ...] = ISLANDS,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    colonies: dict[tuple[str, int, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if str(row["island"]) in allowed_islands:
            colonies[(str(row["island"]), int(row["season"]), str(row["colony"]))].append(row)

    colony_stats: list[dict[str, object]] = []
    dropped_small = 0
    for (island, season, colony), local in sorted(colonies.items()):
        if len(local) < minimum_nests:
            dropped_small += 1
            continue
        values = np.asarray([float(r["creched_chicks"]) for r in local], dtype=float)
        if binary_any_creche:
            values = (values >= 1.0).astype(float)
        colony_stats.append({
            "island": island,
            "season": season,
            "colony": colony,
            "n_nests": len(local),
            "success": float(np.mean(values)),
        })

    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in colony_stats:
        groups[(str(row["island"]), int(row["season"]))].append(row)

    states: list[dict[str, object]] = []
    dropped_groups: list[dict[str, object]] = []
    for (island, season), local in sorted(groups.items()):
        if len(local) < 3:
            dropped_groups.append({"island": island, "season": season, "n_colonies": len(local)})
            continue
        y = np.asarray([float(r["success"]) for r in local], dtype=float)
        sd = float(np.std(y, ddof=1))
        if sd <= 0:
            dropped_groups.append({
                "island": island, "season": season, "n_colonies": len(local),
                "reason": "zero_between_colony_success_variance",
            })
            continue
        z = (y - float(np.mean(y))) / sd
        for row, value in zip(local, z):
            states.append({**row, "state": float(value)})

    return states, {
        "minimum_nests": minimum_nests,
        "binary_any_creche": binary_any_creche,
        "colony_seasons_before_minimum_nests": len(colonies),
        "colony_seasons_after_minimum_nests": len(colony_stats),
        "colony_seasons_dropped_for_small_n": dropped_small,
        "eligible_island_seasons": len({(r["island"], r["season"]) for r in states}),
        "performance_rows": len(states),
        "dropped_island_seasons": dropped_groups,
    }


def redistribution_panel(
    adults: list[dict[str, object]],
    states: list[dict[str, object]],
    *,
    lag: int,
    minimum_prior_size: float = 0.0,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    adult = _adult_lookup(adults)
    raw: list[dict[str, object]] = []
    for row in states:
        island = str(row["island"])
        colony = str(row["colony"])
        season = int(row["season"])
        start_year = season + lag - 1
        k0 = (island, colony, start_year)
        k1 = (island, colony, start_year + 1)
        if k0 not in adult or k1 not in adult:
            continue
        n0 = float(adult[k0])
        n1 = float(adult[k1])
        if n0 < minimum_prior_size:
            continue
        raw.append({
            **row,
            "predictor_group": f"{island}:{season}",
            "start_year": start_year,
            "prior_size": n0,
            "growth": math.log1p(n1) - math.log1p(n0),
        })

    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in raw:
        groups[(str(row["island"]), int(row["start_year"]))].append(row)

    panel: list[dict[str, object]] = []
    dropped: list[dict[str, object]] = []
    for (island, year), local in sorted(groups.items()):
        if len(local) < 3:
            dropped.append({"island": island, "start_year": year, "n_colonies": len(local)})
            continue
        growth = np.asarray([float(r["growth"]) for r in local], dtype=float)
        size = np.log1p(np.asarray([float(r["prior_size"]) for r in local], dtype=float))
        ssd = float(np.std(size, ddof=1))
        zsize = (
            (size - float(np.mean(size))) / ssd
            if ssd > 0 else np.zeros_like(size)
        )
        rel = growth - float(np.mean(growth))
        for row, rg, zs in zip(local, rel, zsize):
            panel.append({
                **row,
                "relative_growth": float(rg),
                "z_prior_size": float(zs),
            })

    return panel, {
        "raw_matches": len(raw),
        "panel_rows": len(panel),
        "predictor_island_seasons": len(
            {(str(r["island"]), int(r["season"])) for r in panel}
        ),
        "dropped_transition_groups_lt3": dropped,
    }


def _fixed_effect_matrix(rows: list[dict[str, object]]) -> np.ndarray:
    levels = sorted({f"{r['island']}:{r['colony']}" for r in rows})
    lookup = {level: idx for idx, level in enumerate(levels)}
    matrix = np.zeros((len(rows), len(levels)), dtype=float)
    for idx, row in enumerate(rows):
        matrix[idx, lookup[f"{row['island']}:{row['colony']}"]] = 1.0
    return matrix


def _state_groups(states: list[dict[str, object]]) -> dict[tuple[str, int], tuple[list[str], np.ndarray]]:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in states:
        grouped[(str(row["island"]), int(row["season"]))].append(row)
    out: dict[tuple[str, int], tuple[list[str], np.ndarray]] = {}
    for key, local in grouped.items():
        local = sorted(local, key=lambda r: str(r["colony"]))
        out[key] = (
            [str(r["colony"]) for r in local],
            np.asarray([float(r["state"]) for r in local], dtype=float),
        )
    return out


def information_gate(panel: list[dict[str, object]]) -> dict[str, object]:
    groups = {(str(r["island"]), int(r["season"])) for r in panel}
    reasons = []
    if len(panel) < MIN_ROWS:
        reasons.append("fewer_than_50_matched_colony_seasons")
    if len(groups) < MIN_GROUPS:
        reasons.append("fewer_than_10_predictor_island_seasons")
    return {
        "n_rows": len(panel),
        "n_predictor_island_seasons": len(groups),
        "required_rows": MIN_ROWS,
        "required_predictor_island_seasons": MIN_GROUPS,
        "pass": not reasons,
        "failure_reasons": reasons,
    }


def prepare_model(
    panel: list[dict[str, object]],
    states: list[dict[str, object]],
) -> dict[str, object]:
    gate = information_gate(panel)
    if not gate["pass"]:
        raise ValueError("minimum-information gate failed")
    y = np.asarray([float(r["relative_growth"]) for r in panel], dtype=float)
    state = np.asarray([float(r["state"]) for r in panel], dtype=float)
    zsize = np.asarray([float(r["z_prior_size"]) for r in panel], dtype=float)
    controls = np.column_stack([zsize, _fixed_effect_matrix(panel)])
    gram_inv = np.linalg.pinv(controls.T @ controls)
    y_resid = y - controls @ (gram_inv @ (controls.T @ y))
    ctx = controls.T @ state
    denom = float(state @ state - ctx @ (gram_inv @ ctx))
    if denom <= 0:
        raise ValueError("zero residual state variance")
    observed = float((state @ y_resid) / denom)

    all_groups = _state_groups(states)
    by_panel: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, row in enumerate(panel):
        by_panel[(str(row["island"]), int(row["season"]))].append(idx)
    group_rows: dict[tuple[str, int], tuple[np.ndarray, np.ndarray]] = {}
    for key, indices in by_panel.items():
        colonies, _ = all_groups[key]
        positions = {name: idx for idx, name in enumerate(colonies)}
        row_indices = np.asarray(indices, dtype=int)
        source_positions = np.asarray(
            [positions[str(panel[idx]["colony"])] for idx in indices], dtype=int
        )
        group_rows[key] = (row_indices, source_positions)
    return {
        "panel": panel,
        "controls": controls,
        "gram_inv": gram_inv,
        "y_resid": y_resid,
        "observed": observed,
        "all_groups": all_groups,
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
    n = len(model["panel"])
    controls = np.asarray(model["controls"], dtype=float)
    gram_inv = np.asarray(model["gram_inv"], dtype=float)
    y_resid = np.asarray(model["y_resid"], dtype=float)
    null = np.empty(permutations, dtype=float)

    offset = 0
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        x = np.empty((batch, n), dtype=float)
        for key in sorted(model["group_rows"]):
            _, values = model["all_groups"][key]
            order = np.argsort(rng.random((batch, len(values))), axis=1)
            assigned = values[order]
            rows, positions = model["group_rows"][key]
            x[:, rows] = assigned[:, positions]
        ctx = x @ controls
        numerator = x @ y_resid
        denominator = np.sum(x * x, axis=1) - np.einsum(
            "bi,ij,bj->b", ctx, gram_inv, ctx, optimize=True
        )
        null[offset: offset + batch] = numerator / denominator
        offset += batch

    observed = float(model["observed"])
    p = float((1 + int(np.sum(null >= observed))) / (permutations + 1))
    return {
        "beta": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": p,
        "supported": bool(observed > 0 and p <= 0.05),
    }


def run_configuration(
    adults: list[dict[str, object]],
    repro_rows: list[dict[str, object]],
    *,
    lag: int = 1,
    minimum_nests: int = MIN_NESTS,
    binary_any_creche: bool = False,
    allowed_islands: tuple[str, ...] = ISLANDS,
    minimum_prior_size: float = 0.0,
    permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    states, state_audit = repro_states(
        repro_rows,
        minimum_nests=minimum_nests,
        binary_any_creche=binary_any_creche,
        allowed_islands=allowed_islands,
    )
    panel, panel_audit = redistribution_panel(
        adults, states, lag=lag, minimum_prior_size=minimum_prior_size
    )
    gate = information_gate(panel)
    result = {
        "lag": lag,
        "state_audit": state_audit,
        "panel_audit": panel_audit,
        "information_gate": gate,
        "estimable": bool(gate["pass"]),
    }
    if not gate["pass"]:
        return result
    model = prepare_model(panel, states)
    result["test"] = permutation_test(
        model, permutations=permutations, seed=seed
    )
    return result


def _observed_beta_if_estimable(
    adults: list[dict[str, object]],
    repro_rows: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    excluded_colony: tuple[str, str] | None = None,
) -> float | None:
    states, _ = repro_states(repro_rows, allowed_islands=allowed_islands)
    if excluded_colony is not None:
        states = [
            r for r in states
            if (str(r["island"]), str(r["colony"])) != excluded_colony
        ]
    panel, _ = redistribution_panel(adults, states, lag=1)
    if not information_gate(panel)["pass"]:
        return None
    return float(prepare_model(panel, states)["observed"])


def convergent_validity(
    nest_states: list[dict[str, object]],
    chick_states: list[dict[str, object]],
) -> dict[str, object]:
    chick = {
        (str(r["island"]), str(r["colony"]), int(r["season"])): float(r["state"])
        for r in chick_states
    }
    x, y = [], []
    for row in nest_states:
        key = (str(row["island"]), str(row["colony"]), int(row["season"]))
        if key in chick:
            x.append(float(row["state"]))
            y.append(chick[key])
    if len(x) < 3 or float(np.std(x)) <= 0 or float(np.std(y)) <= 0:
        return {"n": len(x), "pearson_r": None}
    return {"n": len(x), "pearson_r": float(np.corrcoef(x, y)[0, 1])}


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    repro_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)
    repro, source_audit = load_repro(repro_path)

    primary = run_configuration(
        adults, repro, lag=1, permutations=permutations, seed=SEED
    )
    if not primary["estimable"]:
        return {
            "schema_version": 1,
            "analysis_id": "mina-palmer-repro-redistribution-v1",
            "contract_id": "mina-palmer-repro-redistribution-v1",
            "source_counts": {
                "adult_rows": len(adults),
                "usable_chick_rows": len(chicks),
                "repro_source_audit": source_audit,
            },
            "primary_lag1": primary,
            "secondary_lag2": None,
            "sensitivities": {},
            "decision": {
                "status": "STOP_insufficient_information",
                "independent_nest_validation_supported": None,
                "posthoc_threshold_rescue_allowed": False,
            },
        }

    secondary = run_configuration(
        adults, repro, lag=2, permutations=permutations, seed=SEED + 1
    )
    min10 = run_configuration(
        adults, repro, minimum_nests=10,
        permutations=permutations, seed=SEED + 2
    )
    binary = run_configuration(
        adults, repro, binary_any_creche=True,
        permutations=permutations, seed=SEED + 3
    )
    no_lit = run_configuration(
        adults, repro,
        allowed_islands=tuple(i for i in ISLANDS if i != "LIT"),
        permutations=permutations, seed=SEED + 4
    )
    ge2 = run_configuration(
        adults, repro, minimum_prior_size=2.0,
        permutations=permutations, seed=SEED + 5
    )

    primary_states, _ = repro_states(repro)
    represented_islands = sorted({str(r["island"]) for r in primary_states})
    represented_colonies = sorted(
        {(str(r["island"]), str(r["colony"])) for r in primary_states}
    )
    loo_island = {
        island: _observed_beta_if_estimable(
            adults, repro,
            allowed_islands=tuple(i for i in ISLANDS if i != island),
        )
        for island in represented_islands
    }
    loo_colony = {
        f"{island}:{colony}": _observed_beta_if_estimable(
            adults, repro, excluded_colony=(island, colony)
        )
        for island, colony in represented_colonies
    }

    chick_states = performance_rows(adults, chicks)
    convergence = convergent_validity(primary_states, chick_states)
    support = bool(primary["test"]["supported"])
    strong = bool(
        support
        and min10.get("estimable")
        and min10.get("test", {}).get("beta", 0) > 0
        and binary.get("estimable")
        and binary.get("test", {}).get("beta", 0) > 0
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-repro-redistribution-v1",
        "contract_id": "mina-palmer-repro-redistribution-v1",
        "source_counts": {
            "adult_rows": len(adults),
            "usable_chick_rows": len(chicks),
            "repro_source_audit": source_audit,
        },
        "primary_lag1": primary,
        "secondary_lag2": secondary,
        "sensitivities": {
            "minimum_nests_10": min10,
            "binary_any_creche": binary,
            "exclude_litchfield": no_lit,
            "minimum_prior_size_2": ge2,
            "leave_one_island_out_observed_beta": loo_island,
            "leave_one_colony_out_observed_beta": loo_colony,
        },
        "convergent_validity": convergence,
        "decision": {
            "status": "estimated",
            "independent_nest_validation_supported": support,
            "strong_replication_pattern": strong,
            "individual_public_information_proven": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--repro", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    args = parser.parse_args()
    result = analyze(
        args.adult_census,
        args.chicks,
        args.repro,
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
