#!/usr/bin/env python3
"""Hierarchical integrated process-observation recovery for Paper 2 Gate 2E-C v2."""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.simulate_paper2_integrated_recovery import (
    START_YEAR,
    END_YEAR,
    TRANSITION_YEARS,
    count_to_analysis_scale,
    collapse_same_season,
)
from scripts.simulate_paper2_observation_recovery import (
    prepare_observation_recovery_design,
    fit_observation_calibration_fast,
)


def group_center_traits(frame: pd.DataFrame) -> pd.DataFrame:
    """Center A, H and A:H within the frozen forcing group."""
    required={"forcing_group","A","H","AH"}
    missing=required-set(frame.columns)
    if missing:
        raise ValueError(f"missing trait columns: {sorted(missing)}")
    out=frame.copy()
    for raw,centered in (("A","Ac"),("H","Hc"),("AH","AHc")):
        values=pd.to_numeric(out[raw],errors="coerce")
        if values.isna().any():
            raise ValueError(f"nonfinite trait values in {raw}")
        out[centered]=values-out.groupby("forcing_group")[raw].transform("mean")
    return out


def profile_process_sd(
    residual,
    duration,
    obs_var,
    *,
    min_sd: float=0.005,
    max_sd: float=0.30,
    grid_size: int=80,
) -> float:
    """Profile interval likelihood over process SD without using synthetic truth."""
    r=np.asarray(residual,dtype=float)
    d=np.asarray(duration,dtype=float)
    v=np.asarray(obs_var,dtype=float)
    if not (r.shape==d.shape==v.shape):
        raise ValueError("profile arrays must have identical shape")
    if r.size==0:
        raise ValueError("cannot profile process SD without intervals")
    if np.any(d<=0) or np.any(v<0) or np.any(~np.isfinite(r+d+v)):
        raise ValueError("invalid process-profile inputs")
    grid=np.geomspace(float(min_sd),float(max_sd),int(grid_size))
    nll=[]
    for sd in grid:
        var=d*sd*sd+v
        nll.append(0.5*float(np.sum(np.log(var)+(r*r)/var)))
    return float(grid[int(np.argmin(nll))])


def _site_data(frame:pd.DataFrame,collapsed:pd.DataFrame)->list[dict]:
    out=[]
    for i,row in frame.reset_index(drop=True).iterrows():
        local=collapsed[
            collapsed["site_id"].astype(str).eq(str(row["site_id"]))
            & collapsed["species_id"].astype(str).eq(str(row["species_id"]))
        ].sort_values("season")
        if len(local)<2:
            raise ValueError(f"{row['unit_id']} has fewer than 2 collapsed seasons")
        seasons=local["season"].astype(int).to_numpy()
        z=local["state_hat"].astype(float).to_numpy()
        v=local["observation_var"].astype(float).to_numpy()
        start,end=int(seasons.min()),int(seasons.max())
        years=np.arange(start,end+1,dtype=int)
        x=np.interp(years,seasons,z).astype(float)
        out.append({
            "index":int(i),
            "unit_id":str(row["unit_id"]),
            "group":str(row["forcing_group"]),
            "years":years,
            "seasons":seasons,
            "z":z,
            "v":v,
            "x":x,
        })
    return out


def _forcing_template(frame:pd.DataFrame)->dict[str,np.ndarray]:
    return {
        str(group):np.zeros(len(TRANSITION_YEARS),dtype=float)
        for group in sorted(frame["forcing_group"].astype(str).unique())
    }


def _active_increment(site:dict,year:int)->float|None:
    years=site["years"]
    if year<int(years[0]) or year+1>int(years[-1]):
        return None
    j=year-int(years[0])
    return float(site["x"][j+1]-site["x"][j])


