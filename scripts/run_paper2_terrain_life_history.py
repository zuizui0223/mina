#!/usr/bin/env python3
"""Paper 2 terrain life-history extension under the frozen V3 estimator."""
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
from scripts.run_paper2_v3_permutation import holm_adjust, permutation_bounds
from scripts.simulate_paper2_integrated_recovery import (
    count_to_analysis_scale,
    simulate_species_counts,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
    fit_observation_calibration_fast,
    prepare_observation_recovery_design,
)
from scripts.simulate_paper2_spatial_adjusted_v3 import fit_spatial_species

SPECIES=("ADPE","CHPE","GEPE")
EXPECTED={"ADPE":44,"CHPE":34,"GEPE":29}
B_DEFAULT=9999
SEED_DEFAULT=20260930
RECOVERY_REPLICATES=100
TERRAIN_FIELD="elevation_relief_p90_p10_m_2000m"


def _load_rda(path:Path, expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def build_terrain_frames(
    forcing_units:pd.DataFrame,
    terrain:pd.DataFrame,
    *,
    expected:dict[str,int]|None=EXPECTED,
    terrain_field:str=TERRAIN_FIELD,
)->dict[str,pd.DataFrame]:
    required_units={"unit_id","site_id","species_id","region","ccamlr_id","seasons"}
    missing=required_units-set(forcing_units.columns)
    if missing:
        raise ValueError(f"forcing-unit columns missing: {sorted(missing)}")
    required_terrain={"site_id",terrain_field}
    missing=required_terrain-set(terrain.columns)
    if missing:
        raise ValueError(f"terrain columns missing: {sorted(missing)}")

    atlas=terrain.copy()
    atlas[terrain_field]=pd.to_numeric(atlas[terrain_field],errors="raise")
    if len(atlas.drop_duplicates("site_id"))!=122:
        raise ValueError("terrain atlas must contain exactly 122 distinct sites")
    raw=np.log1p(atlas[terrain_field].to_numpy(dtype=float))
    if np.any(~np.isfinite(raw)):
        raise ValueError("nonfinite terrain relief")
    sd=float(np.std(raw,ddof=0))
    if sd<=0:
        raise ValueError("zero terrain variance")
    atlas["T"]=(raw-float(np.mean(raw)))/sd

    frames={}
    for sp in SPECIES:
        selected=forcing_units[
            forcing_units["species_id"].astype(str).eq(sp)
        ].copy()
        frame=selected.merge(
            atlas[["site_id","T"]],
            on="site_id",how="left",validate="many_to_one",
        )
        if frame["T"].isna().any():
            bad=frame.loc[frame["T"].isna(),"site_id"].astype(str).tolist()
            raise ValueError(f"missing terrain for {sp}: {bad}")
        frame["forcing_group"]=sp
        frame["trait_block"]=(
            frame["ccamlr_id"].astype(str)
            if sp=="ADPE" else frame["region"].astype(str)
        )
        if frame["trait_block"].isin(["nan","None",""]).any():
            raise ValueError(f"missing trait block: {sp}")
        # Reuse the frozen one-predictor A slot without changing the estimator.
        frame["A"]=frame["T"].astype(float)
        frame["H"]=0.0
        frame["AH"]=0.0
        keep=[
            "unit_id","site_id","species_id","forcing_group",
            "A","H","AH","seasons","trait_block",
        ]
        frames[sp]=frame[keep].sort_values("unit_id").reset_index(drop=True)

    if expected is not None:
        got={sp:len(frames[sp]) for sp in SPECIES}
        if got!=expected:
            raise ValueError(f"terrain frame drift: {got} != {expected}")
    return frames


def _local_records(records:pd.DataFrame, frame:pd.DataFrame)->pd.DataFrame:
    ids=set(frame["unit_id"].astype(str))
    x=records.copy()
    x["unit_id"]=x["species_id"].astype(str)+"|"+x["site_id"].astype(str)
    return x[x["unit_id"].isin(ids)].copy().reset_index(drop=True)


def fit_terrain(frame, records, cal)->float:
    fit=fit_spatial_species(
        frame,records,
        delta_image=float(cal["delta_image"]),
        sigma1=float(cal["accuracy"]["1"]["sigma"]),
        sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
        truth_forcing=None,true_lambda=None,
    )
    return float(fit["gamma_a"])


def prepare_real_context(forcing_units,terrain,obs):
    frames=build_terrain_frames(forcing_units,terrain)
    records=build_frozen_real_records(obs)
    cal=calibrate_observation(records)
    local={sp:_local_records(records,frames[sp]) for sp in SPECIES}
    expected_records={"ADPE":None,"CHPE":None,"GEPE":None}
    for sp in SPECIES:
        if local[sp].empty:
            raise ValueError(f"no records for {sp}")
    return frames,local,cal


def _synthetic_fit(
    frames:dict[str,pd.DataFrame],
    metadata:pd.DataFrame,
    *,
    gamma_t:float,
    seed:int,
)->dict[str,float]:
    obs=[]
    for si,sp in enumerate(SPECIES):
        sim=simulate_species_counts(
            frames[sp],metadata,
            gamma_a=float(gamma_t),gamma_ah=0.0,
            seed=int(seed+si*100003),
            forcing_sd=0.08,loading_sd=0.15,process_sd=0.04,
            drift_mean=-0.01,drift_sd=0.01,
            delta_image=float(np.log(1.15)),
            sigma1=float(np.log(1.05)),
            sigma2plus=float(np.log(1.25)),
        )
        obs.append(sim["observations"])
    observations=pd.concat(obs,ignore_index=True)
    design=prepare_observation_recovery_design(observations)
    cal=fit_observation_calibration_fast(
        count_to_analysis_scale(observations["count"].to_numpy(dtype=float)),
        design,
    )
    out={}
    for sp in SPECIES:
        local=_local_records(observations,frames[sp])
        out[sp]=fit_terrain(frames[sp],local,cal)
    return out


def _q(values,p):
    return float(np.quantile(np.asarray(values,dtype=float),p))


def run_recovery(
    forcing_units:pd.DataFrame,
    terrain:pd.DataFrame,
    obs:pd.DataFrame,
    *,
    replicates:int=RECOVERY_REPLICATES,
    seed:int=SEED_DEFAULT,
)->dict:
    frames=build_terrain_frames(forcing_units,terrain)
    metadata=build_frozen_observation_metadata(obs)
    truths={"null":0.0,"negative_terrain":-0.30}
    raw={sp:{name:[] for name in truths} for sp in SPECIES}
    for scenario_i,(name,truth) in enumerate(truths.items()):
        for rep in range(replicates):
            fitted=_synthetic_fit(
                frames,metadata,
                gamma_t=truth,
                seed=seed+scenario_i*1000000+rep,
            )
            for sp,value in fitted.items():
                raw[sp][name].append(float(value))

    species={}
    passed={}
    for sp in SPECIES:
        null=raw[sp]["null"]
        neg=raw[sp]["negative_terrain"]
        summary={
            "null":{
                "median":float(np.median(null)),
                "q05":_q(null,.05),"q95":_q(null,.95),
            },
            "negative_terrain":{
                "truth":-0.30,
                "median":float(np.median(neg)),
                "q05":_q(neg,.05),"q95":_q(neg,.95),
                "negative_fraction":float(np.mean(np.asarray(neg)<0)),
            },
        }
        checks={
            "null_center":abs(summary["null"]["median"])<=0.08,
            "null_contains_zero":summary["null"]["q05"]<=0<=summary["null"]["q95"],
            "negative_bias":abs(summary["negative_terrain"]["median"]+0.30)<=0.12,
            "negative_sign":summary["negative_terrain"]["negative_fraction"]>=0.85,
        }
        summary["checks"]=checks
        summary["passes"]=bool(all(checks.values()))
        species[sp]=summary
        passed[sp]=summary["passes"]
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-terrain-life-history-recovery-v1",
        "replicates_per_scenario":replicates,
        "species":species,
        "gate":{"species_pass":passed,"passes":bool(all(passed.values()))},
        "real_terrain_coefficients_opened":False,
    }


