#!/usr/bin/env python3
"""Prespecified secondary H1: breeding-space buffering under Paper 2 V3."""
from __future__ import annotations
import argparse, glob, json
from pathlib import Path
import numpy as np, pandas as pd, pyreadr

from scripts.run_paper2_real_v3_fit import build_frozen_real_records, calibrate_observation
from scripts.run_paper2_v3_permutation import permutation_bounds, holm_adjust
from scripts.simulate_paper2_spatial_adjusted_v3 import build_v3_frames, fit_spatial_species

SPECIES=("ADPE","CHPE","GEPE")
B_DEFAULT=9999
SEED_DEFAULT=20260929


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x: return x[expected]
    if len(x)==1: return next(iter(x.values()))
    raise ValueError(expected)


def mode_frame(frame:pd.DataFrame,mode:str)->pd.DataFrame:
    out=frame.copy().reset_index(drop=True)
    if mode=="A_only":
        out["H"]=0.0
        out["AH"]=0.0
    elif mode=="H_only":
        out["A"]=0.0
        out["AH"]=0.0
    else:
        raise ValueError(mode)
    return out


def permute_A_within_blocks(
    frame:pd.DataFrame,
    *,
    global_index:int,
    species_index:int,
    seed:int=SEED_DEFAULT,
)->pd.DataFrame:
    out=mode_frame(frame,"A_only")
    rng=np.random.default_rng(
        np.random.SeedSequence([int(seed),int(global_index),int(species_index),101])
    )
    blocks=out["trait_block"].astype(str).to_numpy()
    for block in sorted(set(blocks.tolist())):
        idx=np.flatnonzero(blocks==block)
        if len(idx)<=1: continue
        src=idx[rng.permutation(len(idx))]
        out.loc[idx,"A"]=out.loc[src,"A"].to_numpy(dtype=float)
    return out


def _local_records(records:pd.DataFrame,frame:pd.DataFrame)->pd.DataFrame:
    ids=set(frame["unit_id"].astype(str))
    x=records.copy()
    x["unit_id"]=x["species_id"].astype(str)+"|"+x["site_id"].astype(str)
    return x[x["unit_id"].isin(ids)].copy().reset_index(drop=True)


def prepare_context(fr,fu,br,obs):
    frames=build_v3_frames(fr,fu,br)
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    got={sp:len(frames[sp]) for sp in SPECIES}
    if got!=expected: raise ValueError(f"frame drift {got}")
    records=build_frozen_real_records(obs)
    cal=calibrate_observation(records)
    local={sp:_local_records(records,frames[sp]) for sp in SPECIES}
    return frames,local,cal


def fit_mode(frame,records,cal,mode):
    f=mode_frame(frame,mode)
    fit=fit_spatial_species(
        f,records,
        delta_image=float(cal["delta_image"]),
        sigma1=float(cal["accuracy"]["1"]["sigma"]),
        sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
        truth_forcing=None,true_lambda=None,
    )
    return {
        "gamma_A":float(fit["gamma_a"]),
        "gamma_H":float(fit["gamma_h"]),
        "gamma_AH":float(fit["gamma_ah"]),
        "process_sd":float(fit["process_sd"]),
        "loading_residual_sd":float(fit["loading_residual_sd"]),
    }


def observed_point(frames,local,cal):
    return {
        sp:{
            "A_only":fit_mode(frames[sp],local[sp],cal,"A_only"),
            "H_only":fit_mode(frames[sp],local[sp],cal,"H_only"),
        }
        for sp in SPECIES
    }


