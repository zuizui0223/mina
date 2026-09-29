#!/usr/bin/env python3
"""Block-preserving null for the observed 1/2/5 km interaction reversal."""
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
from scripts.run_paper2_v3_permutation import permutation_bounds
from scripts.simulate_paper2_spatial_adjusted_v3 import (
    build_v3_frames,
    fit_spatial_species,
)

SPECIES=("ADPE","CHPE","GEPE")
RADII=(1000,2000,5000)
B_DEFAULT=9999
SEED_DEFAULT=20260929

OBSERVED={
    1000:-0.0576551287747558,
    2000:-0.31822603579776854,
    5000:0.1067807758917031,
}
OBS_CONTRAST=OBSERVED[5000]-OBSERVED[2000]
OBS_RANGE=max(OBSERVED.values())-min(OBSERVED.values())


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def zscore(x:pd.Series)->pd.Series:
    v=pd.to_numeric(x,errors="coerce")
    sd=float(v.std(ddof=0))
    if not np.isfinite(sd) or sd<=0:
        raise ValueError(f"zero/nonfinite SD for {x.name}")
    return (v-float(v.mean()))/sd


def build_multiradius_frames(forcing_result,forcing_units,breeding):
    base=build_v3_frames(forcing_result,forcing_units,breeding)
    cols=["site_id"]
    for r in RADII:
        cols += [
            f"mapped_ice_free_area_ha_{r}m",
            f"tier2_richness_{r}m",
        ]
    site=breeding[cols].copy()
    out={}
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    for sp in SPECIES:
        f=base[sp].copy()
        f=f.merge(site,on="site_id",how="left",validate="many_to_one")
        for r in RADII:
            a=f"A_{r}"
            h=f"H_{r}"
            ah=f"AH_{r}"
            raw_a=np.log1p(
                pd.to_numeric(
                    f[f"mapped_ice_free_area_ha_{r}m"],
                    errors="coerce",
                )
            )
            raw_h=pd.to_numeric(
                f[f"tier2_richness_{r}m"],
                errors="coerce",
            )
            if raw_a.isna().any() or raw_h.isna().any():
                bad=f.loc[
                    raw_a.isna()|raw_h.isna(),"unit_id"
                ].astype(str).tolist()
                raise ValueError(f"{sp} {r}m missing rows: {bad}")
            f[a]=zscore(raw_a)
            f[h]=zscore(raw_h)
            f[ah]=f[a]*f[h]
        out[sp]=f.reset_index(drop=True)
    got={sp:len(out[sp]) for sp in SPECIES}
    if got!=expected:
        raise ValueError(f"multiradius frame drift {got} != {expected}")
    return out


def radius_frame(multiframe:pd.DataFrame,radius:int)->pd.DataFrame:
    out=multiframe.copy()
    out["A"]=out[f"A_{radius}"].astype(float)
    out["H"]=out[f"H_{radius}"].astype(float)
    out["AH"]=out[f"AH_{radius}"].astype(float)
    return out


def permute_multiradius_within_blocks(
    multiframe:pd.DataFrame,
    *,
    global_index:int,
    species_index:int,
    seed:int=SEED_DEFAULT,
)->pd.DataFrame:
    out=multiframe.copy().reset_index(drop=True)
    blocks=out["trait_block"].astype(str).to_numpy()
    trait_cols=[
        col for r in RADII
        for col in (f"A_{r}",f"H_{r}",f"AH_{r}")
    ]
    rng=np.random.default_rng(
        np.random.SeedSequence(
            [int(seed),int(global_index),int(species_index),202]
        )
    )
    for block in sorted(set(blocks.tolist())):
        idx=np.flatnonzero(blocks==block)
        if len(idx)<=1:
            continue
        src=idx[rng.permutation(len(idx))]
        out.loc[idx,trait_cols]=out.loc[src,trait_cols].to_numpy(dtype=float)
    return out


def _local_records(records:pd.DataFrame,frame:pd.DataFrame)->pd.DataFrame:
    ids=set(frame["unit_id"].astype(str))
    x=records.copy()
    x["unit_id"]=x["species_id"].astype(str)+"|"+x["site_id"].astype(str)
    return x[x["unit_id"].isin(ids)].copy().reset_index(drop=True)


def prepare_context(fr,fu,br,obs):
    frames=build_multiradius_frames(fr,fu,br)
    records=build_frozen_real_records(obs)
    cal=calibrate_observation(records)
    local={sp:_local_records(records,frames[sp]) for sp in SPECIES}
    return frames,local,cal


def fit_permutation(
    frames,
    local,
    cal,
    *,
    global_index:int,
    seed:int,
)->dict:
    species={}
    medians={}
    for si,sp in enumerate(SPECIES):
        perm=permute_multiradius_within_blocks(
            frames[sp],
            global_index=global_index,
            species_index=si,
            seed=seed,
        )
        species[sp]={}
        for r in RADII:
            fit=fit_spatial_species(
                radius_frame(perm,r),
                local[sp],
                delta_image=float(cal["delta_image"]),
                sigma1=float(cal["accuracy"]["1"]["sigma"]),
                sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
                truth_forcing=None,
                true_lambda=None,
            )
            species[sp][str(r)]=float(fit["gamma_ah"])
    for r in RADII:
        vals=np.asarray(
            [species[sp][str(r)] for sp in SPECIES],
            dtype=float,
        )
        medians[str(r)]=float(np.median(vals))
    return {
        "index":int(global_index),
        "median_gamma_ah":medians,
    }