def _update_forcing(
    sites:list[dict],
    frame:pd.DataFrame,
    mu:np.ndarray,
    lam:np.ndarray,
    forcing:dict[str,np.ndarray],
)->tuple[dict[str,np.ndarray],np.ndarray]:
    labels=frame["forcing_group"].astype(str).to_numpy()
    new={g:np.zeros_like(values) for g,values in forcing.items()}
    supported={g:np.zeros(len(TRANSITION_YEARS),dtype=bool) for g in forcing}
    for g in new:
        idx=np.flatnonzero(labels==g)
        for ti,year in enumerate(TRANSITION_YEARS):
            num=0.0
            den=0.0
            for i in idx:
                d=_active_increment(sites[int(i)],int(year))
                if d is None:
                    continue
                num+=float(lam[i])*(d-float(mu[i]))
                den+=float(lam[i])**2
            if den>1e-12:
                new[g][ti]=num/den
                supported[g][ti]=True
        if supported[g].any():
            center=float(new[g][supported[g]].mean())
            new[g][supported[g]]-=center
            # Preserve mu + lambda F after centering F.
            mu[idx]+=lam[idx]*center
    return new,mu


def _smooth_states(
    sites:list[dict],
    mu:np.ndarray,
    lam:np.ndarray,
    forcing:dict[str,np.ndarray],
    process_sd:float,
)->None:
    tau=max(float(process_sd),1e-8)
    for i,site in enumerate(sites):
        years=site["years"]
        n=len(years)
        season_to_local={int(y):j for j,y in enumerate(years)}
        rows=len(site["seasons"])+(n-1)
        A=np.zeros((rows,n),dtype=float)
        b=np.zeros(rows,dtype=float)
        r=0
        for season,z,var in zip(site["seasons"],site["z"],site["v"]):
            j=season_to_local[int(season)]
            sd=np.sqrt(max(float(var),1e-10))
            A[r,j]=1.0/sd
            b[r]=float(z)/sd
            r+=1
        f=forcing[site["group"]]
        for year in range(int(years[0]),int(years[-1])):
            j=year-int(years[0])
            A[r,j]=-1.0/tau
            A[r,j+1]=1.0/tau
            b[r]=(float(mu[i])+float(lam[i])*float(f[year-START_YEAR]))/tau
            r+=1
        site["x"]=np.linalg.lstsq(A,b,rcond=None)[0]


def _update_site_and_gamma_joint(
    sites:list[dict],
    frame:pd.DataFrame,
    forcing:dict[str,np.ndarray],
    process_sd:float,
    loading_sd:float,
    *,
    min_loading_sd:float=0.05,
)->tuple[np.ndarray,np.ndarray,np.ndarray,float]:
    """Jointly update site drift, trait slopes, and residual site loadings.

    Model annual increments as
      d_it = mu_i + F_gt * (1 + X_i gamma + b_i) + error,
    with a Gaussian penalty on b_i and exact within-group mean(b)=0
    identification constraints.
    """
    n=len(frame)
    p=3
    tau=max(float(process_sd),1e-8)
    sig=max(float(loading_sd),1e-8)
    X=frame[["Ac","Hc","AHc"]].to_numpy(dtype=float)
    labels=frame["forcing_group"].astype(str).to_numpy()
    groups=sorted(set(labels.tolist()))

    n_increment_rows=sum(len(site["years"])-1 for site in sites)
    n_prior_rows=n
    n_cols=n+p+n
    A=np.zeros((n_increment_rows+n_prior_rows,n_cols),dtype=float)
    y=np.zeros(n_increment_rows+n_prior_rows,dtype=float)
    r=0
    for i,site in enumerate(sites):
        years=site["years"]
        d=np.diff(site["x"])
        f=np.asarray([
            forcing[site["group"]][int(year)-START_YEAR]
            for year in years[:-1]
        ],dtype=float)
        for delta,ft in zip(d,f):
            A[r,i]=1.0/tau
            A[r,n:n+p]=(float(ft)*X[i])/tau
            A[r,n+p+i]=float(ft)/tau
            y[r]=(float(delta)-float(ft))/tau
            r+=1

    for i in range(n):
        A[r,n+p+i]=1.0/sig
        r+=1

    # Exact identification: residual site loading deviations sum to zero
    # within each frozen forcing group. Because traits are group-centered,
    # this also enforces mean(lambda)=1 in every group.
    C=np.zeros((len(groups),n_cols),dtype=float)
    for gi,g in enumerate(groups):
        idx=np.flatnonzero(labels==g)
        C[gi,n+p+idx]=1.0/len(idx)

    ata=A.T@A
    aty=A.T@y
    kkt=np.block([
        [ata,C.T],
        [C,np.zeros((len(groups),len(groups)),dtype=float)],
    ])
    rhs=np.concatenate([aty,np.zeros(len(groups),dtype=float)])
    sol=np.linalg.lstsq(kkt,rhs,rcond=None)[0][:n_cols]

    mu=sol[:n]
    gamma=sol[n:n+p]
    b=sol[n+p:]
    lam=1.0+X@gamma+b
    residual_sd=float(np.sqrt(np.mean(b*b)))
    loading_sd_new=max(residual_sd,float(min_loading_sd))
    return mu,lam,gamma,loading_sd_new


