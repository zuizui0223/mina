#!/usr/bin/env python3
"""Source robustness for the V4 cross-species generality estimand."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pyreadr

from scripts.audit_paper2_integrated_sensitivity_support import filter_process_support
from scripts.simulate_paper2_integrated_recovery import simulate_integrated_dataset,count_to_analysis_scale
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,prepare_observation_recovery_design,
    fit_observation_calibration_fast
)
from scripts.simulate_paper2_spatial_adjusted_v3 import build_v3_frames,fit_spatial_species

SPECIES=("ADPE","CHPE","GEPE")

def q(x,p): return float(np.quantile(np.asarray(x,float),p))

def filter_records(records,ids,mode):
    x=records.copy();x["unit_id"]=x.species_id.astype(str)+"|"+x.site_id.astype(str)
    x=x[x.unit_id.isin(ids)]
    if mode=="exclude_unknown": return x[x.vantage_family.astype(str)!="unknown"].copy()
    if mode=="ground_only": return x[x.vantage_raw.astype(str)=="ground"].copy()
    raise ValueError(mode)

def prepare(frames,metadata):
    out={}
    expected={"exclude_unknown":{"ADPE":40,"CHPE":30,"GEPE":28},
              "ground_only":{"ADPE":14,"CHPE":26,"GEPE":23}}
    for mode in expected:
        out[mode]={}
        for sp in SPECIES:
            kept,_=filter_process_support(frames[sp],metadata,mode=mode)
            out[mode][sp]=kept
    got={m:{s:len(out[m][s]) for s in SPECIES} for m in expected}
    if got!=expected: raise ValueError(f"support drift {got}")
    return out

def one_replicate(frames,supported,metadata,seed,gamma):
    sim=simulate_integrated_dataset(
      frames,metadata,gamma_a=0.0,gamma_ah=gamma,seed=seed,
      forcing_sd=.08,loading_sd=.15,process_sd=.04,drift_mean=-.01,drift_sd=.01,
      delta_image=float(np.log(1.15)),sigma1=float(np.log(1.05)),sigma2plus=float(np.log(1.25)))
    obs=sim["observations"].reset_index(drop=True)
    cal=fit_observation_calibration_fast(
      count_to_analysis_scale(obs["count"].to_numpy(float)),
      prepare_observation_recovery_design(obs)
    )
    results={}
    for mode,species_list in (("exclude_unknown",SPECIES),("ground_only",("CHPE","GEPE"))):
        est={}
        for sp in species_list:
            frame=supported[mode][sp].reset_index(drop=True)
            ids=set(frame.unit_id.astype(str))
            local=filter_records(obs,ids,mode)
            full=frames[sp].reset_index(drop=True); truth=sim["truth"][sp]
            lm={u:float(v) for u,v in zip(full.unit_id.astype(str),truth["true_lambda"])}
            fit=fit_spatial_species(
              frame,local,delta_image=float(cal["delta_image"]),
              sigma1=float(cal["accuracy"]["1"]["sigma"]),
              sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
              truth_forcing=truth["true_forcing"],true_lambda=[lm[u] for u in frame.unit_id.astype(str)])
            est[sp]=float(fit["gamma_ah"])
        vals=np.asarray(list(est.values()),float)
        results[mode]={
          "gamma":est,
          "aggregate":float(np.median(vals)),
          "n_negative":int(np.sum(vals<0))
        }
    return results

def summarize(records,mode):
    a=[r["aggregate"] for r in records]
    neg=[r["n_negative"] for r in records]
    return {
      "aggregate":{"median":q(a,.5),"q05":q(a,.05),"q95":q(a,.95),"negative_fraction":float(np.mean(np.asarray(a)<0))},
      "replication_fraction":float(np.mean(np.asarray(neg)>=(2 if mode=="exclude_unknown" else 2))),
      "species_median_gamma":{sp:q([r["gamma"][sp] for r in records],.5) for sp in records[0]["gamma"]}
    }

def evaluate(frames,metadata,reps=100):
    supported=prepare(frames,metadata)
    raw={m:{s:[] for s in ("null","common")} for m in ("exclude_unknown","ground_only")}
    for si,(name,gamma) in enumerate((("null",0.0),("common",-0.35))):
        for rep in range(reps):
            rr=one_replicate(frames,supported,metadata,51000000+si*100000+rep,gamma)
            for mode in rr: raw[mode][name].append(rr[mode])
    modes={}
    for mode in raw:
        n=summarize(raw[mode]["null"],mode); c=summarize(raw[mode]["common"],mode)
        checks={
          "common_bias":abs(c["aggregate"]["median"]+.35)<=.10,
          "common_negative_fraction":c["aggregate"]["negative_fraction"]>=.90,
          "replication":c["replication_fraction"]>=.90,
          "null_center":abs(n["aggregate"]["median"])<=.05,
          "null_contains_zero":n["aggregate"]["q05"]<=0<=n["aggregate"]["q95"]
        }
        modes[mode]={"null":n,"common":c,"gate":{"checks":checks,"passes":all(checks.values())}}
    passed=all(v["gate"]["passes"] for v in modes.values())
    return {"modes":modes,"gate":{"passes":passed}}

def load(path,expected):
    x=pyreadr.read_r(str(path));return x[expected] if expected in x else next(iter(x.values()))
def main():
    p=argparse.ArgumentParser();p.add_argument("--forcing-json",type=Path,required=True);p.add_argument("--forcing-csv",type=Path,required=True);p.add_argument("--breeding-csv",type=Path,required=True);p.add_argument("--mapppdr-dir",type=Path,required=True);p.add_argument("--out-json",type=Path,required=True);p.add_argument("--replicates",type=int,default=100);a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv)
    frames=build_v3_frames(fr,fu,br);meta=build_frozen_observation_metadata(load(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs"))
    rec=evaluate(frames,meta,a.replicates)
    out={"schema_version":1,"audit_id":"mina-paper2-v4-source-generality","recovery":rec,
         "decision":{"paper_level_source_robustness_passed":bool(rec["gate"]["passes"]),"ADPE_species_specific_exclude_unknown":"previously_failed_86_of_100","counts_may_be_opened":False,"no_real_count_magnitudes_opened":True}}
    a.out_json.parent.mkdir(parents=True,exist_ok=True);a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,indent=2,sort_keys=True))
    if not rec["gate"]["passes"]: raise SystemExit("V4 source-generality recovery failed")
if __name__=="__main__":main()
