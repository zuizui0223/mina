"""Lagged reproductive-performance redistribution analysis for Palmer Adelie colonies."""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

ISLANDS = ("CHR", "COR", "HUM", "LIT", "TOR")
N_PERMUTATIONS = 100_000
SEED_BASE = 20260930


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _study_season(study: str) -> int:
    match = re.fullmatch(r"PAL(\d\d)(\d\d)", study.strip())
    if not match:
        raise ValueError(f"unparseable PAL study season: {study!r}")
    yy = int(match.group(1))
    zz = int(match.group(2))
    year = 1900 + yy if yy >= 90 else 2000 + yy
    if zz != (year + 1) % 100:
        raise ValueError(f"non-consecutive PAL study season: {study!r}")
    return year


def load_adult_rows(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out: list[dict[str, object]] = []
    seen: set[tuple[str, str, int]] = set()
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS or not _finite(row.get("num_breeding_pairs")):
            continue
        count = float(row["num_breeding_pairs"])
        if count < 0:
            raise ValueError("negative adult breeding-pair count")
        time = str(row.get("time", "")).strip()
        if len(time) < 4 or not time[:4].isdigit():
            continue
        year = int(time[:4])
        colony = str(row.get("colony_code", "")).strip()
        key = (island, colony, year)
        if key in seen:
            raise ValueError(f"duplicate adult census key: {key!r}")
        seen.add(key)
        out.append(
            {"island": island, "colony": colony, "year": year, "adult_pairs": count}
        )
    if not out:
        raise ValueError("no adult census rows parsed")
    return out


def load_chick_rows(path: str | Path) -> list[dict[str, object]]:
    """Use the earlier outcome-blind PALYYZZ season-key contract."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out: list[dict[str, object]] = []
    seen: set[tuple[str, str, int]] = set()
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        if not _finite(row.get("num_breeding_pairs")) or not _finite(
            row.get("num_chicks")
        ):
            continue
        denominator = float(row["num_breeding_pairs"])
        chicks = float(row["num_chicks"])
        if denominator <= 0 or chicks < 0:
            continue
        season = _study_season(str(row.get("study_name", "")).strip())
        colony = str(row.get("colony_code", "")).strip()
        key = (island, colony, season)
        if key in seen:
            raise ValueError(f"duplicate usable chick row: {key!r}")
        seen.add(key)
        out.append(
            {
                "island": island,
                "colony": colony,
                "season": season,
                "chicks": chicks,
                "chick_denominator": denominator,
            }
        )
    if not out:
        raise ValueError("no usable chick rows parsed")
    return out


def _adult_lookup(
    rows: list[dict[str, object]],
) -> dict[tuple[str, str, int], float]:
    return {
        (str(r["island"]), str(r["colony"]), int(r["year"])): float(
            r["adult_pairs"]
        )
        for r in rows
    }


def performance_rows(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    metric: str = "pearson",
    minimum_total_chicks: float = 0.0,
) -> list[dict[str, object]]:
    lookup = _adult_lookup(adults)
    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in chicks:
        island = str(row["island"])
        if island not in allowed_islands:
            continue
        key = (island, str(row["colony"]), int(row["season"]))
        if key not in lookup:
            continue
        groups[(island, int(row["season"]))].append(
            {
                "colony": str(row["colony"]),
                "adult_pairs": lookup[key],
                "chicks": float(row["chicks"]),
            }
        )

    out: list[dict[str, object]] = []
    for (island, season), local in sorted(groups.items()):
        if len(local) < 3:
            continue
        adults_arr = np.asarray(
            [float(r["adult_pairs"]) for r in local], dtype=float
        )
        chicks_arr = np.asarray([float(r["chicks"]) for r in local], dtype=float)
        adult_total = float(np.sum(adults_arr))
        chick_total = float(np.sum(chicks_arr))
        if (
            adult_total <= 0
            or chick_total <= 0
            or chick_total < minimum_total_chicks
        ):
            continue
        share = adults_arr / adult_total
        expected = chick_total * share
        if metric == "pearson":
            value = (chicks_arr - expected) / np.sqrt(
                np.maximum(expected * (1.0 - share), 1e-12)
            )
        elif metric == "logratio":
            value = np.log((chicks_arr + 0.5) / (expected + 0.5))
        else:
            raise ValueError(metric)
        sd = float(np.std(value, ddof=1))
        if sd <= 0:
            continue
        score = (value - float(np.mean(value))) / sd
        for row, state in zip(local, score):
            out.append(
                {
                    "island": island,
                    "colony": str(row["colony"]),
                    "season": season,
                    "state": float(state),
                    "total_chicks": chick_total,
                }
            )
    if not out:
        raise ValueError("no eligible performance states")
    return out


def lag_panel(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    lag: int,
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    minimum_prior_size: float = 0.0,
) -> list[dict[str, object]]:
    lookup = _adult_lookup(adults)
    raw: list[dict[str, object]] = []
    for row in performance:
        island = str(row["island"])
        if island not in allowed_islands:
            continue
        season = int(row["season"])
        start = season + lag - 1
        k0 = (island, str(row["colony"]), start)
        k1 = (island, str(row["colony"]), start + 1)
        if k0 not in lookup or k1 not in lookup:
            continue
        n0 = lookup[k0]
        n1 = lookup[k1]
        if n0 < minimum_prior_size:
            continue
        raw.append(
            {
                "island": island,
                "colony": str(row["colony"]),
                "season": season,
                "start_year": start,
                "state": float(row["state"]),
                "n0": n0,
                "growth": math.log1p(n1) - math.log1p(n0),
            }
        )

    groups: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in raw:
        groups[(str(row["island"]), int(row["start_year"]))].append(row)
    out: list[dict[str, object]] = []
    for _, local in sorted(groups.items()):
        if len(local) < 2:
            continue
        growth = np.asarray([float(r["growth"]) for r in local], dtype=float)
        size = np.log1p(
            np.asarray([float(r["n0"]) for r in local], dtype=float)
        )
        size_sd = float(np.std(size, ddof=1))
        zsize = (
            (size - float(np.mean(size))) / size_sd
            if size_sd > 0
            else np.zeros_like(size)
        )
        relative = growth - float(np.mean(growth))
        for row, rel, z in zip(local, relative, zsize):
            out.append(
                {**row, "relative_growth": float(rel), "zsize": float(z)}
            )
    return out


def _prepare_model(
    panel: list[dict[str, object]],
    performance: list[dict[str, object]],
) -> dict[str, object]:
    colonies = sorted({f"{r['island']}:{r['colony']}" for r in panel})
    cmap = {name: idx for idx, name in enumerate(colonies)}
    n = len(panel)
    fe = np.zeros((n, len(colonies)), dtype=float)
    state = np.empty(n, dtype=float)
    zsize = np.empty(n, dtype=float)
    y = np.empty(n, dtype=float)
    for idx, row in enumerate(panel):
        fe[idx, cmap[f"{row['island']}:{row['colony']}"]] = 1.0
        state[idx] = float(row["state"])
        zsize[idx] = float(row["zsize"])
        y[idx] = float(row["relative_growth"])
    controls = np.column_stack([zsize, fe])
    inv = np.linalg.inv(controls.T @ controls)
    y_residual = y - controls @ (inv @ (controls.T @ y))
    ztx = controls.T @ state
    denominator = float(state @ state - ztx @ (inv @ ztx))
    observed = float((state @ y_residual) / denominator)

    by_perf: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        by_perf[(str(row["island"]), int(row["season"]))].append(row)
    perf_groups: dict[tuple[str, int], tuple[list[str], np.ndarray]] = {}
    for key, local in by_perf.items():
        local = sorted(local, key=lambda r: str(r["colony"]))
        perf_groups[key] = (
            [str(r["colony"]) for r in local],
            np.asarray([float(r["state"]) for r in local], dtype=float),
        )

    group_rows: dict[tuple[str, int], tuple[np.ndarray, np.ndarray]] = {}
    by_panel: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, row in enumerate(panel):
        by_panel[(str(row["island"]), int(row["season"]))].append(idx)
    for key, indices in by_panel.items():
        colonies_full, _ = perf_groups[key]
        positions = {name: idx for idx, name in enumerate(colonies_full)}
        row_indices = np.asarray(indices, dtype=int)
        source_positions = np.asarray(
            [positions[str(panel[idx]["colony"])] for idx in indices], dtype=int
        )
        group_rows[key] = (row_indices, source_positions)

    return {
        "panel": panel,
        "controls": controls,
        "inv": inv,
        "y_residual": y_residual,
        "observed": observed,
        "group_rows": group_rows,
    }


def _beta_from_batch(
    x: np.ndarray, model: dict[str, object]
) -> np.ndarray:
    controls = np.asarray(model["controls"], dtype=float)
    inv = np.asarray(model["inv"], dtype=float)
    y_residual = np.asarray(model["y_residual"], dtype=float)
    ztx = x @ controls
    numerator = x @ y_residual
    denominator = np.sum(x * x, axis=1) - np.einsum(
        "bi,ij,bj->b", ztx, inv, ztx, optimize=True
    )
    return numerator / denominator


def permutation_lag_test(
    models: dict[int, dict[str, object]],
    performance: list[dict[str, object]],
    *,
    permutations: int = N_PERMUTATIONS,
    seed: int = SEED_BASE,
    batch_size: int = 1000,
) -> dict[str, object]:
    by_perf: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        by_perf[(str(row["island"]), int(row["season"]))].append(row)
    perf_groups: dict[tuple[str, int], tuple[list[str], np.ndarray]] = {}
    for key, local in by_perf.items():
        local = sorted(local, key=lambda r: str(r["colony"]))
        perf_groups[key] = (
            [str(r["colony"]) for r in local],
            np.asarray([float(r["state"]) for r in local], dtype=float),
        )

    rng = np.random.default_rng(seed)
    null = {
        lag: np.empty(permutations, dtype=float) for lag in sorted(models)
    }
    keys = sorted(perf_groups)
    offset = 0
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        x = {
            lag: np.empty((batch, len(model["panel"])), dtype=float)
            for lag, model in models.items()
        }
        for key in keys:
            _, values = perf_groups[key]
            order = np.argsort(rng.random((batch, len(values))), axis=1)
            assigned = values[order]
            for lag, model in models.items():
                info = model["group_rows"].get(key)
                if info is None:
                    continue
                row_indices, source_positions = info
                x[lag][:, row_indices] = assigned[:, source_positions]
        for lag, model in models.items():
            null[lag][offset : offset + batch] = _beta_from_batch(
                x[lag], model
            )
        offset += batch

    lag_results: dict[str, object] = {}
    observed = {
        lag: float(model["observed"]) for lag, model in models.items()
    }
    for lag in sorted(models):
        values = null[lag]
        obs = observed[lag]
        p = float(
            (1 + int(np.sum(values >= obs))) / (permutations + 1)
        )
        lag_results[str(lag)] = {
            "n_rows": len(models[lag]["panel"]),
            "beta": obs,
            "null_mean": float(np.mean(values)),
            "null_q025": float(np.quantile(values, 0.025)),
            "null_q975": float(np.quantile(values, 0.975)),
            "one_sided_upper_p": p,
        }

    recruit = (
        0.5 * (observed[4] + observed[5])
        - 0.5 * (observed[2] + observed[3])
    )
    recruit_null = (
        0.5 * (null[4] + null[5])
        - 0.5 * (null[2] + null[3])
    )
    recruit_p = float(
        (1 + int(np.sum(recruit_null >= recruit))) / (permutations + 1)
    )
    return {
        "permutations": permutations,
        "seed": seed,
        "lags": lag_results,
        "recruitment_echo": {
            "contrast": float(recruit),
            "null_mean": float(np.mean(recruit_null)),
            "null_q025": float(np.quantile(recruit_null, 0.025)),
            "null_q975": float(np.quantile(recruit_null, 0.975)),
            "one_sided_upper_p": recruit_p,
            "supported": bool(
                recruit > 0
                and recruit_p <= 0.05
                and (observed[4] > 0 or observed[5] > 0)
            ),
        },
    }


def _run_configuration(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    metric: str = "pearson",
    minimum_total_chicks: float = 0.0,
    minimum_prior_size: float = 0.0,
    permutations: int = N_PERMUTATIONS,
    seed: int = SEED_BASE,
) -> dict[str, object]:
    perf = performance_rows(
        adults,
        chicks,
        allowed_islands=allowed_islands,
        metric=metric,
        minimum_total_chicks=minimum_total_chicks,
    )
    models: dict[int, dict[str, object]] = {}
    for lag in range(1, 6):
        panel = lag_panel(
            adults,
            perf,
            lag,
            allowed_islands=allowed_islands,
            minimum_prior_size=minimum_prior_size,
        )
        models[lag] = _prepare_model(panel, perf)
    result = permutation_lag_test(
        models, perf, permutations=permutations, seed=seed
    )
    result["n_performance_rows"] = len(perf)
    result["n_performance_island_seasons"] = len(
        {(str(r["island"]), int(r["season"])) for r in perf}
    )
    return result


def _observed_only(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    allowed_islands: tuple[str, ...],
) -> dict[str, float | int]:
    perf = performance_rows(adults, chicks, allowed_islands=allowed_islands)
    beta: dict[int, float] = {}
    n2 = 0
    for lag in range(1, 6):
        panel = lag_panel(
            adults, perf, lag, allowed_islands=allowed_islands
        )
        model = _prepare_model(panel, perf)
        beta[lag] = float(model["observed"])
        if lag == 2:
            n2 = len(panel)
    recruit = 0.5 * (beta[4] + beta[5]) - 0.5 * (beta[2] + beta[3])
    return {
        "beta_1": beta[1],
        "beta_2": beta[2],
        "beta_3": beta[3],
        "beta_4": beta[4],
        "beta_5": beta[5],
        "recruitment_echo_contrast": recruit,
        "n_lag2_rows": n2,
    }


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    *,
    permutations: int = N_PERMUTATIONS,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)
    primary = _run_configuration(
        adults, chicks, permutations=permutations, seed=SEED_BASE
    )
    no_lit_islands = tuple(x for x in ISLANDS if x != "LIT")
    no_lit = _run_configuration(
        adults,
        chicks,
        allowed_islands=no_lit_islands,
        permutations=permutations,
        seed=SEED_BASE + 1,
    )
    prior_ge2 = _run_configuration(
        adults,
        chicks,
        minimum_prior_size=2.0,
        permutations=permutations,
        seed=SEED_BASE + 2,
    )
    chick10 = _run_configuration(
        adults,
        chicks,
        minimum_total_chicks=10.0,
        permutations=permutations,
        seed=SEED_BASE + 3,
    )
    logratio = _run_configuration(
        adults,
        chicks,
        metric="logratio",
        permutations=permutations,
        seed=SEED_BASE + 4,
    )
    loo = {
        island: _observed_only(
            adults, chicks, tuple(x for x in ISLANDS if x != island)
        )
        for island in ISLANDS
    }
    beta2 = float(primary["lags"]["2"]["beta"])
    p2 = float(primary["lags"]["2"]["one_sided_upper_p"])
    support = beta2 > 0 and p2 <= 0.05
    return {
        "schema_version": 2,
        "analysis_id": "mina-palmer-performance-redistribution-lags-v2",
        "contract_id": "mina-palmer-performance-redistribution-lags-v2",
        "provenance_status": "post_exposure_provenance_repair_validation",
        "source_counts": {
            "adult_rows": len(adults),
            "usable_chick_rows": len(chicks),
        },
        "primary": primary,
        "sensitivities": {
            "exclude_litchfield": no_lit,
            "minimum_prior_size_2": prior_ge2,
            "minimum_total_chicks_10": chick10,
            "logratio_success_metric": logratio,
            "leave_one_island_out_observed": loo,
        },
        "decision": {
            "bias_resistant_lag2_supported_under_fixed_specification": support,
            "delayed_recruitment_echo_supported": bool(
                primary["recruitment_echo"]["supported"]
            ),
            "confirmatory_preregistration_claim_allowed": False,
        },
        "interpretation_boundary": {
            "individual_public_information_use_proven": False,
            "dynamic_state_adds_temporal_information": support,
            "four_to_five_year_recruitment_echo_supported": bool(
                primary["recruitment_echo"]["supported"]
            ),
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
        args.adult_census, args.chicks, permutations=args.permutations
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
