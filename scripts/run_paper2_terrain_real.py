#!/usr/bin/env python3
"""Real prespecified Paper 2 terrain R-main fit and frozen block permutation inference."""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.paper2_terrain_model import (
    SPECIES,
    build_terrain_frames,
    fit_terrain_species,
)
from scripts.run_paper2_real_v3_fit import (
    build_frozen_real_records,
    calibrate_observation,
)
from scripts.run_paper2_v3_permutation import (
    holm_adjust,
    permutation_bounds,
)

B_DEFAULT=9999
SEED_DEFAULT=20260946


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def _local_records(records:pd.DataFrame,frame:pd.DataFrame)->pd.DataFrame:
    ids=set(frame["unit_id"].astype(str))
    x=records.copy()
    x["unit_id"]=x["species_id"].astype(str)+"|"+x["site_id"].astype(str)
    return x[x["unit_id"].isin(ids)].copy().reset_index(drop=True)


def prepare_context(fr,fu,br,terrain,obs):
    frames=build_terrain_frames(fr,fu,br,terrain)
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    got={sp:int(len(frames[sp])) for sp in SPECIES}
    if got!=expected:
        raise ValueError(f"terrain frame drift: {got} != {expected}")
    records=build_frozen_real_records(obs)
    cal=calibrate_observation(records)
    local={sp:_local_records(records,frames[sp]) for sp in SPECIES}
    return frames,local,cal


def fit_one(frame,records,cal):
    fit=fit_terrain_species(
        frame,
        records,
        delta_image=float(cal["delta_image"]),
        sigma1=float(cal["accuracy"]["1"]["sigma"]),
        sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
        truth_forcing=None,
        true_lambda=None,
    )
    return {
        "gamma_R":float(fit["gamma_r"]),
        "process_sd":float(fit["process_sd"]),
        "loading_residual_sd":float(fit["loading_residual_sd"]),
        "n_units":int(fit["n_units"]),
        "n_collapsed_seasons":int(fit["n_collapsed_seasons"]),
        "block_intercepts":fit["block_intercepts"],
        "block_mean_lambda":fit["block_mean_lambda"],
    }


def observed_point(frames,local,cal):
    return {sp:fit_one(frames[sp],local[sp],cal) for sp in SPECIES}


def permute_r_within_blocks(
    frame:pd.DataFrame,
    *,
    global_index:int,
    species_index:int,
    seed:int=SEED_DEFAULT,
)->pd.DataFrame:
    out=frame.copy().reset_index(drop=True)
    rng=np.random.default_rng(
        np.random.SeedSequence(
            [int(seed),int(global_index),int(species_index),707]
        )
    )
    blocks=out["trait_block"].astype(str).to_numpy()
    for block in sorted(set(blocks.tolist())):
        idx=np.flatnonzero(blocks==block)
        if len(idx)<=1:
            continue
        src=idx[rng.permutation(len(idx))]
        out.loc[idx,"R"]=out.loc[src,"R"].to_numpy(dtype=float)
    return out


def ordered_score(gamma:dict[str,float])->float:
    ad=float(gamma["ADPE"])
    ch=float(gamma["CHPE"])
    ge=float(gamma["GEPE"])
    return float(min(-ad,ch-ad,ge-ch))


def run_shard(fr,fu,br,terrain,obs,*,B,n_shards,shard,seed):
    frames,local,cal=prepare_context(fr,fu,br,terrain,obs)
    observed=observed_point(frames,local,cal)
    start,stop=permutation_bounds(B,n_shards,shard)
    rows=[]
    for k in range(start,stop):
        gamma={}
        for si,sp in enumerate(SPECIES):
            pf=permute_r_within_blocks(
                frames[sp],
                global_index=k,
                species_index=si,
                seed=seed,
            )
            fit=fit_terrain_species(
                pf,
                local[sp],
                delta_image=float(cal["delta_image"]),
                sigma1=float(cal["accuracy"]["1"]["sigma"]),
                sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
                truth_forcing=None,
                true_lambda=None,
            )
            gamma[sp]=float(fit["gamma_r"])
        rows.append({
            "index":int(k),
            "species_gamma_R":gamma,
            "ordered_score":ordered_score(gamma),
        })
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-terrain-real-v1-shard",
        "B":int(B),
        "seed":int(seed),
        "n_shards":int(n_shards),
        "shard":int(shard),
        "start":int(start),
        "stop":int(stop),
        "observed":observed,
        "permutations":rows,
    }


def _q(values,p):
    return float(np.quantile(np.asarray(values,dtype=float),p))