def permute_terrain_within_blocks(
    frame:pd.DataFrame,
    *,
    global_index:int,
    species_index:int,
    seed:int=SEED_DEFAULT,
)->pd.DataFrame:
    out=frame.copy().reset_index(drop=True)
    rng=np.random.default_rng(
        np.random.SeedSequence([int(seed),int(global_index),int(species_index),707])
    )
    blocks=out["trait_block"].astype(str).to_numpy()
    for block in sorted(set(blocks.tolist())):
        idx=np.flatnonzero(blocks==block)
        if len(idx)<=1:
            continue
        src=idx[rng.permutation(len(idx))]
        out.loc[idx,"A"]=out.loc[src,"A"].to_numpy(dtype=float)
    return out


def observed_point(frames,local,cal):
    return {sp:fit_terrain(frames[sp],local[sp],cal) for sp in SPECIES}


def run_shard(
    forcing_units,terrain,obs,
    *,B,n_shards,shard,seed,
):
    frames,local,cal=prepare_real_context(forcing_units,terrain,obs)
    observed=observed_point(frames,local,cal)
    start,stop=permutation_bounds(B,n_shards,shard)
    rows=[]
    for k in range(start,stop):
        gamma={}
        for si,sp in enumerate(SPECIES):
            pf=permute_terrain_within_blocks(
                frames[sp],global_index=k,species_index=si,seed=seed
            )
            gamma[sp]=fit_terrain(pf,local[sp],cal)
        rows.append({
            "index":int(k),
            "gamma_T":gamma,
            "delta_ADPE_GEPE":float(gamma["ADPE"]-gamma["GEPE"]),
        })
    return {
        "schema_version":1,"B":B,"seed":seed,
        "n_shards":n_shards,"shard":shard,
        "start":start,"stop":stop,
        "observed_gamma_T":observed,
        "observed_delta_ADPE_GEPE":float(observed["ADPE"]-observed["GEPE"]),
        "permutations":rows,
    }


