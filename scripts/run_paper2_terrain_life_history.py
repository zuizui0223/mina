#!/usr/bin/env python3
"""Paper 2 terrain × life-history extension with a dedicated one-predictor solver."""
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
    collapse_same_season,
    count_to_analysis_scale,
    simulate_species_counts,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
    fit_observation_calibration_fast,
    prepare_observation_recovery_design,
)
from scripts.simulate_paper2_integrated_hierarchical_recovery import (
    _build_observed_intervals,
    _solve_forcing_interval,
    _profile_interval_process_sd,
    _forcing_sum,
    _interval_variance,
    _solve_constrained_system,
)

SPECIES=("ADPE","CHPE","GEPE")
EXPECTED={"ADPE":44,"CHPE":34,"GEPE":29}
B_DEFAULT=9999
SEED_DEFAULT=20260930
RECOVERY_REPLICATES=100
PRIMARY_FIELD="elevation_relief_p90_p10_m_2000m"
SENSITIVITY_FIELDS={
    "relief_1km":"elevation_relief_p90_p10_m_1000m",
    "relief_5km":"elevation_relief_p90_p10_m_5000m",
    "elevation_sd_2km":"elevation_sd_m_2000m",
}


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def _global_standardized_trait(terrain:pd.DataFrame, field:str)->pd.DataFrame:
    required={"site_id",field}
    missing=required-set(terrain.columns)
    if missing:
        raise ValueError(f"terrain columns missing: {sorted(missing)}")
    atlas=terrain[["site_id",field]].drop_duplicates("site_id").copy()
    if len(atlas)!=122:
        raise ValueError(f"terrain atlas drift: {len(atlas)} != 122 sites")
    values=pd.to_numeric(atlas[field],errors="raise").to_numpy(dtype=float)
    if np.any(~np.isfinite(values)) or np.any(values<0):
        raise ValueError(f"invalid terrain values for {field}")
    raw=np.log1p(values)
    sd=float(np.std(raw,ddof=0))
    if sd<=0:
        raise ValueError(f"zero trait variance for {field}")
    atlas["T"]=(raw-float(np.mean(raw)))/sd
    return atlas[["site_id","T"]]


def build_terrain_frames(
    forcing_units:pd.DataFrame,
    terrain:pd.DataFrame,
    *,
    expected:dict[str,int]|None=EXPECTED,
    terrain_field:str=PRIMARY_FIELD,
)->dict[str,pd.DataFrame]:
    required={"unit_id","site_id","species_id","region","ccamlr_id","seasons"}
    missing=required-set(forcing_units.columns)
    if missing:
        raise ValueError(f"forcing-unit columns missing: {sorted(missing)}")
    trait=_global_standardized_trait(terrain,terrain_field)
    frames={}
    for sp in SPECIES:
        selected=forcing_units[
            forcing_units["species_id"].astype(str).eq(sp)
        ].copy()
        frame=selected.merge(
            trait,on="site_id",how="left",validate="many_to_one"
        )
        if frame["T"].isna().any():
            bad=frame.loc[frame["T"].isna(),"site_id"].astype(str).tolist()
            raise ValueError(f"missing terrain for {sp}: {bad}")
        frame["forcing_group"]=sp
        frame["trait_block"]=(
            frame["ccamlr_id"].astype(str)
            if sp=="ADPE"
            else frame["region"].astype(str)
        )
        if frame["trait_block"].isin(["nan","None",""]).any():
            raise ValueError(f"missing trait block in {sp}")
        keep=[
            "unit_id","site_id","species_id","forcing_group",
            "seasons","trait_block","T",
        ]
        frames[sp]=frame[keep].sort_values("unit_id").reset_index(drop=True)
    if expected is not None:
        got={sp:int(len(frames[sp])) for sp in SPECIES}
        if got!=expected:
            raise ValueError(f"terrain frame drift: {got} != {expected}")
    return frames


def center_terrain_within_block(frame:pd.DataFrame)->pd.DataFrame:
    out=frame.copy().reset_index(drop=True)
    out["Tc"]=(
        pd.to_numeric(out["T"],errors="raise")
        - out.groupby("trait_block")["T"].transform("mean")
    )
    return out


