#!/usr/bin/env python3
"""Synthetic latent-factor schedule recovery for Paper 2 Gate 2E-A."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

START_YEAR = 1980
END_YEAR = 2025
TRANSITION_YEARS = tuple(range(START_YEAR, END_YEAR))
YEAR_INDEX = {year: i for i, year in enumerate(range(START_YEAR, END_YEAR + 1))}
TRANSITION_INDEX = {year: i for i, year in enumerate(TRANSITION_YEARS)}


def _parse_seasons(value: Any) -> list[int]:
    if isinstance(value, (list, tuple, np.ndarray, pd.Series)):
        values = value
    else:
        values = str(value).split(";")
    out = []
    for value in values:
        text = str(value).strip()
        if not text or text.lower() == "nan":
            continue
        year = int(float(text))
        if START_YEAR <= year <= END_YEAR:
            out.append(year)
    return sorted(set(out))


def _group_indices(frame: pd.DataFrame) -> tuple[list[str], dict[str, np.ndarray]]:
    groups = sorted(frame["forcing_group"].astype(str).unique())
    labels = frame["forcing_group"].astype(str).to_numpy()
    return groups, {g: np.flatnonzero(labels == g) for g in groups}


def simulate_latent_schedule(
    frame: pd.DataFrame,
    *,
    gamma_ah: float,
    seed: int,
    forcing_sd: float,
    loading_sd: float,
    process_sd: float,
    drift_mean: float,
    drift_sd: float,
) -> dict:
    """Generate latent annual states, then retain only real observation seasons."""
    required = {"unit_id", "forcing_group", "A", "H", "AH", "seasons"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    local = frame.reset_index(drop=True).copy()
    rng = np.random.default_rng(seed)
    groups, group_rows = _group_indices(local)
    n_sites = len(local)
    n_transitions = len(TRANSITION_YEARS)

    true_forcing: dict[str, np.ndarray] = {}
    for group in groups:
        values = rng.normal(0.0, forcing_sd, n_transitions)
        true_forcing[group] = values - float(values.mean())

    true_lambda = (
        1.0
        + gamma_ah * local["AH"].to_numpy(dtype=float)
        + rng.normal(0.0, loading_sd, n_sites)
    )
    for group, idx in group_rows.items():
        true_lambda[idx] -= float(true_lambda[idx].mean()) - 1.0

    true_mu = rng.normal(drift_mean, drift_sd, n_sites)
    state = np.zeros((n_sites, END_YEAR - START_YEAR + 1), dtype=float)
    state[:, 0] = rng.normal(8.0, 0.5, n_sites)

    group_labels = local["forcing_group"].astype(str).to_numpy()
    for t, year in enumerate(TRANSITION_YEARS):
        forcing = np.array(
            [true_forcing[group][t] for group in group_labels],
            dtype=float,
        )
        state[:, t + 1] = (
            state[:, t]
            + true_mu
            + true_lambda * forcing
            + rng.normal(0.0, process_sd, n_sites)
        )

    records: list[tuple[int, str, int, int, float]] = []
    for i, row in local.iterrows():
        seasons = _parse_seasons(row["seasons"])
        if len(seasons) < 2:
            continue
        group = str(row["forcing_group"])
        for first, last in zip(seasons[:-1], seasons[1:]):
            delta = (
                state[i, YEAR_INDEX[last]]
                - state[i, YEAR_INDEX[first]]
            )
            records.append((i, group, first, last, float(delta)))

    return {
        "intervals": {
            "records": records,
            "true_forcing": {
                group: values.tolist()
                for group, values in true_forcing.items()
            },
            "true_lambda": true_lambda.tolist(),
        },
        "true_forcing": {
            group: values.tolist()
            for group, values in true_forcing.items()
        },
        "true_lambda": true_lambda.tolist(),
    }


def _solve_factor_given_loadings(
    frame: pd.DataFrame,
    records: list[tuple[int, str, int, int, float]],
    loadings: np.ndarray,
    *,
    constraint_weight: float = 100.0,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    n_sites = len(frame)
    groups, _ = _group_indices(frame)
    group_index = {group: j for j, group in enumerate(groups)}
    n_t = len(TRANSITION_YEARS)

    n_rows = len(records) + len(groups)
    matrix = np.zeros((n_rows, n_sites + len(groups) * n_t), dtype=float)
    response = np.zeros(n_rows, dtype=float)

    row_i = 0
    for site_i, group, first, last, delta in records:
        duration = last - first
        weight = 1.0 / math.sqrt(duration)
        matrix[row_i, site_i] = duration * weight
        start_col = n_sites + group_index[group] * n_t
        for year in range(first, last):
            matrix[row_i, start_col + TRANSITION_INDEX[year]] = (
                loadings[site_i] * weight
            )
        response[row_i] = delta * weight
        row_i += 1

    # Identification: each group forcing has mean zero.
    for group in groups:
        start_col = n_sites + group_index[group] * n_t
        matrix[row_i, start_col : start_col + n_t] = (
            constraint_weight / n_t
        )
        row_i += 1

    solution = np.linalg.lstsq(matrix, response, rcond=None)[0]
    mu = solution[:n_sites]
    forcing = {}
    for group in groups:
        start_col = n_sites + group_index[group] * n_t
        forcing[group] = solution[start_col : start_col + n_t].copy()
    return mu, forcing


def _solve_loadings_given_factor(
    frame: pd.DataFrame,
    records: list[tuple[int, str, int, int, float]],
    forcing: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    n_sites = len(frame)
    by_site: list[list[tuple[int, str, int, int, float]]] = [
        [] for _ in range(n_sites)
    ]
    for record in records:
        by_site[record[0]].append(record)

    mu = np.zeros(n_sites, dtype=float)
    loadings = np.zeros(n_sites, dtype=float)

    for site_i, local_records in enumerate(by_site):
        if len(local_records) < 2:
            raise ValueError(
                f"site {frame.iloc[site_i]['unit_id']} has <2 recovery intervals"
            )
        design = []
        response = []
        for _, group, first, last, delta in local_records:
            duration = last - first
            forcing_sum = sum(
                forcing[group][TRANSITION_INDEX[year]]
                for year in range(first, last)
            )
            weight = 1.0 / math.sqrt(duration)
            design.append([duration * weight, forcing_sum * weight])
            response.append(delta * weight)
        coef = np.linalg.lstsq(
            np.asarray(design, dtype=float),
            np.asarray(response, dtype=float),
            rcond=None,
        )[0]
        mu[site_i] = coef[0]
        loadings[site_i] = coef[1]

    groups, group_rows = _group_indices(frame)
    for group in groups:
        idx = group_rows[group]
        mean_loading = float(loadings[idx].mean())
        if abs(mean_loading) < 1e-10:
            raise ValueError(f"near-zero mean loading in group {group}")
        loadings[idx] /= mean_loading
        forcing[group] *= mean_loading

    return mu, loadings


def _loading_regression(frame: pd.DataFrame, loadings: np.ndarray) -> np.ndarray:
    group_dummies = pd.get_dummies(
        frame["forcing_group"].astype(str),
        drop_first=True,
        dtype=float,
    )
    matrix = np.column_stack(
        [
            np.ones(len(frame), dtype=float),
            group_dummies.to_numpy(dtype=float),
            frame[["A", "H", "AH"]].to_numpy(dtype=float),
        ]
    )
    coef = np.linalg.lstsq(matrix, loadings, rcond=None)[0]
    return coef[-3:]


def fit_unknown_factor(
    frame: pd.DataFrame,
    intervals: dict | list,
    *,
    iterations: int = 8,
) -> dict:
    """Fit shared forcing and site loadings without using the true forcing."""
    local = frame.reset_index(drop=True).copy()
    if isinstance(intervals, dict):
        records = intervals["records"]
        true_forcing = intervals.get("true_forcing")
        true_lambda = intervals.get("true_lambda")
    else:
        records = intervals
        true_forcing = None
        true_lambda = None

    loadings = np.ones(len(local), dtype=float)
    forcing: dict[str, np.ndarray] = {}

    for _ in range(iterations):
        _, forcing = _solve_factor_given_loadings(
            local, records, loadings
        )
        _, loadings = _solve_loadings_given_factor(
            local, records, forcing
        )

    gamma = _loading_regression(local, loadings)
    forcing_correlation: dict[str, float] = {}
    if true_forcing is not None:
        for group, estimated in forcing.items():
            truth = np.asarray(true_forcing[group], dtype=float)
            corr = float(np.corrcoef(truth, estimated)[0, 1])
            forcing_correlation[group] = corr

    lambda_correlation = None
    if true_lambda is not None:
        lambda_correlation = float(
            np.corrcoef(
                np.asarray(true_lambda, dtype=float),
                loadings,
            )[0, 1]
        )

    return {
        "gamma_a": float(gamma[0]),
        "gamma_h": float(gamma[1]),
        "gamma_ah": float(gamma[2]),
        "lambda_hat": loadings.tolist(),
        "forcing_hat": {
            group: values.tolist()
            for group, values in forcing.items()
        },
        "forcing_correlation": forcing_correlation,
        "lambda_correlation": lambda_correlation,
        "iterations": int(iterations),
    }



def _zscore(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    sd = float(values.std(ddof=0))
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError(f"zero/nonfinite predictor variance: {series.name}")
    return (values - float(values.mean())) / sd


def build_scale_frame(
    forcing_result: dict,
    forcing_units: pd.DataFrame,
    breeding_options: pd.DataFrame,
    species_id: str,
    scale: str,
) -> pd.DataFrame:
    """Build one outcome-blind recovery frame at a frozen forcing scale."""
    species_id = str(species_id)
    meta = forcing_result["decision"]["modeling_eligibility_by_species"][species_id]

    units = forcing_units[
        forcing_units["species_id"].astype(str).eq(species_id)
    ].copy()

    if scale == "species_wide":
        selected = units
    else:
        if scale != str(meta["level"]):
            raise ValueError(
                f"{species_id}: requested regional scale {scale} != frozen {meta['level']}"
            )
        selected_ids = {str(v) for v in meta["covered_units"]}
        selected = units[
            units["unit_id"].astype(str).isin(selected_ids)
        ].copy()
        if len(selected) != len(selected_ids):
            raise ValueError(
                f"{species_id}: forcing-unit drift {len(selected)} != {len(selected_ids)}"
            )

    bcols = [
        "site_id",
        "mapped_ice_free_pixel_count_2000m",
        "mapped_ice_free_area_ha_2000m",
        "tier2_richness_2000m",
    ]
    frame = selected.merge(
        breeding_options[bcols],
        on="site_id",
        how="left",
        validate="many_to_one",
    )

    pixel_count = pd.to_numeric(
        frame["mapped_ice_free_pixel_count_2000m"],
        errors="coerce",
    )
    frame = frame.loc[pixel_count > 0].copy()
    frame["A_raw"] = np.log1p(
        pd.to_numeric(
            frame["mapped_ice_free_area_ha_2000m"],
            errors="coerce",
        )
    )
    frame["H_raw"] = pd.to_numeric(
        frame["tier2_richness_2000m"],
        errors="coerce",
    )
    frame = frame.dropna(subset=["A_raw", "H_raw", "seasons"]).copy()

    frame["A"] = _zscore(frame["A_raw"])
    frame["H"] = _zscore(frame["H_raw"])
    frame["AH"] = frame["A"] * frame["H"]

    if scale == "ccamlr":
        frame["forcing_group"] = frame["ccamlr_id"]
    elif scale == "apbp_region":
        frame["forcing_group"] = frame["region"]
    elif scale == "species_wide":
        frame["forcing_group"] = species_id
    else:
        raise ValueError(f"unsupported forcing scale: {scale}")

    bad_group = (
        frame["forcing_group"].isna()
        | frame["forcing_group"].astype(str).str.strip().eq("")
    )
    if bool(bad_group.any()):
        bad = frame.loc[bad_group, "unit_id"].astype(str).tolist()
        raise ValueError(f"missing forcing group for units: {bad}")

    keep = [
        "unit_id",
        "site_id",
        "species_id",
        "forcing_group",
        "A",
        "H",
        "AH",
        "seasons",
    ]
    return frame[keep].sort_values("unit_id").reset_index(drop=True)


def _quantile(values: list[float], q: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), q))


def _run_scenario(
    frame: pd.DataFrame,
    *,
    gamma_ah: float,
    replicates: int,
    seed_offset: int,
) -> dict:
    gamma_hats: list[float] = []
    lambda_corrs: list[float] = []
    group_corrs: dict[str, list[float]] = {
        group: []
        for group in sorted(frame["forcing_group"].astype(str).unique())
    }

    for replicate in range(replicates):
        sim = simulate_latent_schedule(
            frame,
            gamma_ah=gamma_ah,
            seed=seed_offset + replicate,
            forcing_sd=0.08,
            loading_sd=0.15,
            process_sd=0.04,
            drift_mean=-0.01,
            drift_sd=0.01,
        )
        fit = fit_unknown_factor(
            frame,
            sim["intervals"],
            iterations=8,
        )
        gamma_hats.append(float(fit["gamma_ah"]))
        if fit["lambda_correlation"] is not None:
            lambda_corrs.append(float(fit["lambda_correlation"]))
        for group, value in fit["forcing_correlation"].items():
            group_corrs[group].append(float(value))

    return {
        "gamma_hats": gamma_hats,
        "lambda_correlations": lambda_corrs,
        "forcing_correlations": group_corrs,
    }


def _scenario_summary(raw: dict) -> dict:
    gamma = raw["gamma_hats"]
    lambdas = raw["lambda_correlations"]
    forcing = {
        group: {
            "median_corr": float(np.median(values)),
            "q05_corr": _quantile(values, 0.05),
            "q95_corr": _quantile(values, 0.95),
        }
        for group, values in sorted(raw["forcing_correlations"].items())
    }
    return {
        "median_gamma_ah": float(np.median(gamma)),
        "mean_gamma_ah": float(np.mean(gamma)),
        "q05_gamma_ah": _quantile(gamma, 0.05),
        "q95_gamma_ah": _quantile(gamma, 0.95),
        "negative_fraction": float(np.mean(np.asarray(gamma) < 0.0)),
        "median_lambda_correlation": (
            float(np.median(lambdas)) if lambdas else None
        ),
        "forcing_groups": forcing,
    }


def evaluate_scale(
    frame: pd.DataFrame,
    *,
    replicates: int,
    seed_offset: int,
) -> dict:
    """Run fixed null and crossover recovery scenarios at one forcing scale."""
    if replicates < 2:
        raise ValueError("replicates must be >=2")

    crossover_raw = _run_scenario(
        frame,
        gamma_ah=-0.35,
        replicates=replicates,
        seed_offset=seed_offset,
    )
    null_raw = _run_scenario(
        frame,
        gamma_ah=0.0,
        replicates=replicates,
        seed_offset=seed_offset + 100000,
    )
    crossover = _scenario_summary(crossover_raw)
    null = _scenario_summary(null_raw)

    groups = sorted(frame["forcing_group"].astype(str).unique())
    forcing_groups = {}
    for group in groups:
        c = crossover["forcing_groups"][group]
        n = null["forcing_groups"][group]
        forcing_groups[group] = {
            "median_corr": min(c["median_corr"], n["median_corr"]),
            "q05_corr": min(c["q05_corr"], n["q05_corr"]),
            "crossover_median_corr": c["median_corr"],
            "null_median_corr": n["median_corr"],
        }

    summary = {
        "n_units": int(len(frame)),
        "n_groups": int(frame["forcing_group"].nunique()),
        "forcing_groups": forcing_groups,
        "crossover": {
            k: v for k, v in crossover.items()
            if k != "forcing_groups"
        },
        "null": {
            k: v for k, v in null.items()
            if k != "forcing_groups"
        },
        "replicates": int(replicates),
    }
    summary["gate"] = evaluate_recovery_gate(
        summary,
        crossover_truth=-0.35,
    )
    return summary


def run_recovery_audit(
    forcing_result: dict,
    forcing_units: pd.DataFrame,
    breeding_options: pd.DataFrame,
    *,
    replicates: int,
) -> dict:
    species_results = {}
    selected = {}

    for index, species_id in enumerate(("ADPE", "CHPE", "GEPE")):
        regional_scale = str(
            forcing_result["decision"]["modeling_eligibility_by_species"][
                species_id
            ]["level"]
        )
        regional_frame = build_scale_frame(
            forcing_result,
            forcing_units,
            breeding_options,
            species_id,
            regional_scale,
        )
        specieswide_frame = build_scale_frame(
            forcing_result,
            forcing_units,
            breeding_options,
            species_id,
            "species_wide",
        )

        regional = evaluate_scale(
            regional_frame,
            replicates=replicates,
            seed_offset=1000000 + index * 200000,
        )
        specieswide = evaluate_scale(
            specieswide_frame,
            replicates=replicates,
            seed_offset=2000000 + index * 200000,
        )
        chosen = select_recovered_scale(
            regional_scale,
            regional["gate"],
            specieswide["gate"],
        )
        selected[species_id] = chosen
        species_results[species_id] = {
            "gate2c_regional_scale": regional_scale,
            "regional": regional,
            "species_wide": specieswide,
            "selected_recovered_scale": chosen,
        }

    return {
        "schema_version": 1,
        "audit_id": "mina-paper2-latent-factor-recovery-v1",
        "primary_window": [START_YEAR, END_YEAR],
        "replicates_per_scale_scenario": int(replicates),
        "simulation": {
            "forcing_sd": 0.08,
            "loading_sd": 0.15,
            "process_sd": 0.04,
            "drift_mean": -0.01,
            "drift_sd": 0.01,
            "crossover_gamma_ah": -0.35,
            "null_gamma_ah": 0.0,
            "als_iterations": 8,
        },
        "species": species_results,
        "decision": {
            "selected_recovered_scale_by_species": selected,
            "all_species_have_recovered_scale": bool(
                all(value is not None for value in selected.values())
            ),
            "no_real_count_magnitudes_opened": True,
            "observation_layer_validated": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forcing-json", required=True, type=Path)
    parser.add_argument("--forcing-csv", required=True, type=Path)
    parser.add_argument("--breeding-csv", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--replicates", type=int, default=100)
    args = parser.parse_args()

    forcing_result = json.loads(
        args.forcing_json.read_text(encoding="utf-8")
    )
    forcing_units = pd.read_csv(args.forcing_csv)
    breeding_options = pd.read_csv(args.breeding_csv)

    result = run_recovery_audit(
        forcing_result,
        forcing_units,
        breeding_options,
        replicates=args.replicates,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["decision"]["all_species_have_recovered_scale"]:
        raise SystemExit("latent-factor recovery failed for one or more species")
    return 0

def evaluate_recovery_gate(
    summary: dict,
    *,
    crossover_truth: float,
) -> dict:
    checks = {
        "factor_median": all(
            float(values["median_corr"]) >= 0.70
            for values in summary["forcing_groups"].values()
        ),
        "factor_q05": all(
            float(values["q05_corr"]) >= 0.30
            for values in summary["forcing_groups"].values()
        ),
        "crossover_bias": (
            abs(
                float(summary["crossover"]["median_gamma_ah"])
                - crossover_truth
            )
            <= 0.10
        ),
        "crossover_sign": (
            float(summary["crossover"]["negative_fraction"]) >= 0.90
        ),
        "null_center": (
            abs(float(summary["null"]["median_gamma_ah"])) <= 0.05
        ),
        "null_contains_zero": (
            float(summary["null"]["q05_gamma_ah"]) <= 0.0
            <= float(summary["null"]["q95_gamma_ah"])
        ),
    }
    return {
        "passes": bool(all(checks.values())),
        "checks": checks,
    }



def _quantile(values: list[float], q: float) -> float:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError("cannot summarize empty replicate vector")
    return float(np.quantile(arr, q))


def evaluate_scale(
    frame: pd.DataFrame,
    *,
    replicates: int = 100,
    seed_offset: int = 0,
) -> dict:
    """Run the frozen null/crossover recovery experiment for one scale."""
    if replicates < 1:
        raise ValueError("replicates must be >=1")
    local = frame.reset_index(drop=True).copy()
    if len(local) < 3:
        raise ValueError("recovery frame has fewer than 3 units")

    params = {
        "forcing_sd": 0.08,
        "loading_sd": 0.15,
        "process_sd": 0.04,
        "drift_mean": -0.01,
        "drift_sd": 0.01,
    }
    crossover_truth = -0.35
    null_estimates: list[float] = []
    crossover_estimates: list[float] = []
    corr_by_group: dict[str, list[float]] = {
        str(g): [] for g in sorted(local["forcing_group"].astype(str).unique())
    }
    lambda_corr_null: list[float] = []
    lambda_corr_crossover: list[float] = []

    for rep in range(replicates):
        null_sim = simulate_latent_schedule(
            local,
            gamma_ah=0.0,
            seed=seed_offset + rep,
            **params,
        )
        null_fit = fit_unknown_factor(local, null_sim["intervals"], iterations=8)
        null_estimates.append(float(null_fit["gamma_ah"]))
        if null_fit["lambda_correlation"] is not None:
            lambda_corr_null.append(float(null_fit["lambda_correlation"]))
        for group, value in null_fit["forcing_correlation"].items():
            corr_by_group[str(group)].append(float(value))

        cross_sim = simulate_latent_schedule(
            local,
            gamma_ah=crossover_truth,
            seed=seed_offset + 100000 + rep,
            **params,
        )
        cross_fit = fit_unknown_factor(local, cross_sim["intervals"], iterations=8)
        crossover_estimates.append(float(cross_fit["gamma_ah"]))
        if cross_fit["lambda_correlation"] is not None:
            lambda_corr_crossover.append(float(cross_fit["lambda_correlation"]))
        for group, value in cross_fit["forcing_correlation"].items():
            corr_by_group[str(group)].append(float(value))

    forcing_groups = {
        group: {
            "n_correlations": len(values),
            "median_corr": _quantile(values, 0.50),
            "q05_corr": _quantile(values, 0.05),
        }
        for group, values in corr_by_group.items()
    }
    summary = {
        "replicates_per_scenario": int(replicates),
        "simulation_parameters": {
            **params,
            "crossover_truth": crossover_truth,
            "iterations": 8,
        },
        "forcing_groups": forcing_groups,
        "null": {
            "median_gamma_ah": _quantile(null_estimates, 0.50),
            "q05_gamma_ah": _quantile(null_estimates, 0.05),
            "q95_gamma_ah": _quantile(null_estimates, 0.95),
            "negative_fraction": float(np.mean(np.asarray(null_estimates) < 0.0)),
            "median_lambda_correlation": (
                _quantile(lambda_corr_null, 0.50)
                if lambda_corr_null else None
            ),
        },
        "crossover": {
            "truth_gamma_ah": crossover_truth,
            "median_gamma_ah": _quantile(crossover_estimates, 0.50),
            "q05_gamma_ah": _quantile(crossover_estimates, 0.05),
            "q95_gamma_ah": _quantile(crossover_estimates, 0.95),
            "negative_fraction": float(
                np.mean(np.asarray(crossover_estimates) < 0.0)
            ),
            "median_lambda_correlation": (
                _quantile(lambda_corr_crossover, 0.50)
                if lambda_corr_crossover else None
            ),
        },
    }
    summary["gate"] = evaluate_recovery_gate(
        summary,
        crossover_truth=crossover_truth,
    )
    return summary

def select_recovered_scale(
    regional_scale: str,
    regional_result: dict,
    specieswide_result: dict,
) -> str | None:
    if regional_result.get("passes"):
        return regional_scale
    if specieswide_result.get("passes"):
        return "species_wide"
    return None


if __name__ == "__main__":
    raise SystemExit(main())
