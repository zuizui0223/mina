"""Independent Signy replication of breeding-patch concentration."""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.audit_signy_replication_support import read_official_zip, season_start

EXPECTED_CSV_SHA256 = "585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62"
YEARS = np.arange(1996, 2020, dtype=int)
PRIMARY_ROSTER = ("A1+A60", "A2", "A3", "A4", "A64")
ERROR_MODELS = (
    ("poisson", 0.0),
    ("gamma_poisson_cv10", 0.10),
    ("gamma_poisson_cv20", 0.20),
)
SIMULATIONS = 100_000
SEED = 20261001
BATCH_SIZE = 2000


def canonical_label(label: str) -> str:
    x = re.sub(r"\s+", " ", str(label).strip())
    if x in {"A1", "A60", "A1 + A60", "A1+A60"}:
        return "A1+A60"
    return x


def _number(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text in {"", "NA", "NaN", "nan"}:
        return None
    try:
        out = float(text)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def stable_roster_matrix(frame: pd.DataFrame) -> np.ndarray:
    required = {"SEASON", "COLONY", "TOTAL_NUMBER_OF_PAIRS"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"missing Signy columns: {missing}")

    grouped: dict[tuple[int, str], float] = {}
    seen_any: set[tuple[int, str]] = set()
    for _, row in frame.iterrows():
        year = season_start(row["SEASON"])
        if year is None or year not in set(YEARS.tolist()):
            continue
        label = canonical_label(row["COLONY"])
        if label not in PRIMARY_ROSTER:
            continue
        value = _number(row["TOTAL_NUMBER_OF_PAIRS"])
        if value is None:
            raise ValueError(f"missing frozen-roster pair count: {(year, label)}")
        if value < 0:
            raise ValueError(f"negative frozen-roster pair count: {(year, label)}")
        key = (int(year), label)
        grouped[key] = grouped.get(key, 0.0) + float(value)
        seen_any.add(key)

    expected = {(int(y), c) for y in YEARS for c in PRIMARY_ROSTER}
    missing_keys = sorted(expected - seen_any)
    if missing_keys:
        raise ValueError(f"incomplete frozen Signy roster: {missing_keys[:12]}")

    matrix = np.asarray(
        [[grouped[(int(y), c)] for y in YEARS] for c in PRIMARY_ROSTER],
        dtype=float,
    )
    return matrix


def effective_number(matrix: np.ndarray) -> np.ndarray:
    """Return N_eff by time for colony x time or replicate x colony x time."""
    arr = np.asarray(matrix, dtype=float)
    if arr.ndim == 2:
        total = np.sum(arr, axis=0)
        squares = np.sum(arr**2, axis=0)
    elif arr.ndim == 3:
        total = np.sum(arr, axis=1)
        squares = np.sum(arr**2, axis=1)
    else:
        raise ValueError("matrix must be colony x time or replicate x colony x time")
    out = np.full(total.shape, np.nan, dtype=float)
    ok = total > 0
    out[ok] = total[ok] ** 2 / squares[ok]
    return out


def slope(values: np.ndarray, years: np.ndarray = YEARS) -> np.ndarray | float:
    arr = np.asarray(values, dtype=float)
    x = np.asarray(years, dtype=float)
    centered = x - float(np.mean(x))
    denom = float(np.sum(centered**2))
    if arr.ndim == 1:
        if arr.size != x.size:
            raise ValueError("time axis mismatch")
        return float(np.sum((arr - float(np.mean(arr))) * centered) / denom)
    if arr.ndim == 2:
        if arr.shape[1] != x.size:
            raise ValueError("time axis mismatch")
        centered_values = arr - np.mean(arr, axis=1, keepdims=True)
        return np.sum(centered_values * centered[None, :], axis=1) / denom
    raise ValueError("values must be time or replicate x time")


def _draw_batch(
    latent: np.ndarray,
    observed_totals: np.ndarray,
    simulations: int,
    multiplicative_cv: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if multiplicative_cv > 0:
        shape = 1.0 / (multiplicative_cv**2)
        factors = rng.gamma(
            shape=shape,
            scale=1.0 / shape,
            size=(simulations,) + latent.shape,
        )
        means = factors * latent[None, :, :]
    else:
        means = np.broadcast_to(latent, (simulations,) + latent.shape)

    local = rng.poisson(means).astype(float)
    for t in np.where(observed_totals > 0)[0]:
        zero = np.where(np.sum(local[:, :, t], axis=1) == 0)[0]
        while zero.size:
            retry = np.broadcast_to(
                latent[:, t], (zero.size, latent.shape[0])
            ).copy()
            if multiplicative_cv > 0:
                shape = 1.0 / (multiplicative_cv**2)
                retry *= rng.gamma(
                    shape=shape,
                    scale=1.0 / shape,
                    size=retry.shape,
                )
            local[zero, :, t] = rng.poisson(retry).astype(float)
            zero = zero[np.sum(local[zero, :, t], axis=1) == 0]
    return local


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "sd": float(np.std(values, ddof=1)),
        "median": float(np.median(values)),
        "q_0_025": float(np.quantile(values, 0.025)),
        "q_0_05": float(np.quantile(values, 0.05)),
        "q_0_95": float(np.quantile(values, 0.95)),
        "q_0_975": float(np.quantile(values, 0.975)),
    }


def analyze_frame(
    frame: pd.DataFrame,
    *,
    simulations: int = SIMULATIONS,
    seed: int = SEED,
    batch_size: int = BATCH_SIZE,
) -> dict[str, object]:
    matrix = stable_roster_matrix(frame)
    totals = np.sum(matrix, axis=0)
    if np.any(totals <= 0):
        raise ValueError("zero total abundance in a frozen Signy primary season")

    neff = effective_number(matrix)
    total_slope = float(slope(totals))
    neff_slope = float(slope(neff))
    decline_gate = bool(total_slope < 0)

    cumulative = np.sum(matrix, axis=1)
    shares = cumulative / float(np.sum(cumulative))
    latent = shares[:, None] * totals[None, :]

    rng = np.random.default_rng(seed)
    outputs: dict[str, object] = {}
    for name, cv in ERROR_MODELS:
        chunks: list[np.ndarray] = []
        completed = 0
        while completed < simulations:
            n = min(batch_size, simulations - completed)
            batch = _draw_batch(latent, totals, n, cv, rng)
            batch_neff = effective_number(batch)
            chunks.append(np.asarray(slope(batch_neff), dtype=float))
            completed += n
        null_slopes = np.concatenate(chunks)
        exceed = int(np.sum(null_slopes <= neff_slope))
        p = float((1 + exceed) / (simulations + 1))
        outputs[name] = {
            "multiplicative_cv": cv,
            "observed_slope": neff_slope,
            "simulated_slopes_le_observed": exceed,
            "one_sided_probability_le_observed": p,
            "null_slope_summary": _summary(null_slopes),
        }

    supported = bool(
        decline_gate
        and neff_slope < 0
        and all(
            float(outputs[name]["one_sided_probability_le_observed"]) <= 0.05
            for name, _ in ERROR_MODELS
        )
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-signy-breeding-patch-concentration-v1",
        "contract_id": "mina-signy-breeding-patch-concentration-v1",
        "status": "independent_system_replication",
        "window": [int(YEARS[0]), int(YEARS[-1])],
        "primary_roster": list(PRIMARY_ROSTER),
        "canonicalization": "A1/A60/A1 + A60 -> A1+A60; sum if multiple source rows occur in a season",
        "simulations_per_error_model": int(simulations),
        "seed": int(seed),
        "batch_size": int(batch_size),
        "decline_eligibility": {
            "stable_roster_total_slope_per_year": total_slope,
            "first_total": float(totals[0]),
            "last_total": float(totals[-1]),
            "passes": decline_gate,
        },
        "observed": {
            "annual_neff": {
                str(int(y)): float(v) for y, v in zip(YEARS, neff)
            },
            "first_neff": float(neff[0]),
            "last_neff": float(neff[-1]),
            "fractional_change_first_to_last": float(neff[-1] / neff[0] - 1.0),
            "neff_slope_per_year": neff_slope,
        },
        "null_composition": {
            "description": "time-invariant cumulative shares on the frozen five-unit roster",
            "pooled_shares": {
                c: float(v) for c, v in zip(PRIMARY_ROSTER, shares)
            },
        },
        "error_models": outputs,
        "decision": {
            "independent_concentration_replication_supported": supported
        },
        "interpretation_boundary": [
            "The endpoint is breeding-patch redistribution, not individual movement.",
            "Canonical colony labels are observational units, not GIS polygons.",
            "No snow, predation, habitat, public-information or dispersal mechanism is identified.",
            "No alternate roster/window/metric/CV may rescue a failed primary replication."
        ],
    }


def analyze_official_zip(
    path: Path,
    *,
    simulations: int = SIMULATIONS,
    seed: int = SEED,
    batch_size: int = BATCH_SIZE,
) -> dict[str, object]:
    frame, source = read_official_zip(path)
    if str(source["selected_csv_sha256"]) != EXPECTED_CSV_SHA256:
        raise ValueError("official Signy CSV hash drift")
    result = analyze_frame(
        frame,
        simulations=simulations,
        seed=seed,
        batch_size=batch_size,
    )
    result["source"] = {
        "doi": "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
        "selected_csv": source["selected_csv"],
        "selected_csv_sha256": source["selected_csv_sha256"],
        "rows": int(len(frame)),
    }
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--official-zip", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--simulations", type=int, default=SIMULATIONS)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    a = p.parse_args()
    result = analyze_official_zip(
        a.official_zip,
        simulations=a.simulations,
        seed=a.seed,
        batch_size=a.batch_size,
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
