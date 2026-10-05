#!/usr/bin/env python3
"""Frozen Stage-C SMP trend-symmetry concentration analysis.

Execution is locked unless the independent Stage-A structural gate and Stage-B
trend-balance gate both passed. The primary panel statistic is delta_gamma:
the observed temporal slope of log effective component number minus the median
slope under a fixed-composition null preserving the exact annual abundance
trajectory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.gate_smp_trend_balance_v1 import _prepare_raw
from scripts.gate_smp_master_site_support_v1 import _norm


DEFAULT_NULL_B = 20000
DEFAULT_BOOT_B = 9999
DEFAULT_SEED = 20261005


def slope_centered(years: np.ndarray, values: np.ndarray) -> float:
    x = np.asarray(years, float)
    y = np.asarray(values, float)
    xc = x - x.mean()
    denom = float(xc @ xc)
    if denom <= 0:
        raise ValueError("zero year variance")
    return float((xc @ y) / denom)


def effective_number(counts: np.ndarray) -> float:
    c = np.asarray(counts, float)
    total = float(c.sum())
    if total <= 0:
        raise ValueError("E undefined for total abundance <= 0")
    p = c / total
    return float(1.0 / np.sum(p * p))


def _integer_counts(values: np.ndarray) -> np.ndarray:
    v = np.asarray(values, float)
    rounded = np.rint(v)
    if not np.allclose(v, rounded, rtol=0.0, atol=1e-9):
        raise ValueError(
            "Non-integer retained count encountered; frozen multinomial null "
            "cannot silently round or change family."
        )
    if (rounded < 0).any():
        raise ValueError("negative count")
    return rounded.astype(np.int64)


def panel_effect(
    x: pd.DataFrame,
    support_panel: dict,
    balance_row: dict,
    *,
    B: int = DEFAULT_NULL_B,
    seed: int = DEFAULT_SEED,
) -> dict:
    if not bool(balance_row.get("composition_eligible")):
        raise ValueError("panel is not Stage-C composition eligible")

    species = str(support_panel["species"])
    master = str(support_panel["master_site"])
    unit = str(support_panel["unit"])
    roster = [str(v) for v in support_panel["retained_site_ids"]]
    years = [int(v) for v in support_panel["complete_years"]]

    g = x[
        x["_species"].eq(species)
        & x["_master_norm"].eq(_norm(master))
        & x["_unit"].eq(unit)
        & x["_site_id"].isin(set(roster))
        & x["year"].isin(years)
    ].copy()

    matrix = (
        g.pivot(index="year", columns="_site_id", values="_count")
        .reindex(index=years, columns=roster)
    )
    if matrix.isna().any().any():
        raise ValueError(f"complete panel drift: {species}|{master}|{unit}")

    counts = _integer_counts(matrix.to_numpy(float))
    totals = counts.sum(axis=1)
    positive = totals > 0
    pos_years = np.asarray(years, int)[positive]
    pos_counts = counts[positive, :]
    pos_totals = totals[positive]

    if len(pos_years) != int(balance_row["n_positive_total_years"]):
        raise ValueError("positive-total year count drift")
    span = int(pos_years.max() - pos_years.min() + 1)
    if span != int(balance_row["positive_total_span_years"]):
        raise ValueError("positive-total span drift")

    E = np.asarray([effective_number(row) for row in pos_counts], float)
    gamma_obs = slope_centered(pos_years, np.log(E))

    pooled = pos_counts.sum(axis=0).astype(float)
    if pooled.sum() <= 0:
        raise ValueError("zero pooled abundance")
    q = pooled / pooled.sum()

    rng = np.random.default_rng(int(seed))
    xc = pos_years.astype(float) - float(pos_years.mean())
    denom = float(xc @ xc)
    null_gamma = np.empty(int(B), float)

    # Batch to bound memory for panels with many components/years.
    batch = 500
    produced = 0
    while produced < int(B):
        k = min(batch, int(B) - produced)
        loge = np.empty((k, len(pos_years)), float)
        for ti, n in enumerate(pos_totals):
            draws = rng.multinomial(int(n), q, size=k)
            ss = np.sum(draws.astype(float) ** 2, axis=1)
            e_sim = (float(n) ** 2) / ss
            loge[:, ti] = np.log(e_sim)
        null_gamma[produced:produced + k] = (loge @ xc) / denom
        produced += k

    null_median = float(np.median(null_gamma))
    delta = float(gamma_obs - null_median)

    return {
        "panel_id": str(balance_row["panel_id"]),
        "species": species,
        "master_site": master,
        "unit": unit,
        "n_components": int(len(roster)),
        "n_complete_years": int(len(years)),
        "n_positive_total_years": int(len(pos_years)),
        "first_positive_year": int(pos_years.min()),
        "last_positive_year": int(pos_years.max()),
        "b_log1pN_per_year": float(balance_row["b_log1pN_per_year"]),
        "trend_label": str(balance_row["trend_label"]),
        "gamma_obs": gamma_obs,
        "gamma_null_median": null_median,
        "gamma_null_sd": float(np.std(null_gamma, ddof=1)),
        "gamma_null_q025": float(np.quantile(null_gamma, 0.025)),
        "gamma_null_q975": float(np.quantile(null_gamma, 0.975)),
        "delta_gamma": delta,
    }


def _percentile_ci(values: np.ndarray) -> dict:
    v = np.asarray(values, float)
    return {
        "lower": float(np.quantile(v, 0.025)),
        "upper": float(np.quantile(v, 0.975)),
    }


def macro_summary(
    panel_df: pd.DataFrame,
    *,
    B: int = DEFAULT_BOOT_B,
    seed: int = DEFAULT_SEED,
) -> dict:
    d = panel_df.copy().reset_index(drop=True)
    if d.empty:
        raise ValueError("no Stage-C panels")

    species_means = d.groupby("species")["delta_gamma"].mean().astype(float)
    alpha = float(species_means.mean())

    b = d["b_log1pN_per_year"].astype(float)
    b_sd = float(b.std(ddof=1))
    if not np.isfinite(b_sd) or b_sd <= 0:
        raise ValueError("zero abundance-trend variance")
    d["b_z"] = (b - float(b.mean())) / b_sd
    d["x_res"] = d["b_z"] - d.groupby("species")["b_z"].transform("mean")
    d["y_res"] = d["delta_gamma"] - d.groupby("species")["delta_gamma"].transform("mean")

    species_contrib = {}
    for sp, g in d.groupby("species"):
        num = float(np.sum(g["x_res"] * g["y_res"]))
        den = float(np.sum(g["x_res"] ** 2))
        species_contrib[str(sp)] = {"num": num, "den": den}

    identified_species = sorted([sp for sp, z in species_contrib.items() if z["den"] > 0])
    if len(identified_species) < 4:
        beta = None
    else:
        num = sum(species_contrib[sp]["num"] for sp in identified_species)
        den = sum(species_contrib[sp]["den"] for sp in identified_species)
        beta = float(num / den)

    class_species_means = {}
    for label in ("increasing", "declining"):
        g = d[d["trend_label"].eq(label)]
        class_species_means[label] = g.groupby("species")["delta_gamma"].mean().astype(float)
    mu_plus = float(class_species_means["increasing"].mean())
    mu_minus = float(class_species_means["declining"].mean())

    rng = np.random.default_rng(int(seed))
    species_all = np.asarray(species_means.index.tolist(), object)
    alpha_boot = np.empty(int(B), float)
    for j in range(int(B)):
        sample = rng.choice(species_all, size=len(species_all), replace=True)
        alpha_boot[j] = float(np.mean([species_means.loc[s] for s in sample]))

    beta_boot = np.full(int(B), np.nan, float)
    if beta is not None:
        sp_beta = np.asarray(identified_species, object)
        for j in range(int(B)):
            sample = rng.choice(sp_beta, size=len(sp_beta), replace=True)
            num = float(sum(species_contrib[s]["num"] for s in sample))
            den = float(sum(species_contrib[s]["den"] for s in sample))
            if den > 0:
                beta_boot[j] = num / den

    def boot_group(series: pd.Series, offset_seed: int) -> tuple[float, dict]:
        local_rng = np.random.default_rng(int(seed) + offset_seed)
        spp = np.asarray(series.index.tolist(), object)
        vals = np.empty(int(B), float)
        for j in range(int(B)):
            sample = local_rng.choice(spp, size=len(spp), replace=True)
            vals[j] = float(np.mean([series.loc[s] for s in sample]))
        return float(series.mean()), _percentile_ci(vals)

    _, plus_ci = boot_group(class_species_means["increasing"], 100001)
    _, minus_ci = boot_group(class_species_means["declining"], 200003)
    alpha_ci = _percentile_ci(alpha_boot)
    beta_ci = (
        _percentile_ci(beta_boot[np.isfinite(beta_boot)])
        if beta is not None and np.isfinite(beta_boot).any()
        else None
    )

    overall_supported = bool(alpha_ci["upper"] < 0)
    coupling_supported = bool(beta_ci is not None and beta_ci["lower"] > 0)
    plus_negative = bool(plus_ci["upper"] < 0)
    plus_positive = bool(plus_ci["lower"] > 0)
    minus_negative = bool(minus_ci["upper"] < 0)

    if minus_negative and plus_positive:
        pattern = "reversible_tracking"
    elif minus_negative and plus_negative:
        pattern = "directional_persistence"
    elif minus_negative and not plus_negative and not plus_positive:
        pattern = "decline_supported_increase_unresolved"
    else:
        pattern = "unresolved"

    return {
        "species_count": int(d["species"].nunique()),
        "panel_count": int(len(d)),
        "alpha_species_balanced": {
            "estimate": alpha,
            "bootstrap_95": alpha_ci,
            "overall_concentration_supported": overall_supported,
        },
        "beta_within_species": {
            "estimate": beta,
            "identified_species": identified_species,
            "identified_species_count": int(len(identified_species)),
            "bootstrap_95": beta_ci,
            "decline_coupling_supported": coupling_supported,
        },
        "trend_class_species_balanced": {
            "mu_plus_increasing": {"estimate": mu_plus, "bootstrap_95": plus_ci},
            "mu_minus_declining": {"estimate": mu_minus, "bootstrap_95": minus_ci},
            "pattern": pattern,
        },
        "boundary": [
            "A beta interval overlapping zero is unresolved and is not evidence of trend-independence.",
            "Directional persistence is ratchet-compatible only; it is not a hysteresis test.",
            "Species are the macroecological resampling unit.",
        ],
    }


def run(
    input_path: Path,
    support_json: Path,
    balance_json: Path,
    *,
    assume_whole_colony_extract: bool = False,
    null_B: int = DEFAULT_NULL_B,
    boot_B: int = DEFAULT_BOOT_B,
    seed: int = DEFAULT_SEED,
) -> tuple[dict, pd.DataFrame]:
    support = json.loads(support_json.read_text(encoding="utf-8"))
    balance = json.loads(balance_json.read_text(encoding="utf-8"))

    if not support.get("decision", {}).get("structural_gate_passed"):
        raise ValueError("Stage-A structural gate did not pass")
    if not balance.get("decision", {}).get("symmetry_identifiability_gate_passed"):
        raise ValueError("Stage-B symmetry identifiability gate did not pass")
    if not balance.get("decision", {}).get("component_concentration_execution_authorized"):
        raise ValueError("Stage-C execution is not authorized")

    x = _prepare_raw(
        input_path,
        assume_whole_colony_extract=assume_whole_colony_extract,
    )

    support_map = {
        f"{p['species']}|{p['master_site']}|{p['unit']}": p
        for p in support["eligible_panels"]
    }
    balance_rows = [
        row for row in balance["panel_trends"]
        if bool(row.get("composition_eligible"))
    ]

    effects = []
    for idx, row in enumerate(balance_rows):
        pid = str(row["panel_id"])
        if pid not in support_map:
            raise ValueError(f"panel roster drift: {pid}")
        effects.append(
            panel_effect(
                x,
                support_map[pid],
                row,
                B=int(null_B),
                seed=int(seed) + idx * 100003,
            )
        )

    frame = pd.DataFrame(effects).sort_values(["species", "master_site", "unit"]).reset_index(drop=True)
    macro = macro_summary(frame, B=int(boot_B), seed=int(seed))

    result = {
        "schema_version": 1,
        "analysis_id": "mina-smp-trend-symmetry-effect-v1",
        "status": "first_and_only_frozen_stage_c_execution",
        "null_simulations_per_panel": int(null_B),
        "species_cluster_bootstrap_resamples": int(boot_B),
        "seed": int(seed),
        "panel_effects": effects,
        "macro": macro,
        "decision": {
            "overall_concentration_supported": macro["alpha_species_balanced"]["overall_concentration_supported"],
            "decline_coupling_supported": macro["beta_within_species"]["decline_coupling_supported"],
            "symmetry_pattern": macro["trend_class_species_balanced"]["pattern"],
        },
        "boundary": [
            "This analysis is valid only after the frozen Stage-A and Stage-B gates pass.",
            "E is effective monitored-component number, not occupied area.",
            "No traits, lags, alternate trend thresholds, or alternate component definitions are opened after this result.",
        ],
    }
    return result, frame


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--support-json", required=True, type=Path)
    p.add_argument("--balance-json", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-panels-csv", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()

    result, frame = run(
        a.input,
        a.support_json,
        a.balance_json,
        assume_whole_colony_extract=a.assume_whole_colony_extract,
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    frame.to_csv(a.out_panels_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
