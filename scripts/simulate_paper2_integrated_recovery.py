#!/usr/bin/env python3
"""Integrated synthetic process-plus-observation recovery for Paper 2 Gate 2E-C."""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.simulate_paper2_latent_factor_recovery import fit_unknown_factor


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
