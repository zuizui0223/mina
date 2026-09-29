#!/usr/bin/env python3
"""V3 spatially adjusted observation-source sensitivity recovery."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pyreadr

from scripts.audit_paper2_integrated_sensitivity_support import filter_process_support
from scripts.simulate_paper2_integrated_recovery import simulate_integrated_dataset,count_to_analysis_scale
from scripts.simulate_paper2_observation_recovery import (
 build_frozen_observation_metadata,prepare_observation_recovery_design,fit_observation_calibration_fast
)
from scripts.simulate_paper2_spatial_adjusted_v3 import build_v3_frames,fit_spatial_species

SPECIES=("ADPE","CHPE","GEPE")
TESTABLE={"exclude_unknown":("ADPE","CHPE","GEPE"),"ground_only":("CHPE","GEPE")}

def q(x,p): return float(np.quantile(np.asarray(x,float),p))

def filter_records(records,ids,mode):
    x=records.copy();x["unit_id"]=x.species_id.astype(str)+"|"+x.site_id.astype(str)
    x=x[x.unit_id.isin(ids)]
    if mode=="exclude_unknown": return x[x.vantage_family.astype(str)!="unknown"].copy()
    if mode=="ground_only": return x[x.vantage_raw.astype(str)=="ground"].copy()
    raise ValueError(mode)

def prepare_support(frames,metadata):
    supported={}; expected={"exclude_unknown":{"ADPE":40,"CHPE":30,"GEPE":28},"ground_only":{"ADPE":14,"CHPE":26,"GEPE":23}}
    for mode in expected:
        supported[mode]={}
        for sp in SPECIES:
            kept,_=filter_process_support(frames[sp],metadata,mode=mode)
            supported[mode][sp]=kept
    got={m:{s:len(supported[m][s]) for s in SPECIES} for m in expected}
    if got!=expected: raise ValueError(f"support drift {got}")
    return supported

def fit_mode(full_frames,supported,sim,mode,cal):
    out={}
    for sp in TESTABLE[mode]:
        frame=supported[mode][sp].reset_index(drop=True); ids=set(frame.unit_id.astype(str))
        obs=filter_records(sim["observations"],ids,mode)
        ff=full_frames[sp].reset_index(drop=True); truth=sim["truth"][sp]
        lm={u:float(v) for u,v in zip(ff.unit_id.astype(str),truth["true_lambda"])}
        out[sp]=fit_spatial_species(
          frame,obs,delta_image=float(cal["delta_image"]),
          sigma1=float(cal["accuracy"]["1"]["sigma"]),
          sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
          truth_forcing=truth["true_forcing"],true_lambda=[lm[u] for u in frame.unit_id.astype(str)]
        )
    return out

def summarize(raw):
    out={}
    for sp in sorted(raw["null"]):
        null=raw["null"][sp];cross=raw["crossover"][sp]
        groups={}
        for g in cross[0]["forcing_correlation"]:
            vals=[float(r["forcing_correlation"][g]) for sc in ("null","crossover") for r in raw[sc][sp]]
            groups[g]={"median_corr":q(vals,.5),"q05_corr":q(vals,.05)}
        n=[float(r["gamma_ah"]) for r in null]; c=[float(r["gamma_ah"]) for r in cross]
        checks={
          "factor_median":all(v["median_corr"]>=.7 for v in groups.values()),
          "factor_q05":all(v["q05_corr"]>=.3 for v in groups.values()),
          "crossover_bias":abs(q(c,.5)+.35)<=.1,
          "crossover_sign":float(np.mean(np.asarray(c)<0))>=.9,
          "null_center":abs(q(n,.5))<=.05,
          "null_contains_zero":q(n,.05)<=0<=q(n,.95)
        }
        out[sp]={"forcing_groups":groups,"null":{"median_gamma_ah":q(n,.5),"q05_gamma_ah":q(n,.05),"q95_gamma_ah":q(n,.95)},
                 "crossover":{"median_gamma_ah":q(c,.5),"negative_fraction":float(np.mean(np.asarray(c)<0))},
                 "gate":{"checks":checks,"passes":all(checks.values())}}
    return out

def run(fr,fu,br,metadata,reps=100):
    frames=build_v3_frames(fr,fu,br); sup=prepare_support(frames,metadata)
    raw={m:{sc:{sp:[] for sp in TESTABLE[m]} for sc in ("null","crossover")} for m in TESTABLE}
    for si,(sc,par) in enumerate((("null",(0.,0.)),("crossover",(0.,-.35)))):
        for rep in range(reps):
            sim=simulate_integrated_dataset(
              frames,metadata,gamma_a=par[0],gamma_ah=par[1],
              seed=26000000+si*100000+rep,forcing_sd=.08,loading_sd=.15,process_sd=.04,
              drift_mean=-.01,drift_sd=.01,delta_image=float(np.log(1.15)),
              sigma1=float(np.log(1.05)),sigma2plus=float(np.log(1.25)))
            obs=sim["observations"].reset_index(drop=True)
            cal=fit_observation_calibration_fast(count_to_analysis_scale(obs["count"].to_numpy(float)),prepare_observation_recovery_design(obs))
            for mode in TESTABLE:
                fits=fit_mode(frames,sup,sim,mode,cal)
                for sp,v in fits.items(): raw[mode][sc][sp].append(v)
    modes={}
    for mode in TESTABLE:
        species=summarize(raw[mode]); modes[mode]={"species":species,"all_testable_species_pass":all(v["gate"]["passes"] for v in species.values())}
    unlock=modes["exclude_unknown"]["all_testable_species_pass"] and modes["ground_only"]["all_testable_species_pass"]
    return {"schema_version":1,"audit_id":"mina-paper2-v3-source-sensitivity","replicates_per_scenario":reps,"modes":modes,
            "decision":{"source_sensitivity_passed":bool(unlock),"ADPE_ground_only":"coverage_limited_nonblocking","counts_may_be_opened":False,"no_real_count_magnitudes_opened":True}}

def load(path,expected):
    x=pyreadr.read_r(str(path));return x[expected] if expected in x else next(iter(x.values()))
def main():
    p=argparse.ArgumentParser();p.add_argument("--forcing-json",type=Path,required=True);p.add_argument("--forcing-csv",type=Path,required=True);p.add_argument("--breeding-csv",type=Path,required=True);p.add_argument("--mapppdr-dir",type=Path,required=True);p.add_argument("--out-json",type=Path,required=True);p.add_argument("--replicates",type=int,default=100);a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv);meta=build_frozen_observation_metadata(load(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs"))
    r=run(fr,fu,br,meta,a.replicates);a.out_json.parent.mkdir(parents=True,exist_ok=True);a.out_json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps(r,indent=2,sort_keys=True))
    if not r["decision"]["source_sensitivity_passed"]: raise SystemExit("V3 source sensitivity failed")
if __name__=="__main__":main()
