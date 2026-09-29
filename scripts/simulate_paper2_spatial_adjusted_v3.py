#!/usr/bin/env python3
"""Spatially adjusted hierarchical recovery for Paper 2 V3."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np, pandas as pd, pyreadr

from scripts.simulate_paper2_integrated_recovery import (
    simulate_integrated_dataset,count_to_analysis_scale,collapse_same_season
)
from scripts.simulate_paper2_latent_factor_recovery import build_scale_frame
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,prepare_observation_recovery_design,
    fit_observation_calibration_fast,
)
from scripts.simulate_paper2_integrated_hierarchical_recovery import (
    _build_observed_intervals,_solve_forcing_interval,_profile_interval_process_sd,
    _forcing_sum,_interval_variance,_solve_constrained_system,_q,
    _hierarchical_scenario_summary,
)

SPECIES=("ADPE","CHPE","GEPE")


def build_v3_frames(forcing_result,forcing_units,breeding):
    frames={}
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    for sp in SPECIES:
        frame=build_scale_frame(forcing_result,forcing_units,breeding,sp,"species_wide")
        meta=forcing_units[forcing_units["species_id"].astype(str).eq(sp)][
            ["unit_id","region","ccamlr_id"]
        ].drop_duplicates("unit_id")
        frame=frame.merge(meta,on="unit_id",how="left",validate="one_to_one")
        frame["trait_block"]=(
            frame["ccamlr_id"].astype(str)
            if sp=="ADPE" else frame["region"].astype(str)
        )
        if frame["trait_block"].isin(["nan","None",""]).any():
            raise ValueError(f"missing trait block in {sp}")
        frames[sp]=frame
    got={sp:len(f) for sp,f in frames.items()}
    if got!=expected: raise ValueError(f"frame drift: {got} != {expected}")
    return frames


def center_within_block(frame):
    out=frame.copy()
    for raw,c in (("A","Ac"),("H","Hc"),("AH","AHc")):
        out[c]=pd.to_numeric(out[raw],errors="raise")-out.groupby("trait_block")[raw].transform("mean")
    return out


def solve_site_gamma_block(intervals,frame,forcing,process_sd,loading_sd,min_loading_sd=0.05):
    n=len(frame); p=3
    X=frame[["Ac","Hc","AHc"]].to_numpy(float)
    blocks=frame["trait_block"].astype(str).to_numpy()
    levels=sorted(set(blocks.tolist())); B=len(levels)
    bindex={b:j for j,b in enumerate(levels)}
    sig=max(float(loading_sd),1e-8)
    cols=n+p+B+n
    A=np.zeros((len(intervals)+n,cols)); y=np.zeros(len(intervals)+n)
    r=0
    for it in intervals:
        i=int(it["site"]); fsum=_forcing_sum(forcing,it)
        w=1/np.sqrt(max(_interval_variance(it,process_sd),1e-12))
        A[r,i]=float(it["duration"])*w
        A[r,n:n+p]=fsum*X[i]*w
        A[r,n+p+bindex[str(blocks[i])]]=fsum*w
        A[r,n+p+B+i]=fsum*w
        y[r]=(float(it["delta"])-fsum)*w
        r+=1
    for i in range(n):
        A[r,n+p+B+i]=1/sig; r+=1

    # block-mean residual loading deviations = 0
    C=np.zeros((B+1,cols))
    for bi,b in enumerate(levels):
        idx=np.flatnonzero(blocks==b)
        C[bi,n+p+B+idx]=1/len(idx)
    # site-count-weighted mean block intercept = 0
    for b in levels:
        idx=np.flatnonzero(blocks==b)
        C[B,n+p+bindex[b]]=len(idx)/n

    sol=_solve_constrained_system(A,y,C)
    mu=sol[:n]; gamma=sol[n:n+p]
    alpha=sol[n+p:n+p+B]; resid=sol[n+p+B:]
    lam=1+X@gamma+np.asarray([alpha[bindex[str(b)]] for b in blocks])+resid
    loading_sd_new=max(float(np.sqrt(np.mean(resid*resid))),float(min_loading_sd))
    return mu,lam,gamma,alpha,resid,loading_sd_new


def fit_spatial_species(frame,observations,*,delta_image,sigma1,sigma2plus,
                        truth_forcing=None,true_lambda=None,iterations=12):
    f=center_within_block(frame.reset_index(drop=True))
    collapsed=collapse_same_season(
        observations,delta_image=delta_image,sigma1=sigma1,sigma2plus=sigma2plus
    )
    intervals=_build_observed_intervals(f,collapsed)
    n=len(f); lam=np.ones(n); process_sd=0.10; loading_sd=0.30
    mu,forcing=_solve_forcing_interval(intervals,f,lam,process_sd)
    alpha=np.zeros(f["trait_block"].nunique()); gamma=np.zeros(3); resid=np.zeros(n)
    for _ in range(iterations):
        mu,forcing=_solve_forcing_interval(intervals,f,lam,process_sd)
        mu,lam,gamma,alpha,resid,loading_sd=solve_site_gamma_block(
            intervals,f,forcing,process_sd,loading_sd
        )
        process_sd=_profile_interval_process_sd(intervals,mu,lam,forcing)
    mu,forcing=_solve_forcing_interval(intervals,f,lam,process_sd)
    mu,lam,gamma,alpha,resid,loading_sd=solve_site_gamma_block(
        intervals,f,forcing,process_sd,loading_sd
    )
    corr={}
    if truth_forcing is not None:
        for g,v in forcing.items():
            corr[g]=float(np.corrcoef(np.asarray(truth_forcing[g],float),v)[0,1])
    lc=None
    if true_lambda is not None:
        lc=float(np.corrcoef(np.asarray(true_lambda,float),lam)[0,1])
    return {
      "gamma_a":float(gamma[0]),"gamma_h":float(gamma[1]),"gamma_ah":float(gamma[2]),
      "forcing_correlation":corr,"lambda_correlation":lc,
      "process_sd":float(process_sd),"loading_residual_sd":float(loading_sd),
      "block_intercepts":{b:float(alpha[i]) for i,b in enumerate(sorted(f["trait_block"].astype(str).unique()))},
      "block_mean_lambda":{b:float(lam[np.flatnonzero(f["trait_block"].astype(str).to_numpy()==b)].mean()) for b in sorted(f["trait_block"].astype(str).unique())},
    }


def fit_dataset(frames,observations,truth):
    rec=observations.reset_index(drop=True)
    design=prepare_observation_recovery_design(rec)
    cal=fit_observation_calibration_fast(count_to_analysis_scale(rec["count"].to_numpy(float)),design)
    species={}
    for sp,frame in frames.items():
        ids=set(frame["unit_id"].astype(str))
        local=rec[(rec["species_id"].astype(str)+"|"+rec["site_id"].astype(str)).isin(ids)].copy()
        meta=truth[sp]
        species[sp]=fit_spatial_species(
            frame,local,
            delta_image=float(cal["delta_image"]),
            sigma1=float(cal["accuracy"]["1"]["sigma"]),
            sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
            truth_forcing=meta["true_forcing"],true_lambda=meta["true_lambda"],
        )
    return {"observation":cal,"species":species}


def evaluate(frames,metadata,replicates=100,seed_offset=22000000):
    scenarios={"null":{"gamma_a":0.0,"gamma_ah":0.0},
               "crossover":{"gamma_a":0.0,"gamma_ah":-0.35},
               "simple_buffering":{"gamma_a":-0.25,"gamma_ah":0.0}}
    records={sp:{s:[] for s in scenarios} for sp in SPECIES}
    fc={sp:{} for sp in SPECIES}; obs=[]
    for si,(sc,par) in enumerate(scenarios.items()):
        for rep in range(replicates):
            sim=simulate_integrated_dataset(
                frames,metadata,gamma_a=par["gamma_a"],gamma_ah=par["gamma_ah"],
                seed=seed_offset+si*100000+rep,forcing_sd=0.08,loading_sd=0.15,
                process_sd=0.04,drift_mean=-0.01,drift_sd=0.01,
                delta_image=float(np.log(1.15)),sigma1=float(np.log(1.05)),
                sigma2plus=float(np.log(1.25))
            )
            fit=fit_dataset(frames,sim["observations"],sim["truth"])
            obs.append(fit["observation"])
            for sp,val in fit["species"].items():
                records[sp][sc].append(val)
                for g,x in val["forcing_correlation"].items():
                    fc[sp].setdefault(g,[]).append(float(x))
    species={}; passes={}
    for sp in SPECIES:
        groups={g:{"median_corr":_q(v,0.5),"q05_corr":_q(v,0.05)} for g,v in fc[sp].items()}
        null=_hierarchical_scenario_summary(records[sp]["null"])
        cross=_hierarchical_scenario_summary(records[sp]["crossover"])
        simple=_hierarchical_scenario_summary(records[sp]["simple_buffering"])
        checks={
          "factor_median":all(x["median_corr"]>=.7 for x in groups.values()),
          "factor_q05":all(x["q05_corr"]>=.3 for x in groups.values()),
          "crossover_bias":abs(cross["median_gamma_ah"]+.35)<=.1,
          "crossover_sign":cross["negative_gamma_ah_fraction"]>=.9,
          "null_center":abs(null["median_gamma_ah"])<=.05,
          "null_contains_zero":null["q05_gamma_ah"]<=0<=null["q95_gamma_ah"],
          "simple_a_bias":abs(simple["median_gamma_a"]+.25)<=.1,
          "simple_a_sign":simple["negative_gamma_a_fraction"]>=.9,
          "simple_no_spurious_crossover":abs(simple["median_gamma_ah"])<=.06,
        }
        species[sp]={"forcing_groups":groups,"null":null,"crossover":cross,
                     "simple_buffering":simple,"gate":{"checks":checks,"passes":all(checks.values())}}
        passes[sp]=bool(all(checks.values()))
    return {"replicates_per_scenario":replicates,"species":species,
            "gate":{"species_pass":passes,"passes":all(passes.values())}}


def load_rda(path,expected):
    x=pyreadr.read_r(str(path)); return x[expected] if expected in x else next(iter(x.values()))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",type=Path,required=True);p.add_argument("--forcing-csv",type=Path,required=True)
    p.add_argument("--breeding-csv",type=Path,required=True);p.add_argument("--mapppdr-dir",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True);p.add_argument("--replicates",type=int,default=100)
    a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv)
    frames=build_v3_frames(fr,fu,br)
    obs=load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    meta=build_frozen_observation_metadata(obs)
    result={"schema_version":3,"audit_id":"mina-paper2-spatial-adjusted-v3",
            "trait_blocks":{sp:frames[sp]["trait_block"].value_counts().to_dict() for sp in SPECIES},
            "recovery":evaluate(frames,meta,a.replicates),
            "decision":{"counts_may_be_opened":False,"no_real_count_magnitudes_opened":True}}
    result["decision"]["spatially_adjusted_core_passed"]=bool(result["recovery"]["gate"]["passes"])
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result["decision"]["spatially_adjusted_core_passed"]:
        raise SystemExit("spatial-adjusted V3 recovery failed")
if __name__=="__main__": main()
