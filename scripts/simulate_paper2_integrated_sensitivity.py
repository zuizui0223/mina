#!/usr/bin/env python3
"""Outcome-blind support filters for integrated observation-source sensitivities."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr

from scripts.simulate_paper2_latent_factor_recovery import build_scale_frame
from scripts.simulate_paper2_observation_recovery import build_frozen_observation_metadata


WINDOW=(1980,2025)


def _thirds(start:int,end:int):
    width=end-start+1
    cut1=start+(width//3)-1
    cut2=start+(2*width//3)-1
    return (start,cut1),(cut1+1,cut2),(cut2+1,end)


def filter_process_support(
    process_frame:pd.DataFrame,
    metadata:pd.DataFrame,
    *,
    mode:str,
)->tuple[pd.DataFrame,dict]:
    """Retain process units with enough filtered seasons for one sensitivity."""
    if mode not in {"exclude_unknown","ground_only"}:
        raise ValueError(f"unsupported sensitivity mode: {mode}")
    required_frame={"unit_id","site_id","species_id"}
    required_meta={"site_id","species_id","season","vantage_family","vantage_raw"}
    missing=required_frame-set(process_frame.columns)
    if missing:
        raise ValueError(f"process frame missing: {sorted(missing)}")
    missing=required_meta-set(metadata.columns)
    if missing:
        raise ValueError(f"metadata missing: {sorted(missing)}")

    records=metadata.copy()
    records["unit_id"]=(
        records["species_id"].astype(str)
        +"|"
        +records["site_id"].astype(str)
    )
    if mode=="exclude_unknown":
        records=records[
            records["vantage_family"].astype(str).ne("unknown")
        ].copy()
    else:
        records=records[
            records["vantage_raw"].astype(str).eq("ground")
        ].copy()

    start,end=WINDOW
    first,_,last=_thirds(start,end)
    supported=[]
    detail={}
    for unit_id in process_frame["unit_id"].astype(str):
        local=records[records["unit_id"].astype(str).eq(unit_id)]
        seasons=sorted({
            int(v) for v in pd.to_numeric(local["season"],errors="coerce").dropna()
            if start<=int(v)<=end
        })
        n=len(seasons)
        span=(max(seasons)-min(seasons)) if seasons else 0
        has_first=any(first[0]<=s<=first[1] for s in seasons)
        has_last=any(last[0]<=s<=last[1] for s in seasons)
        keep=bool(n>=5 and span>=10 and has_first and has_last)
        if keep:
            supported.append(unit_id)
        detail[unit_id]={
            "n_seasons":n,
            "span":int(span),
            "has_first_third":bool(has_first),
            "has_last_third":bool(has_last),
            "supported":keep,
        }

    out=process_frame[
        process_frame["unit_id"].astype(str).isin(set(supported))
    ].copy()
    return out.reset_index(drop=True),{
        "mode":mode,
        "candidate_units":int(len(process_frame)),
        "supported_units":int(len(out)),
        "coverage_fraction":float(len(out)/len(process_frame)) if len(process_frame) else 0.0,
        "supported_unit_ids":sorted(supported),
        "detail":detail,
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


def audit_sensitivity_support(
    forcing_result:dict,
    forcing_units:pd.DataFrame,
    breeding_options:pd.DataFrame,
    latent_result:dict,
    metadata:pd.DataFrame,
)->dict:
    scales={
        str(k):str(v)
        for k,v in latent_result["decision"][
            "selected_recovered_scale_by_species"
        ].items()
    }
    expected={"ADPE":"ccamlr","CHPE":"apbp_region","GEPE":"species_wide"}
    if scales!=expected:
        raise ValueError(f"scale drift: {scales} != {expected}")

    frames={
        sp:build_scale_frame(
            forcing_result,forcing_units,breeding_options,sp,scales[sp]
        )
        for sp in ("ADPE","CHPE","GEPE")
    }
    result={}
    for mode in ("exclude_unknown","ground_only"):
        result[mode]={}
        for sp,frame in frames.items():
            supported,meta=filter_process_support(frame,metadata,mode=mode)
            result[mode][sp]={
                "candidate_units":int(len(frame)),
                "supported_units":int(len(supported)),
                "coverage_fraction":float(
                    len(supported)/len(frame) if len(frame) else 0.0
                ),
                "recovery_testable":bool(len(supported)>=20),
                "supported_unit_ids":meta["supported_unit_ids"],
                "dropped_units":sorted(
                    set(frame["unit_id"].astype(str))
                    -set(supported["unit_id"].astype(str))
                ),
            }
    return {
        "schema_version":1,
        "audit_id":"mina-paper2-integrated-sensitivity-support-v1",
        "primary_scale_by_species":scales,
        "min_supported_units_per_species":20,
        "modes":result,
        "no_real_count_magnitudes_opened":True,
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",required=True,type=Path)
    p.add_argument("--forcing-csv",required=True,type=Path)
    p.add_argument("--breeding-csv",required=True,type=Path)
    p.add_argument("--latent-json",required=True,type=Path)
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()

    forcing_result=json.loads(a.forcing_json.read_text(encoding="utf-8"))
    forcing_units=pd.read_csv(a.forcing_csv)
    breeding_options=pd.read_csv(a.breeding_csv)
    latent_result=json.loads(a.latent_json.read_text(encoding="utf-8"))
    obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    metadata=build_frozen_observation_metadata(obs)
    result=audit_sensitivity_support(
        forcing_result,forcing_units,breeding_options,latent_result,metadata
    )
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
