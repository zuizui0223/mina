#!/usr/bin/env python3
"""Pre-outcome V2 observation-source sensitivity recovery."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.audit_paper2_integrated_sensitivity_support import filter_process_support
from scripts.simulate_paper2_latent_factor_recovery import build_scale_frame
from scripts.simulate_paper2_integrated_recovery import (
    simulate_integrated_dataset,
    count_to_analysis_scale,
)
from scripts.simulate_paper2_integrated_hierarchical_recovery import (
    fit_hierarchical_species,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
    prepare_observation_recovery_design,
    fit_observation_calibration_fast,
)

SPECIES=("ADPE","CHPE","GEPE")
TESTABLE={
    "exclude_unknown":("ADPE","CHPE","GEPE"),
    "ground_only":("CHPE","GEPE"),
}


def _q(values,q):
    return float(np.quantile(np.asarray(values,dtype=float),q))


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def build_frames(forcing_result,forcing_units,breeding):
    frames={
        sp:build_scale_frame(
            forcing_result,forcing_units,breeding,sp,"species_wide"
        )
        for sp in SPECIES
    }
    got={sp:len(f) for sp,f in frames.items()}
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    if got!=expected:
        raise ValueError(f"frame drift: {got} != {expected}")
    return frames


def filter_records(records:pd.DataFrame,unit_ids:set[str],mode:str)->pd.DataFrame:
    local=records.copy()
    local["unit_id"]=local["species_id"].astype(str)+"|"+local["site_id"].astype(str)
    local=local[local["unit_id"].isin(unit_ids)].copy()
    if mode=="exclude_unknown":
        local=local[local["vantage_family"].astype(str).ne("unknown")].copy()
    elif mode=="ground_only":
        local=local[local["vantage_raw"].astype(str).eq("ground")].copy()
    else:
        raise ValueError(mode)
    return local


def prepare_supported_frames(frames,metadata):
    supported={}
    support={}
    for mode in ("exclude_unknown","ground_only"):
        supported[mode]={}; support[mode]={}
        for sp,frame in frames.items():
            kept,meta=filter_process_support(frame,metadata,mode=mode)
            supported[mode][sp]=kept
            support[mode][sp]=meta
    expected={
      "exclude_unknown":{"ADPE":40,"CHPE":30,"GEPE":28},
      "ground_only":{"ADPE":14,"CHPE":26,"GEPE":23},
    }
    got={
      mode:{sp:len(supported[mode][sp]) for sp in SPECIES}
      for mode in expected
    }
    if got!=expected:
        raise ValueError(f"support drift: {got} != {expected}")
    return supported,support


def fit_one_mode(full_frames,supported_frames,sim,mode,calibration):
    out={}
    for sp in TESTABLE[mode]:
        frame=supported_frames[mode][sp].reset_index(drop=True)
        ids=set(frame["unit_id"].astype(str))
        records=filter_records(sim["observations"],ids,mode)
        full_frame=full_frames[sp].reset_index(drop=True)
        truth=sim["truth"][sp]
        lam_map={
            str(unit):float(lam)
            for unit,lam in zip(
                full_frame["unit_id"].astype(str),
                truth["true_lambda"],
            )
        }
        true_lambda=[lam_map[u] for u in frame["unit_id"].astype(str)]
        out[sp]=fit_hierarchical_species(
            frame,
            records,
            delta_image=float(calibration["delta_image"]),
            sigma1=float(calibration["accuracy"]["1"]["sigma"]),
            sigma2plus=float(calibration["accuracy"]["2-5"]["sigma"]),
            truth_forcing=truth["true_forcing"],
            true_lambda=true_lambda,
            iterations=12,
        )
    return out


def summarize(records_by_scenario):
    species={}
    for sp in sorted(records_by_scenario["null"]):
        null=records_by_scenario["null"][sp]
        cross=records_by_scenario["crossover"][sp]
        groups={}
        for group in sorted(cross[0]["forcing_correlation"]):
            vals=[
                float(r["forcing_correlation"][group])
                for name in ("null","crossover")
                for r in records_by_scenario[name][sp]
            ]
            groups[group]={
                "median_corr":_q(vals,0.5),
                "q05_corr":_q(vals,0.05),
            }
        null_ah=[float(r["gamma_ah"]) for r in null]
        cross_ah=[float(r["gamma_ah"]) for r in cross]
        checks={
            "factor_median":all(v["median_corr"]>=0.70 for v in groups.values()),
            "factor_q05":all(v["q05_corr"]>=0.30 for v in groups.values()),
            "crossover_bias":abs(_q(cross_ah,0.5)+0.35)<=0.10,
            "crossover_sign":float(np.mean(np.asarray(cross_ah)<0))>=0.90,
            "null_center":abs(_q(null_ah,0.5))<=0.05,
            "null_contains_zero":_q(null_ah,0.05)<=0<=_q(null_ah,0.95),
        }
        species[sp]={
            "forcing_groups":groups,
            "null":{
                "median_gamma_ah":_q(null_ah,0.5),
                "q05_gamma_ah":_q(null_ah,0.05),
                "q95_gamma_ah":_q(null_ah,0.95),
            },
            "crossover":{
                "median_gamma_ah":_q(cross_ah,0.5),
                "negative_fraction":float(np.mean(np.asarray(cross_ah)<0)),
            },
            "gate":{"checks":checks,"passes":bool(all(checks.values()))},
        }
    return species


def run_audit(forcing_result,forcing_units,breeding,metadata,replicates=100):
    full_frames=build_frames(forcing_result,forcing_units,breeding)
    supported,support=prepare_supported_frames(full_frames,metadata)
    collected={
        mode:{scenario:{sp:[] for sp in TESTABLE[mode]} for scenario in ("null","crossover")}
        for mode in TESTABLE
    }
    truths={
        "null":{"gamma_a":0.0,"gamma_ah":0.0},
        "crossover":{"gamma_a":0.0,"gamma_ah":-0.35},
    }
    for sidx,(scenario,pars) in enumerate(truths.items()):
        for rep in range(replicates):
            sim=simulate_integrated_dataset(
                full_frames,metadata,
                gamma_a=pars["gamma_a"],gamma_ah=pars["gamma_ah"],
                seed=18000000+sidx*100000+rep,
                forcing_sd=0.08,loading_sd=0.15,process_sd=0.04,
                drift_mean=-0.01,drift_sd=0.01,
                delta_image=float(np.log(1.15)),
                sigma1=float(np.log(1.05)),
                sigma2plus=float(np.log(1.25)),
            )
            obs=sim["observations"].reset_index(drop=True)
            design=prepare_observation_recovery_design(obs)
            calibration=fit_observation_calibration_fast(
                count_to_analysis_scale(obs["count"].to_numpy(dtype=float)),
                design,
            )
            for mode in TESTABLE:
                fit=fit_one_mode(full_frames,supported,sim,mode,calibration)
                for sp,val in fit.items():
                    collected[mode][scenario][sp].append(val)
    result_modes={}
    for mode in TESTABLE:
        species=summarize(collected[mode])
        result_modes[mode]={
            "support":{sp:{
                "supported_units":int(len(supported[mode][sp])),
                "classification":support[mode][sp]["classification"],
            } for sp in SPECIES},
            "species":species,
            "all_testable_species_pass":bool(all(v["gate"]["passes"] for v in species.values())),
        }
    unlock=bool(
        result_modes["exclude_unknown"]["all_testable_species_pass"]
        and result_modes["ground_only"]["all_testable_species_pass"]
    )
    return {
        "schema_version":1,
        "audit_id":"mina-paper2-v2-source-sensitivity-recovery",
        "replicates_per_scenario":int(replicates),
        "modes":result_modes,
        "decision":{
            "exclude_unknown_passed":result_modes["exclude_unknown"]["all_testable_species_pass"],
            "ground_only_testable_species_passed":result_modes["ground_only"]["all_testable_species_pass"],
            "ADPE_ground_only":"coverage_limited_nonblocking",
            "observation_source_sensitivity_completed":unlock,
            "counts_may_be_opened":unlock,
            "no_real_count_magnitudes_opened":True,
        },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",type=Path,required=True)
    p.add_argument("--forcing-csv",type=Path,required=True)
    p.add_argument("--breeding-csv",type=Path,required=True)
    p.add_argument("--mapppdr-dir",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    p.add_argument("--replicates",type=int,default=100)
    a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text()); fu=pd.read_csv(a.forcing_csv); br=pd.read_csv(a.breeding_csv)
    obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    metadata=build_frozen_observation_metadata(obs)
    result=run_audit(fr,fu,br,metadata,a.replicates)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result["decision"]["counts_may_be_opened"]:
        raise SystemExit("V2 observation-source sensitivity recovery failed")
if __name__=="__main__": main()