def aggregate(paths:list[Path],*,B:int,seed:int)->dict:
    rows=[];observed=None;delta_obs=None;shards=[]
    for path in sorted(paths):
        x=json.loads(path.read_text())
        if int(x["B"])!=B or int(x["seed"])!=seed:
            raise ValueError(f"contract drift: {path}")
        if observed is None:
            observed={sp:float(x["observed_gamma_T"][sp]) for sp in SPECIES}
            delta_obs=float(x["observed_delta_ADPE_GEPE"])
        else:
            for sp in SPECIES:
                if not np.isclose(
                    observed[sp],float(x["observed_gamma_T"][sp]),
                    rtol=1e-10,atol=1e-10,
                ):
                    raise ValueError(f"observed drift {sp}")
            if not np.isclose(
                delta_obs,float(x["observed_delta_ADPE_GEPE"]),
                rtol=1e-10,atol=1e-10,
            ):
                raise ValueError("delta drift")
        rows.extend(x["permutations"])
        shards.append({
            "shard":int(x["shard"]),"start":int(x["start"]),"stop":int(x["stop"])
        })
    indices=sorted(int(r["index"]) for r in rows)
    if len(rows)!=B or indices!=list(range(B)):
        raise ValueError("invalid permutation coverage")

    delta=[float(r["delta_ADPE_GEPE"]) for r in rows]
    primary_extreme=sum(value<=delta_obs for value in delta)
    primary_p=(1+primary_extreme)/(B+1)

    raw={};species={}
    for sp in SPECIES:
        vals=[float(r["gamma_T"][sp]) for r in rows]
        obs=float(observed[sp])
        extreme=sum(value<=obs for value in vals)
        p=(1+extreme)/(B+1)
        raw[sp]=p
        species[sp]={
            "gamma_T":obs,
            "raw_one_sided_p":p,
            "null":{
                "q01":_q(vals,.01),"q05":_q(vals,.05),
                "median":_q(vals,.5),"q95":_q(vals,.95),"q99":_q(vals,.99),
            },
        }
    holm=holm_adjust(raw)
    for sp in SPECIES:
        species[sp]["holm_p"]=float(holm[sp])

    ordered=bool(
        observed["ADPE"]<observed["CHPE"]<observed["GEPE"]
    )
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-terrain-life-history-v1",
        "B":B,"seed":seed,
        "species":species,
        "primary":{
            "statistic":"gamma_T_ADPE - gamma_T_GEPE",
            "observed":float(delta_obs),
            "alternative":"< 0",
            "extreme_permutations":int(primary_extreme),
            "one_sided_p":float(primary_p),
            "null":{
                "q01":_q(delta,.01),"q05":_q(delta,.05),
                "median":_q(delta,.5),"q95":_q(delta,.95),"q99":_q(delta,.99),
            },
            "supported":bool(delta_obs<0 and primary_p<=0.05),
        },
        "descriptive_order":{
            "ADPE_lt_CHPE_lt_GEPE":ordered,
            "ordered_values":[
                ["ADPE",float(observed["ADPE"])],
                ["CHPE",float(observed["CHPE"])],
                ["GEPE",float(observed["GEPE"])],
            ],
        },
        "decision":{
            "primary_life_history_contrast_supported":bool(
                delta_obs<0 and primary_p<=0.05
            ),
            "adelie_negative_terrain_holm_supported":bool(
                observed["ADPE"]<0 and species["ADPE"]["holm_p"]<=0.05
            ),
            "mechanistic_snow_claim_allowed":False,
        },
        "interpretation_boundary":{
            "terrain_is_not_snow":True,
            "terrain_is_not_occupied_nest_microhabitat":True,
            "other_paper2_outcomes_were_already_known":True,
        },
        "shards":sorted(shards,key=lambda z:z["shard"]),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("recovery","shard","aggregate"),required=True)
    p.add_argument("--forcing-csv",type=Path)
    p.add_argument("--terrain-csv",type=Path)
    p.add_argument("--mapppdr-dir",type=Path)
    p.add_argument("--recovery-json",type=Path)
    p.add_argument("--B",type=int,default=B_DEFAULT)
    p.add_argument("--seed",type=int,default=SEED_DEFAULT)
    p.add_argument("--replicates",type=int,default=RECOVERY_REPLICATES)
    p.add_argument("--n-shards",type=int,default=10)
    p.add_argument("--shard",type=int)
    p.add_argument("--shard-glob")
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()

    if a.mode=="aggregate":
        paths=[Path(x) for x in glob.glob(a.shard_glob or "")]
        out=aggregate(paths,B=a.B,seed=a.seed)
    else:
        if a.forcing_csv is None or a.terrain_csv is None or a.mapppdr_dir is None:
            raise SystemExit("missing input files")
        fu=pd.read_csv(a.forcing_csv)
        terrain=pd.read_csv(a.terrain_csv)
        obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
        if a.mode=="recovery":
            out=run_recovery(
                fu,terrain,obs,replicates=a.replicates,seed=a.seed
            )
        else:
            if a.shard is None:
                raise SystemExit("missing shard")
            if a.recovery_json is None:
                raise SystemExit("recovery receipt required")
            gate=json.loads(a.recovery_json.read_text())
            if not bool(gate.get("gate",{}).get("passes",False)):
                raise SystemExit("terrain recovery gate did not pass")
            out=run_shard(
                fu,terrain,obs,B=a.B,n_shards=a.n_shards,
                shard=a.shard,seed=a.seed,
            )

    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    if a.mode=="recovery" and not out["gate"]["passes"]:
        raise SystemExit("terrain-specific recovery failed")


if __name__=="__main__":
    main()