def _profile_from_observed_intervals(
    sites:list[dict],
    frame:pd.DataFrame,
    mu:np.ndarray,
    lam:np.ndarray,
    forcing:dict[str,np.ndarray],
)->float:
    residual=[]
    duration=[]
    obsvar=[]
    for i,site in enumerate(sites):
        seasons=site["seasons"]
        z=site["z"]
        v=site["v"]
        f=forcing[site["group"]]
        for k in range(len(seasons)-1):
            first,last=int(seasons[k]),int(seasons[k+1])
            fsum=float(np.sum(f[first-START_YEAR:last-START_YEAR]))
            pred=(last-first)*float(mu[i])+float(lam[i])*fsum
            residual.append(float(z[k+1]-z[k])-pred)
            duration.append(float(last-first))
            obsvar.append(float(v[k+1]+v[k]))
    return profile_process_sd(
        residual,duration,obsvar,
        min_sd=0.005,max_sd=0.30,grid_size=80,
    )


def _build_observed_intervals(
    frame:pd.DataFrame,
    collapsed:pd.DataFrame,
)->list[dict]:
    intervals=[]
    local_frame=frame.reset_index(drop=True)
    for i,row in local_frame.iterrows():
        local=collapsed[
            collapsed["site_id"].astype(str).eq(str(row["site_id"]))
            & collapsed["species_id"].astype(str).eq(str(row["species_id"]))
        ].sort_values("season")
        if len(local)<2:
            raise ValueError(f"{row['unit_id']} has fewer than 2 collapsed seasons")
        seasons=local["season"].astype(int).to_numpy()
        z=local["state_hat"].astype(float).to_numpy()
        v=local["observation_var"].astype(float).to_numpy()
        for k in range(len(seasons)-1):
            first,last=int(seasons[k]),int(seasons[k+1])
            intervals.append({
                "site":int(i),
                "group":str(row["forcing_group"]),
                "first":first,
                "last":last,
                "duration":float(last-first),
                "delta":float(z[k+1]-z[k]),
                "obs_var":float(v[k+1]+v[k]),
            })
    return intervals


def _interval_variance(interval:dict,process_sd:float)->float:
    return (
        float(interval["duration"])*float(process_sd)**2
        +float(interval["obs_var"])
    )


def _solve_forcing_interval(
    intervals:list[dict],
    frame:pd.DataFrame,
    lam:np.ndarray,
    process_sd:float,
)->tuple[np.ndarray,dict[str,np.ndarray]]:
    n=len(frame)
    groups=sorted(frame["forcing_group"].astype(str).unique())
    gindex={g:j for j,g in enumerate(groups)}
    T=len(TRANSITION_YEARS)
    cols=n+len(groups)*T
    A=np.zeros((len(intervals),cols),dtype=float)
    y=np.zeros(len(intervals),dtype=float)
    for r,it in enumerate(intervals):
        i=int(it["site"])
        g=str(it["group"])
        var=max(_interval_variance(it,process_sd),1e-12)
        w=1.0/np.sqrt(var)
        A[r,i]=float(it["duration"])*w
        start=n+gindex[g]*T
        for year in range(int(it["first"]),int(it["last"])):
            A[r,start+(year-START_YEAR)]=float(lam[i])*w
        y[r]=float(it["delta"])*w

    C=np.zeros((len(groups),cols),dtype=float)
    for gi,g in enumerate(groups):
        start=n+gi*T
        C[gi,start:start+T]=1.0/T
    ata=A.T@A
    aty=A.T@y
    kkt=np.block([
        [ata,C.T],
        [C,np.zeros((len(groups),len(groups)),dtype=float)],
    ])
    rhs=np.concatenate([aty,np.zeros(len(groups),dtype=float)])
    sol=np.linalg.lstsq(kkt,rhs,rcond=None)[0][:cols]
    mu=sol[:n]
    forcing={
        g:sol[n+gindex[g]*T:n+(gindex[g]+1)*T].copy()
        for g in groups
    }
    return mu,forcing


