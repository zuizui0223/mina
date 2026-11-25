#!/usr/bin/env python3
"""Bounded MAPPPD regional breeding-site concentration test.

Uses only the pinned MAPPPD snapshot and reuses the frozen Paper 2 observation
cohort/calibration. APBP published regions are parent networks; site_id values
are monitored breeding-site components.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.run_paper2_real_v3_fit import (
    build_frozen_real_records,
    calibrate_observation,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
)
from scripts.simulate_paper2_integrated_recovery import collapse_same_season

PINNED = "88c73a507e0921b2541c218c71eaf16721bc6502"
SPECIES = ("ADPE", "CHPE", "GEPE")
MIN_COMPONENTS = 3
MIN_COMPLETE = 5
MIN_SPAN = 10
SIMULATIONS = 20_000
SEED = 20261003


def load_rda(path: Path, expected: str) -> pd.DataFrame:
    x = pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x) == 1:
        return next(iter(x.values()))
    raise ValueError(expected)


def slope(x, y) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xc = x - float(np.mean(x))
    denom = float(np.sum(xc * xc))
    if denom <= 0:
        return float("nan")
    return float(np.sum(xc * (y - float(np.mean(y)))) / denom)


def effective_number(v) -> float:
    x = np.asarray(v, dtype=float)
    total = float(np.sum(x))
    ss = float(np.sum(x * x))
    if total <= 0 or ss <= 0:
        return float("nan")
    return total * total / ss


def choose_roster(local: pd.DataFrame) -> dict:
    seasons_by_site = {
        str(site): set(int(v) for v in g["season"].unique())
        for site, g in local.groupby("site_id", sort=True)
    }
    roster = sorted(seasons_by_site)
    history = []
    while len(roster) >= MIN_COMPONENTS:
        complete = sorted(set.intersection(*(seasons_by_site[s] for s in roster)))
        span = complete[-1] - complete[0] if len(complete) >= 2 else 0
        if len(complete) >= MIN_COMPLETE and span >= MIN_SPAN:
            return {
                "eligible": True,
                "roster": roster,
                "complete_seasons": complete,
                "calendar_span": int(span),
                "pruning_history": history,
            }
        counts = {s: len(seasons_by_site[s]) for s in roster}
        m = min(counts.values())
        tied = sorted([s for s in roster if counts[s] == m])
        remove = tied[-1]
        history.append({"removed": remove, "observed_seasons": int(m)})
        roster.remove(remove)
    return {
        "eligible": False,
        "roster": roster,
        "complete_seasons": [],
        "calendar_span": 0,
        "pruning_history": history,
    }


def build_support(metadata: pd.DataFrame, sites: pd.DataFrame) -> list[dict]:
    site_meta = sites[["site_id", "region"]].copy()
    site_meta["site_id"] = site_meta["site_id"].astype(str)
    m = metadata.merge(site_meta, on="site_id", how="left", validate="many_to_one")
    if m["region"].isna().any():
        bad = sorted(m.loc[m["region"].isna(), "site_id"].astype(str).unique())
        raise ValueError(f"missing region for sites: {bad}")
    units = m[["species_id", "region", "site_id", "season"]].drop_duplicates()
    out = []
    for (sp, region), local in units.groupby(["species_id", "region"], sort=True):
        support = choose_roster(local)
        out.append({
            "species_id": str(sp),
            "region": str(region),
            "candidate_sites": int(local["site_id"].nunique()),
            "eligible": bool(support["eligible"]),
            "retained_sites": [str(x) for x in support["roster"]],
            "n_retained_sites": int(len(support["roster"])),
            "complete_seasons": [int(x) for x in support["complete_seasons"]],
            "n_complete_seasons": int(len(support["complete_seasons"])),
            "calendar_span": int(support["calendar_span"]),
            "pruning_history": support["pruning_history"],
        })
    return out


def kappa_from_matrix(count_matrix: np.ndarray, totals: np.ndarray) -> float:
    e = np.asarray([effective_number(row) for row in count_matrix], dtype=float)
    if np.any(~np.isfinite(e)) or np.any(e <= 0) or np.any(totals <= 0):
        return float("nan")
    return slope(np.log(totals), np.log(e))


def simulate_null(
    counts: np.ndarray,
    obs_var: np.ndarray,
    *,
    simulations: int,
    seed: int,
) -> dict:
    totals = np.sum(counts, axis=1)
    q = np.sum(counts, axis=0)
    q = q / float(np.sum(q))
    n_int = np.maximum(np.rint(totals).astype(int), 1)
    rng = np.random.default_rng(seed)
    kappas = np.empty(simulations, dtype=float)
    kappas_error = np.empty(simulations, dtype=float)
    for r in range(simulations):
        sim = np.vstack([rng.multinomial(int(n), q) for n in n_int]).astype(float)
        kappas[r] = kappa_from_matrix(sim, totals)
        z = np.log1p(sim)
        noisy = np.expm1(z + rng.normal(0.0, np.sqrt(obs_var)))
        noisy = np.maximum(noisy, 0.0)
        kappas_error[r] = kappa_from_matrix(noisy, totals)
    return {
        "q": q,
        "kappa_null": kappas[np.isfinite(kappas)],
        "kappa_null_error": kappas_error[np.isfinite(kappas_error)],
    }


def one_sided_p(null: np.ndarray, obs: float) -> float:
    return float((1 + np.sum(null >= obs)) / (len(null) + 1))


def sign_p(successes: int, n: int) -> float | None:
    if n <= 0:
        return None
    return float(sum(math.comb(n, k) for k in range(successes, n + 1)) / (2 ** n))


def analyse_panel(panel: dict, collapsed: pd.DataFrame, *, index: int) -> dict:
    sp = panel["species_id"]
    roster = panel["retained_sites"]
    seasons = panel["complete_seasons"]
    x = collapsed[
        collapsed["species_id"].astype(str).eq(sp)
        & collapsed["site_id"].astype(str).isin(roster)
        & collapsed["season"].isin(seasons)
    ].copy()
    x["adjusted_count"] = np.maximum(np.expm1(x["state_hat"].to_numpy(float)), 0.0)
    expected = len(roster) * len(seasons)
    if len(x) != expected:
        raise ValueError(f"incomplete panel after collapse: {sp} {panel['region']} {len(x)} != {expected}")
    pivot = x.pivot(index="season", columns="site_id", values="adjusted_count").reindex(index=seasons, columns=roster)
    varp = x.pivot(index="season", columns="site_id", values="observation_var").reindex(index=seasons, columns=roster)
    counts = pivot.to_numpy(dtype=float)
    obs_var = varp.to_numpy(dtype=float)
    totals = counts.sum(axis=1)
    e = np.asarray([effective_number(row) for row in counts], dtype=float)
    positive = (totals > 0) & np.isfinite(e) & (e > 0)
    years = np.asarray(seasons, dtype=float)[positive]
    totals2 = totals[positive]
    e2 = e[positive]
    counts2 = counts[positive]
    obsvar2 = obs_var[positive]
    if len(years) < MIN_COMPLETE:
        raise ValueError("too few positive complete seasons")
    kappa = slope(np.log(totals2), np.log(e2))
    abundance_year_slope = slope(years, np.log(totals2))
    nout = simulate_null(
        counts2, obsvar2,
        simulations=SIMULATIONS,
        seed=SEED + index * 100003,
    )
    null = nout["kappa_null"]
    nullerr = nout["kappa_null_error"]
    med = float(np.median(null))
    mederr = float(np.median(nullerr))
    p = one_sided_p(null, kappa)
    perr = one_sided_p(nullerr, kappa)
    return {
        "species_id": sp,
        "region": panel["region"],
        "retained_sites": roster,
        "n_sites": len(roster),
        "seasons": [int(v) for v in years],
        "n_seasons": int(len(years)),
        "calendar_span": int(years[-1] - years[0]),
        "first_total": float(totals2[0]),
        "last_total": float(totals2[-1]),
        "abundance_year_slope": float(abundance_year_slope),
        "direction": "decline" if abundance_year_slope < 0 else "increase" if abundance_year_slope > 0 else "flat",
        "first_E": float(e2[0]),
        "last_E": float(e2[-1]),
        "kappa_obs": float(kappa),
        "fixed_composition_null": {
            "median_kappa": med,
            "q025": float(np.quantile(null, 0.025)),
            "q975": float(np.quantile(null, 0.975)),
            "delta_kappa": float(kappa - med),
            "p_upper": p,
        },
        "observation_error_null": {
            "median_kappa": mederr,
            "q025": float(np.quantile(nullerr, 0.025)),
            "q975": float(np.quantile(nullerr, 0.975)),
            "delta_kappa": float(kappa - mederr),
            "p_upper": perr,
        },
        "supported_excess_concentration": bool(
            kappa > med and kappa > mederr and p <= 0.05 and perr <= 0.05
        ),
    }


def run(root: Path) -> dict:
    obs = load_rda(root / "data" / "penguin_obs.rda", "penguin_obs")
    sites = load_rda(root / "data" / "sites.rda", "sites")
    metadata = build_frozen_observation_metadata(obs)
    support = build_support(metadata, sites)
    eligible = [x for x in support if x["eligible"]]

    records = build_frozen_real_records(obs)
    cal = calibrate_observation(records)
    collapsed = collapse_same_season(
        records,
        delta_image=float(cal["delta_image"]),
        sigma1=float(cal["accuracy"]["1"]["sigma"]),
        sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
    )
    results = [analyse_panel(p, collapsed, index=i) for i, p in enumerate(eligible)]

    declining = [x for x in results if x["direction"] == "decline"]
    pos = sum(x["observation_error_null"]["delta_kappa"] > 0 for x in declining)
    supported = sum(x["supported_excess_concentration"] for x in declining)
    by_species = {}
    for sp in SPECIES:
        local = [x for x in results if x["species_id"] == sp]
        dec = [x for x in local if x["direction"] == "decline"]
        by_species[sp] = {
            "eligible_networks": len(local),
            "declining_networks": len(dec),
            "positive_delta_kappa_declining": sum(x["observation_error_null"]["delta_kappa"] > 0 for x in dec),
            "supported_declining": sum(x["supported_excess_concentration"] for x in dec),
            "median_delta_kappa_declining": (
                float(np.median([x["observation_error_null"]["delta_kappa"] for x in dec]))
                if dec else None
            ),
        }

    return {
        "schema_version": 1,
        "analysis_id": "mina-mapppd-regional-concentration-v1",
        "source": {"mapppdr_commit": PINNED},
        "support_gate": {
            "minimum_components": MIN_COMPONENTS,
            "minimum_complete_seasons": MIN_COMPLETE,
            "minimum_calendar_span_years": MIN_SPAN,
            "candidate_species_region_groups": len(support),
            "eligible_species_region_networks": len(eligible),
            "eligible_species": sorted(set(x["species_id"] for x in eligible)),
            "eligible_regions": sorted(set(x["region"] for x in eligible)),
        },
        "observation_calibration": {
            "delta_image": float(cal["delta_image"]),
            "sigma_accuracy_1": float(cal["accuracy"]["1"]["sigma"]),
            "sigma_accuracy_2_5": float(cal["accuracy"]["2-5"]["sigma"]),
        },
        "support_table": support,
        "panel_results": results,
        "declining_network_synthesis": {
            "n": len(declining),
            "positive_delta_kappa": int(pos),
            "supported_excess_concentration": int(supported),
            "sign_test_one_sided_p_positive": sign_p(int(pos), len(declining)),
            "median_delta_kappa_observation_error_null": (
                float(np.median([x["observation_error_null"]["delta_kappa"] for x in declining]))
                if declining else None
            ),
        },
        "species_synthesis": by_species,
        "interpretation_boundary": [
            "APBP regions are monitored geographic networks, not closed demographic populations.",
            "The analysis tests redistribution among a fixed subset of repeatedly observed sites, not total regional occupied area.",
            "MAPPPD is geographically and methodologically uneven; the observation-error sensitivity uses the previously frozen Paper 2 calibration.",
            "This is an existing-data extension after the penguin concentration rule was discovered, not an independent preregistered multi-taxon confirmation."
        ],
        "stop_rule": "No alternate radii, hand-built clusters, thresholds, lags, hinges, or trait searches are opened from this result."
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()
    out = run(a.mapppdr_dir)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "support_gate": out["support_gate"],
        "declining_network_synthesis": out["declining_network_synthesis"],
        "species_synthesis": out["species_synthesis"],
        "panels": [
            {
                "species_id": x["species_id"],
                "region": x["region"],
                "n_sites": x["n_sites"],
                "n_seasons": x["n_seasons"],
                "direction": x["direction"],
                "kappa_obs": x["kappa_obs"],
                "delta_kappa": x["observation_error_null"]["delta_kappa"],
                "p_error": x["observation_error_null"]["p_upper"],
                "supported": x["supported_excess_concentration"],
            }
            for x in out["panel_results"]
        ],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