def aggregate(paths,*,B,seed):
    rows=[]
    observed=None
    shards=[]
    for path in sorted(paths):
        x=json.loads(path.read_text(encoding="utf-8"))
        if int(x["B"])!=int(B) or int(x["seed"])!=int(seed):
            raise ValueError(f"shard contract drift: {path}")
        if observed is None:
            observed=x["observed"]
        else:
            for sp in SPECIES:
                ref=float(observed[sp]["gamma_R"])
                cur=float(x["observed"][sp]["gamma_R"])
                if not np.isclose(ref,cur,rtol=1e-10,atol=1e-10):
                    raise ValueError(
                        f"observed gamma_R drift {sp}: {cur} != {ref}"
                    )
        rows.extend(x["permutations"])
        shards.append({
            "shard":int(x["shard"]),
            "start":int(x["start"]),
            "stop":int(x["stop"]),
        })

    indices=sorted(int(r["index"]) for r in rows)
    if len(rows)!=B or indices!=list(range(B)):
        raise ValueError("permutation coverage invalid")

    raw={}
    species={}
    for sp in SPECIES:
        obs=float(observed[sp]["gamma_R"])
        vals=np.asarray(
            [float(r["species_gamma_R"][sp]) for r in rows],
            dtype=float,
        )
        extreme=int(np.sum(np.abs(vals)>=abs(obs)))
        pval=float((1+extreme)/(B+1))
        raw[sp]=pval
        species[sp]={
            **observed[sp],
            "permutation":{
                "alternative":"two_sided",
                "extreme_permutations":extreme,
                "raw_p_value":pval,
                "distribution":{
                    "q01":_q(vals,.01),
                    "q05":_q(vals,.05),
                    "median":_q(vals,.50),
                    "q95":_q(vals,.95),
                    "q99":_q(vals,.99),
                },
            },
        }
    holm=holm_adjust(raw)
    for sp in SPECIES:
        species[sp]["permutation"]["holm_p_value"]=float(holm[sp])

    obs_gamma={sp:float(observed[sp]["gamma_R"]) for sp in SPECIES}
    obs_score=ordered_score(obs_gamma)
    null_scores=np.asarray([float(r["ordered_score"]) for r in rows],dtype=float)
    order_extreme=int(np.sum(null_scores>=obs_score))
    order_p=float((1+order_extreme)/(B+1))
    order_supported=bool(obs_score>0 and order_p<=0.05)

    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-terrain-real-v1",
        "contract_id":"mina-paper2-terrain-life-history-v1",
        "B":int(B),
        "seed":int(seed),
        "terrain_trait":"z(log1p(elevation_relief_p90_p10_m_2000m))",
        "species":species,
        "life_history_order":{
            "prediction":"gamma_R_ADPE < gamma_R_CHPE < gamma_R_GEPE and gamma_R_ADPE < 0",
            "observed_gamma_R":obs_gamma,
            "observed_ordered_score":float(obs_score),
            "upper_tail_extreme_permutations":order_extreme,
            "upper_tail_p_value":order_p,
            "null_distribution":{
                "q01":_q(null_scores,.01),
                "q05":_q(null_scores,.05),
                "median":_q(null_scores,.50),
                "q95":_q(null_scores,.95),
                "q99":_q(null_scores,.99),
            },
            "supported":order_supported,
        },
        "decision":{
            "species_specific_holm_significant":[
                sp for sp in SPECIES
                if float(species[sp]["permutation"]["holm_p_value"])<=0.05
            ],
            "life_history_order_supported":order_supported,
        },
        "interpretation_boundary":{
            "R_main_prespecified_before_primary_counts_opened":True,
            "species_order_frozen_after_AH_but_before_R_fit":True,
            "relief_is_not_direct_snow_or_wind_measurement":True,
            "loading_effect_is_response_filter_not_mean_growth_effect":True,
        },
        "shards":sorted(shards,key=lambda z:z["shard"]),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("shard","aggregate"),required=True)
    p.add_argument("--B",type=int,default=B_DEFAULT)
    p.add_argument("--seed",type=int,default=SEED_DEFAULT)
    p.add_argument("--n-shards",type=int,default=10)
    p.add_argument("--shard",type=int)
    p.add_argument("--forcing-json",type=Path)
    p.add_argument("--forcing-csv",type=Path)
    p.add_argument("--breeding-csv",type=Path)
    p.add_argument("--terrain-csv",type=Path)
    p.add_argument("--mapppdr-dir",type=Path)
    p.add_argument("--shard-glob")
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()

    if a.mode=="shard":
        if None in (
            a.shard,a.forcing_json,a.forcing_csv,
            a.breeding_csv,a.terrain_csv,a.mapppdr_dir,
        ):
            raise SystemExit("missing shard inputs")
        fr=json.loads(a.forcing_json.read_text(encoding="utf-8"))
        fu=pd.read_csv(a.forcing_csv)
        br=pd.read_csv(a.breeding_csv)
        terrain=pd.read_csv(a.terrain_csv)
        obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
        out=run_shard(
            fr,fu,br,terrain,obs,
            B=a.B,n_shards=a.n_shards,shard=a.shard,seed=a.seed,
        )
    else:
        paths=[Path(x) for x in glob.glob(a.shard_glob or "")]
        out=aggregate(paths,B=a.B,seed=a.seed)

    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