def _forcing_sum(forcing:dict[str,np.ndarray],it:dict)->float:
    f=forcing[str(it["group"])]
    return float(np.sum(
        f[int(it["first"])-START_YEAR:int(it["last"])-START_YEAR]
    ))


def _solve_site_gamma_interval(
    intervals:list[dict],
    frame:pd.DataFrame,
    forcing:dict[str,np.ndarray],
    process_sd:float,
    loading_sd:float,
    *,
    min_loading_sd:float=0.05,
)->tuple[np.ndarray,np.ndarray,np.ndarray,float]:
    n=len(frame)
    p=3
    X=frame[["Ac","Hc","AHc"]].to_numpy(dtype=float)
    labels=frame["forcing_group"].astype(str).to_numpy()
    groups=sorted(set(labels.tolist()))
    sig=max(float(loading_sd),1e-8)
    cols=n+p+n
    A=np.zeros((len(intervals)+n,cols),dtype=float)
    y=np.zeros(len(intervals)+n,dtype=float)
    r=0
    for it in intervals:
        i=int(it["site"])
        fsum=_forcing_sum(forcing,it)
        var=max(_interval_variance(it,process_sd),1e-12)
        w=1.0/np.sqrt(var)
        A[r,i]=float(it["duration"])*w
        A[r,n:n+p]=fsum*X[i]*w
        A[r,n+p+i]=fsum*w
        y[r]=(float(it["delta"])-fsum)*w
        r+=1
    for i in range(n):
        A[r,n+p+i]=1.0/sig
        r+=1

    C=np.zeros((len(groups),cols),dtype=float)
    for gi,g in enumerate(groups):
        idx=np.flatnonzero(labels==g)
        C[gi,n+p+idx]=1.0/len(idx)
    ata=A.T@A
    aty=A.T@y
    kkt=np.block([
        [ata,C.T],
        [C,np.zeros((len(groups),len(groups)),dtype=float)],
    ])
    rhs=np.concatenate([aty,np.zeros(len(groups),dtype=float)])
    sol=np.linalg.lstsq(kkt,rhs,rcond=None)[0][:cols]
    mu=sol[:n]
    gamma=sol[n:n+p]
    b=sol[n+p:]
    lam=1.0+X@gamma+b
    loading_sd_new=max(
        float(np.sqrt(np.mean(b*b))),
        float(min_loading_sd),
    )
    return mu,lam,gamma,loading_sd_new


def _profile_interval_process_sd(
    intervals:list[dict],
    mu:np.ndarray,
    lam:np.ndarray,
    forcing:dict[str,np.ndarray],
)->float:
    residual=[]
    duration=[]
    obs_var=[]
    for it in intervals:
        i=int(it["site"])
        fsum=_forcing_sum(forcing,it)
        pred=float(it["duration"])*float(mu[i])+float(lam[i])*fsum
        residual.append(float(it["delta"])-pred)
        duration.append(float(it["duration"]))
        obs_var.append(float(it["obs_var"]))
    return profile_process_sd(
        residual,duration,obs_var,
        min_sd=0.005,max_sd=0.30,grid_size=80,
    )