def run_shard(fr,fu,br,obs,*,B,n_shards,shard,seed):
    frames,local,cal=prepare_context(fr,fu,br,obs)
    observed=observed_point(frames,local,cal)
    start,stop=permutation_bounds(B,n_shards,shard)
    rows=[]
    for k in range(start,stop):
        gamma={}
        for si,sp in enumerate(SPECIES):
            pf=permute_A_within_blocks(
                frames[sp],global_index=k,species_index=si,seed=seed
            )
            fit=fit_spatial_species(
                pf,local[sp],
                delta_image=float(cal["delta_image"]),
                sigma1=float(cal["accuracy"]["1"]["sigma"]),
                sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
                truth_forcing=None,true_lambda=None,
            )
            gamma[sp]=float(fit["gamma_a"])
        rows.append({"index":k,"species_gamma_A":gamma})
    return {
        "schema_version":1,"B":B,"seed":seed,"n_shards":n_shards,
        "shard":shard,"start":start,"stop":stop,
        "observed":observed,"permutations":rows,
    }


def q(vals,p):
    return float(np.quantile(np.asarray(vals,float),p))


def aggregate(paths,*,B,seed):
    shards=[]
    rows=[]
    observed=None
    for path in sorted(paths):
        x=json.loads(path.read_text())
        if int(x["B"])!=B or int(x["seed"])!=seed:
            raise ValueError(f"shard contract drift {path}")
        if observed is None:
            observed=x["observed"]
        elif x["observed"]!=observed:
            raise ValueError("observed point estimates differ across shards")
        rows.extend(x["permutations"])
        shards.append({"shard":int(x["shard"]),"start":int(x["start"]),"stop":int(x["stop"])})
    indices=sorted(int(r["index"]) for r in rows)
    if len(rows)!=B or indices!=list(range(B)):
        raise ValueError("permutation coverage invalid")
    raw={}
    species={}
    for sp in SPECIES:
        obs=float(observed[sp]["A_only"]["gamma_A"])
        vals=[float(r["species_gamma_A"][sp]) for r in rows]
        extreme=sum(v<=obs for v in vals)
        pval=(1+extreme)/(B+1)
        raw[sp]=pval
        species[sp]={
            "A_only":observed[sp]["A_only"],
            "H_only":observed[sp]["H_only"],
            "A_permutation":{
                "alternative":"gamma_A < 0",
                "extreme_permutations":extreme,
                "raw_p_value":pval,
                "distribution":{
                    "q01":q(vals,.01),"q05":q(vals,.05),"median":q(vals,.5),
                    "q95":q(vals,.95),"q99":q(vals,.99),
                },
            },
        }
    holm=holm_adjust(raw)
    for sp in SPECIES:
        species[sp]["A_permutation"]["holm_p_value"]=float(holm[sp])
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-a-buffering-secondary-v1",
        "B":B,"seed":seed,
        "species":species,
        "directional_concordance":{
            "negative_A_species":sum(species[sp]["A_only"]["gamma_A"]<0 for sp in SPECIES),
            "negative_H_species":sum(species[sp]["H_only"]["gamma_H"]<0 for sp in SPECIES),
        },
        "interpretation_boundary":{
            "status":"prespecified_secondary_H1",
            "primary_AH_result_replaced":False,
            "cross_species_A_p_value_created":False,
            "terrain_R_inference_opened":False,
        },
        "shards":sorted(shards,key=lambda z:z["shard"]),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("shard","aggregate"),required=True)
    p.add_argument("--B",type=int,default=B_DEFAULT);p.add_argument("--seed",type=int,default=SEED_DEFAULT)
    p.add_argument("--n-shards",type=int,default=20);p.add_argument("--shard",type=int)
    p.add_argument("--forcing-json",type=Path);p.add_argument("--forcing-csv",type=Path);p.add_argument("--breeding-csv",type=Path);p.add_argument("--mapppdr-dir",type=Path)
    p.add_argument("--shard-glob");p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    if a.mode=="shard":
        if None in (a.shard,a.forcing_json,a.forcing_csv,a.breeding_csv,a.mapppdr_dir):
            raise SystemExit("missing shard inputs")
        fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv)
        obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
        out=run_shard(fr,fu,br,obs,B=a.B,n_shards=a.n_shards,shard=a.shard,seed=a.seed)
    else:
        paths=[Path(x) for x in glob.glob(a.shard_glob or "")]
        out=aggregate(paths,B=a.B,seed=a.seed)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
