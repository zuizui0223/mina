#!/usr/bin/env python3
"""Pre-outcome recovery of a nonzero H main effect under V3."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pyreadr
from scripts.simulate_paper2_integrated_recovery import (
    simulate_integrated_dataset,count_to_analysis_scale
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,prepare_observation_recovery_design,
    fit_observation_calibration_fast
)
from scripts.simulate_paper2_spatial_adjusted_v3 import build_v3_frames,fit_spatial_species

SPECIES=("ADPE","CHPE","GEPE")

def q(x,p): return float(np.quantile(np.asarray(x,float),p))

def fit_dataset(original_frames,sim_frames,metadata,seed,gamma_a):
    sim=simulate_integrated_dataset(
      sim_frames,metadata,gamma_a=gamma_a,gamma_ah=0.0,seed=seed,
      forcing_sd=.08,loading_sd=.15,process_sd=.04,drift_mean=-.01,drift_sd=.01,
      delta_image=float(np.log(1.15)),sigma1=float(np.log(1.05)),sigma2plus=float(np.log(1.25)))
    obs=sim["observations"].reset_index(drop=True)
    cal=fit_observation_calibration_fast(
      count_to_analysis_scale(obs["count"].to_numpy(float)),
      prepare_observation_recovery_design(obs)
    )
    out={}
    for sp in SPECIES:
        frame=original_frames[sp].reset_index(drop=True)
        ids=set(frame["unit_id"].astype(str))
        local=obs[(obs["species_id"].astype(str)+"|"+obs["site_id"].astype(str)).isin(ids)].copy()
        truth=sim["truth"][sp]
        out[sp]=fit_spatial_species(
          frame,local,delta_image=float(cal["delta_image"]),
          sigma1=float(cal["accuracy"]["1"]["sigma"]),
          sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
          truth_forcing=truth["true_forcing"],true_lambda=truth["true_lambda"])
    return out

def evaluate(frames,metadata,reps=100):
    sim_frames={sp:frames[sp].copy() for sp in SPECIES}
    for sp in SPECIES:
        sim_frames[sp]["A"]=frames[sp]["H"].to_numpy(float)
    raw={"null":{sp:[] for sp in SPECIES},"h_effect":{sp:[] for sp in SPECIES}}
    for rep in range(reps):
        nfit=fit_dataset(frames,frames,metadata,41000000+rep,0.0)
        hfit=fit_dataset(frames,sim_frames,metadata,42000000+rep,-0.25)
        for sp in SPECIES:
            raw["null"][sp].append(float(nfit[sp]["gamma_h"]))
            raw["h_effect"][sp].append(float(hfit[sp]["gamma_h"]))
    species={}
    for sp in SPECIES:
        n=raw["null"][sp]; h=raw["h_effect"][sp]
        checks={
          "h_bias":abs(q(h,.5)+.25)<=.10,
          "h_sign":float(np.mean(np.asarray(h)<0))>=.90,
          "null_center":abs(q(n,.5))<=.05,
          "null_contains_zero":q(n,.05)<=0<=q(n,.95)
        }
        species[sp]={
          "null":{"median_gamma_h":q(n,.5),"q05":q(n,.05),"q95":q(n,.95)},
          "h_effect":{"median_gamma_h":q(h,.5),"negative_fraction":float(np.mean(np.asarray(h)<0))},
          "gate":{"checks":checks,"passes":all(checks.values())}
        }
    return {"species":species,"gate":{"passes":all(v["gate"]["passes"] for v in species.values())}}

def load(path,expected):
    x=pyreadr.read_r(str(path)); return x[expected] if expected in x else next(iter(x.values()))
def main():
    p=argparse.ArgumentParser();p.add_argument("--forcing-json",type=Path,required=True);p.add_argument("--forcing-csv",type=Path,required=True);p.add_argument("--breeding-csv",type=Path,required=True);p.add_argument("--mapppdr-dir",type=Path,required=True);p.add_argument("--out-json",type=Path,required=True);p.add_argument("--replicates",type=int,default=100);a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv)
    frames=build_v3_frames(fr,fu,br);meta=build_frozen_observation_metadata(load(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs"))
    rec=evaluate(frames,meta,a.replicates)
    out={"schema_version":1,"audit_id":"mina-paper2-h-main-recovery-v5","recovery":rec,"decision":{"h_main_recoverable":rec["gate"]["passes"],"counts_may_be_opened":False,"no_real_count_magnitudes_opened":True}}
    a.out_json.parent.mkdir(parents=True,exist_ok=True);a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
    if not rec["gate"]["passes"]: raise SystemExit("H main recovery failed")
if __name__=="__main__":main()
