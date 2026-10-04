#!/usr/bin/env python3
"""Pre-outcome recovery test for the frozen dynamic-island Paper 2D estimator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


NETWORKS = {
    ("ADPE", "South Shetland Islands"): 6,
    ("ADPE", "Victoria Land"): 24,
    ("CHPE", "Central-west Antarctic Peninsula"): 17,
    ("CHPE", "South Shetland Islands"): 14,
    ("GEPE", "Central-west Antarctic Peninsula"): 18,
    ("GEPE", "South Shetland Islands"): 6,
}
SPECIES = ("ADPE", "CHPE", "GEPE")


def parse_seasons(value) -> list[int]:
    return sorted({int(x) for x in str(value).split(";") if str(x).strip() and str(x).lower() != "nan"})


def build_primary_frame(forcing_csv: Path, exposure_csv: Path) -> pd.DataFrame:
    f = pd.read_csv(forcing_csv)
    e = pd.read_csv(exposure_csv)
    needed = {"site_id", "rate_p50_per_year", "rate_p67_per_year"}
    if not needed.issubset(e.columns):
        raise ValueError(f"missing exposure columns: {sorted(needed-set(e.columns))}")
    x = f.merge(e[list(needed)], on="site_id", how="inner", validate="m:1")
    pieces = []
    for (sp, region), expected in NETWORKS.items():
        g = x[(x.species_id.astype(str) == sp) & (x.region.astype(str) == region)].copy()
        if len(g) != expected:
            raise ValueError(f"primary roster drift {sp} / {region}: {len(g)} != {expected}")
        pieces.append(g)
    out = pd.concat(pieces, ignore_index=True)
    if len(out) != 85:
        raise ValueError(f"primary unit drift: {len(out)} != 85")
    return out.sort_values(["species_id", "region", "site_id"]).reset_index(drop=True)


def observation_schedule(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in frame.iterrows():
        for season in parse_seasons(r.seasons):
            rows.append({
                "unit_id": r.unit_id,
                "site_id": r.site_id,
                "species_id": r.species_id,
                "region": r.region,
                "season": season,
                "h_raw": float(r.rate_p50_per_year),
            })
    d = pd.DataFrame(rows)
    # Require contemporaneous cross-site support exactly as frozen.
    counts = d.groupby(["species_id", "region", "season"]).size().rename("n_contemporary")
    d = d.merge(counts, on=["species_id", "region", "season"], how="left")
    d = d[d.n_contemporary >= 3].copy()
    # Species-standardized exposure is fixed from the unit roster, not observation frequency.
    stats = frame.groupby("species_id").rate_p50_per_year.agg(["mean", "std"])
    zmap = {}
    for _, r in frame.iterrows():
        mu = float(stats.loc[r.species_id, "mean"])
        sd = float(stats.loc[r.species_id, "std"])
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError(f"zero exposure SD for {r.species_id}")
        zmap[r.unit_id] = (float(r.rate_p50_per_year) - mu) / sd
    d["h_z"] = d.unit_id.map(zmap)
    for sp in SPECIES:
        mask = d.species_id.eq(sp)
        mean_t = float(d.loc[mask, "season"].mean())
        d.loc[mask, "tau"] = (d.loc[mask, "season"].astype(float) - mean_t) / 10.0
    d["x"] = d.h_z * d.tau
    return d.reset_index(drop=True)


def _fit_ols(y: np.ndarray, x: pd.DataFrame) -> float:
    # Explicit site and region-season fixed effects; drop_first handles intercept redundancy.
    site = pd.get_dummies(x["site_id"].astype(str), prefix="site", drop_first=True, dtype=float)
    rt = pd.get_dummies(
        x["region"].astype(str) + "|" + x["season"].astype(str),
        prefix="rt", drop_first=True, dtype=float
    )
    design = pd.concat([
        pd.Series(1.0, index=x.index, name="intercept"),
        x[["x"]].astype(float),
        site.reset_index(drop=True),
        rt.reset_index(drop=True),
    ], axis=1)
    coef, *_ = np.linalg.lstsq(design.to_numpy(float), np.asarray(y, float), rcond=None)
    return float(coef[1])


def simulate_once(schedule: pd.DataFrame, beta: float, rng: np.random.Generator, noise_sd: float = 0.35) -> dict:
    result = {}
    for sp in SPECIES:
        d = schedule[schedule.species_id.eq(sp)].copy().reset_index(drop=True)
        sites = sorted(d.site_id.unique())
        rts = sorted((d.region.astype(str) + "|" + d.season.astype(str)).unique())
        a = {s: rng.normal(0, 0.8) for s in sites}
        g = {k: rng.normal(0, 0.5) for k in rts}
        y = np.array([
            a[row.site_id]
            + g[f"{row.region}|{row.season}"]
            + beta * row.x
            + rng.normal(0, noise_sd)
            for row in d.itertuples(index=False)
        ])
        result[sp] = _fit_ols(y, d)
    return result


def recovery(frame: pd.DataFrame, reps: int, seed: int) -> dict:
    schedule = observation_schedule(frame)
    rng = np.random.default_rng(seed)
    truths = [0.0, 0.15, 0.30]
    out = {}
    for truth in truths:
        rows = [simulate_once(schedule, truth, rng) for _ in range(reps)]
        by_sp = {}
        for sp in SPECIES:
            vals = np.asarray([r[sp] for r in rows], dtype=float)
            by_sp[sp] = {
                "mean_beta_hat": float(vals.mean()),
                "bias": float(vals.mean() - truth),
                "rmse": float(np.sqrt(np.mean((vals-truth)**2))),
                "positive_fraction": float(np.mean(vals > 0)),
            }
        out[str(truth)] = by_sp

    passed = True
    for sp in SPECIES:
        if abs(out["0.0"][sp]["bias"]) > 0.03:
            passed = False
        if abs(out["0.3"][sp]["bias"]) > 0.05:
            passed = False
        if out["0.3"][sp]["positive_fraction"] < 0.90:
            passed = False

    return {
        "schema_version": 1,
        "result_id": "mina-paper2d-dynamic-outcome-recovery-v1",
        "reps": reps,
        "seed": seed,
        "schedule_rows": int(len(schedule)),
        "schedule_units": int(schedule.unit_id.nunique()),
        "schedule_by_species": {
            sp: {
                "rows": int((schedule.species_id == sp).sum()),
                "units": int(schedule.loc[schedule.species_id == sp, "unit_id"].nunique()),
                "region_seasons": int(schedule.loc[schedule.species_id == sp, ["region","season"]].drop_duplicates().shape[0])
            } for sp in SPECIES
        },
        "truths": out,
        "decision": {
            "estimator_recovery_passed": bool(passed),
            "real_dynamic_association_authorized_if_other_contract_checks_pass": bool(passed)
        },
        "boundary": [
            "Synthetic recovery only; no count magnitude is read.",
            "The observed exposure distribution and frozen observation schedule are used only to reproduce the design geometry.",
            "Passing recovery validates the estimator under these simulation truths, not the biological hypothesis."
        ]
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--forcing-csv", required=True, type=Path)
    p.add_argument("--exposure-csv", required=True, type=Path)
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--reps", type=int, default=500)
    p.add_argument("--seed", type=int, default=20261004)
    a = p.parse_args()
    json.loads(a.contract.read_text(encoding="utf-8"))
    frame = build_primary_frame(a.forcing_csv, a.exposure_csv)
    result = recovery(frame, a.reps, a.seed)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["decision"]["estimator_recovery_passed"]:
        raise SystemExit("dynamic estimator recovery failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
