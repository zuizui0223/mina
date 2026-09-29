#!/usr/bin/env python3
"""Pre-state-space empirical coupling diagnostic for mina Paper 2."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr
import statsmodels.api as sm

SPECIES = ("ADPE", "CHPE", "GEPE")
DIRECT = {"ground", "aerial", "offshore vessel"}
IMAGE = {"ground photo", "aerial photo", "uav", "vhr", "landsat", "sentinel"}
WINDOW = (1980, 2025)


def family(value) -> str:
    if pd.isna(value):
        return "unknown"
    v = str(value).strip().lower()
    if v in DIRECT:
        return "direct"
    if v in IMAGE:
        return "image_based"
    return "unknown"


def estimate_image_offsets(obs: pd.DataFrame) -> dict[str, float]:
    """Estimate species-specific image minus direct offsets on log1p scale."""
    x = obs.copy()
    x["count_num"] = pd.to_numeric(x["count"], errors="coerce")
    x = x[x["count_num"].notna() & (x["count_num"] >= 0)].copy()
    x["family"] = x["vantage"].map(family)
    x["log_count"] = np.log1p(x["count_num"].astype(float))

    offsets: dict[str, float] = {}
    for sp in sorted(set(x["species_id"].astype(str))):
        local = x[x["species_id"].astype(str) == sp]
        diffs = []
        for _, g in local.groupby(["site_id", "species_id", "season"], dropna=False):
            direct = g.loc[g["family"] == "direct", "log_count"]
            image = g.loc[g["family"] == "image_based", "log_count"]
            if len(direct) and len(image):
                diffs.append(float(np.median(image) - np.median(direct)))
        offsets[sp] = float(np.median(diffs)) if diffs else 0.0
    return offsets


def image_offset_support(obs: pd.DataFrame, offsets: dict[str, float]) -> dict:
    x = obs.copy()
    x["family"] = x["vantage"].map(family)
    out = {}
    for sp in SPECIES:
        local = x[x["species_id"].astype(str) == sp]
        mixed = 0
        for _, g in local.groupby(["site_id", "species_id", "season"], dropna=False):
            fams = set(g["family"])
            if {"direct", "image_based"} <= fams:
                mixed += 1
        out[sp] = {
            "mixed_site_species_seasons": int(mixed),
            "image_log_offset": float(offsets.get(sp, 0.0)),
        }
    return out


def aggregate_site_season(obs: pd.DataFrame, offsets: dict[str, float]) -> pd.DataFrame:
    x = obs.copy()
    x["count_num"] = pd.to_numeric(x["count"], errors="coerce")
    x["season"] = pd.to_numeric(x["season"], errors="coerce")
    x = x[
        x["count_num"].notna()
        & (x["count_num"] >= 0)
        & x["season"].notna()
    ].copy()
    x["species_id"] = x["species_id"].astype(str)
    x["site_id"] = x["site_id"].astype(str)
    x["season"] = x["season"].astype(int)
    x["family"] = x["vantage"].map(family)
    x["adjusted_log_count"] = np.log1p(x["count_num"].astype(float))
    is_image = x["family"] == "image_based"
    x.loc[is_image, "adjusted_log_count"] -= x.loc[is_image, "species_id"].map(
        offsets
    ).fillna(0.0)
    result = (
        x.groupby(["site_id", "species_id", "season"], as_index=False)[
            "adjusted_log_count"
        ]
        .median()
        .sort_values(["species_id", "site_id", "season"])
        .reset_index(drop=True)
    )
    result["unit_id"] = result["species_id"] + "|" + result["site_id"]
    return result


def detrend_units(season_frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    residual_rows = []
    trend_rows = []
    for unit_id, g in season_frame.groupby("unit_id"):
        g = g.sort_values("season")
        if len(g) < 3:
            continue
        season = g["season"].to_numpy(dtype=float)
        y = g["adjusted_log_count"].to_numpy(dtype=float)
        centered = season - season.mean()
        X = np.column_stack([np.ones(len(g)), centered])
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        fitted = X @ beta
        resid = y - fitted
        species_id = str(g["species_id"].iloc[0])
        site_id = str(g["site_id"].iloc[0])
        trend_rows.append(
            {
                "unit_id": unit_id,
                "site_id": site_id,
                "species_id": species_id,
                "trend_slope": float(beta[1]),
                "n_seasons": int(len(g)),
                "residual_sd": float(np.std(resid, ddof=1)) if len(g) > 1 else 0.0,
            }
        )
        for idx, row in enumerate(g.itertuples(index=False)):
            residual_rows.append(
                {
                    "unit_id": unit_id,
                    "site_id": site_id,
                    "species_id": species_id,
                    "season": int(row.season),
                    "residual": float(resid[idx]),
                    "forcing_group": str(row.forcing_group),
                }
            )
    return pd.DataFrame(residual_rows), pd.DataFrame(trend_rows)


def leave_one_out_forcing(
    residuals: pd.DataFrame,
    min_peers: int = 3,
) -> pd.DataFrame:
    """Attach a peer-only contemporaneous forcing to each focal residual."""
    out = []
    for (sp, group, season), g in residuals.groupby(
        ["species_id", "forcing_group", "season"]
    ):
        rows = list(g.itertuples(index=False))
        for row in rows:
            peers = [r.residual for r in rows if r.unit_id != row.unit_id]
            if len(peers) < min_peers:
                continue
            out.append(
                {
                    "unit_id": row.unit_id,
                    "site_id": row.site_id,
                    "species_id": sp,
                    "forcing_group": group,
                    "season": int(season),
                    "residual": float(row.residual),
                    "forcing_raw": float(np.median(peers)),
                    "peer_n": int(len(peers)),
                }
            )
    return pd.DataFrame(out)


def estimate_lambda(frame: pd.DataFrame, min_n: int = 6) -> dict | None:
    x = frame[["residual", "forcing_raw"]].dropna()
    if len(x) < min_n:
        return None
    f = x["forcing_raw"].to_numpy(dtype=float)
    sd = float(np.std(f, ddof=1))
    if not np.isfinite(sd) or sd <= 1e-12:
        return None
    z = (f - float(np.mean(f))) / sd
    y = x["residual"].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(x)), z])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    pred = X @ beta
    sst = float(np.sum((y - np.mean(y)) ** 2))
    sse = float(np.sum((y - pred) ** 2))
    r2 = 1.0 - sse / sst if sst > 0 else 0.0
    return {
        "lambda": float(beta[1]),
        "lambda_intercept": float(beta[0]),
        "n_matched": int(len(x)),
        "forcing_raw_sd": sd,
        "lambda_r2": float(r2),
    }


def estimate_all_lambdas(
    matched: pd.DataFrame,
    min_n: int = 6,
) -> pd.DataFrame:
    rows = []
    for unit_id, g in matched.groupby("unit_id"):
        fit = estimate_lambda(g, min_n=min_n)
        if fit is None:
            continue
        rows.append(
            {
                "unit_id": unit_id,
                "site_id": str(g["site_id"].iloc[0]),
                "species_id": str(g["species_id"].iloc[0]),
                "forcing_group": str(g["forcing_group"].iloc[0]),
                **fit,
            }
        )
    return pd.DataFrame(rows)


def _design_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    X = pd.DataFrame(
        {
            "intercept": 1.0,
            "A": df["A"].astype(float),
            "H": df["H"].astype(float),
            "R": df["R"].astype(float),
            "A_x_H": (df["A"] * df["H"]).astype(float),
        },
        index=df.index,
    )
    groups = sorted(df["forcing_group"].astype(str).unique())
    for group in groups[1:]:
        X[f"group[{group}]"] = (df["forcing_group"].astype(str) == group).astype(float)
    return X, groups


def fit_trait_regression(
    df: pd.DataFrame,
    response: str,
    permutations: int = 5000,
    seed: int = 20260929,
) -> dict:
    data = df[[response, "A", "H", "R", "forcing_group"]].dropna().copy()
    X, groups = _design_matrix(data)
    y = data[response].astype(float)
    fit = sm.OLS(y, X).fit(cov_type="HC3")
    coeff = {k: float(v) for k, v in fit.params.items()}
    ses = {k: float(v) for k, v in fit.bse.items()}
    pvals = {k: float(v) for k, v in fit.pvalues.items()}
    beta_h = coeff["H"]
    beta_ah = coeff["A_x_H"]

    perm_p = None
    if permutations:
        rng = np.random.default_rng(seed)
        Xn = X.to_numpy(dtype=float)
        yi = y.to_numpy(dtype=float)
        interaction_index = list(X.columns).index("A_x_H")
        labels = data["forcing_group"].astype(str).to_numpy()
        perm_betas = np.empty(permutations, dtype=float)
        for b in range(permutations):
            yp = yi.copy()
            for group in groups:
                idx = np.flatnonzero(labels == group)
                yp[idx] = yi[rng.permutation(idx)]
            perm_betas[b] = np.linalg.lstsq(Xn, yp, rcond=None)[0][interaction_index]
        perm_p = float((1 + np.sum(perm_betas <= beta_ah)) / (permutations + 1))

    low = float(beta_h - beta_ah)
    high = float(beta_h + beta_ah)
    return {
        "n": int(len(data)),
        "forcing_groups": {
            str(k): int(v)
            for k, v in data["forcing_group"].astype(str).value_counts().sort_index().items()
        },
        "coefficients": coeff,
        "hc3_se": ses,
        "hc3_p_two_sided": pvals,
        "beta_AH_permutation_p_one_sided_negative": perm_p,
        "marginal_H_at_A_minus1": low,
        "marginal_H_at_A_plus1": high,
        "crossover_direction_pattern": bool(beta_ah < 0 and low >= 0 and high < 0),
    }


def _load_rda(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        value = result[expected]
    elif len(result) == 1:
        value = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(value, pd.DataFrame):
        raise TypeError(expected)
    return value


def _z(series: pd.Series) -> pd.Series:
    x = series.astype(float)
    sd = float(x.std(ddof=1))
    if not np.isfinite(sd) or sd <= 1e-12:
        raise ValueError("cannot standardize constant predictor")
    return (x - float(x.mean())) / sd


def build_trait_table(options: pd.DataFrame, terrain: pd.DataFrame) -> pd.DataFrame:
    left = options[
        [
            "site_id",
            "region",
            "ccamlr_id",
            "mapped_ice_free_area_ha_2000m",
            "tier2_richness_2000m",
        ]
    ].copy()
    right = terrain[["site_id", "elevation_relief_p90_p10_m_2000m"]].copy()
    left["site_id"] = left["site_id"].astype(str)
    right["site_id"] = right["site_id"].astype(str)
    return left.merge(right, on="site_id", how="left", validate="one_to_one")


def assign_forcing_groups(
    season_frame: pd.DataFrame,
    traits: pd.DataFrame,
    support: dict,
) -> pd.DataFrame:
    x = season_frame.merge(
        traits[["site_id", "region", "ccamlr_id"]],
        on="site_id",
        how="left",
        validate="many_to_one",
    )
    pieces = []
    eligibility = support["decision"]["modeling_eligibility_by_species"]
    for sp in SPECIES:
        info = eligibility[sp]
        covered = set(info["covered_units"])
        level = info["level"]
        field = "region" if level == "apbp_region" else "ccamlr_id"
        allowed = {str(v) for v in info["qualifying_groups"]}
        local = x[
            (x["species_id"] == sp)
            & x["unit_id"].isin(covered)
        ].copy()
        local["forcing_group"] = local[field].astype(str)
        local = local[local["forcing_group"].isin(allowed)].copy()
        pieces.append(local)
    return pd.concat(pieces, ignore_index=True)


def prepare_species_model_frame(
    lambdas: pd.DataFrame,
    trends: pd.DataFrame,
    traits: pd.DataFrame,
    species_id: str,
) -> pd.DataFrame:
    x = lambdas[lambdas["species_id"] == species_id].merge(
        trends[["unit_id", "trend_slope", "residual_sd"]],
        on="unit_id",
        how="left",
        validate="one_to_one",
    )
    x = x.merge(
        traits[
            [
                "site_id",
                "mapped_ice_free_area_ha_2000m",
                "tier2_richness_2000m",
                "elevation_relief_p90_p10_m_2000m",
            ]
        ],
        on="site_id",
        how="left",
        validate="many_to_one",
    )
    x["A_raw"] = np.log1p(pd.to_numeric(x["mapped_ice_free_area_ha_2000m"], errors="coerce"))
    x["H_raw"] = pd.to_numeric(x["tier2_richness_2000m"], errors="coerce")
    x["R_raw"] = np.log1p(
        pd.to_numeric(x["elevation_relief_p90_p10_m_2000m"], errors="coerce")
    )
    x = x.dropna(subset=["A_raw", "H_raw", "R_raw", "lambda"]).copy()
    x["A"] = _z(x["A_raw"])
    x["H"] = _z(x["H_raw"])
    x["R"] = _z(x["R_raw"])
    return x


def run_pipeline(
    obs: pd.DataFrame,
    support: dict,
    options: pd.DataFrame,
    terrain: pd.DataFrame,
    permutations: int = 5000,
    direct_only: bool = False,
) -> tuple[dict, pd.DataFrame]:
    traits = build_trait_table(options, terrain)
    eligibility = support["decision"]["modeling_eligibility_by_species"]
    covered = {
        unit
        for sp in SPECIES
        for unit in eligibility[sp]["covered_units"]
    }

    x = obs[
        obs["species_id"].astype(str).isin(SPECIES)
        & (obs["type"] == "nests")
        & obs["count"].notna()
    ].copy()
    x["species_id"] = x["species_id"].astype(str)
    x["site_id"] = x["site_id"].astype(str)
    x["unit_id"] = x["species_id"] + "|" + x["site_id"]
    x["season"] = pd.to_numeric(x["season"], errors="coerce")
    x = x[
        x["unit_id"].isin(covered)
        & x["season"].between(WINDOW[0], WINDOW[1], inclusive="both")
    ].copy()
    if direct_only:
        x = x[x["vantage"].map(family) == "direct"].copy()

    offsets = (
        {sp: 0.0 for sp in SPECIES}
        if direct_only
        else estimate_image_offsets(x)
    )
    offset_details = image_offset_support(x, offsets)
    season_frame = aggregate_site_season(x, offsets)
    season_frame = assign_forcing_groups(season_frame, traits, support)

    residuals, trends = detrend_units(season_frame)
    matched = leave_one_out_forcing(residuals, min_peers=3)
    lambdas = estimate_all_lambdas(matched, min_n=6)

    species_results = {}
    site_outputs = []
    for sp in SPECIES:
        model_df = prepare_species_model_frame(lambdas, trends, traits, sp)
        lambda_fit = None
        trend_fit = None
        if len(model_df) >= 10 and model_df["forcing_group"].nunique() >= 2:
            lambda_fit = fit_trait_regression(
                model_df,
                "lambda",
                permutations=permutations,
                seed=20260929,
            )
            trend_fit = fit_trait_regression(
                model_df,
                "trend_slope",
                permutations=permutations,
                seed=20260929 + 100,
            )

        species_results[sp] = {
            "coupling_candidate_units": int(len(eligibility[sp]["covered_units"])),
            "lambda_estimable_units": int((lambdas["species_id"] == sp).sum()) if len(lambdas) else 0,
            "trait_complete_lambda_units": int(len(model_df)),
            "image_offset": offset_details.get(sp, {}),
            "lambda_distribution": (
                {
                    "median": float(model_df["lambda"].median()),
                    "q25": float(model_df["lambda"].quantile(0.25)),
                    "q75": float(model_df["lambda"].quantile(0.75)),
                    "min": float(model_df["lambda"].min()),
                    "max": float(model_df["lambda"].max()),
                }
                if len(model_df)
                else None
            ),
            "lambda_trait_model": lambda_fit,
            "mean_trend_trait_model": trend_fit,
        }
        if len(model_df):
            site_outputs.append(model_df)

    sites = pd.concat(site_outputs, ignore_index=True) if site_outputs else pd.DataFrame()
    result = {
        "schema_version": 1,
        "diagnostic_id": "mina-paper2-empirical-coupling-diagnostic-v1",
        "window": list(WINDOW),
        "method": "detrended abundance residual coupling to leave-one-out contemporaneous regional median",
        "direct_only": bool(direct_only),
        "species": species_results,
    }
    return result, sites


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--support-result", required=True, type=Path)
    p.add_argument("--options-csv", required=True, type=Path)
    p.add_argument("--terrain-csv", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-site-csv", required=True, type=Path)
    p.add_argument("--permutations", type=int, default=5000)
    args = p.parse_args()

    obs = _load_rda(args.mapppdr_dir / "data" / "penguin_obs.rda", "penguin_obs")
    support = json.loads(args.support_result.read_text(encoding="utf-8"))
    options = pd.read_csv(args.options_csv)
    terrain = pd.read_csv(args.terrain_csv)

    primary, sites = run_pipeline(
        obs,
        support,
        options,
        terrain,
        permutations=args.permutations,
        direct_only=False,
    )
    direct, _ = run_pipeline(
        obs,
        support,
        options,
        terrain,
        permutations=args.permutations,
        direct_only=True,
    )
    for sp in SPECIES:
        n = direct["species"][sp]["trait_complete_lambda_units"]
        primary["species"][sp]["direct_only_sensitivity"] = (
            direct["species"][sp] if n >= 20 else {"available": False, "trait_complete_lambda_units": n}
        )
    primary["boundary"] = [
        "This is an empirical pre-state-space diagnostic, not the final demographic model.",
        "Regional forcing is leave-one-out; the focal unit never contributes to its own forcing predictor.",
        "No trait, radius, forcing geography, year subset or interaction was selected from the diagnostic outcomes.",
    ]

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sites.to_csv(args.out_site_csv, index=False)
    print(json.dumps(primary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
