#!/usr/bin/env python3
"""Pre-R-outcome synthetic recovery gate for the prespecified Paper 2 terrain main effect."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.simulate_paper2_integrated_recovery import (
    count_to_analysis_scale,
    simulate_integrated_dataset,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
    fit_observation_calibration_fast,
    prepare_observation_recovery_design,
)
from scripts.simulate_paper2_spatial_adjusted_v3 import (
    build_v3_frames,
    fit_spatial_species,
)

SPECIES=("ADPE","CHPE","GEPE")
R_COL="elevation_relief_p90_p10_m_2000m"


def _q(values,p):
    return float(np.quantile(np.asarray(values,dtype=float),p))


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def build_r_frames(forcing_result,forcing_units,breeding,terrain):
    base=build_v3_frames(forcing_result,forcing_units,breeding)
    terrain=terrain[["site_id",R_COL]].copy()
    if terrain["site_id"].duplicated().any():
        raise ValueError("duplicate terrain site_id")
    frames={}
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    for sp in SPECIES:
        frame=base[sp].merge(terrain,on="site_id",how="left",validate="many_to_one")
        raw=np.log1p(pd.to_numeric(frame[R_COL],errors="raise").to_numpy(dtype=float))
        if np.any(~np.isfinite(raw)):
            raise ValueError(f"nonfinite R in {sp}")
        sd=float(np.std(raw,ddof=1))
        if sd<=0:
            raise ValueError(f"zero R variance in {sp}")
        r=(raw-float(np.mean(raw)))/sd
        frame["R"]=r
        # Reuse the frozen one-active-trait V3 engine: A slot carries R.
        frame["A"]=r
        frame["H"]=0.0
        frame["AH"]=0.0
        frames[sp]=frame.reset_index(drop=True)
    got={sp:len(frames[sp]) for sp in SPECIES}
    if got!=expected:
        raise ValueError(f"R frame drift: {got} != {expected}")
    return frames


def fit_dataset(frames,metadata,seed,gamma_r):
    sim=simulate_integrated_dataset(
        frames,metadata,
        gamma_a=gamma_r,gamma_ah=0.0,seed=seed,
        forcing_sd=.08,loading_sd=.15,process_sd=.04,
        drift_mean=-.01,drift_sd=.01,
        delta_image=float(np.log(1.15)),
        sigma1=float(np.log(1.05)),
        sigma2plus=float(np.log(1.25)),
    )
    obs=sim["observations"].reset_index(drop=True)
    cal=fit_observation_calibration_fast(
        count_to_analysis_scale(obs["count"].to_numpy(float)),
        prepare_observation_recovery_design(obs),
    )
    out={}
    for sp in SPECIES:
        frame=frames[sp].reset_index(drop=True)
        ids=set(frame["unit_id"].astype(str))
        local=obs[
            (obs["species_id"].astype(str)+"|"+obs["site_id"].astype(str)).isin(ids)
        ].copy()
        truth=sim["truth"][sp]
        fit=fit_spatial_species(
            frame,local,
            delta_image=float(cal["delta_image"]),
            sigma1=float(cal["accuracy"]["1"]["sigma"]),
            sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
            truth_forcing=truth["true_forcing"],
            true_lambda=truth["true_lambda"],
        )
        out[sp]=fit
    return out


def evaluate(frames,metadata,reps=100):
    raw={"null":{sp:[] for sp in SPECIES},"R_effect":{sp:[] for sp in SPECIES}}
    for rep in range(reps):
        null=fit_dataset(frames,metadata,43000000+rep,0.0)
        effect=fit_dataset(frames,metadata,44000000+rep,-0.25)
        for sp in SPECIES:
            raw["null"][sp].append(float(null[sp]["gamma_a"]))
            raw["R_effect"][sp].append(float(effect[sp]["gamma_a"]))

    species={}
    for sp in SPECIES:
        n=np.asarray(raw["null"][sp],dtype=float)
        e=np.asarray(raw["R_effect"][sp],dtype=float)
        checks={
            "R_effect_bias":abs(float(np.median(e))+0.25)<=0.10,
            "R_effect_sign":float(np.mean(e<0))>=0.90,
            "null_center":abs(float(np.median(n)))<=0.05,
            "null_contains_zero":float(np.quantile(n,.05))<=0<=float(np.quantile(n,.95)),
        }
        species[sp]={
            "null":{
                "median_gamma_R":float(np.median(n)),
                "q05":_q(n,.05),
                "q95":_q(n,.95),
            },
            "R_effect":{
                "truth_gamma_R":-0.25,
                "median_gamma_R":float(np.median(e)),
                "q05":_q(e,.05),
                "q95":_q(e,.95),
                "negative_fraction":float(np.mean(e<0)),
            },
            "gate":{"checks":checks,"passes":bool(all(checks.values()))},
        }
    return {
        "replicates_per_scenario":reps,
        "species":species,
        "gate":{
            "species_pass":{sp:bool(species[sp]["gate"]["passes"]) for sp in SPECIES},
            "passes":bool(all(species[sp]["gate"]["passes"] for sp in SPECIES)),
        },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",type=Path,required=True)
    p.add_argument("--forcing-csv",type=Path,required=True)
    p.add_argument("--breeding-csv",type=Path,required=True)
    p.add_argument("--terrain-csv",type=Path,required=True)
    p.add_argument("--mapppdr-dir",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    p.add_argument("--replicates",type=int,default=100)
    a=p.parse_args()

    fr=json.loads(a.forcing_json.read_text(encoding="utf-8"))
    fu=pd.read_csv(a.forcing_csv)
    br=pd.read_csv(a.breeding_csv)
    tr=pd.read_csv(a.terrain_csv)
    frames=build_r_frames(fr,fu,br,tr)
    obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    metadata=build_frozen_observation_metadata(obs)
    recovery=evaluate(frames,metadata,a.replicates)
    out={
        "schema_version":1,
        "analysis_id":"mina-paper2-r-main-recovery-v1",
        "contract_id":"mina-paper2-r-main-recovery-v1",
        "terrain_trait":R_COL,
        "frame_sizes":{sp:int(len(frames[sp])) for sp in SPECIES},
        "recovery":recovery,
        "decision":{
            "R_main_recoverable":bool(recovery["gate"]["passes"]),
            "real_R_outcome_may_be_opened":bool(recovery["gate"]["passes"]),
            "real_R_outcome_opened_by_this_script":False,
        },
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
    if not recovery["gate"]["passes"]:
        raise SystemExit("R main recovery failed")


if __name__=="__main__":
    main()
