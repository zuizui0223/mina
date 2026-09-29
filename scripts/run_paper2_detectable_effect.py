#!/usr/bin/env python3
"""Retrospective detectable-effect analysis for Paper 2."""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.simulate_paper2_cross_species_generality_v4 import (
    simulate_species_effects,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
)
from scripts.simulate_paper2_spatial_adjusted_v3 import (
    build_v3_frames,
)

SPECIES=("ADPE","CHPE","GEPE")
B=9999
PERM_DENOM=B+1


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def build_permutation_reference(paths:list[Path])->dict:
    rows=[]
    for path in sorted(paths):
        x=json.loads(path.read_text(encoding="utf-8"))
        rows.extend(float(r["paper_median_gamma_ah"]) for r in x["permutations"])
    if len(rows)!=B:
        raise ValueError(f"expected {B} primary permutation statistics, got {len(rows)}")
    values=np.sort(np.asarray(rows,dtype=float))
    # Largest permutation statistic that still corresponds to <=499 extremes
    # when the synthetic statistic equals that value. Continuous simulated
    # statistics are evaluated by exact rank instead of threshold alone.
    return {
        "B":B,
        "sorted_paper_median_gamma_ah":values.tolist(),
        "q05":float(np.quantile(values,0.05)),
        "rank_499_value":float(values[498]),
        "rank_500_value":float(values[499]),
    }


def exact_frozen_p(stat:float,sorted_null:np.ndarray)->float:
    # number of frozen permutation statistics <= candidate statistic
    count=int(np.searchsorted(sorted_null,float(stat),side="right"))
    return float((1+count)/PERM_DENOM)


def prepare_context(fr,fu,br,obs):
    frames=build_v3_frames(fr,fu,br)
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    got={sp:int(len(frames[sp])) for sp in SPECIES}
    if got!=expected:
        raise ValueError(f"frame drift {got} != {expected}")
    metadata=build_frozen_observation_metadata(obs)
    if len(metadata)!=2100:
        raise ValueError(f"metadata drift {len(metadata)} != 2100")
    return frames,metadata


def wilson(success:int,n:int,z:float=1.959963984540054)->tuple[float,float]:
    if n<=0:
        raise ValueError("n must be positive")
    p=success/n
    den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0.0,center-half),min(1.0,center+half)


def run_effect(
    frames,
    metadata,
    *,
    effect:float,
    sorted_null:np.ndarray,
    replicates:int,
    seed_base:int,
)->dict:
    stats=[]
    pvals=[]
    detections=[]
    effects={sp:float(effect) for sp in SPECIES}
    for rep in range(replicates):
        est,_=simulate_species_effects(
            frames,
            metadata,
            effects,
            seed=int(seed_base+rep),
        )
        vals=np.asarray([float(est[sp]) for sp in SPECIES],dtype=float)
        stat=float(np.median(vals))
        p=exact_frozen_p(stat,sorted_null)
        stats.append(stat)
        pvals.append(p)
        detections.append(p<=0.05)
    success=int(sum(detections))
    lo,hi=wilson(success,replicates)
    arr=np.asarray(stats,dtype=float)
    return {
        "truth_gamma_ah":float(effect),
        "abs_truth":float(abs(effect)),
        "replicates":int(replicates),
        "detections":success,
        "detection_fraction":float(success/replicates),
        "wilson95":[float(lo),float(hi)],
        "fitted_statistic":{
            "median":float(np.median(arr)),
            "q05":float(np.quantile(arr,0.05)),
            "q95":float(np.quantile(arr,0.95)),
        },
        "p_value":{
            "median":float(np.median(np.asarray(pvals,dtype=float))),
            "q05":float(np.quantile(np.asarray(pvals,dtype=float),0.05)),
            "q95":float(np.quantile(np.asarray(pvals,dtype=float),0.95)),
        },
    }


def isotonic_non_decreasing(y:list[float],weights:list[float]|None=None)->list[float]:
    vals=[float(v) for v in y]
    w=[1.0]*len(vals) if weights is None else [float(v) for v in weights]
    blocks=[]
    for i,(val,wt) in enumerate(zip(vals,w)):
        blocks.append({"start":i,"end":i,"weight":wt,"mean":val})
        while len(blocks)>=2 and blocks[-2]["mean"]>blocks[-1]["mean"]:
            b=blocks.pop()
            a=blocks.pop()
            tw=a["weight"]+b["weight"]
            mean=(a["mean"]*a["weight"]+b["mean"]*b["weight"])/tw
            blocks.append({
                "start":a["start"],"end":b["end"],"weight":tw,"mean":mean
            })
    out=[0.0]*len(vals)
    for block in blocks:
        for i in range(block["start"],block["end"]+1):
            out[i]=float(block["mean"])
    return out


