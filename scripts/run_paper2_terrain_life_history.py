#!/usr/bin/env python3
"""Execute the frozen Paper 2 terrain R-main and life-history order tests."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.paper2_terrain_model import (
    SPECIES,
    build_terrain_frames,
    fit_terrain_species,
)
from scripts.run_paper2_real_v3_fit import (
    build_frozen_real_records,
    calibrate_observation,
)

B = 9999
SEED = 20260946


def _load_rda(path: Path, expected: str) -> pd.DataFrame:
    x = pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x) == 1:
        return next(iter(x.values()))
    raise ValueError(expected)


def _local_records(records: pd.DataFrame, frame: pd.DataFrame) -> pd.DataFrame:
    ids = set(frame["unit_id"].astype(str))
    x = records.copy()
    x["unit_id"] = (
        x["species_id"].astype(str) + "|" + x["site_id"].astype(str)
    )
    return x[x["unit_id"].isin(ids)].copy()


def _fit_species_frames(frames, records, cal):
    out = {}
    for sp in SPECIES:
        out[sp] = fit_terrain_species(
            frames[sp],
            _local_records(records, frames[sp]),
            delta_image=float(cal["delta_image"]),
            sigma1=float(cal["accuracy"]["1"]["sigma"]),
            sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
        )
    return out


def _permute_trait_within_blocks(
    frame: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    out = frame.copy()
    values = out["R"].to_numpy(float).copy()
    blocks = out["trait_block"].astype(str).to_numpy()
    perm = values.copy()
    for block in sorted(set(blocks.tolist())):
        idx = np.flatnonzero(blocks == block)
        if len(idx) > 1:
            perm[idx] = rng.permutation(values[idx])
    out["R"] = perm
    return out


def ordered_score(gamma: dict[str, float]) -> float:
    """Positive only when ADPE<CHPE<GEPE and ADPE is negative."""
    ad = float(gamma["ADPE"])
    ch = float(gamma["CHPE"])
    ge = float(gamma["GEPE"])
    return float(min(-ad, ch - ad, ge - ch))


def holm_adjust(pvals: dict[str, float]) -> dict[str, float]:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted = {}
    running = 0.0
    for rank, (name, p) in enumerate(items):
        value = min(1.0, (m - rank) * float(p))
        running = max(running, value)
        adjusted[name] = running
    return {name: float(adjusted[name]) for name in pvals}


def run_permutation(frames, records, cal, observed, *, B=B, seed=SEED):
    rng = {sp: np.random.default_rng(seed + i * 100000) for i, sp in enumerate(SPECIES)}
    null = {sp: np.empty(B, dtype=float) for sp in SPECIES}
    order_null = np.empty(B, dtype=float)

    local_records = {
        sp: _local_records(records, frames[sp]) for sp in SPECIES
    }
    for b in range(B):
        gammas = {}
        for sp in SPECIES:
            pf = _permute_trait_within_blocks(frames[sp], rng[sp])
            fit = fit_terrain_species(
                pf,
                local_records[sp],
                delta_image=float(cal["delta_image"]),
                sigma1=float(cal["accuracy"]["1"]["sigma"]),
                sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
            )
            gammas[sp] = float(fit["gamma_r"])
            null[sp][b] = gammas[sp]
        order_null[b] = ordered_score(gammas)

    observed_gamma = {
        sp: float(observed[sp]["gamma_r"]) for sp in SPECIES
    }
    species_p = {}
    species_summary = {}
    for sp in SPECIES:
        obs = observed_gamma[sp]
        x = null[sp]
        p = (1 + int(np.sum(np.abs(x) >= abs(obs)))) / (B + 1)
        species_p[sp] = float(p)
        species_summary[sp] = {
            "observed_gamma_r": obs,
            "two_sided_p": float(p),
            "null_mean": float(np.mean(x)),
            "null_q025": float(np.quantile(x, 0.025)),
            "null_q975": float(np.quantile(x, 0.975)),
        }
    holm = holm_adjust(species_p)
    for sp in SPECIES:
        species_summary[sp]["holm_p"] = holm[sp]

    obs_order = ordered_score(observed_gamma)
    order_p = (1 + int(np.sum(order_null >= obs_order))) / (B + 1)
    return {
        "B": int(B),
        "seed": int(seed),
        "species": species_summary,
        "life_history_order": {
            "prediction": "gamma_R_ADPE < gamma_R_CHPE < gamma_R_GEPE and gamma_R_ADPE < 0",
            "observed_gamma_r": observed_gamma,
            "observed_ordered_score": float(obs_order),
            "null_mean_ordered_score": float(np.mean(order_null)),
            "null_q95_ordered_score": float(np.quantile(order_null, 0.95)),
            "one_sided_upper_p": float(order_p),
            "supported": bool(obs_order > 0 and order_p <= 0.05),
        },
    }


def _sensitivity_point_estimates(
    forcing_result,
    forcing_units,
    breeding,
    terrain,
    records,
    cal,
):
    specs = {
        "relief_1000m": "elevation_relief_p90_p10_m_1000m",
        "relief_5000m": "elevation_relief_p90_p10_m_5000m",
        "elevation_sd_2000m": "elevation_sd_m_2000m",
    }
    out = {}
    for name, field in specs.items():
        frames = build_terrain_frames(
            forcing_result,
            forcing_units,
            breeding,
            terrain,
            field=field,
        )
        fit = _fit_species_frames(frames, records, cal)
        out[name] = {
            sp: {
                "gamma_r": float(fit[sp]["gamma_r"]),
                "n_units": int(fit[sp]["n_units"]),
            }
            for sp in SPECIES
        }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--recovery-json", required=True, type=Path)
    p.add_argument("--forcing-json", required=True, type=Path)
    p.add_argument("--forcing-csv", required=True, type=Path)
    p.add_argument("--breeding-csv", required=True, type=Path)
    p.add_argument("--terrain-csv", required=True, type=Path)
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--permutations", type=int, default=B)
    a = p.parse_args()

    recovery = json.loads(a.recovery_json.read_text(encoding="utf-8"))
    if not recovery.get("decision", {}).get("terrain_r_main_recoverable", False):
        raise SystemExit("terrain recovery gate has not passed")
    if recovery.get("decision", {}).get("no_real_gamma_r_computed") is not True:
        raise SystemExit("unexpected recovery provenance state")

    forcing_result = json.loads(a.forcing_json.read_text(encoding="utf-8"))
    forcing_units = pd.read_csv(a.forcing_csv)
    breeding = pd.read_csv(a.breeding_csv)
    terrain = pd.read_csv(a.terrain_csv)
    frames = build_terrain_frames(
        forcing_result, forcing_units, breeding, terrain
    )

    obs = _load_rda(
        a.mapppdr_dir / "data" / "penguin_obs.rda",
        "penguin_obs",
    )
    records = build_frozen_real_records(obs)
    cal = calibrate_observation(records)

    observed = _fit_species_frames(frames, records, cal)
    inference = run_permutation(
        frames,
        records,
        cal,
        observed,
        B=a.permutations,
        seed=SEED,
    )
    sensitivities = _sensitivity_point_estimates(
        forcing_result,
        forcing_units,
        breeding,
        terrain,
        records,
        cal,
    )

    result = {
        "schema_version": 1,
        "analysis_id": "mina-paper2-terrain-life-history-v1",
        "contract_id": "mina-paper2-terrain-life-history-v1",
        "recovery_gate": {
            "analysis_id": recovery.get("analysis_id"),
            "passed": True,
        },
        "observation_calibration": {
            "delta_image": float(cal["delta_image"]),
            "sigma_accuracy_1": float(cal["accuracy"]["1"]["sigma"]),
            "sigma_accuracy_2_5": float(cal["accuracy"]["2-5"]["sigma"]),
        },
        "primary_R_main": {
            sp: {
                "gamma_r": float(observed[sp]["gamma_r"]),
                "process_sd": float(observed[sp]["process_sd"]),
                "loading_residual_sd": float(observed[sp]["loading_residual_sd"]),
                "n_units": int(observed[sp]["n_units"]),
            }
            for sp in SPECIES
        },
        "permutation_inference": inference,
        "terrain_metric_sensitivities_point_estimates_only": sensitivities,
        "decision": {
            "species_holm_rejections": [
                sp
                for sp in SPECIES
                if inference["species"][sp]["holm_p"] <= 0.05
            ],
            "life_history_order_supported": bool(
                inference["life_history_order"]["supported"]
            ),
            "snow_clearing_mechanism_identified": False,
        },
        "interpretation_boundary": [
            "A gamma_R effect is a terrain association with loading on shared forcing, not a direct snow/wind mechanism.",
            "The life-history order is a secondary post-primary-outcome prediction frozen before R execution.",
            "Metric/radius sensitivities are point-estimate diagnostics and cannot replace the 2-km relief primary.",
        ],
    }
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
