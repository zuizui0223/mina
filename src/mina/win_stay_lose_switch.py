"""Mechanism diagnostics for Palmer win-stay / lose-switch redistribution."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .performance_redistribution_lags import (
    ISLANDS,
    lag_panel,
    load_adult_rows,
    load_chick_rows,
    performance_rows,
)

BOOTSTRAPS = 20_000
P3_PERMUTATIONS = 100_000
LOG_5_PERCENT = math.log(1.05)


def _adult_lookup(adults: list[dict[str, object]]) -> dict[tuple[str, str, int], float]:
    return {
        (str(r["island"]), str(r["colony"]), int(r["year"])): float(r["adult_pairs"])
        for r in adults
    }


def _island_totals(adults: list[dict[str, object]]) -> dict[tuple[str, int], float]:
    out: dict[tuple[str, int], float] = defaultdict(float)
    for row in adults:
        out[(str(row["island"]), int(row["year"]))] += float(row["adult_pairs"])
    return dict(out)


def _zscore(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    sd = float(np.std(values, ddof=1))
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("non-positive standard deviation")
    return (values - float(np.mean(values))) / sd


def build_p1_panel(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
) -> list[dict[str, object]]:
    lookup = _adult_lookup(adults)
    totals = _island_totals(adults)
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        grouped[(str(row["island"]), int(row["season"]))].append(row)

    out: list[dict[str, object]] = []
    for (island, season), local in sorted(grouped.items()):
        matched = []
        for row in local:
            key = (island, str(row["colony"]), season)
            if key not in lookup:
                continue
            matched.append((row, float(lookup[key])))
        if not matched:
            continue
        matched_total = float(sum(n for _, n in matched))
        island_total_t = totals.get((island, season))
        prior = totals.get((island, season + 1))
        future = totals.get((island, season + 2))
        if (
            matched_total <= 0
            or island_total_t is None
            or island_total_t <= 0
            or prior is None
            or future is None
        ):
            continue
        poor = float(
            sum(n for row, n in matched if float(row["state"]) < 0.0)
        )
        out.append(
            {
                "island": island,
                "season": season,
                "transition_year": season + 1,
                "poor_share": poor / matched_total,
                "matched_pairs": matched_total,
                "island_pairs_t": float(island_total_t),
                "matched_coverage": matched_total / float(island_total_t),
                "prior_total": float(prior),
                "island_growth": math.log1p(float(future)) - math.log1p(float(prior)),
            }
        )
    return out


def build_p2_performance(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
) -> list[dict[str, object]]:
    lookup = _adult_lookup(adults)
    island_season: dict[tuple[str, int], dict[str, float]] = defaultdict(
        lambda: {"pairs": 0.0, "chicks": 0.0}
    )
    for row in chicks:
        island = str(row["island"])
        season = int(row["season"])
        key = (island, str(row["colony"]), season)
        if key not in lookup:
            continue
        island_season[(island, season)]["pairs"] += float(lookup[key])
        island_season[(island, season)]["chicks"] += float(row["chicks"])

    by_season: dict[int, list[dict[str, object]]] = defaultdict(list)
    for (island, season), values in sorted(island_season.items()):
        if values["pairs"] <= 0:
            continue
        by_season[season].append(
            {
                "island": island,
                "season": season,
                "matched_pairs": float(values["pairs"]),
                "chicks": float(values["chicks"]),
            }
        )

    out: list[dict[str, object]] = []
    for season, local in sorted(by_season.items()):
        if len(local) < 3:
            continue
        pairs = np.asarray([float(r["matched_pairs"]) for r in local], dtype=float)
        chick = np.asarray([float(r["chicks"]) for r in local], dtype=float)
        pair_total = float(np.sum(pairs))
        chick_total = float(np.sum(chick))
        if pair_total <= 0 or chick_total <= 0:
            continue
        share = pairs / pair_total
        expected = chick_total * share
        residual = (chick - expected) / np.sqrt(
            np.maximum(expected * (1.0 - share), 1e-12)
        )
        sd = float(np.std(residual, ddof=1))
        if sd <= 0:
            continue
        state = (residual - float(np.mean(residual))) / sd
        for row, value in zip(local, state):
            out.append({**row, "island_state": float(value)})
    return out


def build_p2_panel(
    adults: list[dict[str, object]],
    island_performance: list[dict[str, object]],
) -> list[dict[str, object]]:
    totals = _island_totals(adults)
    out: list[dict[str, object]] = []
    for row in island_performance:
        island = str(row["island"])
        season = int(row["season"])
        prior = totals.get((island, season + 1))
        future = totals.get((island, season + 2))
        if prior is None or future is None:
            continue
        out.append(
            {
                **row,
                "transition_year": season + 1,
                "prior_total": float(prior),
                "island_growth": math.log1p(float(future)) - math.log1p(float(prior)),
            }
        )
    return out


def _design_controls(
    rows: list[dict[str, object]],
    *,
    numeric_controls: tuple[str, ...],
    fe_keys: tuple[str, ...],
) -> np.ndarray:
    cols: list[np.ndarray] = []
    n = len(rows)
    for key in numeric_controls:
        cols.append(np.asarray([float(r[key]) for r in rows], dtype=float))
    for key in fe_keys:
        levels = sorted({str(r[key]) for r in rows})
        for level in levels:
            cols.append(
                np.asarray([1.0 if str(r[key]) == level else 0.0 for r in rows])
            )
    if not cols:
        return np.zeros((n, 0), dtype=float)
    return np.column_stack(cols)


def _residualize(v: np.ndarray, controls: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    if controls.shape[1] == 0:
        return v.copy()
    coef = np.linalg.pinv(controls) @ v
    return v - controls @ coef


def fit_panel_slope(
    rows: list[dict[str, object]],
    *,
    x_key: str,
    y_key: str,
    numeric_controls: tuple[str, ...],
    fe_keys: tuple[str, ...],
) -> float:
    if len(rows) < 3:
        raise ValueError("too few rows")
    controls = _design_controls(
        rows, numeric_controls=numeric_controls, fe_keys=fe_keys
    )
    x = np.asarray([float(r[x_key]) for r in rows], dtype=float)
    y = np.asarray([float(r[y_key]) for r in rows], dtype=float)
    xr = _residualize(x, controls)
    yr = _residualize(y, controls)
    den = float(xr @ xr)
    if den <= 1e-12:
        raise ValueError("non-positive residual predictor variance")
    return float((xr @ yr) / den)


def _prepare_island_panel(
    rows: list[dict[str, object]],
    *,
    x_key: str,
) -> list[dict[str, object]]:
    if not rows:
        raise ValueError("empty island panel")
    x = np.asarray([float(r[x_key]) for r in rows], dtype=float)
    z = _zscore(x)
    prior = np.log1p(np.asarray([float(r["prior_total"]) for r in rows], dtype=float))
    zprior = _zscore(prior)
    return [
        {**row, "predictor_z": float(zz), "prior_z": float(zp)}
        for row, zz, zp in zip(rows, z, zprior)
    ]


def transition_year_bootstrap(
    rows: list[dict[str, object]],
    *,
    replicates: int,
    seed: int,
) -> dict[str, object]:
    years = sorted({int(r["transition_year"]) for r in rows})
    by_year: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_year[int(row["transition_year"])].append(row)
    observed = fit_panel_slope(
        rows,
        x_key="predictor_z",
        y_key="island_growth",
        numeric_controls=("prior_z",),
        fe_keys=("island", "transition_year"),
    )
    rng = np.random.default_rng(seed)
    boot = np.empty(replicates, dtype=float)
    for b in range(replicates):
        sampled = rng.choice(years, size=len(years), replace=True)
        local: list[dict[str, object]] = []
        for draw, year in enumerate(sampled):
            for row in by_year[int(year)]:
                local.append({**row, "boot_year": f"{draw}:{int(year)}"})
        boot[b] = fit_panel_slope(
            local,
            x_key="predictor_z",
            y_key="island_growth",
            numeric_controls=("prior_z",),
            fe_keys=("island", "boot_year"),
        )
    return {
        "n_rows": len(rows),
        "n_transition_years": len(years),
        "beta": observed,
        "bootstrap_replicates": int(replicates),
        "q05": float(np.quantile(boot, 0.05)),
        "q50": float(np.quantile(boot, 0.50)),
        "q95": float(np.quantile(boot, 0.95)),
    }


def p1_compensation_diagnostic(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
) -> dict[str, object]:
    lookup = _adult_lookup(adults)
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in performance:
        island = str(row["island"])
        season = int(row["season"])
        k0 = (island, str(row["colony"]), season + 1)
        k1 = (island, str(row["colony"]), season + 2)
        if k0 not in lookup or k1 not in lookup:
            continue
        grouped[(island, season)].append(
            {
                "state": float(row["state"]),
                "n0": float(lookup[k0]),
                "n1": float(lookup[k1]),
            }
        )
    ratios = []
    rows = []
    for (island, season), local in sorted(grouped.items()):
        poor_loss = sum(
            max(float(r["n0"]) - float(r["n1"]), 0.0)
            for r in local
            if float(r["state"]) < 0
        )
        good_gain = sum(
            max(float(r["n1"]) - float(r["n0"]), 0.0)
            for r in local
            if float(r["state"]) >= 0
        )
        ratio = good_gain / poor_loss if poor_loss > 0 else None
        if ratio is not None:
            ratios.append(float(ratio))
        rows.append(
            {
                "island": island,
                "season": season,
                "poor_loss": float(poor_loss),
                "good_gain": float(good_gain),
                "compensation_ratio": ratio,
            }
        )
    return {
        "n_island_seasons": len(rows),
        "n_with_positive_poor_loss": len(ratios),
        "median_compensation_ratio": (
            float(np.median(ratios)) if ratios else None
        ),
        "q25_compensation_ratio": (
            float(np.quantile(ratios, 0.25)) if ratios else None
        ),
        "q75_compensation_ratio": (
            float(np.quantile(ratios, 0.75)) if ratios else None
        ),
    }


def fit_hinge(panel: list[dict[str, object]]) -> dict[str, float]:
    if len(panel) < 4:
        raise ValueError("too few hinge rows")
    controls = _design_controls(
        panel,
        numeric_controls=("zsize",),
        fe_keys=("island_colony",),
    ) if "island_colony" in panel[0] else _design_controls(
        [
            {**r, "island_colony": f"{r['island']}:{r['colony']}"}
            for r in panel
        ],
        numeric_controls=("zsize",),
        fe_keys=("island_colony",),
    )
    state = np.asarray([float(r["state"]) for r in panel], dtype=float)
    y = np.asarray([float(r["relative_growth"]) for r in panel], dtype=float)
    x = np.column_stack([np.minimum(state, 0.0), np.maximum(state, 0.0)])
    xr = np.column_stack(
        [_residualize(x[:, j], controls) for j in range(2)]
    )
    yr = _residualize(y, controls)
    beta = np.linalg.pinv(xr) @ yr
    loss = float(beta[0])
    win = float(beta[1])
    return {
        "beta_loss": loss,
        "beta_win": win,
        "delta": loss - win,
    }


def _p3_prepare(panel: list[dict[str, object]]) -> dict[str, object]:
    rows = [
        {**r, "island_colony": f"{r['island']}:{r['colony']}"}
        for r in panel
    ]
    controls = _design_controls(
        rows, numeric_controls=("zsize",), fe_keys=("island_colony",)
    )
    state = np.asarray([float(r["state"]) for r in rows], dtype=float)
    y = np.asarray([float(r["relative_growth"]) for r in rows], dtype=float)

    null_design = np.column_stack([state, controls])
    null_coef = np.linalg.pinv(null_design) @ y
    fitted = null_design @ null_coef
    residual = y - fitted

    hinge = np.column_stack([np.minimum(state, 0.0), np.maximum(state, 0.0)])
    hinge_r = np.column_stack(
        [_residualize(hinge[:, j], controls) for j in range(2)]
    )
    h_inv = np.linalg.pinv(hinge_r.T @ hinge_r)
    observed_beta = h_inv @ (hinge_r.T @ y)

    groups: dict[tuple[str, int], list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        groups[(str(row["island"]), int(row["season"]))].append(idx)

    return {
        "rows": rows,
        "fitted_null": fitted,
        "residual_null": residual,
        "hinge_r": hinge_r,
        "hinge_inv": h_inv,
        "groups": groups,
        "observed_beta": observed_beta,
    }


def p3_freedman_lane(
    panel: list[dict[str, object]],
    *,
    permutations: int,
    seed: int,
    batch_size: int = 1000,
) -> dict[str, object]:
    model = _p3_prepare(panel)
    observed = np.asarray(model["observed_beta"], dtype=float)
    observed_delta = float(observed[0] - observed[1])
    residual = np.asarray(model["residual_null"], dtype=float)
    fitted = np.asarray(model["fitted_null"], dtype=float)
    hinge_r = np.asarray(model["hinge_r"], dtype=float)
    h_inv = np.asarray(model["hinge_inv"], dtype=float)
    groups = model["groups"]

    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=float)
    offset = 0
    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        e = np.empty((batch, len(panel)), dtype=float)
        for indices in groups.values():
            idx = np.asarray(indices, dtype=int)
            values = residual[idx]
            order = np.argsort(rng.random((batch, len(idx))), axis=1)
            e[:, idx] = values[order]
        ystar = fitted[None, :] + e
        beta = (ystar @ hinge_r) @ h_inv
        null[offset : offset + batch] = beta[:, 0] - beta[:, 1]
        offset += batch

    p = float((1 + int(np.sum(null >= observed_delta))) / (permutations + 1))
    loss = float(observed[0])
    win = float(observed[1])
    return {
        "n_rows": len(panel),
        "beta_loss": loss,
        "beta_win": win,
        "delta": observed_delta,
        "permutations": int(permutations),
        "seed": int(seed),
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": p,
        "supported": bool(observed_delta > 0 and loss > 0 and p <= 0.05),
    }


def _p1_analysis(
    adults: list[dict[str, object]],
    performance: list[dict[str, object]],
    *,
    coverage_min: float | None = None,
) -> dict[str, object]:
    raw = build_p1_panel(adults, performance)
    if coverage_min is not None:
        raw = [r for r in raw if float(r["matched_coverage"]) >= coverage_min]
    rows = _prepare_island_panel(raw, x_key="poor_share")
    boot = transition_year_bootstrap(
        rows, replicates=BOOTSTRAPS, seed=20261001 + (1 if coverage_min else 0)
    )
    if boot["q05"] > -LOG_5_PERCENT:
        decision = "compatible_with_within_island_redistribution"
    elif boot["q95"] < -LOG_5_PERCENT:
        decision = "meaningful_loss_channel_supported"
    else:
        decision = "inconclusive"
    return {
        **boot,
        "margin": LOG_5_PERCENT,
        "decision": decision,
        "mean_matched_coverage": float(
            np.mean([float(r["matched_coverage"]) for r in rows])
        ),
        "minimum_matched_coverage": float(
            np.min([float(r["matched_coverage"]) for r in rows])
        ),
    }


def _p2_analysis(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
) -> dict[str, object]:
    perf = build_p2_performance(adults, chicks)
    raw = build_p2_panel(adults, perf)
    # Z_I,t is already standardized within season; retain that scale.
    prior = np.log1p(np.asarray([float(r["prior_total"]) for r in raw], dtype=float))
    zprior = _zscore(prior)
    rows = [
        {
            **row,
            "predictor_z": float(row["island_state"]),
            "prior_z": float(zp),
        }
        for row, zp in zip(raw, zprior)
    ]
    boot = transition_year_bootstrap(
        rows, replicates=BOOTSTRAPS, seed=20261002
    )
    if boot["q95"] < LOG_5_PERCENT:
        decision = "island_boundary_compatible"
    elif boot["q05"] > LOG_5_PERCENT:
        decision = "meaningful_cross_island_tracking_supported"
    else:
        decision = "inconclusive"
    return {
        **boot,
        "margin": LOG_5_PERCENT,
        "decision": decision,
        "n_island_performance_rows": len(perf),
        "n_performance_seasons": len({int(r["season"]) for r in perf}),
    }


def _p3_configuration(
    adults: list[dict[str, object]],
    chicks: list[dict[str, object]],
    *,
    allowed_islands: tuple[str, ...] = ISLANDS,
    metric: str = "pearson",
    minimum_prior_size: float = 0.0,
    seed: int,
) -> dict[str, object]:
    perf = performance_rows(
        adults, chicks, allowed_islands=allowed_islands, metric=metric
    )
    panel = lag_panel(
        adults,
        perf,
        2,
        allowed_islands=allowed_islands,
        minimum_prior_size=minimum_prior_size,
    )
    return p3_freedman_lane(
        panel, permutations=P3_PERMUTATIONS, seed=seed
    )


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
) -> dict[str, object]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)
    perf = performance_rows(adults, chicks)

    p1 = _p1_analysis(adults, perf)
    p1_cov = _p1_analysis(adults, perf, coverage_min=0.80)
    p2 = _p2_analysis(adults, chicks)

    p3 = _p3_configuration(
        adults, chicks, seed=20261003
    )
    p3_no_lit = _p3_configuration(
        adults,
        chicks,
        allowed_islands=tuple(x for x in ISLANDS if x != "LIT"),
        seed=20261004,
    )
    p3_size = _p3_configuration(
        adults,
        chicks,
        minimum_prior_size=2.0,
        seed=20261005,
    )
    p3_log = _p3_configuration(
        adults,
        chicks,
        metric="logratio",
        seed=20261006,
    )
    loo = {}
    for island in ISLANDS:
        allowed = tuple(x for x in ISLANDS if x != island)
        perf_loo = performance_rows(adults, chicks, allowed_islands=allowed)
        panel_loo = lag_panel(
            adults, perf_loo, 2, allowed_islands=allowed
        )
        loo[island] = fit_hinge(panel_loo)

    strongest = bool(
        p1["decision"] == "compatible_with_within_island_redistribution"
        and p2["decision"] == "island_boundary_compatible"
        and p3["supported"]
    )
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-win-stay-lose-switch-v1",
        "contract_id": "mina-palmer-win-stay-lose-switch-v1",
        "source_counts": {
            "adult_rows": len(adults),
            "usable_chick_rows": len(chicks),
            "performance_rows": len(perf),
        },
        "P1": {
            "primary": p1,
            "coverage_ge_0_80": p1_cov,
            "compensation_diagnostic": p1_compensation_diagnostic(adults, perf),
        },
        "P2": p2,
        "P3": {
            "primary": p3,
            "sensitivities": {
                "exclude_litchfield": p3_no_lit,
                "minimum_prior_size_2": p3_size,
                "alternate_logratio_metric": p3_log,
                "leave_one_island_out_observed": loo,
            },
        },
        "decision": {
            "strongest_joint_pattern_supported": strongest,
            "P1": p1["decision"],
            "P2": p2["decision"],
            "P3_supported": bool(p3["supported"]),
        },
        "interpretation_boundary": {
            "individual_movement_proven": False,
            "public_information_proven": False,
            "mortality_or_nonbreeding_excluded": False,
            "independent_confirmation": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = analyze(args.adult_census, args.chicks)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