def run_shard(fr,fu,br,obs,*,B,n_shards,shard,seed):
    frames,local,cal=prepare_context(fr,fu,br,obs)
    start,stop=permutation_bounds(B,n_shards,shard)
    rows=[
        fit_permutation(
            frames,local,cal,
            global_index=k,
            seed=seed,
        )
        for k in range(start,stop)
    ]
    return {
        "schema_version":1,
        "B":int(B),
        "seed":int(seed),
        "n_shards":int(n_shards),
        "shard":int(shard),
        "start":int(start),
        "stop":int(stop),
        "permutations":rows,
    }


def mc_p(count:int,B:int)->float:
    return float((1+int(count))/(B+1))


def aggregate(paths:list[Path],*,B:int,seed:int)->dict:
    rows=[]
    shard_meta=[]
    for path in sorted(paths):
        x=json.loads(path.read_text(encoding="utf-8"))
        if int(x["B"])!=B or int(x["seed"])!=seed:
            raise ValueError(f"shard contract drift {path}")
        rows.extend(x["permutations"])
        shard_meta.append({
            "shard":int(x["shard"]),
            "start":int(x["start"]),
            "stop":int(x["stop"]),
        })
    indices=sorted(int(r["index"]) for r in rows)
    if len(rows)!=B or indices!=list(range(B)):
        raise ValueError(
            f"permutation coverage invalid n={len(rows)} unique={len(set(indices))}"
        )

    metrics={
        "directional_sign_switch_2_to_5":0,
        "contrast_5_minus_2_ge_observed":0,
        "joint_switch_and_contrast":0,
        "range_ge_observed":0,
        "ordered_2_lt_1_lt_5_and_range":0,
    }
    contrast=[]
    ranges=[]
    for row in rows:
        m1=float(row["median_gamma_ah"]["1000"])
        m2=float(row["median_gamma_ah"]["2000"])
        m5=float(row["median_gamma_ah"]["5000"])
        con=m5-m2
        ran=max(m1,m2,m5)-min(m1,m2,m5)
        switch=(m2<0 and m5>0)
        metrics["directional_sign_switch_2_to_5"]+=int(switch)
        metrics["contrast_5_minus_2_ge_observed"]+=int(con>=OBS_CONTRAST)
        metrics["joint_switch_and_contrast"]+=int(
            switch and con>=OBS_CONTRAST
        )
        metrics["range_ge_observed"]+=int(ran>=OBS_RANGE)
        metrics["ordered_2_lt_1_lt_5_and_range"]+=int(
            m2<m1<m5 and ran>=OBS_RANGE
        )
        contrast.append(con)
        ranges.append(ran)

    probabilities={
        key:{
            "count":int(value),
            "mc_probability":float(value/B),
            "plus1_probability":mc_p(value,B),
        }
        for key,value in metrics.items()
    }
    primary_diag=probabilities["joint_switch_and_contrast"]["plus1_probability"]
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-radius-sign-switch-null-v1",
        "B":int(B),
        "seed":int(seed),
        "observed":{
            "median_gamma_ah":{
                "1000":OBSERVED[1000],
                "2000":OBSERVED[2000],
                "5000":OBSERVED[5000],
            },
            "contrast_5000_minus_2000":OBS_CONTRAST,
            "range":OBS_RANGE,
        },
        "null_probabilities":probabilities,
        "null_distributions":{
            "contrast_5000_minus_2000":{
                "q05":float(np.quantile(contrast,0.05)),
                "median":float(np.quantile(contrast,0.50)),
                "q95":float(np.quantile(contrast,0.95)),
            },
            "range":{
                "q05":float(np.quantile(ranges,0.05)),
                "median":float(np.quantile(ranges,0.50)),
                "q95":float(np.quantile(ranges,0.95)),
            },
        },
        "decision":{
            "joint_switch_plus_contrast_probability":primary_diag,
            "ecological_scale_dependence_language_allowed":bool(
                primary_diag<=0.05
            ),
            "diagnostic_not_primary_inference":True,
        },
        "shards":sorted(shard_meta,key=lambda x:x["shard"]),
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("shard","aggregate"),required=True)
    p.add_argument("--B",type=int,default=B_DEFAULT)
    p.add_argument("--seed",type=int,default=SEED_DEFAULT)
    p.add_argument("--n-shards",type=int,default=20)
    p.add_argument("--shard",type=int)
    p.add_argument("--forcing-json",type=Path)
    p.add_argument("--forcing-csv",type=Path)
    p.add_argument("--breeding-csv",type=Path)
    p.add_argument("--mapppdr-dir",type=Path)
    p.add_argument("--shard-glob")
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()

    if a.mode=="shard":
        if None in (
            a.shard,a.forcing_json,a.forcing_csv,
            a.breeding_csv,a.mapppdr_dir
        ):
            raise SystemExit("missing shard inputs")
        fr=json.loads(a.forcing_json.read_text(encoding="utf-8"))
        fu=pd.read_csv(a.forcing_csv)
        br=pd.read_csv(a.breeding_csv)
        obs=_load_rda(
            a.mapppdr_dir/"data"/"penguin_obs.rda",
            "penguin_obs",
        )
        out=run_shard(
            fr,fu,br,obs,
            B=a.B,
            n_shards=a.n_shards,
            shard=a.shard,
            seed=a.seed,
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
    return 0


if __name__=="__main__":
    raise SystemExit(main())