def _solve_site_gamma_terrain(
    intervals:list[dict],
    frame:pd.DataFrame,
    forcing:dict[str,np.ndarray],
    process_sd:float,
    loading_sd:float,
    min_loading_sd:float=0.05,
):
    """V3 loading solve with exactly one terrain coefficient."""
    n=len(frame)
    x=frame["Tc"].to_numpy(dtype=float)
    blocks=frame["trait_block"].astype(str).to_numpy()
    levels=sorted(set(blocks.tolist()))
    B=len(levels)
    bindex={b:j for j,b in enumerate(levels)}
    sig=max(float(loading_sd),1e-8)

    # columns: site drift mu[n], gamma_T[1], block alpha[B], residual loading[n]
    cols=n+1+B+n
    A=np.zeros((len(intervals)+n,cols),dtype=float)
    y=np.zeros(len(intervals)+n,dtype=float)
    row=0
    for it in intervals:
        i=int(it["site"])
        fsum=_forcing_sum(forcing,it)
        w=1.0/np.sqrt(max(_interval_variance(it,process_sd),1e-12))
        A[row,i]=float(it["duration"])*w
        A[row,n]=fsum*x[i]*w
        A[row,n+1+bindex[str(blocks[i])]]=fsum*w
        A[row,n+1+B+i]=fsum*w
        y[row]=(float(it["delta"])-fsum)*w
        row+=1
    for i in range(n):
        A[row,n+1+B+i]=1.0/sig
        row+=1

    # Same V3 identification: residual loading has block mean 0;
    # site-count-weighted block intercept mean is 0.
    C=np.zeros((B+1,cols),dtype=float)
    for bi,b in enumerate(levels):
        idx=np.flatnonzero(blocks==b)
        C[bi,n+1+B+idx]=1.0/len(idx)
    for b in levels:
        idx=np.flatnonzero(blocks==b)
        C[B,n+1+bindex[b]]=len(idx)/n

    sol=_solve_constrained_system(A,y,C)
    mu=sol[:n]
    gamma=float(sol[n])
    alpha=sol[n+1:n+1+B]
    resid=sol[n+1+B:]
    lam=(
        1.0
        + gamma*x
        + np.asarray([alpha[bindex[str(b)]] for b in blocks])
        + resid
    )
    loading_sd_new=max(
        float(np.sqrt(np.mean(resid*resid))),
        float(min_loading_sd),
    )
    return mu,lam,gamma,alpha,resid,loading_sd_new


def fit_terrain_species(
    frame:pd.DataFrame,
    observations:pd.DataFrame,
    *,
    delta_image:float,
    sigma1:float,
    sigma2plus:float,
    truth_forcing:dict|None=None,
    true_lambda:list[float]|None=None,
    iterations:int=12,
)->dict:
    f=center_terrain_within_block(frame)
    collapsed=collapse_same_season(
        observations,
        delta_image=delta_image,
        sigma1=sigma1,
        sigma2plus=sigma2plus,
    )
    intervals=_build_observed_intervals(f,collapsed)
    n=len(f)
    lam=np.ones(n,dtype=float)
    process_sd=0.10
    loading_sd=0.30
    mu,forcing=_solve_forcing_interval(intervals,f,lam,process_sd)
    alpha=np.zeros(f["trait_block"].nunique(),dtype=float)
    resid=np.zeros(n,dtype=float)
    gamma=0.0
    for _ in range(iterations):
        mu,forcing=_solve_forcing_interval(intervals,f,lam,process_sd)
        mu,lam,gamma,alpha,resid,loading_sd=_solve_site_gamma_terrain(
            intervals,f,forcing,process_sd,loading_sd
        )
        process_sd=_profile_interval_process_sd(intervals,mu,lam,forcing)
    mu,forcing=_solve_forcing_interval(intervals,f,lam,process_sd)
    mu,lam,gamma,alpha,resid,loading_sd=_solve_site_gamma_terrain(
        intervals,f,forcing,process_sd,loading_sd
    )

    forcing_corr={}
    if truth_forcing is not None:
        for group,value in forcing.items():
            forcing_corr[group]=float(
                np.corrcoef(
                    np.asarray(truth_forcing[group],dtype=float),
                    np.asarray(value,dtype=float),
                )[0,1]
            )
    lambda_corr=None
    if true_lambda is not None:
        lambda_corr=float(
            np.corrcoef(
                np.asarray(true_lambda,dtype=float),
                np.asarray(lam,dtype=float),
            )[0,1]
        )
    return {
        "gamma_T":float(gamma),
        "process_sd":float(process_sd),
        "loading_residual_sd":float(loading_sd),
        "forcing_correlation":forcing_corr,
        "lambda_correlation":lambda_corr,
        "block_intercepts":{
            b:float(alpha[i]) for i,b in enumerate(
                sorted(f["trait_block"].astype(str).unique())
            )
        },
    }


def _local_records(records:pd.DataFrame,frame:pd.DataFrame)->pd.DataFrame:
    ids=set(frame["unit_id"].astype(str))
    x=records.copy()
    x["unit_id"]=x["species_id"].astype(str)+"|"+x["site_id"].astype(str)
    return x[x["unit_id"].isin(ids)].copy().reset_index(drop=True)


