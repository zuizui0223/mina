#!/usr/bin/env python3
"""Pre-outcome recovery of the cross-species generality estimand."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pyreadr

from scripts.simulate_paper2_integrated_recovery import (
    simulate_integrated_dataset,simulate_species_counts,count_to_analysis_scale
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,prepare_observation_recovery_design,
    fit_observation_calibration_fast
)
from scripts.simulate_paper2_spatial_adjusted_v3 import build_v3_frames,fit_spatial_species

SPECIES=("ADPE","CHPE","GEPE")
SCENARIOS={
  "null":{"ADPE":0.0,"CHPE":0.0,"GEPE":0.0},
  "common":{"ADPE":-0.35,"CHPE":-0.35,"GEPE":-0.35},
  "adelie_only":{"ADPE":-0.35,"CHPE":0.0,"GEPE":0.0},
  "chinstrap_only":{"ADPE":0.0,"CHPE":-0.35,"GEPE":0.0},
  "gentoo_only":{"ADPE":0.0,"CHPE":0.0,"GEPE":-0.35},
}

def q(v,p): return float(np.quantile(np.asarray(v,float),p))

def simulate_species_effects(frames,metadata,effects,seed):
    # Calibration dataset is generated on the full frozen metadata layout and
    # is independent of the site-trait scenario.
    base=simulate_integrated_dataset(
      frames,metadata,gamma_a=0.0,gamma_ah=0.0,seed=seed,
      forcing_sd=.08,loading_sd=.15,process_sd=.04,drift_mean=-.01,drift_sd=.01,
      delta_image=float(np.log(1.15)),sigma1=float(np.log(1.05)),sigma2plus=float(np.log(1.25)))
    obs=base["observations"].reset_index(drop=True)
    cal=fit_observation_calibration_fast(
      count_to_analysis_scale(obs["count"].to_numpy(float)),
      prepare_observation_recovery_design(obs)
    )
    estimates={}; truths={}
    for k,sp in enumerate(SPECIES):
        sim=simulate_species_counts(
          frames[sp],metadata,gamma_a=0.0,gamma_ah=float(effects[sp]),
          seed=seed+30000*(k+1),forcing_sd=.08,loading_sd=.15,process_sd=.04,
          drift_mean=-.01,drift_sd=.01,delta_image=float(np.log(1.15)),
          sigma1=float(np.log(1.05)),sigma2plus=float(np.log(1.25)))
        fit=fit_spatial_species(
          frames[sp],sim["observations"],
          delta_image=float(cal["delta_image"]),
          sigma1=float(cal["accuracy"]["1"]["sigma"]),
          sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
          truth_forcing=sim["true_forcing"],true_lambda=sim["true_lambda"]
        )
        estimates[sp]=float(fit["gamma_ah"])
        truths[sp]=float(effects[sp])
    return estimates,truths

def summarize(raw):
    med=[float(r["median_gamma"]) for r in raw]
    at_least_two=[int(r["n_negative"]>=2) for r in raw]
    return {
      "median_of_species_gamma":{
        "median":q(med,.5),"q05":q(med,.05),"q95":q(med,.95),
        "negative_fraction":float(np.mean(np.asarray(med)<0))
      },
      "at_least_two_species_negative_fraction":float(np.mean(at_least_two)),
      "species_median_gamma":{
        sp:q([r["gamma"][sp] for r in raw],.5) for sp in SPECIES
      }
    }

def evaluate(frames,metadata,reps=100):
    records={s:[] for s in SCENARIOS}
    for si,(name,effects) in enumerate(SCENARIOS.items()):
        for rep in range(reps):
            est,_=simulate_species_effects(frames,metadata,effects,31000000+si*100000+rep)
            vals=np.asarray([est[sp] for sp in SPECIES],float)
            records[name].append({
              "gamma":est,
              "median_gamma":float(np.median(vals)),
              "n_negative":int(np.sum(vals<0))
            })
    summary={name:summarize(v) for name,v in records.items()}
    common=summary["common"]["median_of_species_gamma"]
    null=summary["null"]["median_of_species_gamma"]
    checks={
      "common_bias":abs(common["median"]+0.35)<=0.10,
      "common_negative_fraction":common["negative_fraction"]>=0.90,
      "common_replication":summary["common"]["at_least_two_species_negative_fraction"]>=0.90,
      "null_center":abs(null["median"])<=0.05,
      "null_contains_zero":null["q05"]<=0<=null["q95"],
    }
    guards={}
    for name in ("adelie_only","chinstrap_only","gentoo_only"):
        x=summary[name]
        guards[name]={
          "median_near_zero":abs(x["median_of_species_gamma"]["median"])<=0.10,
          "replication_not_systematic":x["at_least_two_species_negative_fraction"]<=0.80,
        }
    passes=bool(all(checks.values()) and all(all(g.values()) for g in guards.values()))
    return {"replicates_per_scenario":reps,"scenarios":summary,
            "gate":{"checks":checks,"single_species_guards":guards,"passes":passes}}

def load(path,expected):
    x=pyreadr.read_r(str(path));return x[expected] if expected in x else next(iter(x.values()))

def main():
    p=argparse.ArgumentParser();p.add_argument("--forcing-json",type=Path,required=True);p.add_argument("--forcing-csv",type=Path,required=True);p.add_argument("--breeding-csv",type=Path,required=True);p.add_argument("--mapppdr-dir",type=Path,required=True);p.add_argument("--out-json",type=Path,required=True);p.add_argument("--replicates",type=int,default=100);a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv)
    frames=build_v3_frames(fr,fu,br); meta=build_frozen_observation_metadata(load(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs"))
    rec=evaluate(frames,meta,a.replicates)
    out={"schema_version":1,"audit_id":"mina-paper2-cross-species-generality-v4","recovery":rec,
         "decision":{"generality_estimand_recoverable":bool(rec["gate"]["passes"]),"counts_may_be_opened":False,"no_real_count_magnitudes_opened":True}}
    a.out_json.parent.mkdir(parents=True,exist_ok=True);a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
    if not rec["gate"]["passes"]: raise SystemExit("V4 generality recovery failed")
if __name__=="__main__":main()
