"""Independent monitored-nest reproductive-performance replication."""
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
    _study_season,
    lag_panel,
    load_adult_rows,
)

N_PERMUTATIONS = 100_000
SEED = 20260990

EXPECTED_COLUMNS = [
    "studyName",
    "Island",
    "Colony",
    "Site Number",
    "Nest Number",
    "Egg 1 Lay Date",
    "Egg 2 Lay Date",
    "Egg 1 Loss Date",
    "Egg 2 Loss Date",
    "Chick 1 Hatch Date",
    "Chick 2 Hatch Date",
    "Chick 1 Loss Date",
    "Chick 2 Loss Date",
    "Chick 1 Creche Date",
    "Chick 2 Creche Date",
    "Notes",
]


def _event_observed(value: str | None) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    if text.lower() in {"", "null", "none", "na", "nan", "<na>"}:
        return False
    try:
        number = float(text)
    except ValueError:
        return False
    if not math.isfinite(number):
        return False
    return 1 <= number <= 998 and float(number).is_integer()


def load_repro(
    path: str | Path,
    *,
    success_kind: str = "creche",
) -> tuple[list[dict[str, object]], dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if list(reader.fieldnames or []) != EXPECTED_COLUMNS:
            raise ValueError(f"unexpected REPRO columns: {reader.fieldnames!r}")
        rows = list(reader)

    parsed: list[tuple[tuple[int, str, str, str, str], dict[str, object]]] = []
    key_counts: dict[tuple[int, str, str, str, str], int] = defaultdict(int)
    ineligible_no_lay = 0
    for row in rows:
        island = str(row["Island"]).strip()
        if island not in ISLANDS:
            continue
        season = _study_season(str(row["studyName"]).strip())
        colony = str(row["Colony"]).strip()
        site = str(row["Site Number"]).strip()
        nest = str(row["Nest Number"]).strip()

        has_lay = _event_observed(row["Egg 1 Lay Date"]) or _event_observed(
            row["Egg 2 Lay Date"]
        )
        if not has_lay:
            ineligible_no_lay += 1
            continue

        if success_kind == "creche":
            success = _event_observed(row["Chick 1 Creche Date"]) or _event_observed(
                row["Chick 2 Creche Date"]
            )
        elif success_kind == "hatch":
            success = _event_observed(row["Chick 1 Hatch Date"]) or _event_observed(
                row["Chick 2 Hatch Date"]
            )
        else:
            raise ValueError(success_kind)

        key = (season, island, colony, site, nest)
        record = {
            "season": season,
            "island": island,
            "colony": colony,
            "site": site,
            "nest": nest,
            "success": int(success),
        }
        parsed.append((key, record))
        key_counts[key] += 1

    duplicate_keys = {key for key, count in key_counts.items() if count > 1}
    out = [record for key, record in parsed if key not in duplicate_keys]
    return out, {
        "raw_rows": len(rows),
        "eligible_rows_before_duplicate_exclusion": len(parsed),
        "duplicate_eligible_nest_keys_excluded": len(duplicate_keys),
        "rows_excluded_by_duplicate_rule": sum(
            count for key, count in key_counts.items() if key in duplicate_keys
        ),
        "eligible_nest_rows": len(out),
        "ineligible_rows_without_observed_lay_date": ineligible_no_lay,
        "success_kind": success_kind,
    }

def colony_performance(
    nests: list[dict[str, object]],
    *,
    minimum_nests: int = 5,
    allowed_islands: tuple[str, ...] = ISLANDS,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    groups: dict[tuple[str, int, str], list[dict[str, object]]] = defaultdict(list)
    for row in nests:
        if str(row["island"]) in allowed_islands:
            groups[
                (str(row["island"]), int(row["season"]), str(row["colony"]))
            ].append(row)

    colony_rows: list[dict[str, object]] = []
    for (island, season, colony), local in sorted(groups.items()):
        if len(local) < minimum_nests:
            continue
        colony_rows.append(
            {
                "island": island,
                "season": season,
                "colony": colony,
                "n_nests": len(local),
                "successes": sum(int(r["success"]) for r in local),
            }
        )

    by_island_season: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in colony_rows:
        by_island_season[(str(row["island"]), int(row["season"]))].append(row)

    out: list[dict[str, object]] = []
    dropped_lt3 = []
    dropped_no_variation = []
    for key, local in sorted(by_island_season.items()):
        if len(local) < 3:
            dropped_lt3.append({"island": key[0], "season": key[1]})
            continue
        total_n = sum(int(r["n_nests"]) for r in local)
        total_success = sum(int(r["successes"]) for r in local)
        if total_n <= 0:
            continue
        p = total_success / total_n
        residual = []
        for row in local:
            n = int(row["n_nests"])
            s = int(row["successes"])
            denom = math.sqrt(max(n * p * (1.0 - p), 1e-12))
            residual.append((s - n * p) / denom)
        sd = float(np.std(np.asarray(residual, dtype=float), ddof=1))
        if sd <= 0:
            dropped_no_variation.append({"island": key[0], "season": key[1]})
            continue
        mean = float(np.mean(residual))
        for row, value in zip(local, residual):
            out.append(
                {
                    "island": str(row["island"]),
                    "season": int(row["season"]),
                    "colony": str(row["colony"]),
                    "state": float((value - mean) / sd),
                    "n_nests": int(row["n_nests"]),
                    "successes": int(row["successes"]),
                }
            )

    return out, {
        "minimum_nests": minimum_nests,
        "eligible_colony_seasons_before_island_season_gate": len(colony_rows),
        "performance_rows": len(out),
        "performance_island_seasons": len(
            {(str(r["island"]), int(r["season"])) for r in out}
        ),
        "performance_islands": sorted({str(r["island"]) for r in out}),
        "performance_colony_codes": sorted(
            {f"{r['island']}:{r['colony']}" for r in out}
        ),
        "dropped_island_seasons_with_lt3_colonies": dropped_lt3,
        "dropped_island_seasons_with_no_relative_variation": dropped_no_variation,
    }


def _colony_fe(panel: list[dict[str, object]]) -> np.ndarray:
    levels = sorted({f"{r['island']}:{r['colony']}" for r in panel})
    lookup = {value: idx for idx, value in enumerate(levels)}
    x = np.zeros((len(panel), len(levels)), dtype=float)
    for idx, row in enumerate(panel):
        x[idx, lookup[f"{row['island']}:{row['colony']}"]] = 1.0
    return x


def _prepare_model(
    panel: list[dict[str, object]],
    performance: list[dict[str, object]],
) -> dict[str, object]:
    state = np.asarray([float(r["state"]) for r in panel], dtype=float)
    y = np.asarray([float(r["relative_growth"]) for r in panel], dtype=float)
    zsize = np.asarray([float(r["zsize"]) for r in panel], dtype=float)
    controls = np.column_stack([zsize, _colony_fe(panel)])
    gram_inv = np.linalg.pinv(controls.T @ controls)
    y_resid = y - controls @ (gram_inv @ (controls.T @ y))
    ctx = controls.T @ state
    denominator = float(state @ state - ctx @ (gram_inv @ ctx))
    if denominator <= 0:
        raise ValueError("zero residual REPRO-performance variance")
    observed = float((state @ y_resid) / denominator)

    full_groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        full_groups[(str(row["island"]), int(row["season"]))].append(row)
    perf_groups: dict[tuple[str, int], tuple[list[str], np.ndarray]] = {}
    for key, local in full_groups.items():
        local = sorted(local, key=lambda r: str(r["colony"]))
        perf_groups[key] = (
            [str(r["colony"]) for r in local],
            np.asarray([float(r["state"]) for r in local], dtype=float),
        )

    by_panel: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, row in enumerate(panel):
        by_panel[(str(row["island"]), int(row["season"]))].append(idx)
    group_rows = {}
    for key, indices in by_panel.items():
        colonies, _ = perf_groups[key]
        positions = {name: idx for idx, name in enumerate(colonies)}
        group_rows[key] = (
            np.asarray(indices, dtype=int),
            np.asarray(
                [positions[str(panel[idx]["colony"])] for idx in indices],
                dtype=int,
            ),
        )

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
        for key in sorted(model["group_rows"]):
            _, values = model["perf_groups"][key]
            order = np.argsort(rng.random((batch, len(values))), axis=1)
            assigned = values[order]
            row_indices, source_positions = model["group_rows"][key]
            x[:, row_indices] = assigned[:, source_positions]
        ctx = x @ controls
        numerator = x @ y_resid
        denominator = np.sum(x * x, axis=1) - np.einsum(
            "bi,ij,bj->b", ctx, gram_inv, ctx, optimize=True
        )
        null[offset : offset + batch] = numerator / denominator
        offset += batch

    observed = float(model["observed"])
    p = float((1 + int(np.sum(null >= observed))) / (permutations + 1))
    return {
        "n_rows": len(panel),
        "n_predictor_seasons": len({int(r["season"]) for r in panel}),
        "beta_repro": observed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": p,
        "supported": bool(observed > 0 and p <= 0.05),
    }


def run_configuration(
    adults: list[dict[str, object]],
    nests: list[dict[str, object]],
    *,
    minimum_nests: int = 5,
    allowed_islands: tuple[str, ...] = ISLANDS,
    permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
) -> dict[str, object]:
    performance, perf_audit = colony_performance(
        nests,
        minimum_nests=minimum_nests,
        allowed_islands=allowed_islands,
    )
    panel = lag_panel(
        adults,
        performance,
        2,
        allowed_islands=allowed_islands,
    )
    info = {
        "n_matched_colony_seasons": len(panel),
        "n_unique_predictor_seasons": len({int(r["season"]) for r in panel}),
        "matched_islands": sorted({str(r["island"]) for r in panel}),
        "matched_colony_codes": sorted(
            {f"{r['island']}:{r['colony']}" for r in panel}
        ),
    }
    reasons = []
    if len(panel) < 30:
        reasons.append("fewer_than_30_matched_colony_seasons")
    if info["n_unique_predictor_seasons"] < 8:
        reasons.append("fewer_than_8_predictor_seasons")
    if reasons:
        return {
            "estimable": False,
            "failure_reasons": reasons,
            "performance_audit": perf_audit,
            "information_gate": info,
        }

    model = _prepare_model(panel, performance)
    test = permutation_test(model, permutations=permutations, seed=seed)
    return {
        "estimable": True,
        "performance_audit": perf_audit,
        "information_gate": info,
        "test": test,
    }


def observed_beta(
    adults: list[dict[str, object]],
    nests: list[dict[str, object]],
    allowed_islands: tuple[str, ...],
) -> float | None:
    performance, _ = colony_performance(
        nests, minimum_nests=5, allowed_islands=allowed_islands
    )
    panel = lag_panel(adults, performance, 2, allowed_islands=allowed_islands)
    if len(panel) < 30 or len({int(r["season"]) for r in panel}) < 8:
        return None
    return float(_prepare_model(panel, performance)["observed"])


def analyze(
    adult_path: str | Path,
    repro_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    primary_nests, source_audit = load_repro(repro_path, success_kind="creche")
    primary = run_configuration(
        adults,
        primary_nests,
        minimum_nests=5,
        permutations=permutations,
        seed=SEED,
    )

    if not primary["estimable"]:
        return {
            "schema_version": 1,
            "analysis_id": "mina-palmer-repro-performance-replication-v1",
            "contract_id": "mina-palmer-repro-performance-replication-v1",
            "source_counts": {
                "adult_rows": len(adults),
                "repro_source_audit": source_audit,
            },
            "primary": primary,
            "sensitivities": {},
            "decision": {
                "status": "STOP_insufficient_information",
                "independent_replication_supported": None,
                "posthoc_colony_crosswalk_allowed": False,
            },
        }

    min10 = run_configuration(
        adults,
        primary_nests,
        minimum_nests=10,
        permutations=permutations,
        seed=SEED + 1,
    )
    hatch_nests, hatch_audit = load_repro(repro_path, success_kind="hatch")
    hatch = run_configuration(
        adults,
        hatch_nests,
        minimum_nests=5,
        permutations=permutations,
        seed=SEED + 2,
    )
    no_lit = tuple(x for x in ISLANDS if x != "LIT")
    exclude_lit = run_configuration(
        adults,
        primary_nests,
        minimum_nests=5,
        allowed_islands=no_lit,
        permutations=permutations,
        seed=SEED + 3,
    )
    loo = {
        island: observed_beta(
            adults,
            primary_nests,
            tuple(x for x in ISLANDS if x != island),
        )
        for island in ISLANDS
    }

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-repro-performance-replication-v1",
        "contract_id": "mina-palmer-repro-performance-replication-v1",
        "source_counts": {
            "adult_rows": len(adults),
            "repro_source_audit": source_audit,
        },
        "primary": primary,
        "sensitivities": {
            "minimum_10_nests": min10,
            "hatch_success": {
                "source_audit": hatch_audit,
                "analysis": hatch,
            },
            "exclude_litchfield": exclude_lit,
            "leave_one_island_out_observed_beta": loo,
        },
        "decision": {
            "status": "estimated",
            "independent_replication_supported": bool(
                primary["test"]["supported"]
            ),
            "individual_movement_identified": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--repro", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=N_PERMUTATIONS)
    args = parser.parse_args()
    result = analyze(
        args.adult_census,
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
