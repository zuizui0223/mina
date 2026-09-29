#!/usr/bin/env python3
"""Integrated synthetic process-plus-observation recovery for Paper 2 Gate 2E-C."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.simulate_paper2_latent_factor_recovery import (
    build_scale_frame,
    fit_unknown_factor,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
    fit_observation_calibration_fast,
    prepare_observation_recovery_design,
)
from scripts.simulate_paper2_observation_recovery import (
    DELTA_IMAGE_TRUTH,
    SIGMA_1_TRUTH,
    SIGMA_2PLUS_TRUTH,
    fit_observation_calibration_fast,
    prepare_observation_recovery_design,
)


def count_to_analysis_scale(counts) -> np.ndarray:
    """Zero-safe frozen analysis transform z = log1p(count)."""
    values=np.asarray(counts,dtype=float)
    if np.any(~np.isfinite(values)):
        raise ValueError("count contains non-finite values")
    if np.any(values<0):
        raise ValueError("count must be nonnegative")
    return np.log1p(values)


def counts_from_analysis_scale(z) -> np.ndarray:
    """Map synthetic analysis-scale observations to nonnegative integer counts."""
    values=np.asarray(z,dtype=float)
    if np.any(~np.isfinite(values)):
        raise ValueError("analysis-scale value contains non-finite values")
    counts=np.rint(np.expm1(values))
    counts=np.maximum(counts,0.0)
    return counts.astype(np.int64)


def collapse_same_season(
    frame:pd.DataFrame,
    *,
    delta_image:float,
    sigma1:float,
    sigma2plus:float,
)->pd.DataFrame:
    """Method-correct and precision-collapse repeated records within a season."""
    required={
        "group_id","site_id","species_id","season",
        "vantage_family","accuracy_group","count",
    }
    missing=required-set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if sigma1<=0 or sigma2plus<=0:
        raise ValueError("observation sigmas must be positive")

    local=frame.copy()
    local["z"]=count_to_analysis_scale(
        pd.to_numeric(local["count"],errors="coerce").to_numpy()
    )
    family=local["vantage_family"].astype(str)
    local["z_corrected"]=(
        local["z"]
        - float(delta_image)*family.eq("image_based").astype(float)
    )
    accuracy=local["accuracy_group"].astype(str)
    sigma=np.where(
        accuracy.eq("1"),
        float(sigma1),
        np.where(accuracy.eq("2-5"),float(sigma2plus),np.nan),
    )
    if np.any(~np.isfinite(sigma)):
        bad=sorted(set(accuracy[~np.isfinite(sigma)].tolist()))
        raise ValueError(f"unsupported accuracy groups: {bad}")
    local["weight"]=1.0/(sigma*sigma)

    rows=[]
    for group_id,g in local.groupby("group_id",sort=True):
        weights=g["weight"].to_numpy(dtype=float)
        values=g["z_corrected"].to_numpy(dtype=float)
        total=float(weights.sum())
        if total<=0:
            raise ValueError(f"nonpositive precision in group {group_id}")
        first=g.iloc[0]
        rows.append({
            "group_id":str(group_id),
            "site_id":str(first["site_id"]),
            "species_id":str(first["species_id"]),
            "season":int(first["season"]),
            "state_hat":float(np.sum(weights*values)/total),
            "observation_var":float(1.0/total),
            "n_records":int(len(g)),
        })
    return pd.DataFrame(rows).sort_values(
        ["species_id","site_id","season"]
    ).reset_index(drop=True)


START_YEAR=1980
END_YEAR=2025
TRANSITION_YEARS=tuple(range(START_YEAR,END_YEAR))
YEAR_INDEX={year:i for i,year in enumerate(range(START_YEAR,END_YEAR+1))}


def _group_rows(frame:pd.DataFrame)->dict[str,np.ndarray]:
    labels=frame["forcing_group"].astype(str).to_numpy()
    return {
        group:np.flatnonzero(labels==group)
        for group in sorted(set(labels.tolist()))
    }


def simulate_species_counts(
    process_frame:pd.DataFrame,
    observation_metadata:pd.DataFrame,
    *,
    gamma_a:float,
    gamma_ah:float,
    seed:int,
    forcing_sd:float,
    loading_sd:float,
    process_sd:float,
    drift_mean:float,
    drift_sd:float,
    delta_image:float,
    sigma1:float,
    sigma2plus:float,
)->dict:
    """Generate annual latent states and synthetic integer counts on real metadata."""
    required={
        "unit_id","site_id","species_id","forcing_group","A","H","AH","seasons",
    }
    missing=required-set(process_frame.columns)
    if missing:
        raise ValueError(f"missing process columns: {sorted(missing)}")
    mrequired={
        "group_id","site_id","species_id","season",
        "vantage_family","accuracy_group",
    }
    mmissing=mrequired-set(observation_metadata.columns)
    if mmissing:
        raise ValueError(f"missing observation columns: {sorted(mmissing)}")

    frame=process_frame.reset_index(drop=True).copy()
    rng=np.random.default_rng(seed)
    groups=_group_rows(frame)
    n=len(frame)

    true_forcing={}
    for group in groups:
        values=rng.normal(0.0,forcing_sd,len(TRANSITION_YEARS))
        true_forcing[group]=values-float(values.mean())

    true_lambda=(
        1.0
        +float(gamma_a)*frame["A"].to_numpy(dtype=float)
        +float(gamma_ah)*frame["AH"].to_numpy(dtype=float)
        +rng.normal(0.0,loading_sd,n)
    )
    for group,idx in groups.items():
        true_lambda[idx]-=float(true_lambda[idx].mean())-1.0

    true_mu=rng.normal(drift_mean,drift_sd,n)
    state=np.zeros((n,END_YEAR-START_YEAR+1),dtype=float)
    state[:,0]=rng.normal(8.0,0.5,n)
    labels=frame["forcing_group"].astype(str).to_numpy()
    for t,_year in enumerate(TRANSITION_YEARS):
        forcing=np.asarray(
            [true_forcing[group][t] for group in labels],dtype=float
        )
        state[:,t+1]=(
            state[:,t]+true_mu+true_lambda*forcing
            +rng.normal(0.0,process_sd,n)
        )

    unit_index={
        str(row["unit_id"]):i
        for i,row in frame.iterrows()
    }
    obs=observation_metadata.copy()
    obs["unit_id"]=(
        obs["species_id"].astype(str)+"|"+obs["site_id"].astype(str)
    )
    obs=obs[obs["unit_id"].isin(unit_index)].copy().reset_index(drop=True)

    counts=[]
    for row in obs.to_dict(orient="records"):
        season=int(row["season"])
        if not START_YEAR<=season<=END_YEAR:
            raise ValueError(f"season outside frozen window: {season}")
        i=unit_index[str(row["unit_id"])]
        family=str(row["vantage_family"])
        accuracy=str(row["accuracy_group"])
        if accuracy=="1":
            sigma=float(sigma1)
        elif accuracy=="2-5":
            sigma=float(sigma2plus)
        else:
            raise ValueError(f"unsupported accuracy group: {accuracy}")
        method=float(delta_image) if family=="image_based" else 0.0
        z=(
            state[i,YEAR_INDEX[season]]
            +method
            +float(rng.normal(0.0,sigma))
        )
        counts.append(int(counts_from_analysis_scale(np.asarray([z]))[0]))
    obs["count"]=counts

    return {
        "observations":obs,
        "true_forcing":{
            group:values.tolist() for group,values in true_forcing.items()
        },
        "true_lambda":true_lambda.tolist(),
        "true_mu":true_mu.tolist(),
    }


def build_interval_payload(
    process_frame:pd.DataFrame,
    collapsed:pd.DataFrame,
)->dict:
    """Create the adjacent-season interval records used by the frozen factor fit."""
    frame=process_frame.reset_index(drop=True).copy()
    records=[]
    for i,row in frame.iterrows():
        local=collapsed[
            collapsed["site_id"].astype(str).eq(str(row["site_id"]))
            & collapsed["species_id"].astype(str).eq(str(row["species_id"]))
        ].sort_values("season")
        if len(local)<2:
            raise ValueError(f"{row['unit_id']} has fewer than 2 collapsed seasons")
        seasons=local["season"].astype(int).tolist()
        values=local["state_hat"].astype(float).tolist()
        group=str(row["forcing_group"])
        for k in range(len(seasons)-1):
            first,last=seasons[k],seasons[k+1]
            records.append(
                (int(i),group,int(first),int(last),float(values[k+1]-values[k]))
            )
    return {"records":records}


def fit_species_from_counts(
    process_frame:pd.DataFrame,
    observations:pd.DataFrame,
    *,
    delta_image:float,
    sigma1:float,
    sigma2plus:float,
    truth_forcing:dict|None=None,
    true_lambda:list[float]|None=None,
)->dict:
    """Collapse synthetic counts, then recover the unknown factor/loadings."""
    collapsed=collapse_same_season(
        observations,
        delta_image=delta_image,
        sigma1=sigma1,
        sigma2plus=sigma2plus,
    )
    payload=build_interval_payload(process_frame,collapsed)
    if truth_forcing is not None:
        payload["true_forcing"]=truth_forcing
    if true_lambda is not None:
        payload["true_lambda"]=true_lambda
    fit=fit_unknown_factor(
        process_frame.reset_index(drop=True),
        payload,
        iterations=8,
    )
    fit["collapsed_seasons"]=int(len(collapsed))
    return fit


def run_integrated_replicate(
    process_frames:dict[str,pd.DataFrame],
    observation_metadata:pd.DataFrame,
    *,
    gamma_a:float,
    gamma_ah:float,
    seed:int,
    forcing_sd:float,
    loading_sd:float,
    process_sd:float,
    drift_mean:float,
    drift_sd:float,
)->dict:
    """Generate synthetic counts, calibrate observation error, then fit each species."""
    if not process_frames:
        raise ValueError("no process frames")

    simulations={}
    observation_parts=[]
    for index,species_id in enumerate(sorted(process_frames)):
        sim=simulate_species_counts(
            process_frames[species_id],
            observation_metadata[
                observation_metadata["species_id"].astype(str).eq(str(species_id))
            ],
            gamma_a=gamma_a,
            gamma_ah=gamma_ah,
            seed=seed+index*10000,
            forcing_sd=forcing_sd,
            loading_sd=loading_sd,
            process_sd=process_sd,
            drift_mean=drift_mean,
            drift_sd=drift_sd,
            delta_image=DELTA_IMAGE_TRUTH,
            sigma1=SIGMA_1_TRUTH,
            sigma2plus=SIGMA_2PLUS_TRUTH,
        )
        simulations[species_id]=sim
        observation_parts.append(sim["observations"])

    combined=pd.concat(observation_parts,ignore_index=True)
    design=prepare_observation_recovery_design(combined)
    calibration=fit_observation_calibration_fast(
        count_to_analysis_scale(combined["count"].to_numpy(dtype=float)),
        design,
    )

    species_fit={}
    for species_id,frame in sorted(process_frames.items()):
        obs=combined[
            combined["species_id"].astype(str).eq(str(species_id))
        ].copy()
        sim=simulations[species_id]
        species_fit[species_id]=fit_species_from_counts(
            frame,
            obs,
            delta_image=float(calibration["delta_image"]),
            sigma1=float(calibration["accuracy"]["1"]["sigma"]),
            sigma2plus=float(calibration["accuracy"]["2-5"]["sigma"]),
            truth_forcing=sim["true_forcing"],
            true_lambda=sim["true_lambda"],
        )

    return {
        "observation":calibration,
        "species":species_fit,
    }


def simulate_integrated_dataset(
    frames:dict[str,pd.DataFrame],
    observation_metadata:pd.DataFrame,
    *,
    gamma_a:float,
    gamma_ah:float,
    seed:int,
    forcing_sd:float,
    loading_sd:float,
    process_sd:float,
    drift_mean:float,
    drift_sd:float,
    delta_image:float,
    sigma1:float,
    sigma2plus:float,
)->dict:
    """Generate one joint synthetic count dataset with shared observation nuisance."""
    metadata=observation_metadata.reset_index(drop=True).copy()
    required={
        "group_id","site_id","species_id","season",
        "vantage_family","accuracy_group",
    }
    missing=required-set(metadata.columns)
    if missing:
        raise ValueError(f"missing observation metadata columns: {sorted(missing)}")
    metadata["record_id"]=np.arange(len(metadata),dtype=int)
    metadata["unit_id"]=(
        metadata["species_id"].astype(str)+"|"+metadata["site_id"].astype(str)
    )
    count=np.full(len(metadata),np.nan,dtype=float)
    truths={}
    covered_ids:set[int]=set()

    for index,species_id in enumerate(sorted(frames)):
        frame=frames[species_id].reset_index(drop=True).copy()
        sim=simulate_species_counts(
            frame,
            metadata,
            gamma_a=gamma_a,
            gamma_ah=gamma_ah,
            seed=seed+10000*(index+1),
            forcing_sd=forcing_sd,
            loading_sd=loading_sd,
            process_sd=process_sd,
            drift_mean=drift_mean,
            drift_sd=drift_sd,
            delta_image=delta_image,
            sigma1=sigma1,
            sigma2plus=sigma2plus,
        )
        observed=sim["observations"]
        for rid,value in zip(
            observed["record_id"].astype(int),
            observed["count"].astype(int),
        ):
            count[rid]=float(value)
            covered_ids.add(int(rid))
        truths[species_id]={
            "true_forcing":sim["true_forcing"],
            "true_lambda":sim["true_lambda"],
            "true_mu":sim["true_mu"],
        }

    # Calibration-only units outside the trait/process frames retain the actual
    # metadata structure but receive an independent same-season latent mean.
    remaining=np.flatnonzero(~np.isfinite(count))
    if len(remaining):
        rng=np.random.default_rng(seed+9000000)
        remain_frame=metadata.iloc[remaining].copy()
        latent_by_group={
            str(group):float(rng.normal(8.0,1.0))
            for group in sorted(remain_frame["group_id"].astype(str).unique())
        }
        for rid in remaining:
            row=metadata.iloc[int(rid)]
            accuracy=str(row["accuracy_group"])
            if accuracy=="1":
                sigma=float(sigma1)
            elif accuracy=="2-5":
                sigma=float(sigma2plus)
            else:
                raise ValueError(f"unsupported accuracy group: {accuracy}")
            method=(
                float(delta_image)
                if str(row["vantage_family"])=="image_based"
                else 0.0
            )
            z=(
                latent_by_group[str(row["group_id"])]
                +method
                +float(rng.normal(0.0,sigma))
            )
            count[int(rid)]=float(
                counts_from_analysis_scale(np.asarray([z]))[0]
            )

    if np.any(~np.isfinite(count)):
        raise ValueError("synthetic count generation left missing records")
    metadata["count"]=count.astype(np.int64)
    return {
        "observations":metadata.drop(columns=["record_id"]),
        "truth":truths,
    }


def fit_integrated_dataset(
    frames:dict[str,pd.DataFrame],
    observations:pd.DataFrame,
    truth:dict[str,dict]|None=None,
)->dict:
    """Estimate shared nuisance once, then recover each species process."""
    records=observations.reset_index(drop=True).copy()
    design=prepare_observation_recovery_design(records)
    log_observed=count_to_analysis_scale(
        pd.to_numeric(records["count"],errors="coerce").to_numpy()
    )
    observation=fit_observation_calibration_fast(log_observed,design)

    species={}
    for species_id in sorted(frames):
        frame=frames[species_id].reset_index(drop=True).copy()
        target=set(frame["unit_id"].astype(str))
        local=records[
            (
                records["species_id"].astype(str)
                +"|"
                +records["site_id"].astype(str)
            ).isin(target)
        ].copy()
        truth_meta=(truth or {}).get(species_id,{})
        fit=fit_species_from_counts(
            frame,
            local,
            delta_image=float(observation["delta_image"]),
            sigma1=float(observation["accuracy"]["1"]["sigma"]),
            sigma2plus=float(observation["accuracy"]["2-5"]["sigma"]),
            truth_forcing=truth_meta.get("true_forcing"),
            true_lambda=truth_meta.get("true_lambda"),
        )
        species[species_id]=fit

    return {
        "observation":observation,
        "species":species,
    }


def _quantile(values:list[float],q:float)->float:
    arr=np.asarray(values,dtype=float)
    if arr.size==0:
        raise ValueError("cannot summarize empty vector")
    return float(np.quantile(arr,q))


def _scenario_gamma_summary(records:list[dict])->dict:
    gamma_a=[float(r["gamma_a"]) for r in records]
    gamma_ah=[float(r["gamma_ah"]) for r in records]
    lambda_corr=[
        float(r["lambda_correlation"])
        for r in records
        if r.get("lambda_correlation") is not None
    ]
    return {
        "median_gamma_a":_quantile(gamma_a,0.50),
        "q05_gamma_a":_quantile(gamma_a,0.05),
        "q95_gamma_a":_quantile(gamma_a,0.95),
        "negative_gamma_a_fraction":float(np.mean(np.asarray(gamma_a)<0.0)),
        "median_gamma_ah":_quantile(gamma_ah,0.50),
        "q05_gamma_ah":_quantile(gamma_ah,0.05),
        "q95_gamma_ah":_quantile(gamma_ah,0.95),
        "negative_gamma_ah_fraction":float(np.mean(np.asarray(gamma_ah)<0.0)),
        "median_lambda_correlation":(
            _quantile(lambda_corr,0.50) if lambda_corr else None
        ),
    }


def evaluate_integrated_configuration(
    frames:dict[str,pd.DataFrame],
    observation_metadata:pd.DataFrame,
    *,
    replicates:int=100,
    seed_offset:int=0,
)->dict:
    """Run frozen null/crossover/simple-buffering integrated recovery."""
    if replicates<2:
        raise ValueError("replicates must be >=2")
    scenarios={
        "null":{"gamma_a":0.0,"gamma_ah":0.0},
        "crossover":{"gamma_a":0.0,"gamma_ah":-0.35},
        "simple_buffering":{"gamma_a":-0.25,"gamma_ah":0.0},
    }
    forcing_sd=0.08
    loading_sd=0.15
    process_sd=0.04
    drift_mean=-0.01
    drift_sd=0.01
    delta_truth=float(np.log(1.15))
    sigma1_truth=float(np.log(1.05))
    sigma2_truth=float(np.log(1.25))

    observation_records=[]
    species_records={
        sp:{name:[] for name in scenarios}
        for sp in sorted(frames)
    }
    forcing_corr={
        sp:{} for sp in sorted(frames)
    }
    finite=0
    total=0

    for scenario_index,(scenario,truths) in enumerate(scenarios.items()):
        for rep in range(replicates):
            seed=seed_offset+scenario_index*100000+rep
            sim=simulate_integrated_dataset(
                frames,
                observation_metadata,
                gamma_a=float(truths["gamma_a"]),
                gamma_ah=float(truths["gamma_ah"]),
                seed=seed,
                forcing_sd=forcing_sd,
                loading_sd=loading_sd,
                process_sd=process_sd,
                drift_mean=drift_mean,
                drift_sd=drift_sd,
                delta_image=delta_truth,
                sigma1=sigma1_truth,
                sigma2plus=sigma2_truth,
            )
            fit=fit_integrated_dataset(
                frames,
                sim["observations"],
                sim["truth"],
            )
            obs=fit["observation"]
            observation_records.append({
                "scenario":scenario,
                "delta_image":float(obs["delta_image"]),
                "sigma1":float(obs["accuracy"]["1"]["sigma"]),
                "sigma2plus":float(obs["accuracy"]["2-5"]["sigma"]),
            })
            current_finite=all(np.isfinite([
                float(obs["delta_image"]),
                float(obs["accuracy"]["1"]["sigma"]),
                float(obs["accuracy"]["2-5"]["sigma"]),
            ]))
            for sp,sfit in fit["species"].items():
                species_records[sp][scenario].append(sfit)
                current_finite=current_finite and all(np.isfinite([
                    float(sfit["gamma_a"]),
                    float(sfit["gamma_h"]),
                    float(sfit["gamma_ah"]),
                ]))
                for group,value in sfit["forcing_correlation"].items():
                    forcing_corr[sp].setdefault(str(group),[]).append(float(value))
                    current_finite=current_finite and np.isfinite(float(value))
            total+=1
            if current_finite:
                finite+=1

    delta_vals=[r["delta_image"] for r in observation_records]
    sigma1_vals=[r["sigma1"] for r in observation_records]
    sigma2_vals=[r["sigma2plus"] for r in observation_records]
    observation={
        "truth":{
            "delta_image":delta_truth,
            "sigma1":sigma1_truth,
            "sigma2plus":sigma2_truth,
        },
        "delta_image":{
            "median":_quantile(delta_vals,0.50),
            "q05":_quantile(delta_vals,0.05),
            "q95":_quantile(delta_vals,0.95),
        },
        "sigma1":{
            "median":_quantile(sigma1_vals,0.50),
        },
        "sigma2plus":{
            "median":_quantile(sigma2_vals,0.50),
        },
    }
    observation["delta_image"]["bias"]=(
        observation["delta_image"]["median"]-delta_truth
    )
    observation["sigma1"]["relative_bias"]=(
        (observation["sigma1"]["median"]-sigma1_truth)/sigma1_truth
    )
    observation["sigma2plus"]["relative_bias"]=(
        (observation["sigma2plus"]["median"]-sigma2_truth)/sigma2_truth
    )

    species={}
    species_checks={}
    for sp in sorted(frames):
        groups={
            group:{
                "median_corr":_quantile(values,0.50),
                "q05_corr":_quantile(values,0.05),
            }
            for group,values in sorted(forcing_corr[sp].items())
        }
        null=_scenario_gamma_summary(species_records[sp]["null"])
        crossover=_scenario_gamma_summary(species_records[sp]["crossover"])
        simple=_scenario_gamma_summary(species_records[sp]["simple_buffering"])
        checks={
            "factor_median":all(v["median_corr"]>=0.70 for v in groups.values()),
            "factor_q05":all(v["q05_corr"]>=0.25 for v in groups.values()),
            "crossover_bias":abs(crossover["median_gamma_ah"]+0.35)<=0.12,
            "crossover_sign":crossover["negative_gamma_ah_fraction"]>=0.90,
            "null_center":abs(null["median_gamma_ah"])<=0.06,
            "null_contains_zero":(
                null["q05_gamma_ah"]<=0.0<=null["q95_gamma_ah"]
            ),
            "simple_a_bias":abs(simple["median_gamma_a"]+0.25)<=0.10,
            "simple_a_sign":simple["negative_gamma_a_fraction"]>=0.90,
            "simple_no_spurious_crossover":abs(simple["median_gamma_ah"])<=0.06,
        }
        species[sp]={
            "forcing_groups":groups,
            "null":null,
            "crossover":crossover,
            "simple_buffering":simple,
            "gate":{"passes":bool(all(checks.values())),"checks":checks},
        }
        species_checks[sp]=bool(all(checks.values()))

    observation_checks={
        "offset_bias":abs(observation["delta_image"]["bias"])<=0.03,
        "accuracy1_bias":abs(observation["sigma1"]["relative_bias"])<=0.15,
        "accuracy2plus_bias":abs(
            observation["sigma2plus"]["relative_bias"]
        )<=0.30,
    }
    observation_gate={
        "passes":bool(all(observation_checks.values())),
        "checks":observation_checks,
    }
    gate={
        "passes":bool(
            all(species_checks.values())
            and observation_gate["passes"]
            and finite==total
        ),
        "species_pass":species_checks,
        "observation_checks":observation_checks,
        "finite_estimate_fraction":float(finite/total),
    }
    return {
        "replicates_per_scenario":int(replicates),
        "simulation":{
            "forcing_sd":forcing_sd,
            "loading_sd":loading_sd,
            "process_sd":process_sd,
            "drift_mean":drift_mean,
            "drift_sd":drift_sd,
            "delta_image":delta_truth,
            "sigma1":sigma1_truth,
            "sigma2plus":sigma2_truth,
        },
        "observation":observation,
        "observation_gate":observation_gate,
        "species":species,
        "gate":gate,
    }


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    result=pyreadr.read_r(str(path))
    if expected in result:
        frame=result[expected]
    elif len(result)==1:
        frame=next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(frame,pd.DataFrame):
        raise TypeError(expected)
    return frame


def build_recovery_frames(
    forcing_result:dict,
    forcing_units:pd.DataFrame,
    breeding_options:pd.DataFrame,
    scale_by_species:dict[str,str],
)->dict[str,pd.DataFrame]:
    frames={}
    for species_id in ("ADPE","CHPE","GEPE"):
        scale=str(scale_by_species[species_id])
        frame=build_scale_frame(
            forcing_result,
            forcing_units,
            breeding_options,
            species_id,
            scale,
        )
        frames[species_id]=frame
    return frames


def run_integrated_audit(
    forcing_result:dict,
    forcing_units:pd.DataFrame,
    breeding_options:pd.DataFrame,
    observation_metadata:pd.DataFrame,
    latent_recovery_result:dict,
    *,
    replicates:int=100,
)->dict:
    """Run primary retained scales plus mandatory species-wide sensitivity."""
    retained={
        str(k):str(v)
        for k,v in latent_recovery_result["decision"][
            "selected_recovered_scale_by_species"
        ].items()
    }
    if retained != {
        "ADPE":"ccamlr",
        "CHPE":"apbp_region",
        "GEPE":"species_wide",
    }:
        raise ValueError(f"retained scale drift: {retained}")

    primary_frames=build_recovery_frames(
        forcing_result,
        forcing_units,
        breeding_options,
        retained,
    )
    expected_primary={"ADPE":40,"CHPE":33,"GEPE":29}
    observed_primary={
        sp:int(len(frame)) for sp,frame in primary_frames.items()
    }
    if observed_primary!=expected_primary:
        raise ValueError(
            f"primary integrated frame drift: {observed_primary} != {expected_primary}"
        )

    specieswide_scales={
        "ADPE":"species_wide",
        "CHPE":"species_wide",
        "GEPE":"species_wide",
    }
    specieswide_frames=build_recovery_frames(
        forcing_result,
        forcing_units,
        breeding_options,
        specieswide_scales,
    )
    expected_specieswide={"ADPE":41,"CHPE":34,"GEPE":29}
    observed_specieswide={
        sp:int(len(frame)) for sp,frame in specieswide_frames.items()
    }
    if observed_specieswide!=expected_specieswide:
        raise ValueError(
            "species-wide integrated frame drift: "
            f"{observed_specieswide} != {expected_specieswide}"
        )

    primary=evaluate_integrated_configuration(
        primary_frames,
        observation_metadata,
        replicates=replicates,
        seed_offset=4000000,
    )
    specieswide=evaluate_integrated_configuration(
        specieswide_frames,
        observation_metadata,
        replicates=replicates,
        seed_offset=6000000,
    )

    selected={}
    for sp in ("ADPE","CHPE","GEPE"):
        if primary["species"][sp]["gate"]["passes"]:
            selected[sp]=retained[sp]
        elif specieswide["species"][sp]["gate"]["passes"]:
            selected[sp]="species_wide"
        else:
            selected[sp]=None

    decision={
        "selected_integrated_scale_by_species":selected,
        "all_species_have_integrated_scale":bool(
            all(value is not None for value in selected.values())
        ),
        "primary_observation_gate_passed":bool(primary["observation_gate"]["passes"]),
        "specieswide_observation_gate_passed":bool(
            specieswide["observation_gate"]["passes"]
        ),
        "primary_integrated_gate_passed":bool(primary["gate"]["passes"]),
        "specieswide_integrated_gate_passed":bool(
            specieswide["gate"]["passes"]
        ),
        "specieswide_sensitivity_completed":True,
        "no_real_demographic_count_magnitudes_opened":True,
    }
    decision["counts_may_be_opened"] = bool(
        decision["all_species_have_integrated_scale"]
        and decision["primary_observation_gate_passed"]
        and decision["specieswide_integrated_gate_passed"]
    )

    return {
        "schema_version":1,
        "audit_id":"mina-paper2-integrated-recovery-v1",
        "replicates_per_scenario":int(replicates),
        "primary_scale_by_species":retained,
        "primary_frame_units":observed_primary,
        "specieswide_frame_units":observed_specieswide,
        "primary":primary,
        "species_wide_sensitivity":specieswide,
        "decision":decision,
    }


def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--forcing-json",required=True,type=Path)
    parser.add_argument("--forcing-csv",required=True,type=Path)
    parser.add_argument("--breeding-csv",required=True,type=Path)
    parser.add_argument("--latent-recovery-json",required=True,type=Path)
    parser.add_argument("--mapppdr-dir",required=True,type=Path)
    parser.add_argument("--out-json",required=True,type=Path)
    parser.add_argument("--replicates",type=int,default=100)
    args=parser.parse_args()

    forcing_result=json.loads(
        args.forcing_json.read_text(encoding="utf-8")
    )
    forcing_units=pd.read_csv(args.forcing_csv)
    breeding_options=pd.read_csv(args.breeding_csv)
    latent_result=json.loads(
        args.latent_recovery_json.read_text(encoding="utf-8")
    )
    obs=_load_rda(
        args.mapppdr_dir/"data"/"penguin_obs.rda",
        "penguin_obs",
    )
    metadata=build_frozen_observation_metadata(obs)
    if len(metadata)!=2100:
        raise ValueError(f"observation metadata drift: {len(metadata)} != 2100")

    result=run_integrated_audit(
        forcing_result,
        forcing_units,
        breeding_options,
        metadata,
        latent_result,
        replicates=args.replicates,
    )
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result["decision"]["counts_may_be_opened"]:
        raise SystemExit("integrated recovery gate failed")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
