#!/usr/bin/env python3
"""Frozen real-outcome permutation inference for Paper 2 V3."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.run_paper2_real_v3_fit import (
    build_frozen_real_records,
    calibrate_observation,
)
from scripts.simulate_paper2_spatial_adjusted_v3 import (
    build_v3_frames,
    fit_spatial_species,
)

SPECIES=("ADPE","CHPE","GEPE")
B_DEFAULT=9999
SEED_DEFAULT=20260929


def permutation_bounds(B:int,n_shards:int,shard:int)->tuple[int,int]:
    if B<1 or n_shards<1 or not 0<=shard<n_shards:
        raise ValueError("invalid shard specification")
    q,r=divmod(B,n_shards)
    start=shard*q+min(shard,r)
    stop=start+q+(1 if shard<r else 0)
    return start,stop


def permute_traits_within_blocks(
    frame:pd.DataFrame,
    *,
    global_index:int,
    species_index:int,
    seed:int=SEED_DEFAULT,
)->pd.DataFrame:
    required={"trait_block","A","H","AH"}
    missing=required-set(frame.columns)
    if missing:
        raise ValueError(f"missing permutation columns: {sorted(missing)}")
    out=frame.copy().reset_index(drop=True)
    rng=np.random.default_rng(
        np.random.SeedSequence([int(seed),int(global_index),int(species_index)])
    )
    for block in sorted(out["trait_block"].astype(str).unique()):
        idx=np.flatnonzero(out["trait_block"].astype(str).to_numpy()==block)
        if len(idx)<=1:
            continue
        src=idx[rng.permutation(len(idx))]
        out.loc[idx,["A","H","AH"]]=(
            out.loc[src,["A","H","AH"]].to_numpy(dtype=float)
        )
    return out


def holm_adjust(pvalues:dict[str,float])->dict[str,float]:
    ordered=sorted(pvalues.items(),key=lambda kv:kv[1])
    m=len(ordered)
    adjusted={}
    running=0.0
    for rank,(name,p) in enumerate(ordered):
        val=min(1.0,(m-rank)*float(p))
        running=max(running,val)
        adjusted[name]=running
    return adjusted


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def _species_records(records:pd.DataFrame,frame:pd.DataFrame)->pd.DataFrame:
    ids=set(frame["unit_id"].astype(str))
    local=records.copy()
    local["unit_id"]=(
        local["species_id"].astype(str)+"|"+local["site_id"].astype(str)
    )
    return local[local["unit_id"].isin(ids)].copy().reset_index(drop=True)


def prepare_real_context(
    forcing_result:dict,
    forcing_units:pd.DataFrame,
    breeding_options:pd.DataFrame,
    obs:pd.DataFrame,
)->tuple[dict[str,pd.DataFrame],dict[str,pd.DataFrame],dict]:
    frames=build_v3_frames(forcing_result,forcing_units,breeding_options)
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    got={sp:int(len(frames[sp])) for sp in SPECIES}
    if got!=expected:
        raise ValueError(f"V3 frame drift: {got} != {expected}")
    records=build_frozen_real_records(obs)
    if len(records)!=2100:
        raise ValueError(f"record drift: {len(records)} != 2100")
    calibration=calibrate_observation(records)
    local={sp:_species_records(records,frames[sp]) for sp in SPECIES}
    return frames,local,calibration


def fit_permuted_index(
    frames:dict[str,pd.DataFrame],
    local_records:dict[str,pd.DataFrame],
    calibration:dict,
    *,
    global_index:int,
    seed:int=SEED_DEFAULT,
)->dict:
    gamma={}
    for species_index,sp in enumerate(SPECIES):
        perm=permute_traits_within_blocks(
            frames[sp],
            global_index=global_index,
            species_index=species_index,
            seed=seed,
        )
        fit=fit_spatial_species(
            perm,
            local_records[sp],
            delta_image=float(calibration["delta_image"]),
            sigma1=float(calibration["accuracy"]["1"]["sigma"]),
            sigma2plus=float(calibration["accuracy"]["2-5"]["sigma"]),
            truth_forcing=None,
            true_lambda=None,
        )
        gamma[sp]=float(fit["gamma_ah"])
    vals=np.asarray([gamma[sp] for sp in SPECIES],dtype=float)
    return {
        "index":int(global_index),
        "paper_median_gamma_ah":float(np.median(vals)),
        "species_gamma_ah":gamma,
    }


def run_shard(
    forcing_result:dict,
    forcing_units:pd.DataFrame,
    breeding_options:pd.DataFrame,
    obs:pd.DataFrame,
    *,
    B:int,
    n_shards:int,
    shard:int,
    seed:int,
)->dict:
    frames,local,cal=prepare_real_context(
        forcing_result,forcing_units,breeding_options,obs
    )
    start,stop=permutation_bounds(B,n_shards,shard)
    rows=[
        fit_permuted_index(
            frames,local,cal,global_index=k,seed=seed
        )
        for k in range(start,stop)
    ]
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-v3-permutation-shard",
        "B":int(B),
        "seed":int(seed),
        "n_shards":int(n_shards),
        "shard":int(shard),
        "start":int(start),
        "stop":int(stop),
        "n_permutations":int(len(rows)),
        "permutations":rows,
    }


def _quantiles(values:list[float])->dict:
    arr=np.asarray(values,dtype=float)
    return {
        "q01":float(np.quantile(arr,0.01)),
        "q05":float(np.quantile(arr,0.05)),
        "median":float(np.quantile(arr,0.50)),
        "q95":float(np.quantile(arr,0.95)),
        "q99":float(np.quantile(arr,0.99)),
    }


def aggregate(
    shard_paths:list[Path],
    point_result:dict,
    *,
    B:int,
    seed:int,
)->dict:
    rows=[]
    shard_meta=[]
    for path in sorted(shard_paths):
        x=json.loads(path.read_text(encoding="utf-8"))
        if int(x["B"])!=B or int(x["seed"])!=seed:
            raise ValueError(f"shard contract drift: {path}")
        rows.extend(x["permutations"])
        shard_meta.append({
            "shard":int(x["shard"]),
            "start":int(x["start"]),
            "stop":int(x["stop"]),
            "n_permutations":int(x["n_permutations"]),
        })
    indices=[int(r["index"]) for r in rows]
    if len(rows)!=B or sorted(indices)!=list(range(B)):
        raise ValueError(
            f"permutation coverage invalid: n={len(rows)}, unique={len(set(indices))}"
        )

    observed_paper=float(
        point_result["primary_cross_species"]["median_gamma_ah"]
    )
    observed_species={
        sp:float(point_result["primary"][sp]["gamma_ah"])
        for sp in SPECIES
    }

    perm_paper=[float(r["paper_median_gamma_ah"]) for r in rows]
    paper_extreme=sum(v<=observed_paper for v in perm_paper)
    paper_p=(1+paper_extreme)/(B+1)

    raw_p={}
    species_perm={}
    for sp in SPECIES:
        vals=[float(r["species_gamma_ah"][sp]) for r in rows]
        species_perm[sp]=vals
        extreme=sum(v<=observed_species[sp] for v in vals)
        raw_p[sp]=(1+extreme)/(B+1)
    holm=holm_adjust(raw_p)

    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-v3-permutation-inference-v1",
        "B":int(B),
        "seed":int(seed),
        "primary":{
            "statistic":"median gamma_AH across ADPE, CHPE, GEPE",
            "alternative":"more negative",
            "observed":observed_paper,
            "extreme_permutations":int(paper_extreme),
            "p_value":float(paper_p),
            "permutation_distribution":_quantiles(perm_paper),
        },
        "species":{
            sp:{
                "observed_gamma_ah":observed_species[sp],
                "raw_p_value":float(raw_p[sp]),
                "holm_p_value":float(holm[sp]),
                "permutation_distribution":_quantiles(species_perm[sp]),
            }
            for sp in SPECIES
        },
        "observed_context":{
            "all_species_gamma_ah_negative":bool(
                point_result["primary_cross_species"]["all_species_negative"]
            ),
            "crossover_classification_species":point_result[
                "primary_cross_species"
            ]["species_with_crossover_classification"],
        },
        "shards":sorted(shard_meta,key=lambda x:x["shard"]),
        "provenance":{
            "point_estimate_receipt":"results/PAPER2_FIRST_REAL_V3_FIT_RESULT_V1.json",
            "permutation_contract":"contracts/PAPER2_V3_PERMUTATION_EXECUTION_V1.json",
            "real_count_magnitudes_used":True,
        },
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("shard","aggregate"),required=True)
    p.add_argument("--B",type=int,default=B_DEFAULT)
    p.add_argument("--seed",type=int,default=SEED_DEFAULT)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--forcing-json",type=Path)
    p.add_argument("--forcing-csv",type=Path)
    p.add_argument("--breeding-csv",type=Path)
    p.add_argument("--mapppdr-dir",type=Path)
    p.add_argument("--n-shards",type=int,default=20)
    p.add_argument("--shard",type=int)
    p.add_argument("--shard-glob")
    p.add_argument("--point-result",type=Path)
    a=p.parse_args()

    if a.mode=="shard":
        required=(a.forcing_json,a.forcing_csv,a.breeding_csv,a.mapppdr_dir)
        if any(v is None for v in required) or a.shard is None:
            raise SystemExit("missing shard inputs")
        fr=json.loads(a.forcing_json.read_text(encoding="utf-8"))
        fu=pd.read_csv(a.forcing_csv)
        br=pd.read_csv(a.breeding_csv)
        obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
        out=run_shard(
            fr,fu,br,obs,
            B=a.B,n_shards=a.n_shards,shard=a.shard,seed=a.seed
        )
    else:
        if not a.shard_glob or a.point_result is None:
            raise SystemExit("missing aggregate inputs")
        paths=[Path(x) for x in glob.glob(a.shard_glob)]
        point=json.loads(a.point_result.read_text(encoding="utf-8"))
        out=aggregate(paths,point,B=a.B,seed=a.seed)

    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