def fit_hierarchical_species(
    process_frame:pd.DataFrame,
    observations:pd.DataFrame,
    *,
    delta_image:float,
    sigma1:float,
    sigma2plus:float,
    truth_forcing:dict|None=None,
    true_lambda:list[float]|None=None,
    iterations:int=12,
)->dict:
    """Hierarchical interval-marginal fit with observation-error propagation."""
    frame=group_center_traits(process_frame.reset_index(drop=True))
    collapsed=collapse_same_season(
        observations,
        delta_image=float(delta_image),
        sigma1=float(sigma1),
        sigma2plus=float(sigma2plus),
    )
    intervals=_build_observed_intervals(frame,collapsed)

    n=len(frame)
    gamma=np.zeros(3,dtype=float)
    lam=np.ones(n,dtype=float)
    process_sd_initial=0.10
    process_sd=process_sd_initial
    loading_sd=0.30
    mu,forcing=_solve_forcing_interval(
        intervals,frame,lam,process_sd
    )

    for _ in range(int(iterations)):
        mu,forcing=_solve_forcing_interval(
            intervals,frame,lam,process_sd
        )
        mu,lam,gamma,loading_sd=_solve_site_gamma_interval(
            intervals,frame,forcing,process_sd,loading_sd
        )
        process_sd=_profile_interval_process_sd(
            intervals,mu,lam,forcing
        )

    mu,forcing=_solve_forcing_interval(
        intervals,frame,lam,process_sd
    )
    mu,lam,gamma,loading_sd=_solve_site_gamma_interval(
        intervals,frame,forcing,process_sd,loading_sd
    )

    corr={}
    if truth_forcing is not None:
        for g,values in forcing.items():
            truth=np.asarray(truth_forcing[g],dtype=float)
            corr[g]=float(np.corrcoef(truth,values)[0,1])
    lambda_corr=None
    if true_lambda is not None:
        lambda_corr=float(np.corrcoef(
            np.asarray(true_lambda,dtype=float),lam
        )[0,1])

    labels=frame["forcing_group"].astype(str).to_numpy()
    means={
        g:float(lam[np.flatnonzero(labels==g)].mean())
        for g in sorted(set(labels.tolist()))
    }
    return {
        "gamma_a":float(gamma[0]),
        "gamma_h":float(gamma[1]),
        "gamma_ah":float(gamma[2]),
        "lambda_hat":lam.tolist(),
        "mu_hat":mu.tolist(),
        "forcing_hat":{g:v.tolist() for g,v in forcing.items()},
        "forcing_correlation":corr,
        "lambda_correlation":lambda_corr,
        "group_mean_lambda":means,
        "process_sd":float(process_sd),
        "process_sd_initial":float(process_sd_initial),
        "loading_residual_sd":float(loading_sd),
        "iterations":int(iterations),
        "intervals":int(len(intervals)),
        "estimator":"hierarchical_interval_marginal",
    }


def fit_hierarchical_dataset(
    frames:dict[str,pd.DataFrame],
    observations:pd.DataFrame,
    truth:dict[str,dict]|None=None,
)->dict:
    records=observations.reset_index(drop=True).copy()
    design=prepare_observation_recovery_design(records)
    z=count_to_analysis_scale(
        pd.to_numeric(records["count"],errors="coerce").to_numpy()
    )
    observation=fit_observation_calibration_fast(z,design)

    species={}
    for sp in sorted(frames):
        frame=frames[sp].reset_index(drop=True)
        target=set(frame["unit_id"].astype(str))
        local=records[
            (
                records["species_id"].astype(str)
                +"|"
                +records["site_id"].astype(str)
            ).isin(target)
        ].copy()
        meta=(truth or {}).get(sp,{})
        species[sp]=fit_hierarchical_species(
            frame,
            local,
            delta_image=float(observation["delta_image"]),
            sigma1=float(observation["accuracy"]["1"]["sigma"]),
            sigma2plus=float(observation["accuracy"]["2-5"]["sigma"]),
            truth_forcing=meta.get("true_forcing"),
            true_lambda=meta.get("true_lambda"),
            iterations=12,
        )
    return {"observation":observation,"species":species}
