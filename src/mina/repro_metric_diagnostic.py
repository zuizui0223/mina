"""Post-result detectability and decomposition diagnostic for Palmer REPRO."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .performance_redistribution_lags import (
    load_adult_rows,
    load_chick_rows,
    performance_rows,
)
from .repro_redistribution import (
    load_repro,
    repro_states,
    redistribution_panel,
)

BENCHMARK_BETA = 0.10402777305744605
EFFECT_GRID = (0.03, 0.06, BENCHMARK_BETA, 0.15)
SIMULATIONS = 2000
SIM_PERMUTATIONS = 9999
BOOTSTRAPS = 5000
DECOMP_PERMUTATIONS = 100000


def _key(row: dict[str, object]) -> tuple[str, int, str]:
    return str(row["island"]), int(row["season"]), str(row["colony"])


def _common_panel(
    adult_path: str | Path,
    chick_path: str | Path,
    repro_path: str | Path,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    adults = load_adult_rows(adult_path)
    chicks = load_chick_rows(chick_path)
    repro, _ = load_repro(repro_path)

    nest_states, _ = repro_states(repro)
    panel, _ = redistribution_panel(adults, nest_states, lag=1)
    chick_states = {_key(r): float(r["state"]) for r in performance_rows(adults, chicks)}

    common: list[dict[str, object]] = []
    for row in panel:
        key = _key(row)
        if key in chick_states:
            common.append({**row, "chick_state": chick_states[key]})
    common.sort(key=lambda r: (str(r["island"]), int(r["season"]), str(r["colony"])))
    return common, repro, adults


def _controls(rows: list[dict[str, object]]) -> np.ndarray:
    levels = sorted({f"{r['island']}:{r['colony']}" for r in rows})
    lookup = {level: i for i, level in enumerate(levels)}
    fe = np.zeros((len(rows), len(levels)), dtype=float)
    for i, row in enumerate(rows):
        fe[i, lookup[f"{row['island']}:{row['colony']}"]] = 1.0
    return np.column_stack(
        [np.asarray([float(r["z_prior_size"]) for r in rows], dtype=float), fe]
    )


def _residualized_fit(
    rows: list[dict[str, object]],
    x: np.ndarray,
) -> dict[str, object]:
    y = np.asarray([float(r["relative_growth"]) for r in rows], dtype=float)
    controls = _controls(rows)
    gram_inv = np.linalg.pinv(controls.T @ controls)
    residual_maker = np.eye(len(rows)) - controls @ gram_inv @ controls.T
    yr = residual_maker @ y
    xr = residual_maker @ x
    denom = float(xr @ xr)
    beta = float(xr @ yr / denom)
    resid = yr - beta * xr
    rank = int(np.linalg.matrix_rank(np.column_stack([x, controls])))
    df_resid = len(rows) - rank
    sigma = float(np.sqrt((resid @ resid) / df_resid))
    se = float(sigma / np.sqrt(denom))
    return {
        "beta": beta,
        "y_resid": yr,
        "x_resid": xr,
        "controls": controls,
        "gram_inv": gram_inv,
        "residual_maker": residual_maker,
        "sigma": sigma,
        "se": se,
        "df_resid": df_resid,
    }


def _groups(rows: list[dict[str, object]]) -> list[np.ndarray]:
    grouped: dict[tuple[str, int], list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        grouped[(str(row["island"]), int(row["season"]))].append(i)
    return [np.asarray(v, dtype=int) for _, v in sorted(grouped.items())]


def _permuted_residualized_predictors(
    rows: list[dict[str, object]],
    x: np.ndarray,
    controls: np.ndarray,
    gram_inv: np.ndarray,
    *,
    permutations: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    xp = np.empty((permutations, len(rows)), dtype=float)
    for indices in _groups(rows):
        base = x[indices]
        order = np.argsort(rng.random((permutations, len(indices))), axis=1)
        xp[:, indices] = base[order]
    xr = xp - (xp @ controls) @ gram_inv @ controls.T
    denom = np.sum(xr * xr, axis=1)
    return xr, denom


def _permutation_result(
    rows: list[dict[str, object]],
    x: np.ndarray,
    *,
    permutations: int,
    seed: int,
) -> dict[str, object]:
    fit = _residualized_fit(rows, x)
    xr_perm, denom = _permuted_residualized_predictors(
        rows,
        x,
        np.asarray(fit["controls"]),
        np.asarray(fit["gram_inv"]),
        permutations=permutations,
        seed=seed,
    )
    null = (xr_perm @ np.asarray(fit["y_resid"])) / denom
    beta = float(fit["beta"])
    return {
        "n_rows": len(rows),
        "n_predictor_seasons": len(_groups(rows)),
        "beta": beta,
        "null_q05": float(np.quantile(null, 0.05)),
        "null_q95": float(np.quantile(null, 0.95)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": float(
            (1 + int(np.sum(null >= beta))) / (permutations + 1)
        ),
    }


def _detectability(
    rows: list[dict[str, object]],
    *,
    simulations: int = SIMULATIONS,
    permutations: int = SIM_PERMUTATIONS,
    seed: int = 20261001,
) -> dict[str, object]:
    x = np.asarray([float(r["state"]) for r in rows], dtype=float)
    fit = _residualized_fit(rows, x)
    controls = np.asarray(fit["controls"])
    gram_inv = np.asarray(fit["gram_inv"])
    residual_maker = np.asarray(fit["residual_maker"])
    xr = np.asarray(fit["x_resid"])
    xr_denom = float(xr @ xr)

    xr_perm, perm_denom = _permuted_residualized_predictors(
        rows,
        x,
        controls,
        gram_inv,
        permutations=permutations,
        seed=seed + 1,
    )
    rng = np.random.default_rng(seed + 2)
    sigma = float(fit["sigma"])

    power: dict[str, object] = {}
    batch_size = 100
    for effect in EFFECT_GRID:
        detected = 0
        beta_hats: list[float] = []
        done = 0
        while done < simulations:
            batch = min(batch_size, simulations - done)
            noise = rng.normal(0.0, sigma, size=(batch, len(rows)))
            noise = noise @ residual_maker.T
            y = effect * xr[None, :] + noise
            beta_hat = (y @ xr) / xr_denom
            null = (y @ xr_perm.T) / perm_denom[None, :]
            p = (1.0 + np.sum(null >= beta_hat[:, None], axis=1)) / (
                permutations + 1.0
            )
            detected += int(np.sum(p <= 0.05))
            beta_hats.extend(float(v) for v in beta_hat)
            done += batch
        power[f"{effect:.15g}"] = {
            "effect": float(effect),
            "detection_fraction": float(detected / simulations),
            "mean_beta_hat": float(np.mean(beta_hats)),
        }

    observed_null = _permutation_result(
        rows,
        x,
        permutations=100000,
        seed=seed + 3,
    )
    observed_null["benchmark_beta_tail_probability"] = float(
        # Re-use a fresh fixed null sample for this descriptive threshold.
        # The exact tail is recomputed below from the same permutation machinery.
        0.0
    )
    xr100k, den100k = _permuted_residualized_predictors(
        rows,
        x,
        controls,
        gram_inv,
        permutations=100000,
        seed=seed + 4,
    )
    null100k = (xr100k @ np.asarray(fit["y_resid"])) / den100k
    observed_null["benchmark_beta_tail_probability"] = float(
        (1 + int(np.sum(null100k >= BENCHMARK_BETA))) / 100001
    )
    return {
        "benchmark_beta": BENCHMARK_BETA,
        "observed_repro_fit": {
            "beta": float(fit["beta"]),
            "residual_sd": sigma,
            "coefficient_se_gaussian_reference": float(fit["se"]),
            "df_resid": int(fit["df_resid"]),
        },
        "common_panel_permutation_calibration": observed_null,
        "simulation": {
            "simulations_per_effect": simulations,
            "permutations_per_simulation": permutations,
            "power": power,
        },
    }


def _bootstrap_stability(
    common: list[dict[str, object]],
    repro_rows: list[dict[str, object]],
    *,
    replicates: int = BOOTSTRAPS,
    seed: int = 20261002,
) -> dict[str, object]:
    keys = {_key(r) for r in common}
    nests: dict[tuple[str, int, str], np.ndarray] = {}
    for key in keys:
        vals = [
            float(r["creched_chicks"])
            for r in repro_rows
            if _key(r) == key
        ]
        nests[key] = np.asarray(vals, dtype=float)

    season_groups: dict[tuple[str, int], list[tuple[str, int, str]]] = defaultdict(list)
    for row in common:
        season_groups[(str(row["island"]), int(row["season"]))].append(_key(row))

    original = {_key(r): float(r["state"]) for r in common}
    order = [_key(r) for r in common]
    rng = np.random.default_rng(seed)
    correlations: list[float] = []
    undefined = 0

    for _ in range(replicates):
        zvals: dict[tuple[str, int, str], float] = {}
        valid = True
        for _, group_keys in sorted(season_groups.items()):
            means = []
            for key in group_keys:
                values = nests[key]
                sample = values[rng.integers(0, len(values), size=len(values))]
                means.append(float(np.mean(sample)))
            means_arr = np.asarray(means, dtype=float)
            sd = float(np.std(means_arr, ddof=1))
            if sd <= 0:
                valid = False
                break
            z = (means_arr - float(np.mean(means_arr))) / sd
            for key, value in zip(group_keys, z):
                zvals[key] = float(value)
        if not valid:
            undefined += 1
            continue
        x = np.asarray([original[k] for k in order], dtype=float)
        y = np.asarray([zvals[k] for k in order], dtype=float)
        correlations.append(float(np.corrcoef(x, y)[0, 1]))

    arr = np.asarray(correlations, dtype=float)
    return {
        "bootstrap_replicates": replicates,
        "defined_replicates": len(correlations),
        "undefined_replicates": undefined,
        "defined_fraction": float(len(correlations) / replicates),
        "correlation_with_original_state": {
            "median": float(np.median(arr)),
            "mean": float(np.mean(arr)),
            "q025": float(np.quantile(arr, 0.025)),
            "q975": float(np.quantile(arr, 0.975)),
        },
        "nest_sample_size": {
            "median": float(np.median([len(nests[k]) for k in order])),
            "minimum": int(min(len(nests[k]) for k in order)),
            "maximum": int(max(len(nests[k]) for k in order)),
        },
    }


def _successful_brood_state(
    common: list[dict[str, object]],
    repro_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    common_lookup = {_key(r): r for r in common}
    grouped: dict[tuple[str, int, str], list[float]] = defaultdict(list)
    for row in repro_rows:
        key = _key(row)
        if key in common_lookup and float(row["creched_chicks"]) >= 1.0:
            grouped[key].append(float(row["creched_chicks"]))

    raw: dict[tuple[str, int, str], float] = {
        key: float(np.mean(values))
        for key, values in grouped.items()
        if values
    }
    season_groups: dict[tuple[str, int], list[tuple[str, int, str]]] = defaultdict(list)
    for key in raw:
        season_groups[(key[0], key[1])].append(key)

    standardized: dict[tuple[str, int, str], float] = {}
    for _, keys in sorted(season_groups.items()):
        if len(keys) < 3:
            continue
        values = np.asarray([raw[k] for k in keys], dtype=float)
        sd = float(np.std(values, ddof=1))
        if sd <= 0:
            continue
        z = (values - float(np.mean(values))) / sd
        for key, value in zip(keys, z):
            standardized[key] = float(value)

    rows = []
    for row in common:
        key = _key(row)
        if key in standardized:
            rows.append({**row, "successful_brood_state": standardized[key]})

    # Fail closed if dropping undefined rows leaves <3 colonies in any season.
    counts: dict[tuple[str, int], int] = defaultdict(int)
    for row in rows:
        counts[(str(row["island"]), int(row["season"]))] += 1
    valid_groups = {key for key, n in counts.items() if n >= 3}
    return [
        row
        for row in rows
        if (str(row["island"]), int(row["season"])) in valid_groups
    ]


def analyze(
    adult_path: str | Path,
    chick_path: str | Path,
    repro_path: str | Path,
) -> dict[str, object]:
    common, repro_rows, _ = _common_panel(adult_path, chick_path, repro_path)
    if len(common) != 61 or len(_groups(common)) != 15:
        raise ValueError(
            f"expected frozen 61-row/15-season common panel, observed "
            f"{len(common)} rows/{len(_groups(common))} seasons"
        )

    detectability = _detectability(common)
    stability = _bootstrap_stability(common, repro_rows)
    brood_rows = _successful_brood_state(common, repro_rows)
    brood_x = np.asarray(
        [float(r["successful_brood_state"]) for r in brood_rows], dtype=float
    )
    brood = _permutation_result(
        brood_rows,
        brood_x,
        permutations=DECOMP_PERMUTATIONS,
        seed=20261003,
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-repro-detectability-decomposition-v1",
        "diagnostic_id": "mina-palmer-repro-detectability-decomposition-v1",
        "status": "post_result_interpretation_diagnostic",
        "common_panel": {
            "rows": len(common),
            "predictor_seasons": len(_groups(common)),
            "islands": sorted({str(r["island"]) for r in common}),
        },
        "detectability": detectability,
        "bootstrap_state_stability": stability,
        "decomposition": {
            "identity": (
                "mean chicks per monitored nest = proportion of nests with any "
                "creched chick × mean creched chicks among successful nests"
            ),
            "success_frequency_existing_sensitivity": {
                "beta": 0.06788778857921648,
                "one_sided_upper_p": 0.040519594804051956,
                "role": "prespecified sensitivity only; cannot rescue primary",
            },
            "successful_nest_brood_size_posthoc": brood,
        },
        "decision": {
            "low_panel_detectability_alone_is_sufficient_explanation": bool(
                detectability["simulation"]["power"][f"{BENCHMARK_BETA:.15g}"][
                    "detection_fraction"
                ] < 0.5
            ),
            "sampling_noise_nontrivial": bool(
                stability["correlation_with_original_state"]["median"] < 0.9
            ),
            "metric_mismatch_remains_material": True,
            "primary_repro_result_rescued": False,
        },
        "claim_boundary": [
            "All power, bootstrap and brood-size results are post-result diagnostics.",
            "Do not use the success-frequency sensitivity to rescue the failed primary REPRO endpoint.",
            "High conditional detectability does not eliminate monitored-nest measurement error or sampling selectivity.",
            "Do not infer the cue perceived by penguins from this diagnostic.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adult-census", required=True, type=Path)
    parser.add_argument("--chicks", required=True, type=Path)
    parser.add_argument("--repro", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = analyze(args.adult_census, args.chicks, args.repro)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
