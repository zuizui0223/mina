"""Frozen cross-species Signy chinstrap breeding-patch concentration test."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.audit_signy_replication_support import read_official_zip, season_start
from mina.signy_concentration import (
    YEARS,
    ERROR_MODELS,
    SIMULATIONS,
    SEED,
    BATCH_SIZE,
    effective_number,
    slope,
    _draw_batch,
    _summary,
)

EXPECTED_CSV_SHA256="e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b"
PRIMARY_ROSTER=("C15","C16","C17","C18","C46","C47","C79","C80","C81")
YEAR_SET=set(int(x) for x in YEARS)


def _number(value: object)->float|None:
    if value is None or pd.isna(value):
        return None
    text=str(value).strip()
    if text in {"","NA","NaN","nan"}:
        return None
    try:
        out=float(text)
    except (TypeError,ValueError):
        return None
    return out if math.isfinite(out) else None


def stable_roster_matrix(frame: pd.DataFrame)->np.ndarray:
    required={"SEASON","COLONY","TOTAL_NUMBER_OF_PAIRS"}
    missing=sorted(required-set(frame.columns))
    if missing:
        raise ValueError(f"missing Signy chinstrap columns: {missing}")

    lookup={}
    for _,row in frame.iterrows():
        year=season_start(row["SEASON"])
        if year is None or int(year) not in YEAR_SET:
            continue
        colony=str(row["COLONY"]).strip()
        if colony not in PRIMARY_ROSTER:
            continue
        value=_number(row["TOTAL_NUMBER_OF_PAIRS"])
        if value is None:
            raise ValueError(f"missing frozen chinstrap pair count: {(year,colony)}")
        if value<0:
            raise ValueError(f"negative frozen chinstrap pair count: {(year,colony)}")
        key=(int(year),colony)
        if key in lookup:
            raise ValueError(f"duplicate frozen chinstrap row: {key}")
        lookup[key]=float(value)

    expected={(int(y),c) for y in YEARS for c in PRIMARY_ROSTER}
    absent=sorted(expected-set(lookup))
    if absent:
        raise ValueError(f"incomplete frozen chinstrap roster: {absent[:12]}")
    return np.asarray(
        [[lookup[(int(y),c)] for y in YEARS] for c in PRIMARY_ROSTER],
        dtype=float,
    )


def analyze_frame(
    frame: pd.DataFrame,
    *,
    simulations: int=SIMULATIONS,
    seed: int=SEED,
    batch_size: int=BATCH_SIZE,
)->dict[str,object]:
    matrix=stable_roster_matrix(frame)
    totals=np.sum(matrix,axis=0)
    if np.any(totals<=0):
        raise ValueError("zero total abundance in frozen chinstrap primary season")

    patch_eff=effective_number(matrix)
    total_slope=float(slope(totals))
    patch_slope=float(slope(patch_eff))
    decline=bool(total_slope<0)

    cumulative=np.sum(matrix,axis=1)
    shares=cumulative/float(np.sum(cumulative))
    latent=shares[:,None]*totals[None,:]

    rng=np.random.default_rng(seed)
    outputs={}
    for name,cv in ERROR_MODELS:
        chunks=[]
        completed=0
        while completed<simulations:
            n=min(batch_size,simulations-completed)
            batch=_draw_batch(latent,totals,n,cv,rng)
            chunks.append(np.asarray(slope(effective_number(batch)),dtype=float))
            completed+=n
        null=np.concatenate(chunks)
        extreme=int(np.sum(null<=patch_slope))
        outputs[name]={
            "multiplicative_cv":cv,
            "observed_slope":patch_slope,
            "simulated_slopes_le_observed":extreme,
            "one_sided_probability_le_observed":float((1+extreme)/(simulations+1)),
            "null_slope_summary":_summary(null),
        }

    supported=bool(
        decline and patch_slope<0 and all(
            float(outputs[name]["one_sided_probability_le_observed"])<=0.05
            for name,_ in ERROR_MODELS
        )
    )
    return {
        "schema_version":1,
        "analysis_id":"mina-signy-chinstrap-breeding-patch-concentration-v1",
        "contract_id":"mina-signy-chinstrap-breeding-patch-concentration-v1",
        "status":"prospectively_frozen_cross_species_replication",
        "primary_seasons":[int(x) for x in YEARS],
        "excluded_incomplete_seasons":[1997,2010],
        "primary_roster":list(PRIMARY_ROSTER),
        "decline_eligibility":{
            "first_total":float(totals[0]),
            "last_total":float(totals[-1]),
            "stable_roster_total_slope_per_year":total_slope,
            "passes":decline,
        },
        "observed":{
            "annual_effective_breeding_patch_number":{
                str(int(y)):float(v) for y,v in zip(YEARS,patch_eff)
            },
            "first_effective_breeding_patch_number":float(patch_eff[0]),
            "last_effective_breeding_patch_number":float(patch_eff[-1]),
            "fractional_change_first_to_last":float(patch_eff[-1]/patch_eff[0]-1.0),
            "effective_breeding_patch_slope_per_year":patch_slope,
        },
        "null_composition":{
            "pooled_shares":{c:float(v) for c,v in zip(PRIMARY_ROSTER,shares)}
        },
        "error_models":outputs,
        "decision":{"cross_species_concentration_replication_supported":supported},
        "interpretation_boundary":[
            "Effective breeding-patch number is a Hill-number distribution metric, not genetic Ne or Nb.",
            "The endpoint does not identify individual dispersal or a causal environmental mechanism.",
            "No alternate roster, season set, pooling, metric, CV or tail may rescue a failed result."
        ],
        "simulations_per_error_model":int(simulations),
        "seed":int(seed),
        "batch_size":int(batch_size),
    }


def analyze_official_zip(path:Path,**kwargs)->dict[str,object]:
    frame,source=read_official_zip(path)
    if str(source["selected_csv_sha256"])!=EXPECTED_CSV_SHA256:
        raise ValueError("official Signy chinstrap CSV hash drift")
    result=analyze_frame(frame,**kwargs)
    result["source"]={
        "doi":"10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9",
        "selected_csv":source["selected_csv"],
        "selected_csv_sha256":source["selected_csv_sha256"],
        "rows":int(len(frame)),
    }
    return result


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--official-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--simulations",type=int,default=SIMULATIONS)
    p.add_argument("--seed",type=int,default=SEED)
    p.add_argument("--batch-size",type=int,default=BATCH_SIZE)
    a=p.parse_args()
    result=analyze_official_zip(
        a.official_zip,simulations=a.simulations,seed=a.seed,batch_size=a.batch_size
    )
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