def interpolate_mde(mags:list[float],power:list[float],target:float)->float|None:
    for i,p in enumerate(power):
        if p>=target:
            if i==0:
                return float(mags[0])
            x0,x1=float(mags[i-1]),float(mags[i])
            y0,y1=float(power[i-1]),float(power[i])
            if y1<=y0:
                return x1
            frac=(target-y0)/(y1-y0)
            return float(x0+frac*(x1-x0))
    return None


def aggregate(effect_paths:list[Path],reference:dict)->dict:
    effects=[]
    for path in sorted(effect_paths):
        x=json.loads(path.read_text(encoding="utf-8"))
        effects.append(x)
    effects=sorted(effects,key=lambda x:float(x["abs_truth"]))
    mags=[float(x["abs_truth"]) for x in effects]
    raw=[float(x["detection_fraction"]) for x in effects]
    reps=[int(x["replicates"]) for x in effects]
    iso=isotonic_non_decreasing(raw,[float(n) for n in reps])
    mde80=interpolate_mde(mags,iso,0.80)
    mde90=interpolate_mde(mags,iso,0.90)
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-retrospective-detectable-effect-v1",
        "frozen_permutation_reference":{
            "B":int(reference["B"]),
            "q05":float(reference["q05"]),
            "rank_499_value":float(reference["rank_499_value"]),
            "rank_500_value":float(reference["rank_500_value"]),
        },
        "effects":effects,
        "isotonic_detection_curve":[
            {
                "abs_gamma_ah":mags[i],
                "raw_detection_fraction":raw[i],
                "isotonic_detection_fraction":iso[i],
            }
            for i in range(len(mags))
        ],
        "thresholds":{
            "MDE80_abs_gamma_ah":mde80,
            "MDE90_abs_gamma_ah":mde90,
        },
        "observed_reference":{
            "observed_cross_species_median_gamma_ah":-0.31822603579776854,
            "observed_permutation_p":0.0947,
        },
        "interpretation_boundary":{
            "prospective_power_claim":False,
            "post_inference_operating_characteristic":True,
            "primary_inference_replaced":False,
        },
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("reference","effect","aggregate"),required=True)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--perm-shard-glob")
    p.add_argument("--reference-json",type=Path)
    p.add_argument("--effect-glob")
    p.add_argument("--effect",type=float)
    p.add_argument("--replicates",type=int,default=300)
    p.add_argument("--seed-base",type=int,default=41000000)
    p.add_argument("--forcing-json",type=Path)
    p.add_argument("--forcing-csv",type=Path)
    p.add_argument("--breeding-csv",type=Path)
    p.add_argument("--mapppdr-dir",type=Path)
    a=p.parse_args()

    if a.mode=="reference":
        paths=[Path(x) for x in glob.glob(a.perm_shard_glob or "")]
        out=build_permutation_reference(paths)
    elif a.mode=="effect":
        if None in (a.reference_json,a.effect,a.forcing_json,a.forcing_csv,a.breeding_csv,a.mapppdr_dir):
            raise SystemExit("missing effect inputs")
        ref=json.loads(a.reference_json.read_text(encoding="utf-8"))
        sorted_null=np.asarray(ref["sorted_paper_median_gamma_ah"],dtype=float)
        fr=json.loads(a.forcing_json.read_text(encoding="utf-8"))
        fu=pd.read_csv(a.forcing_csv); br=pd.read_csv(a.breeding_csv)
        obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
        frames,metadata=prepare_context(fr,fu,br,obs)
        tag=int(round(abs(float(a.effect))*1000))
        out=run_effect(
            frames,metadata,
            effect=float(a.effect),
            sorted_null=sorted_null,
            replicates=int(a.replicates),
            seed_base=int(a.seed_base+tag*10000),
        )
    else:
        if a.reference_json is None:
            raise SystemExit("missing reference-json")
        ref=json.loads(a.reference_json.read_text(encoding="utf-8"))
        paths=[Path(x) for x in glob.glob(a.effect_glob or "")]
        out=aggregate(paths,ref)

    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
