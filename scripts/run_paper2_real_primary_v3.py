#!/usr/bin/env python3
"""Locked Paper 2 V3 primary real-outcome runner."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pyreadr

from scripts.check_paper2_real_unlock import assert_real_outcome_unlocked
from scripts.simulate_paper2_observation_recovery import (
    SPECIES,WINDOW,EXPECTED_GATE0,EXPECTED_BRIDGED,_thirds,_vantage_family,_accuracy_group,
    prepare_observation_recovery_design,fit_observation_calibration_fast,
)
from scripts.simulate_paper2_integrated_recovery import count_to_analysis_scale
from scripts.simulate_paper2_spatial_adjusted_v3 import build_v3_frames,fit_spatial_species


def load_rda(path:Path,expected:str):
    x=pyreadr.read_r(str(path)); return x[expected] if expected in x else next(iter(x.values()))


def build_frozen_real_records(obs:pd.DataFrame)->pd.DataFrame:
    required={"site_id","species_id","type","count","year","season","vantage","accuracy"}
    missing=required-set(obs.columns)
    if missing: raise ValueError(f"missing columns {sorted(missing)}")
    nest=obs[obs.species_id.isin(SPECIES)&obs.type.eq("nests")&obs["count"].notna()].copy()
    nest["year"]=pd.to_numeric(nest.year,errors="coerce");nest["season"]=pd.to_numeric(nest.season,errors="coerce")
    gate0=[]
    for (site,sp),local in nest.dropna(subset=["year"]).groupby(["site_id","species_id"]):
        years=sorted({int(v) for v in local.year})
        if len(years)>=5 and max(years)-min(years)>=10: gate0.append((str(site),str(sp)))
    got={sp:sum(s==sp for _,s in gate0) for sp in SPECIES}
    if got!=EXPECTED_GATE0: raise ValueError(f"gate0 drift {got}")
    grouped={(str(a),str(b)):x for (a,b),x in nest.groupby(["site_id","species_id"])}
    start,end=WINDOW;first,_,last=_thirds(start,end);bridged=[]
    for site,sp in gate0:
        ss=sorted({int(v) for v in grouped[(site,sp)].season.dropna() if start<=int(v)<=end})
        if ss and len(ss)>=5 and max(ss)-min(ss)>=10 and any(first[0]<=v<=first[1] for v in ss) and any(last[0]<=v<=last[1] for v in ss):
            bridged.append((site,sp))
    got={sp:sum(s==sp for _,s in bridged) for sp in SPECIES}
    if got!=EXPECTED_BRIDGED: raise ValueError(f"bridged drift {got}")
    keys=set(bridged)
    cohort=nest[nest.apply(lambda r:(str(r.site_id),str(r.species_id)) in keys,axis=1)&nest.season.between(start,end)].copy()
    out=pd.DataFrame({
      "site_id":cohort.site_id.astype(str),"species_id":cohort.species_id.astype(str),
      "season":cohort.season.astype(int),"count":pd.to_numeric(cohort["count"],errors="raise").astype(float),
      "vantage_family":cohort.vantage.map(_vantage_family),
      "vantage_raw":cohort.vantage.map(lambda v:"missing" if pd.isna(v) else str(v).strip().lower().replace("_"," ")),
      "accuracy_group":cohort.accuracy.map(_accuracy_group),
    })
    out["group_id"]=out.site_id+"|"+out.species_id+"|"+out.season.astype(str)
    out=out.sort_values(["species_id","site_id","season","vantage_family","accuracy_group"]).reset_index(drop=True)
    if len(out)!=2100: raise ValueError(f"record drift {len(out)} != 2100")
    if (out["count"]<0).any(): raise ValueError("negative count")
    return out


def fit_primary(frames,records):
    cal=fit_observation_calibration_fast(
      count_to_analysis_scale(records["count"].to_numpy(float)),
      prepare_observation_recovery_design(records)
    )
    species={}
    for sp,frame in frames.items():
        ids=set(frame.unit_id.astype(str))
        local=records[(records.species_id.astype(str)+"|"+records.site_id.astype(str)).isin(ids)].copy()
        fit=fit_spatial_species(
          frame,local,delta_image=float(cal["delta_image"]),
          sigma1=float(cal["accuracy"]["1"]["sigma"]),sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
          truth_forcing=None,true_lambda=None
        )
        species[sp]={
          "n_units":int(len(frame)),
          "gamma_a":fit["gamma_a"],"gamma_h":fit["gamma_h"],"gamma_ah":fit["gamma_ah"],
          "low_area_H_slope":float(fit["gamma_h"]-fit["gamma_ah"]),
          "high_area_H_slope":float(fit["gamma_h"]+fit["gamma_ah"]),
          "process_sd":fit["process_sd"],"loading_residual_sd":fit["loading_residual_sd"],
          "block_intercepts":fit["block_intercepts"],
          "block_mean_lambda":fit["block_mean_lambda"],
          "crossover_directional_pattern":bool(
             fit["gamma_ah"]<0 and (fit["gamma_h"]-fit["gamma_ah"])>=0 and (fit["gamma_h"]+fit["gamma_ah"])<0
          )
        }
    return {"observation":cal,"species":species}


def main():
    p=argparse.ArgumentParser();p.add_argument("--repo-root",type=Path,default=Path("."));p.add_argument("--mapppdr-dir",type=Path,required=True)
    p.add_argument("--forcing-json",type=Path,required=True);p.add_argument("--forcing-csv",type=Path,required=True);p.add_argument("--breeding-csv",type=Path,required=True);p.add_argument("--out-json",type=Path,required=True);a=p.parse_args()
    unlock=assert_real_outcome_unlocked(a.repo_root)  # MUST precede reading penguin_obs.rda
    fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv)
    frames=build_v3_frames(fr,fu,br)
    obs=load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    records=build_frozen_real_records(obs)
    result={"schema_version":1,"analysis_id":"mina-paper2-v3-real-primary","unlock":unlock,"primary":fit_primary(frames,records)}
    a.out_json.parent.mkdir(parents=True,exist_ok=True);a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
