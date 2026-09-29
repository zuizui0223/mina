#!/usr/bin/env python3
"""Integrated synthetic process-plus-observation recovery for Paper 2 Gate 2E-C."""
from __future__ import annotations

import numpy as np
import pandas as pd


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
