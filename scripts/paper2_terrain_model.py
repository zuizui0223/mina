#!/usr/bin/env python3
"""Single-trait V3 terrain loading model for Paper 2."""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

from scripts.simulate_paper2_integrated_recovery import collapse_same_season
from scripts.simulate_paper2_spatial_adjusted_v3 import build_v3_frames
from scripts.simulate_paper2_integrated_hierarchical_recovery import (
    _build_observed_intervals,
    _solve_forcing_interval,
    _profile_interval_process_sd,
    _forcing_sum,
    _interval_variance,
    _solve_constrained_system,
)

SPECIES = ("ADPE", "CHPE", "GEPE")
EXPECTED_PRIMARY = {"ADPE": 41, "CHPE": 34, "GEPE": 29}
PRIMARY_TERRAIN_FIELD = "elevation_relief_p90_p10_m_2000m"


def _zscore(values: pd.Series) -> pd.Series:
    x = pd.to_numeric(values, errors="raise").astype(float)
    sd = float(x.std(ddof=1))
    if not math.isfinite(sd) or sd <= 0:
        raise ValueError("zero/nonfinite terrain variance")
    return (x - float(x.mean())) / sd


def build_terrain_frames(
    forcing_result: dict,
    forcing_units: pd.DataFrame,
    breeding_options: pd.DataFrame,
    terrain: pd.DataFrame,
    *,
    field: str = PRIMARY_TERRAIN_FIELD,
) -> dict[str, pd.DataFrame]:
    """Attach one frozen terrain trait to the exact V3 primary frames."""
    base = build_v3_frames(forcing_result, forcing_units, breeding_options)
    if field not in terrain.columns:
        raise ValueError(f"missing terrain field: {field}")
    t = terrain[["site_id", field]].copy()
    t["site_id"] = t["site_id"].astype(str)
    if t["site_id"].duplicated().any():
        raise ValueError("duplicate terrain site_id")
    t["R_raw"] = np.log1p(pd.to_numeric(t[field], errors="raise"))
    if (~np.isfinite(t["R_raw"].to_numpy(float))).any():
        raise ValueError("nonfinite transformed terrain")

    out: dict[str, pd.DataFrame] = {}
    for sp in SPECIES:
        f = base[sp].merge(
            t[["site_id", "R_raw"]],
            on="site_id",
            how="left",
            validate="many_to_one",
        )
        if f["R_raw"].isna().any():
            missing = f.loc[f["R_raw"].isna(), "site_id"].astype(str).tolist()
            raise ValueError(f"{sp}: missing terrain for {missing}")
        f["R"] = _zscore(f["R_raw"])
        out[sp] = f.sort_values("unit_id").reset_index(drop=True)

    got = {sp: int(len(out[sp])) for sp in SPECIES}
    if got != EXPECTED_PRIMARY:
        raise ValueError(f"terrain frame drift: {got} != {EXPECTED_PRIMARY}")
    return out