def _fit_with_calibration(frame,records,cal,truth=None)->dict:
    truth=truth or {}
    return fit_terrain_species(
        frame,records,
        delta_image=float(cal["delta_image"]),
        sigma1=float(cal["accuracy"]["1"]["sigma"]),
        sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
        truth_forcing=truth.get("true_forcing"),
        true_lambda=truth.get("true_lambda"),
    )


def _simulation_frame(frame:pd.DataFrame)->pd.DataFrame:
    """Give the frozen simulator the exact within-block terrain truth in A slot."""
    out=center_terrain_within_block(frame)
    out["A"]=out["Tc"].astype(float)
    out["H"]=0.0
    out["AH"]=0.0
    return out


def _synthetic_dataset(
    frames:dict[str,pd.DataFrame],
    metadata:pd.DataFrame,
    *,
    gamma_t:float,
    seed:int,
):
    pieces=[]
    truth={}
    for si,sp in enumerate(SPECIES):
        sim=simulate_species_counts(
            _simulation_frame(frames[sp]),
            metadata,
            gamma_a=float(gamma_t),
            gamma_ah=0.0,
            seed=int(seed+si*100003),
            forcing_sd=0.08,
            loading_sd=0.15,
            process_sd=0.04,
            drift_mean=-0.01,
            drift_sd=0.01,
            delta_image=float(np.log(1.15)),
            sigma1=float(np.log(1.05)),
            sigma2plus=float(np.log(1.25)),
        )
        pieces.append(sim["observations"])
        truth[sp]={
            "true_forcing":sim["true_forcing"],
            "true_lambda":sim["true_lambda"],
        }
    observations=pd.concat(pieces,ignore_index=True)
    return observations,truth


