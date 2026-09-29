#!/usr/bin/env python3
"""First frozen real-outcome fit for Paper 2.

This script is the first permitted code path that reads MAPPPD count magnitudes.
Estimator definitions are imported unchanged from the pre-outcome V3 recovery.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from scripts.audit_paper2_integrated_sensitivity_support import filter_process_support
from scripts.simulate_paper2_integrated_recovery import count_to_analysis_scale
from scripts.simulate_paper2_observation_recovery import (
    SPECIES, WINDOW, EXPECTED_GATE0, EXPECTED_BRIDGED,
    _thirds, _vantage_family, _accuracy_group,
    build_frozen_observation_metadata,
    prepare_observation_recovery_design,
    fit_observation_calibration_fast,
)
from scripts.simulate_paper2_spatial_adjusted_v3 import (
    build_v3_frames,
    fit_spatial_species,
)

EXPECTED_RECORDS=2100
EXPECTED_PRIMARY={"ADPE":41,"CHPE":34,"GEPE":29}
EXPECTED_EXCLUDE_UNKNOWN={"ADPE":40,"CHPE":30,"GEPE":28}
EXPECTED_GROUND={"ADPE":14,"CHPE":26,"GEPE":23}


def _load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        return x[expected]
    if len(x)==1:
        return next(iter(x.values()))
    raise ValueError(expected)


def build_frozen_real_records(obs:pd.DataFrame)->pd.DataFrame:
    """Reconstruct exactly the frozen 107-unit cohort while retaining count."""
    required={"site_id","species_id","type","count","year","season","vantage","accuracy"}
    missing=required-set(obs.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    nest=obs[
        obs["species_id"].isin(SPECIES)
        & obs["type"].eq("nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest["season"]=pd.to_numeric(nest["season"],errors="coerce")
    nest["count"]=pd.to_numeric(nest["count"],errors="raise")

    gate0=[]
    for (site,species),local in nest.dropna(subset=["year"]).groupby(
        ["site_id","species_id"]
    ):
        years=sorted({int(v) for v in local["year"]})
        if len(years)>=5 and max(years)-min(years)>=10:
            gate0.append((str(site),str(species)))
    gate0_by_species={
        sp:sum(s==sp for _,s in gate0) for sp in SPECIES
    }
    if gate0_by_species!=EXPECTED_GATE0:
        raise ValueError(f"Gate0 drift: {gate0_by_species} != {EXPECTED_GATE0}")

    grouped={
        (str(site),str(species)):local
        for (site,species),local in nest.groupby(["site_id","species_id"])
    }
    start,end=WINDOW
    first,_,last=_thirds(start,end)
    bridged=[]
    for site,species in gate0:
        local=grouped[(site,species)]
        seasons=sorted({
            int(v) for v in local["season"].dropna()
            if start<=int(v)<=end
        })
        if not seasons:
            continue
        span=max(seasons)-min(seasons)
        if (
            len(seasons)>=5 and span>=10
            and any(first[0]<=v<=first[1] for v in seasons)
            and any(last[0]<=v<=last[1] for v in seasons)
        ):
            bridged.append((site,species))
    bridged_by_species={
        sp:sum(s==sp for _,s in bridged) for sp in SPECIES
    }
    if bridged_by_species!=EXPECTED_BRIDGED:
        raise ValueError(
            f"bridged drift: {bridged_by_species} != {EXPECTED_BRIDGED}"
        )

    keys=set(bridged)
    mask=nest.apply(
        lambda row:(str(row["site_id"]),str(row["species_id"])) in keys,
        axis=1,
    )
    cohort=nest[
        mask & nest["season"].between(start,end,inclusive="both")
    ].copy()
    out=pd.DataFrame({
        "site_id":cohort["site_id"].astype(str),
        "species_id":cohort["species_id"].astype(str),
        "season":cohort["season"].astype(int),
        "vantage_family":cohort["vantage"].map(_vantage_family),
        "vantage_raw":cohort["vantage"].map(
            lambda v:"missing" if pd.isna(v)
            else str(v).strip().lower().replace("_"," ")
        ),
        "accuracy_group":cohort["accuracy"].map(_accuracy_group),
        "count":cohort["count"].astype(float),
    })
    out["group_id"]=(
        out["site_id"]+"|"+out["species_id"]+"|"+out["season"].astype(str)
    )
    out=out.sort_values(
        ["species_id","site_id","season","vantage_family","accuracy_group","count"]
    ).reset_index(drop=True)
    if len(out)!=EXPECTED_RECORDS:
        raise ValueError(f"record drift: {len(out)} != {EXPECTED_RECORDS}")

    # Independently reconstruct count-blind metadata and assert the same cohort.
    meta=build_frozen_observation_metadata(obs).sort_values(
        ["species_id","site_id","season","vantage_family","accuracy_group"]
    ).reset_index(drop=True)
    left=out.drop(columns=["count"]).sort_values(
        ["species_id","site_id","season","vantage_family","accuracy_group"]
    ).reset_index(drop=True)
    if not left.equals(meta):
        raise ValueError("real-record cohort does not match frozen metadata cohort")
    return out


def calibrate_observation(records:pd.DataFrame)->dict:
    design=prepare_observation_recovery_design(records)
    z=count_to_analysis_scale(records["count"].to_numpy(dtype=float))
    return fit_observation_calibration_fast(z,design)


def _filter_records(records:pd.DataFrame,unit_ids:set[str],mode:str)->pd.DataFrame:
    x=records.copy()
    x["unit_id"]=x["species_id"].astype(str)+"|"+x["site_id"].astype(str)
    x=x[x["unit_id"].isin(unit_ids)].copy()
    if mode=="exclude_unknown":
        return x[x["vantage_family"].astype(str).ne("unknown")].copy()
    if mode=="ground_only":
        return x[x["vantage_raw"].astype(str).eq("ground")].copy()
    raise ValueError(mode)


def fit_frame(frame:pd.DataFrame,records:pd.DataFrame,cal:dict)->dict:
    fit=fit_spatial_species(
        frame.reset_index(drop=True),
        records,
        delta_image=float(cal["delta_image"]),
        sigma1=float(cal["accuracy"]["1"]["sigma"]),
        sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
        truth_forcing=None,
        true_lambda=None,
    )
    ga=float(fit["gamma_a"])
    gh=float(fit["gamma_h"])
    gah=float(fit["gamma_ah"])
    return {
        "gamma_a":ga,
        "gamma_h":gh,
        "gamma_ah":gah,
        "low_area_H_slope":gh-gah,
        "high_area_H_slope":gh+gah,
        "crossover_classification":bool(
            gah<0 and (gh-gah)>=0 and (gh+gah)<0
        ),
        "process_sd":float(fit["process_sd"]),
        "loading_residual_sd":float(fit["loading_residual_sd"]),
        "block_intercepts":fit["block_intercepts"],
        "block_mean_lambda":fit["block_mean_lambda"],
        "n_units":int(len(frame)),
        "n_records":int(len(records)),
    }


def run_real_fit(
    forcing_result:dict,
    forcing_units:pd.DataFrame,
    breeding_options:pd.DataFrame,
    records:pd.DataFrame,
)->dict:
    frames=build_v3_frames(
        forcing_result,forcing_units,breeding_options
    )
    got={sp:int(len(frames[sp])) for sp in SPECIES}
    if got!=EXPECTED_PRIMARY:
        raise ValueError(f"primary frame drift: {got} != {EXPECTED_PRIMARY}")

    cal=calibrate_observation(records)

    primary={}
    for sp in SPECIES:
        ids=set(frames[sp]["unit_id"].astype(str))
        local=_filter_records(records,ids,"exclude_unknown")
        # Primary uses all records, not the exclusion filter.
        all_local=records.copy()
        all_local["unit_id"]=(
            all_local["species_id"].astype(str)
            +"|"+all_local["site_id"].astype(str)
        )
        all_local=all_local[all_local["unit_id"].isin(ids)].copy()
        primary[sp]=fit_frame(frames[sp],all_local,cal)

    primary_gamma=np.asarray(
        [primary[sp]["gamma_ah"] for sp in SPECIES],dtype=float
    )
    primary_summary={
        "median_gamma_ah":float(np.median(primary_gamma)),
        "negative_species":int(np.sum(primary_gamma<0)),
        "all_species_negative":bool(np.all(primary_gamma<0)),
        "species_with_crossover_classification":[
            sp for sp in SPECIES
            if primary[sp]["crossover_classification"]
        ],
    }

    sensitivities={}
    for mode,expected in (
        ("exclude_unknown",EXPECTED_EXCLUDE_UNKNOWN),
        ("ground_only",EXPECTED_GROUND),
    ):
        species_fit={}
        support={}
        for sp in SPECIES:
            kept,meta=filter_process_support(
                frames[sp],
                records.drop(columns=["count"]),
                mode=mode,
            )
            support[sp]=int(len(kept))
            if len(kept)!=expected[sp]:
                raise ValueError(
                    f"{mode} support drift {sp}: {len(kept)} != {expected[sp]}"
                )
            if mode=="ground_only" and sp=="ADPE":
                continue
            ids=set(kept["unit_id"].astype(str))
            local=_filter_records(records,ids,mode)
            species_fit[sp]=fit_frame(kept,local,cal)
        vals=np.asarray(
            [species_fit[sp]["gamma_ah"] for sp in sorted(species_fit)],
            dtype=float,
        )
        sensitivities[mode]={
            "support_units":support,
            "species":species_fit,
            "aggregate_median_gamma_ah":float(np.median(vals)),
            "negative_species":int(np.sum(vals<0)),
        }

    return {
        "schema_version":1,
        "analysis_id":"mina-paper2-first-real-v3-fit",
        "observation_calibration":{
            "delta_image":float(cal["delta_image"]),
            "image_multiplicative_factor":float(np.exp(cal["delta_image"])),
            "sigma_accuracy_1":float(cal["accuracy"]["1"]["sigma"]),
            "sigma_accuracy_2_5":float(cal["accuracy"]["2-5"]["sigma"]),
        },
        "primary":primary,
        "primary_cross_species":primary_summary,
        "source_sensitivities":sensitivities,
        "inference_status":"point_estimates_only; frozen 9999-permutation inference pending",
        "process_variance_interpretation_allowed":False,
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--unlock-contract",required=True,type=Path)
    p.add_argument("--forcing-json",required=True,type=Path)
    p.add_argument("--forcing-csv",required=True,type=Path)
    p.add_argument("--breeding-csv",required=True,type=Path)
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()

    lock=json.loads(a.unlock_contract.read_text(encoding="utf-8"))
    if lock.get("status")!="UNLOCKED_FOR_FROZEN_EXECUTION":
        raise SystemExit("real outcomes remain locked")

    fr=json.loads(a.forcing_json.read_text(encoding="utf-8"))
    fu=pd.read_csv(a.forcing_csv)
    br=pd.read_csv(a.breeding_csv)
    obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    records=build_frozen_real_records(obs)
    result=run_real_fit(fr,fu,br,records)
    result["provenance"]={
        "mapppdr_commit":"88c73a507e0921b2541c218c71eaf16721bc6502",
        "unlock_status":lock["status"],
        "real_count_magnitudes_opened":True,
        "frozen_records":EXPECTED_RECORDS,
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