def center_r_within_block(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.reset_index(drop=True).copy()
    out["Rc"] = (
        pd.to_numeric(out["R"], errors="raise")
        - out.groupby("trait_block")["R"].transform("mean")
    )
    return out


def solve_site_gamma_r(
    intervals: list[dict],
    frame: pd.DataFrame,
    forcing: dict,
    process_sd: float,
    loading_sd: float,
    *,
    min_loading_sd: float = 0.05,
):
    """One-trait analogue of the frozen V3 loading step."""
    n = len(frame)
    rtrait = frame["Rc"].to_numpy(float)
    blocks = frame["trait_block"].astype(str).to_numpy()
    levels = sorted(set(blocks.tolist()))
    B = len(levels)
    bindex = {b: j for j, b in enumerate(levels)}
    sig = max(float(loading_sd), 1e-8)

    # [site drift mu (n), gamma_R (1), block intercepts (B), residual loadings (n)]
    cols = n + 1 + B + n
    A = np.zeros((len(intervals) + n, cols), dtype=float)
    y = np.zeros(len(intervals) + n, dtype=float)
    row = 0
    for it in intervals:
        i = int(it["site"])
        fsum = _forcing_sum(forcing, it)
        w = 1.0 / np.sqrt(max(_interval_variance(it, process_sd), 1e-12))
        A[row, i] = float(it["duration"]) * w
        A[row, n] = fsum * rtrait[i] * w
        A[row, n + 1 + bindex[str(blocks[i])]] = fsum * w
        A[row, n + 1 + B + i] = fsum * w
        y[row] = (float(it["delta"]) - fsum) * w
        row += 1

    for i in range(n):
        A[row, n + 1 + B + i] = 1.0 / sig
        row += 1

    C = np.zeros((B + 1, cols), dtype=float)
    # residual loadings mean zero within each block
    for bi, b in enumerate(levels):
        idx = np.flatnonzero(blocks == b)
        C[bi, n + 1 + B + idx] = 1.0 / len(idx)
    # site-count-weighted mean block intercept is zero
    for b in levels:
        idx = np.flatnonzero(blocks == b)
        C[B, n + 1 + bindex[b]] = len(idx) / n

    sol = _solve_constrained_system(A, y, C)
    mu = sol[:n]
    gamma_r = float(sol[n])
    alpha = sol[n + 1 : n + 1 + B]
    resid = sol[n + 1 + B :]
    lam = (
        1.0
        + rtrait * gamma_r
        + np.asarray([alpha[bindex[str(b)]] for b in blocks])
        + resid
    )
    loading_sd_new = max(
        float(np.sqrt(np.mean(resid * resid))),
        float(min_loading_sd),
    )
    return mu, lam, gamma_r, alpha, resid, loading_sd_new


def fit_terrain_species(
    frame: pd.DataFrame,
    observations: pd.DataFrame,
    *,
    delta_image: float,
    sigma1: float,
    sigma2plus: float,
    truth_forcing: dict | None = None,
    true_lambda: list[float] | None = None,
    iterations: int = 12,
) -> dict:
    f = center_r_within_block(frame)
    collapsed = collapse_same_season(
        observations,
        delta_image=delta_image,
        sigma1=sigma1,
        sigma2plus=sigma2plus,
    )
    intervals = _build_observed_intervals(f, collapsed)
    n = len(f)
    lam = np.ones(n, dtype=float)
    process_sd = 0.10
    loading_sd = 0.30
    mu, forcing = _solve_forcing_interval(intervals, f, lam, process_sd)
    alpha = np.zeros(f["trait_block"].nunique(), dtype=float)
    resid = np.zeros(n, dtype=float)
    gamma_r = 0.0

    for _ in range(iterations):
        mu, forcing = _solve_forcing_interval(intervals, f, lam, process_sd)
        mu, lam, gamma_r, alpha, resid, loading_sd = solve_site_gamma_r(
            intervals, f, forcing, process_sd, loading_sd
        )
        process_sd = _profile_interval_process_sd(intervals, mu, lam, forcing)

    mu, forcing = _solve_forcing_interval(intervals, f, lam, process_sd)
    mu, lam, gamma_r, alpha, resid, loading_sd = solve_site_gamma_r(
        intervals, f, forcing, process_sd, loading_sd
    )

    forcing_corr = {}
    if truth_forcing is not None:
        for g, values in forcing.items():
            forcing_corr[g] = float(
                np.corrcoef(
                    np.asarray(truth_forcing[g], dtype=float),
                    np.asarray(values, dtype=float),
                )[0, 1]
            )
    lambda_corr = None
    if true_lambda is not None:
        lambda_corr = float(
            np.corrcoef(
                np.asarray(true_lambda, dtype=float),
                np.asarray(lam, dtype=float),
            )[0, 1]
        )

    levels = sorted(f["trait_block"].astype(str).unique())
    blocks = f["trait_block"].astype(str).to_numpy()
    return {
        "gamma_r": float(gamma_r),
        "process_sd": float(process_sd),
        "loading_residual_sd": float(loading_sd),
        "block_intercepts": {
            b: float(alpha[i]) for i, b in enumerate(levels)
        },
        "block_mean_lambda": {
            b: float(
                lam[np.flatnonzero(blocks == b)].mean()
            )
            for b in levels
        },
        "forcing_correlation": forcing_corr,
        "lambda_correlation": lambda_corr,
        "n_units": int(len(f)),
        "n_collapsed_seasons": int(len(collapsed)),
    }
