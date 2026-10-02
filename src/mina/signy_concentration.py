"""Independent Signy replication of Palmer within-island breeding concentration."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from scripts.audit_signy_replication_support import read_official_zip
from mina.signy_replication import EXPECTED_CSV_SHA256, build_signy_rows

SIMULATIONS = 100_000
SEED = 20261030
BATCH_SIZE = 2000
ERROR_MODELS = (
    ("poisson", 0.0),
    ("gamma_poisson_cv10", 0.10),
    ("gamma_poisson_cv20", 0.20),
)
PRIMARY_YEARS = tuple(range(1998, 2010))
PRIMARY_ROSTER = (
    "A1 + A60",
    "A2",
    "A3",
    "A4",
    "A41",
    "A62",
    "A63",
    "A64",
)


def effective_number(matrix: np.ndarray) -> np.ndarray:
    total = np.sum(matrix, axis=1, dtype=float)
    squares = np.sum(np.asarray(matrix, dtype=float) ** 2, axis=1)
    out = np.full(total.shape, np.nan, dtype=float)
    valid = total > 0
    out[valid] = total[valid] ** 2 / squares[valid]
    return out


def slope(values: np.ndarray, years: np.ndarray) -> float:
    x = np.asarray(years, dtype=float)
    y = np.asarray(values, dtype=float)
    xc = x - float(np.mean(x))
    return float(np.sum((y - float(np.mean(y))) * xc) / np.sum(xc**2))


def _matrix_for_epoch(
    adults: list[dict[str, object]],
    years: tuple[int, ...],
    expected_roster: tuple[str, ...] | None = None,
) -> tuple[np.ndarray, tuple[str, ...]]:
    by_year: dict[int, dict[str, float]] = defaultdict(dict)
    for row in adults:
        year = int(row["year"])
        if year not in years:
            continue
        colony = str(row["colony"])
        if colony in by_year[year]:
            raise ValueError(f"duplicate Signy colony-year: {(year, colony)}")
        by_year[year][colony] = float(row["adult_pairs"])

    missing_years = [year for year in years if year not in by_year]
    if missing_years:
        raise ValueError(f"missing Signy seasons: {missing_years}")

    if expected_roster is None:
        sets = [set(by_year[y]) for y in years]
        roster = tuple(sorted(sets[0]))
        if any(set(roster) != s for s in sets[1:]):
            raise ValueError("later epoch literal roster is not fixed")
    else:
        roster = tuple(expected_roster)
        for year in years:
            actual = set(by_year[year])
            expected = set(roster)
            if actual != expected:
                raise ValueError(
                    f"primary roster gate failed in {year}: "
                    f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
                )
    matrix = np.asarray(
        [[by_year[y][c] for y in years] for c in roster],
        dtype=float,
    )
    if np.any(~np.isfinite(matrix)) or np.any(matrix < 0):
        raise ValueError("invalid Signy breeding-pair matrix")
    return matrix, roster


def _simulate_slopes(
    latent: np.ndarray,
    totals: np.ndarray,
    years: np.ndarray,
    *,
    cv: float,
    simulations: int,
    rng: np.random.Generator,
) -> np.ndarray:
    chunks = []
    completed = 0
    while completed < simulations:
        n = min(BATCH_SIZE, simulations - completed)
        if cv > 0:
            shape = 1.0 / (cv**2)
            factors = rng.gamma(
                shape=shape,
                scale=1.0 / shape,
                size=(n,) + latent.shape,
            )
            means = factors * latent[None, :, :]
        else:
            means = np.broadcast_to(latent, (n,) + latent.shape)

        counts = rng.poisson(means).astype(float)
        for yi in np.where(totals > 0)[0]:
            zero = np.where(np.sum(counts[:, :, yi], axis=1) == 0)[0]
            while zero.size:
                retry = np.broadcast_to(
                    latent[:, yi], (zero.size, latent.shape[0])
                ).copy()
                if cv > 0:
                    shape = 1.0 / (cv**2)
                    retry *= rng.gamma(
                        shape=shape,
                        scale=1.0 / shape,
                        size=retry.shape,
                    )
                counts[zero, :, yi] = rng.poisson(retry).astype(float)
                still = np.sum(counts[zero, :, yi], axis=1) == 0
                zero = zero[still]

        total = np.sum(counts, axis=1)
        sq = np.sum(counts**2, axis=1)
        neff = total**2 / sq
        xc = years - float(np.mean(years))
        yc = neff - np.mean(neff, axis=1, keepdims=True)
        slopes = np.sum(yc * xc[None, :], axis=1) / np.sum(xc**2)
        chunks.append(slopes)
        completed += n
    return np.concatenate(chunks)


def analyze(path: Path, *, simulations: int = SIMULATIONS) -> dict[str, object]:
    frame, source = read_official_zip(path)
    actual_sha = str(source["selected_csv_sha256"])
    if actual_sha != EXPECTED_CSV_SHA256:
        raise ValueError(
            f"official Signy CSV hash drift: {actual_sha} != {EXPECTED_CSV_SHA256}"
        )
    adults, _, source_meta = build_signy_rows(frame)

    observed_matrix, roster = _matrix_for_epoch(
        adults, PRIMARY_YEARS, PRIMARY_ROSTER
    )
    years = np.asarray(PRIMARY_YEARS, dtype=float)
    totals = np.sum(observed_matrix, axis=0)
    obs_neff = effective_number(observed_matrix.T)
    obs_slope = slope(obs_neff, years)

    cumulative = np.sum(observed_matrix, axis=1)
    shares = cumulative / float(np.sum(cumulative))
    latent = shares[:, None] * totals[None, :]

    rng = np.random.default_rng(SEED)
    errors = {}
    all_pass = obs_slope < 0
    for name, cv in ERROR_MODELS:
        values = _simulate_slopes(
            latent,
            totals,
            years,
            cv=cv,
            simulations=simulations,
            rng=rng,
        )
        exceed = int(np.sum(values <= obs_slope))
        p = float((1 + exceed) / (simulations + 1))
        errors[name] = {
            "multiplicative_cv": cv,
            "observed_slope": obs_slope,
            "null_mean": float(np.mean(values)),
            "null_q025": float(np.quantile(values, 0.025)),
            "null_q975": float(np.quantile(values, 0.975)),
            "simulated_slopes_le_observed": exceed,
            "one_sided_probability_le_observed": p,
        }
        all_pass = all_pass and p <= 0.05

    secondary = {"status": "not_estimable"}
    later_years = tuple(range(2011, 2020))
    try:
        later_matrix, later_roster = _matrix_for_epoch(adults, later_years, None)
        later_neff = effective_number(later_matrix.T)
        secondary = {
            "status": "fixed_roster_estimable",
            "years": [2011, 2019],
            "roster": list(later_roster),
            "first_neff": float(later_neff[0]),
            "last_neff": float(later_neff[-1]),
            "fractional_change": float(later_neff[-1] / later_neff[0] - 1.0),
            "slope_per_year": slope(
                later_neff, np.asarray(later_years, dtype=float)
            ),
        }
    except ValueError as exc:
        secondary = {"status": "not_estimable", "reason": str(exc)}

    return {
        "schema_version": 1,
        "analysis_id": "mina-signy-concentration-replication-v2",
        "contract_id": "mina-signy-concentration-replication-v2",
        "source": {
            "doi": "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
            "selected_csv": source["selected_csv"],
            "selected_csv_sha256": actual_sha,
            "rows": int(len(frame)),
            "source_meta": source_meta,
        },
        "primary": {
            "years": [1998, 2009],
            "n_years": len(PRIMARY_YEARS),
            "roster": list(roster),
            "n_colonies": len(roster),
            "first_total_pairs": float(totals[0]),
            "last_total_pairs": float(totals[-1]),
            "first_neff": float(obs_neff[0]),
            "last_neff": float(obs_neff[-1]),
            "fractional_neff_change": float(obs_neff[-1] / obs_neff[0] - 1.0),
            "neff_slope_per_year": float(obs_slope),
            "pooled_shares": {
                c: float(v) for c, v in zip(roster, shares)
            },
        },
        "error_models": errors,
        "secondary_later_epoch": secondary,
        "decision": {
            "primary_slope_negative": bool(obs_slope < 0),
            "replication_supported_under_all_frozen_error_models": bool(all_pass),
        },
        "interpretation_boundary": [
            "A supported result replicates within-island concentration beyond proportional thinning plus the frozen stylized count-error family.",
            "It does not identify movement, habitat causation, Allee effects, predation, or public-information use.",
            "The later epoch cannot rescue a failed 1998-2009 primary result.",
        ],
        "simulations_per_error_model": int(simulations),
        "seed": SEED,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--official-zip", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--simulations", type=int, default=SIMULATIONS)
    a = p.parse_args()
    result = analyze(a.official_zip, simulations=a.simulations)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
