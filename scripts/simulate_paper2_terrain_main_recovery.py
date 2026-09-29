#!/usr/bin/env python3
"""Recovery gate for the Paper 2 one-trait terrain loading model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.paper2_terrain_model import SPECIES, build_terrain_frames, fit_terrain_species
from scripts.simulate_paper2_integrated_recovery import (
    simulate_integrated_dataset,
    count_to_analysis_scale,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
    prepare_observation_recovery_design,
    fit_observation_calibration_fast,
)

REPS = 100


def _q(values, p):
    return float(np.quantile(np.asarray(values, dtype=float), p))


def _load_rda(path: Path, expected: str) -> pd.DataFrame:
    x = pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x) == 1:
        return next(iter(x.values()))
    raise ValueError(expected)


def _fit_one(
    terrain_frames,
    observation_metadata,
    *,
    gamma_r: float,
    seed: int,
):
    sim_frames = {}
    for sp in SPECIES:
        f = terrain_frames[sp].copy()
        # Reuse the validated synthetic generator: its gamma_a * A term becomes
        # gamma_R * R for simulation only. The fitted model remains R-only.
        f["A"] = f["R"].to_numpy(float)
        f["H"] = 0.0
        f["AH"] = 0.0
        sim_frames[sp] = f

    sim = simulate_integrated_dataset(
        sim_frames,
        observation_metadata,
        gamma_a=float(gamma_r),
        gamma_ah=0.0,
        seed=seed,
        forcing_sd=0.08,
        loading_sd=0.15,
        process_sd=0.04,
        drift_mean=-0.01,
        drift_sd=0.01,
        delta_image=float(np.log(1.15)),
        sigma1=float(np.log(1.05)),
        sigma2plus=float(np.log(1.25)),
    )
    obs = sim["observations"].reset_index(drop=True)
    cal = fit_observation_calibration_fast(
        count_to_analysis_scale(obs["count"].to_numpy(float)),
        prepare_observation_recovery_design(obs),
    )

    out = {}
    for sp in SPECIES:
        frame = terrain_frames[sp].reset_index(drop=True)
        ids = set(frame["unit_id"].astype(str))
        local = obs[
            (
                obs["species_id"].astype(str)
                + "|"
                + obs["site_id"].astype(str)
            ).isin(ids)
        ].copy()
        truth = sim["truth"][sp]
        out[sp] = fit_terrain_species(
            frame,
            local,
            delta_image=float(cal["delta_image"]),
            sigma1=float(cal["accuracy"]["1"]["sigma"]),
            sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
            truth_forcing=truth["true_forcing"],
            true_lambda=truth["true_lambda"],
        )
    return out


def evaluate(terrain_frames, observation_metadata, reps: int = REPS):
    raw = {
        "null": {sp: [] for sp in SPECIES},
        "terrain_effect": {sp: [] for sp in SPECIES},
    }
    for rep in range(reps):
        null_fit = _fit_one(
            terrain_frames,
            observation_metadata,
            gamma_r=0.0,
            seed=51000000 + rep,
        )
        effect_fit = _fit_one(
            terrain_frames,
            observation_metadata,
            gamma_r=-0.25,
            seed=52000000 + rep,
        )
        for sp in SPECIES:
            raw["null"][sp].append(float(null_fit[sp]["gamma_r"]))
            raw["terrain_effect"][sp].append(float(effect_fit[sp]["gamma_r"]))

    species = {}
    passes = {}
    for sp in SPECIES:
        n = np.asarray(raw["null"][sp], dtype=float)
        e = np.asarray(raw["terrain_effect"][sp], dtype=float)
        checks = {
            "terrain_effect_bias": abs(float(np.median(e)) + 0.25) <= 0.10,
            "terrain_effect_sign": float(np.mean(e < 0.0)) >= 0.90,
            "null_center": abs(float(np.median(n))) <= 0.05,
            "null_contains_zero": _q(n, 0.05) <= 0.0 <= _q(n, 0.95),
        }
        species[sp] = {
            "null": {
                "median_gamma_r": float(np.median(n)),
                "q05": _q(n, 0.05),
                "q95": _q(n, 0.95),
            },
            "terrain_effect": {
                "truth_gamma_r": -0.25,
                "median_gamma_r": float(np.median(e)),
                "q05": _q(e, 0.05),
                "q95": _q(e, 0.95),
                "negative_fraction": float(np.mean(e < 0.0)),
            },
            "gate": {"checks": checks, "passes": bool(all(checks.values()))},
        }
        passes[sp] = bool(all(checks.values()))
    return {
        "replicates_per_scenario": int(reps),
        "species": species,
        "gate": {
            "species_pass": passes,
            "passes": bool(all(passes.values())),
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--forcing-json", required=True, type=Path)
    p.add_argument("--forcing-csv", required=True, type=Path)
    p.add_argument("--breeding-csv", required=True, type=Path)
    p.add_argument("--terrain-csv", required=True, type=Path)
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--replicates", type=int, default=REPS)
    a = p.parse_args()

    forcing_result = json.loads(a.forcing_json.read_text(encoding="utf-8"))
    forcing_units = pd.read_csv(a.forcing_csv)
    breeding = pd.read_csv(a.breeding_csv)
    terrain = pd.read_csv(a.terrain_csv)
    frames = build_terrain_frames(
        forcing_result, forcing_units, breeding, terrain
    )
    metadata = build_frozen_observation_metadata(
        _load_rda(a.mapppdr_dir / "data" / "penguin_obs.rda", "penguin_obs")
    )
    recovery = evaluate(frames, metadata, reps=a.replicates)
    out = {
        "schema_version": 1,
        "analysis_id": "mina-paper2-terrain-main-recovery-v1",
        "recovery": recovery,
        "decision": {
            "terrain_r_main_recoverable": bool(recovery["gate"]["passes"]),
            "real_gamma_r_may_be_opened": bool(recovery["gate"]["passes"]),
            "no_real_gamma_r_computed": True,
        },
    }
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(out, indent=2, sort_keys=True))
    if not recovery["gate"]["passes"]:
        raise SystemExit("terrain R-main recovery gate failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