def _calibrate_synthetic(observations:pd.DataFrame)->dict:
    design=prepare_observation_recovery_design(observations)
    return fit_observation_calibration_fast(
        count_to_analysis_scale(observations["count"].to_numpy(dtype=float)),
        design,
    )


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
    if replicates<10:
        raise ValueError("recovery requires at least 10 replicates")
    frames=build_terrain_frames(forcing_units,terrain)
    metadata=build_frozen_observation_metadata(obs)
    truths={"null":0.0,"negative_terrain":-0.30}
    raw={sp:{name:[] for name in truths} for sp in SPECIES}
    corr={sp:{name:[] for name in truths} for sp in SPECIES}
    for scenario_i,(name,truth_value) in enumerate(truths.items()):
        for rep in range(replicates):
            observations,truth=_synthetic_dataset(
                frames,metadata,
                gamma_t=truth_value,
                seed=seed+scenario_i*1000000+rep,
            )
            cal=_calibrate_synthetic(observations)
            for sp in SPECIES:
                local=_local_records(observations,frames[sp])
                fit=_fit_with_calibration(
                    frames[sp],local,cal,truth[sp]
                )
                raw[sp][name].append(float(fit["gamma_T"]))
                if fit["lambda_correlation"] is not None:
                    corr[sp][name].append(float(fit["lambda_correlation"]))

    species={}
    passes={}
    for sp in SPECIES:
        null=raw[sp]["null"]
        neg=raw[sp]["negative_terrain"]
        summary={
            "null":{
                "median":float(np.median(null)),
                "q05":_q(null,.05),
                "q95":_q(null,.95),
            },
            "negative_terrain":{
                "truth":-0.30,
                "median":float(np.median(neg)),
                "q05":_q(neg,.05),
                "q95":_q(neg,.95),
                "negative_fraction":float(np.mean(np.asarray(neg)<0)),
            },
            "median_lambda_correlation":{
                name:(float(np.median(vals)) if vals else None)
                for name,vals in corr[sp].items()
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
        passes[sp]=summary["passes"]
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-terrain-life-history-recovery-v1",
        "contract_id":"mina-paper2-terrain-life-history-v1",
        "replicates_per_scenario":int(replicates),
        "frame_units":{sp:int(len(frames[sp])) for sp in SPECIES},
        "species":species,
        "gate":{"species_pass":passes,"passes":bool(all(passes.values()))},
        "real_terrain_coefficients_opened":False,
    }


def prepare_real_context(forcing_units,terrain,obs,*,terrain_field=PRIMARY_FIELD):
    frames=build_terrain_frames(
        forcing_units,terrain,terrain_field=terrain_field
    )
    records=build_frozen_real_records(obs)
    if len(records)!=2100:
        raise ValueError(f"record drift: {len(records)} != 2100")
    cal=calibrate_observation(records)
    local={sp:_local_records(records,frames[sp]) for sp in SPECIES}
    return frames,local,cal


def observed_point(frames,local,cal):
    return {
        sp:float(
            _fit_with_calibration(frames[sp],local[sp],cal)["gamma_T"]
        )
        for sp in SPECIES
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
        out.loc[idx,"T"]=out.loc[src,"T"].to_numpy(dtype=float)
    return out


def _sensitivity_point_estimates(forcing_units,terrain,obs):
    out={}
    for label,field in SENSITIVITY_FIELDS.items():
        frames,local,cal=prepare_real_context(
            forcing_units,terrain,obs,terrain_field=field
        )
        out[label]={
            "terrain_field":field,
            "gamma_T":observed_point(frames,local,cal),
            "inferential_role":"prespecified sensitivity; no new p-value",
        }
    return out


def run_shard(
    forcing_units,
    terrain,
    obs,
    *,
    B,
    n_shards,
    shard,
    seed,
):
    frames,local,cal=prepare_real_context(forcing_units,terrain,obs)
    observed=observed_point(frames,local,cal)
    sensitivities=_sensitivity_point_estimates(forcing_units,terrain,obs)
    start,stop=permutation_bounds(B,n_shards,shard)
    rows=[]
    for k in range(start,stop):
        gamma={}
        for si,sp in enumerate(SPECIES):
            perm=permute_terrain_within_blocks(
                frames[sp],
                global_index=k,
                species_index=si,
                seed=seed,
            )
            gamma[sp]=float(
                _fit_with_calibration(perm,local[sp],cal)["gamma_T"]
            )
        rows.append({
            "index":int(k),
            "gamma_T":gamma,
            "delta_ADPE_GEPE":float(gamma["ADPE"]-gamma["GEPE"]),
        })
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-terrain-life-history-permutation-shard-v1",
        "B":int(B),
        "seed":int(seed),
        "n_shards":int(n_shards),
        "shard":int(shard),
        "start":int(start),
        "stop":int(stop),
        "observed_gamma_T":observed,
        "observed_delta_ADPE_GEPE":float(
            observed["ADPE"]-observed["GEPE"]
        ),
        "sensitivity_point_estimates":sensitivities,
        "permutations":rows,
    }


def aggregate(paths:list[Path],*,B:int,seed:int)->dict:
    rows=[]
    observed=None
    delta_obs=None
    sensitivities=None
    shards=[]
    for path in sorted(paths):
        x=json.loads(path.read_text(encoding="utf-8"))
        if int(x["B"])!=B or int(x["seed"])!=seed:
            raise ValueError(f"contract drift: {path}")
        current={sp:float(x["observed_gamma_T"][sp]) for sp in SPECIES}
        current_delta=float(x["observed_delta_ADPE_GEPE"])
        if observed is None:
            observed=current
            delta_obs=current_delta
            sensitivities=x.get("sensitivity_point_estimates")
        else:
            for sp in SPECIES:
                if not np.isclose(
                    observed[sp],current[sp],rtol=1e-10,atol=1e-10
                ):
                    raise ValueError(f"observed coefficient drift: {sp}")
            if not np.isclose(
                delta_obs,current_delta,rtol=1e-10,atol=1e-10
            ):
                raise ValueError("observed contrast drift")
        rows.extend(x["permutations"])
        shards.append({
            "shard":int(x["shard"]),
            "start":int(x["start"]),
            "stop":int(x["stop"]),
        })

    indices=sorted(int(r["index"]) for r in rows)
    if len(rows)!=B or indices!=list(range(B)):
        raise ValueError(
            f"invalid permutation coverage n={len(rows)} unique={len(set(indices))}"
        )

    delta=[float(r["delta_ADPE_GEPE"]) for r in rows]
    primary_extreme=sum(v<=float(delta_obs) for v in delta)
    primary_p=(1+primary_extreme)/(B+1)

    raw={}
    species={}
    for sp in SPECIES:
        vals=[float(r["gamma_T"][sp]) for r in rows]
        obs=float(observed[sp])
        extreme=sum(v<=obs for v in vals)
        p=(1+extreme)/(B+1)
        raw[sp]=p
        species[sp]={
            "gamma_T":obs,
            "raw_one_sided_p":float(p),
            "permutation_distribution":{
                "q01":_q(vals,.01),
                "q05":_q(vals,.05),
                "median":_q(vals,.50),
                "q95":_q(vals,.95),
                "q99":_q(vals,.99),
            },
        }
    holm=holm_adjust(raw)
    for sp in SPECIES:
        species[sp]["holm_p"]=float(holm[sp])

    chinstrap_between=bool(
        min(observed["ADPE"],observed["GEPE"])
        <= observed["CHPE"]
        <= max(observed["ADPE"],observed["GEPE"])
    )
    primary_supported=bool(float(delta_obs)<0 and primary_p<=0.05)
    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-terrain-life-history-v1",
        "contract_id":"mina-paper2-terrain-life-history-v1",
        "B":int(B),
        "seed":int(seed),
        "species":species,
        "primary":{
            "statistic":"gamma_T_ADPE - gamma_T_GEPE",
            "alternative":"more negative",
            "observed":float(delta_obs),
            "extreme_permutations":int(primary_extreme),
            "p_value":float(primary_p),
            "permutation_distribution":{
                "q01":_q(delta,.01),
                "q05":_q(delta,.05),
                "median":_q(delta,.50),
                "q95":_q(delta,.95),
                "q99":_q(delta,.99),
            },
        },
        "descriptive_order":{
            "prediction":"ADPE more negative than GEPE; CHPE intermediate is secondary",
            "chinstrap_between_endpoints":chinstrap_between,
            "strict_ADPE_CHPE_GEPE_order":bool(
                observed["ADPE"]<observed["CHPE"]<observed["GEPE"]
            ),
        },
        "sensitivities":sensitivities,
        "decision":{
            "primary_life_history_contrast_supported":primary_supported,
            "adelie_terrain_association_holm_supported":bool(
                observed["ADPE"]<0 and holm["ADPE"]<=0.05
            ),
            "chinstrap_terrain_association_holm_supported":bool(
                observed["CHPE"]<0 and holm["CHPE"]<=0.05
            ),
            "gentoo_terrain_association_holm_supported":bool(
                observed["GEPE"]<0 and holm["GEPE"]<=0.05
            ),
            "mechanistic_snow_claim_allowed":False,
        },
        "shards":sorted(shards,key=lambda z:z["shard"]),
        "interpretation_boundary":{
            "relief_is_not_snow_depth_or_wind_exposure":True,
            "static_association_is_not_causal_resilience":True,
            "species_geography_adjusted_with_frozen_blocks":True,
            "sensitivities_do_not_replace_primary":True,
        },
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("recovery","shard","aggregate"),required=True)
    p.add_argument("--forcing-csv",type=Path)
    p.add_argument("--terrain-csv",type=Path)
    p.add_argument("--mapppdr-dir",type=Path)
    p.add_argument("--recovery-json",type=Path)
    p.add_argument("--replicates",type=int,default=RECOVERY_REPLICATES)
    p.add_argument("--B",type=int,default=B_DEFAULT)
    p.add_argument("--seed",type=int,default=SEED_DEFAULT)
    p.add_argument("--n-shards",type=int,default=10)
    p.add_argument("--shard",type=int)
    p.add_argument("--shard-glob")
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()

    if a.mode=="aggregate":
        if not a.shard_glob:
            raise SystemExit("aggregate mode requires --shard-glob")
        out=aggregate(
            [Path(x) for x in glob.glob(a.shard_glob)],
            B=a.B,
            seed=a.seed,
        )
    else:
        required=(a.forcing_csv,a.terrain_csv,a.mapppdr_dir)
        if any(v is None for v in required):
            raise SystemExit("missing forcing/terrain/mapppdr input")
        forcing_units=pd.read_csv(a.forcing_csv)
        terrain=pd.read_csv(a.terrain_csv)
        if a.mode=="shard":
            if a.recovery_json is None or a.shard is None:
                raise SystemExit("shard mode requires recovery receipt and shard")
            recovery=json.loads(a.recovery_json.read_text(encoding="utf-8"))
            if not recovery.get("gate",{}).get("passes",False):
                raise SystemExit("terrain recovery gate did not pass; real fit locked")
        obs=_load_rda(
            a.mapppdr_dir/"data"/"penguin_obs.rda",
            "penguin_obs",
        )
        if a.mode=="recovery":
            out=run_recovery(
                forcing_units,terrain,obs,
                replicates=a.replicates,
                seed=a.seed,
            )
            if not out["gate"]["passes"]:
                a.out_json.parent.mkdir(parents=True,exist_ok=True)
                a.out_json.write_text(
                    json.dumps(out,indent=2,sort_keys=True)+"\n",
                    encoding="utf-8",
                )
                raise SystemExit("terrain recovery gate failed")
        else:
            out=run_shard(
                forcing_units,terrain,obs,
                B=a.B,
                n_shards=a.n_shards,
                shard=a.shard,
                seed=a.seed,
            )

    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
