#!/usr/bin/env python3
"""First and frozen real dynamic-island association for Antarctic Paper 2D."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.run_paper2_real_v3_fit import (
    build_frozen_real_records,
    calibrate_observation,
)


SPECIES = ("ADPE", "CHPE", "GEPE")


def _load_rda(path: Path, expected: str) -> pd.DataFrame:
    x = pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x) == 1:
        return next(iter(x.values()))
    raise ValueError(expected)


def holm_adjust(pvals: dict[str, float]) -> dict[str, float]:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted = {}
    running = 0.0
    for rank, (name, p) in enumerate(items, start=1):
        value = min(1.0, (m - rank + 1) * float(p))
        running = max(running, value)
        adjusted[name] = running
    return {k: float(adjusted[k]) for k in pvals}


def collapse_records(records: pd.DataFrame, cal: dict) -> pd.DataFrame:
    x = records.copy()
    x["log1p_count"] = np.log1p(pd.to_numeric(x["count"], errors="raise").astype(float))
    delta = float(cal["delta_image"])
    x["corrected"] = (
        x["log1p_count"]
        - delta * x["vantage_family"].astype(str).eq("image_based").astype(float)
    )
    sigma1 = float(cal["accuracy"]["1"]["sigma"])
    sigma25 = float(cal["accuracy"]["2-5"]["sigma"])
    x["obs_var"] = np.where(
        x["accuracy_group"].astype(str).eq("1"),
        sigma1**2,
        sigma25**2,
    )
    x["precision"] = 1.0 / x["obs_var"]
    x["wy"] = x["precision"] * x["corrected"]
    g = x.groupby(["site_id","species_id","season"], as_index=False).agg(
        sum_w=("precision","sum"),
        sum_wy=("wy","sum"),
        n_records=("corrected","size"),
    )
    g["y"] = g["sum_wy"] / g["sum_w"]
    g["collapsed_var"] = 1.0 / g["sum_w"]
    return g


def parse_contract_networks(contract: dict) -> pd.DataFrame:
    rows = []
    for n in contract["primary_roster"]["networks"]:
        rows.append({
            "species_id": str(n["species_id"]),
            "region": str(n["region"]),
            "expected_units": int(n["units"]),
        })
    return pd.DataFrame(rows)


def build_unit_frame(forcing: pd.DataFrame, exposure: pd.DataFrame, contract: dict, exposure_field: str) -> pd.DataFrame:
    ecols = {"site_id", exposure_field}
    if not ecols.issubset(exposure.columns):
        raise ValueError(f"missing exposure fields: {sorted(ecols-set(exposure.columns))}")
    x = forcing.merge(exposure[["site_id", exposure_field]], on="site_id", how="inner", validate="m:1")
    pieces = []
    for row in parse_contract_networks(contract).itertuples(index=False):
        g = x[
            x["species_id"].astype(str).eq(row.species_id)
            & x["region"].astype(str).eq(row.region)
        ].copy()
        if len(g) != row.expected_units:
            raise ValueError(
                f"roster drift {row.species_id}/{row.region}: {len(g)} != {row.expected_units}"
            )
        pieces.append(g)
    out = pd.concat(pieces, ignore_index=True)
    if len(out) != int(contract["primary_roster"]["units"]):
        raise ValueError("primary unit count drift")
    out = out.sort_values(["species_id","region","site_id"]).reset_index(drop=True)
    # Species-level standardization is based on unit roster, not observation frequency.
    out["h_z"] = np.nan
    for sp in SPECIES:
        mask = out["species_id"].astype(str).eq(sp)
        vals = pd.to_numeric(out.loc[mask, exposure_field], errors="raise").astype(float)
        sd = float(vals.std(ddof=1))
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError(f"zero exposure variance for {sp}")
        out.loc[mask, "h_z"] = (vals - float(vals.mean())) / sd
    out["unit_id"] = out["species_id"].astype(str) + "|" + out["site_id"].astype(str)
    return out


def build_analysis_rows(collapsed: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    x = collapsed.merge(
        units[["unit_id","site_id","species_id","region","h_z"]],
        on=["site_id","species_id"],
        how="inner",
        validate="m:1",
    )
    # Require contemporaneous support of >=3 sites in every species-region-season.
    counts = x.groupby(["species_id","region","season"]).size().rename("n_contemporary")
    x = x.merge(counts, on=["species_id","region","season"], how="left")
    x = x[x["n_contemporary"] >= 3].copy()
    for sp in SPECIES:
        mask = x["species_id"].astype(str).eq(sp)
        mean_t = float(x.loc[mask, "season"].mean())
        x.loc[mask, "tau"] = (x.loc[mask, "season"].astype(float) - mean_t) / 10.0
    x["x"] = x["h_z"].astype(float) * x["tau"].astype(float)
    return x.sort_values(["species_id","region","season","site_id"]).reset_index(drop=True)


def nuisance_qr(d: pd.DataFrame):
    site = pd.get_dummies(d["site_id"].astype(str), prefix="site", drop_first=True, dtype=float)
    rt = pd.get_dummies(
        d["region"].astype(str) + "|" + d["season"].astype(str),
        prefix="rt", drop_first=True, dtype=float
    )
    D = pd.concat([
        pd.Series(1.0, index=d.index, name="intercept"),
        site.reset_index(drop=True),
        rt.reset_index(drop=True),
    ], axis=1).to_numpy(float)
    q, _ = np.linalg.qr(D, mode="reduced")
    return q


def residualize(q: np.ndarray, v: np.ndarray) -> np.ndarray:
    return v - q @ (q.T @ v)


def beta_from_residuals(xr: np.ndarray, yr: np.ndarray, weights: np.ndarray | None = None) -> float:
    if weights is None:
        denom = float(xr @ xr)
        if denom <= 0:
            raise ValueError("zero residualized exposure variance")
        return float((xr @ yr) / denom)
    w = np.asarray(weights, float)
    denom = float(np.sum(w * xr * xr))
    if denom <= 0:
        raise ValueError("zero weighted residualized exposure variance")
    return float(np.sum(w * xr * yr) / denom)


def observed_fit(d: pd.DataFrame) -> dict:
    q = nuisance_qr(d)
    y = d["y"].to_numpy(float)
    x = d["x"].to_numpy(float)
    yr = residualize(q, y)
    xr = residualize(q, x)
    beta = beta_from_residuals(xr, yr)
    # Frozen precision-weighted sensitivity: residualize sqrt(w)* variables and nuisance.
    w = 1.0 / d["collapsed_var"].to_numpy(float)
    sw = np.sqrt(w)
    site = pd.get_dummies(d["site_id"].astype(str), prefix="site", drop_first=True, dtype=float)
    rt = pd.get_dummies(
        d["region"].astype(str) + "|" + d["season"].astype(str),
        prefix="rt", drop_first=True, dtype=float
    )
    D = pd.concat([
        pd.Series(1.0, index=d.index, name="intercept"),
        site.reset_index(drop=True),
        rt.reset_index(drop=True),
    ], axis=1).to_numpy(float)
    qw, _ = np.linalg.qr(D * sw[:,None], mode="reduced")
    yrw = residualize(qw, y * sw)
    xrw = residualize(qw, x * sw)
    beta_w = beta_from_residuals(xrw, yrw)

    # Cluster-robust SE for the primary coefficient after FWL, clustered by physical site.
    resid = yr - beta * xr
    denom = float(xr @ xr)
    meat = 0.0
    for _, idx in d.groupby("site_id").groups.items():
        ii = np.asarray(list(idx), dtype=int)
        score = float(np.sum(xr[ii] * resid[ii]))
        meat += score * score
    se = float(np.sqrt(meat / (denom * denom)))
    return {
        "beta": beta,
        "cluster_site_se": se,
        "precision_weighted_beta": beta_w,
        "n_rows": int(len(d)),
        "n_units": int(d["site_id"].nunique()),
        "n_region_seasons": int(d[["region","season"]].drop_duplicates().shape[0]),
        "_q": q,
        "_yr": yr,
    }


def exposure_basis(d: pd.DataFrame, q: np.ndarray) -> tuple[np.ndarray, list[str], dict[str,list[int]]]:
    sites = sorted(d["site_id"].astype(str).unique())
    site_index = {s:i for i,s in enumerate(sites)}
    B = np.zeros((len(d), len(sites)), dtype=float)
    for row_i, row in enumerate(d.itertuples(index=False)):
        B[row_i, site_index[str(row.site_id)]] = float(row.tau)
    Br = B - q @ (q.T @ B)
    by_region = {}
    unit_region = d[["site_id","region"]].drop_duplicates()
    for region, g in unit_region.groupby("region"):
        by_region[str(region)] = [site_index[s] for s in g["site_id"].astype(str)]
    return Br, sites, by_region


def permutation_p(d: pd.DataFrame, fit: dict, Bn: int, seed: int) -> tuple[float, dict]:
    q = fit["_q"]
    yr = fit["_yr"]
    Br, sites, by_region = exposure_basis(d, q)
    hmap = d[["site_id","h_z"]].drop_duplicates().set_index("site_id")["h_z"].to_dict()
    h0 = np.asarray([float(hmap[s]) for s in sites], dtype=float)
    observed = float(fit["beta"])
    rng = np.random.default_rng(seed)
    ge = 0
    batch = 250
    produced = 0
    null_sum = 0.0
    null_sumsq = 0.0
    while produced < Bn:
        k = min(batch, Bn-produced)
        H = np.repeat(h0[:,None], k, axis=1)
        for cols in by_region.values():
            base = h0[np.asarray(cols)]
            for j in range(k):
                H[np.asarray(cols), j] = rng.permutation(base)
        XR = Br @ H
        num = yr @ XR
        den = np.sum(XR*XR, axis=0)
        vals = num / den
        ge += int(np.sum(vals >= observed))
        null_sum += float(np.sum(vals))
        null_sumsq += float(np.sum(vals*vals))
        produced += k
    p = (1 + ge) / (Bn + 1)
    mean = null_sum/Bn
    sd = float(np.sqrt(max(0.0, null_sumsq/Bn - mean*mean)))
    return float(p), {"null_mean": float(mean), "null_sd": sd, "permutations": int(Bn)}


def run_one_exposure(collapsed, forcing, exposure, contract, exposure_field, Bn, seed):
    units = build_unit_frame(forcing, exposure, contract, exposure_field)
    rows = build_analysis_rows(collapsed, units)
    species_out = {}
    raw_p = {}
    for offset, sp in enumerate(SPECIES):
        d = rows[rows["species_id"].astype(str).eq(sp)].copy().reset_index(drop=True)
        fit = observed_fit(d)
        p, null = permutation_p(d, fit, Bn, seed + offset*100003)
        raw_p[sp] = p
        species_out[sp] = {
            k:v for k,v in fit.items() if not str(k).startswith("_")
        }
        species_out[sp]["permutation_p_one_sided_positive"] = p
        species_out[sp]["permutation_null"] = null
        species_out[sp]["regions"] = sorted(d["region"].astype(str).unique().tolist())
    adj = holm_adjust(raw_p)
    for sp in SPECIES:
        species_out[sp]["holm_p"] = adj[sp]
    betas = np.asarray([species_out[sp]["beta"] for sp in SPECIES], dtype=float)
    return {
        "exposure_field": exposure_field,
        "species": species_out,
        "cross_species_descriptive": {
            "median_beta": float(np.median(betas)),
            "positive_species": int(np.sum(betas > 0)),
            "all_positive": bool(np.all(betas > 0)),
        },
        "analysis_rows": int(len(rows)),
        "analysis_units": int(rows[["site_id","species_id"]].drop_duplicates().shape[0]),
    }, rows


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--unlock-contract", required=True, type=Path)
    p.add_argument("--recovery-json", required=True, type=Path)
    p.add_argument("--forcing-csv", required=True, type=Path)
    p.add_argument("--exposure-csv", required=True, type=Path)
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-collapsed-csv", required=True, type=Path)
    args = p.parse_args()

    unlock = json.loads(args.unlock_contract.read_text(encoding="utf-8"))
    if unlock.get("status") != "UNLOCKED_FOR_FROZEN_DYNAMIC_EXECUTION":
        raise SystemExit("dynamic outcome remains locked")
    recovery = json.loads(args.recovery_json.read_text(encoding="utf-8"))
    if not recovery.get("decision",{}).get("estimator_recovery_passed"):
        raise SystemExit("dynamic estimator recovery did not pass")
    contract = json.loads(
        (args.unlock_contract.parent / "ANTARCTIC_ISLAND_ECOLOGY_PAPER2D_DYNAMIC_OUTCOME_V1.json").read_text(encoding="utf-8")
    )

    forcing = pd.read_csv(args.forcing_csv)
    exposure = pd.read_csv(args.exposure_csv)
    obs = _load_rda(args.mapppdr_dir / "data" / "penguin_obs.rda", "penguin_obs")
    records = build_frozen_real_records(obs)
    cal = calibrate_observation(records)
    collapsed = collapse_records(records, cal)

    Bn = int(unlock["primary"]["permutations"])
    seed = int(unlock["primary"]["seed"])
    primary, rows_primary = run_one_exposure(
        collapsed, forcing, exposure, contract, "rate_p50_per_year", Bn, seed
    )
    p67, _ = run_one_exposure(
        collapsed, forcing, exposure, contract, "rate_p67_per_year", Bn, seed + 700000
    )

    result = {
        "schema_version": 1,
        "analysis_id": "mina-paper2d-first-real-dynamic-outcome-v1",
        "observation_calibration": {
            "delta_image": float(cal["delta_image"]),
            "image_multiplicative_factor": float(np.exp(cal["delta_image"])),
            "sigma_accuracy_1": float(cal["accuracy"]["1"]["sigma"]),
            "sigma_accuracy_2_5": float(cal["accuracy"]["2-5"]["sigma"]),
        },
        "primary_p50": primary,
        "measurement_sensitivity_p67": p67,
        "provenance": {
            "mapppdr_commit": "88c73a507e0921b2541c218c71eaf16721bc6502",
            "real_dynamic_association_opened": true,
            "model_contract": contract["contract_id"],
            "execution_contract": unlock["contract_id"],
        },
        "claim_boundary": [
            "This tests relative breeding-use change, not literal occupied guano footprint.",
            "Region-season fixed effects remove contemporaneous regional mean state before estimating the exposure-linked trend difference.",
            "Marine covariates remain locked.",
            "No model, roster, exposure threshold or region is changed after this result."
        ]
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows_primary.to_csv(args.out_collapsed_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
