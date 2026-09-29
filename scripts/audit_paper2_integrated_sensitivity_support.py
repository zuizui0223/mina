#!/usr/bin/env python3
"""Outcome-blind support audit for Paper 2 observation-source sensitivities."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyreadr

from scripts.simulate_paper2_latent_factor_recovery import build_scale_frame
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
)

SPECIES=("ADPE","CHPE","GEPE")
WINDOW=(1980,2025)
MIN_TESTABLE_UNITS=20


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
    details={}
    for unit_id in process_frame["unit_id"].astype(str):
        local=records[records["unit_id"].astype(str).eq(unit_id)]
        seasons=sorted({
            int(v)
            for v in pd.to_numeric(local["season"],errors="coerce").dropna()
            if start<=int(v)<=end
        })
        n=len(seasons)
        span=(max(seasons)-min(seasons)) if seasons else 0
        has_first=any(first[0]<=v<=first[1] for v in seasons)
        has_last=any(last[0]<=v<=last[1] for v in seasons)
        keep=bool(n>=5 and span>=10 and has_first and has_last)
        if keep:
            supported.append(unit_id)
        details[unit_id]={
            "n_seasons":int(n),
            "span":int(span),
            "has_first_third":bool(has_first),
            "has_last_third":bool(has_last),
            "supported":keep,
        }

    retained=process_frame[
        process_frame["unit_id"].astype(str).isin(set(supported))
    ].copy()
    summary={
        "mode":mode,
        "candidate_units":int(len(process_frame)),
        "supported_units":int(len(retained)),
        "coverage_fraction":(
            float(len(retained)/len(process_frame)) if len(process_frame) else 0.0
        ),
        "classification":(
            "testable" if len(retained)>=MIN_TESTABLE_UNITS else "coverage_limited"
        ),
        "supported_unit_ids":sorted(supported),
        "details":details,
    }
    return retained.reset_index(drop=True),summary


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


def run_support_audit(
    forcing_result:dict,
    forcing_units:pd.DataFrame,
    breeding_options:pd.DataFrame,
    latent_recovery_result:dict,
    metadata:pd.DataFrame,
)->dict:
    selected={
        str(k):str(v)
        for k,v in latent_recovery_result["decision"][
            "selected_recovered_scale_by_species"
        ].items()
    }
    expected={"ADPE":"ccamlr","CHPE":"apbp_region","GEPE":"species_wide"}
    if selected!=expected:
        raise ValueError(f"forcing-scale drift: {selected} != {expected}")

    frames={
        sp:build_scale_frame(
            forcing_result,forcing_units,breeding_options,sp,selected[sp]
        )
        for sp in SPECIES
    }
    expected_n={"ADPE":40,"CHPE":33,"GEPE":29}
    observed_n={sp:int(len(frame)) for sp,frame in frames.items()}
    if observed_n!=expected_n:
        raise ValueError(f"primary frame drift: {observed_n} != {expected_n}")

    modes={}
    for mode in ("exclude_unknown","ground_only"):
        by_species={}
        for sp in SPECIES:
            _,summary=filter_process_support(frames[sp],metadata,mode=mode)
            by_species[sp]=summary
        modes[mode]={
            "by_species":by_species,
            "all_species_testable":bool(
                all(v["classification"]=="testable" for v in by_species.values())
            ),
        }

    return {
        "schema_version":1,
        "audit_id":"mina-paper2-integrated-sensitivity-support-v1",
        "primary_frame_units":observed_n,
        "forcing_scale_by_species":selected,
        "modes":modes,
        "decision":{
            "exclude_unknown_all_species_testable":modes["exclude_unknown"]["all_species_testable"],
            "ground_only_all_species_testable":modes["ground_only"]["all_species_testable"],
            "no_real_demographic_count_magnitudes_opened":True,
        },
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",required=True,type=Path)
    p.add_argument("--forcing-csv",required=True,type=Path)
    p.add_argument("--breeding-csv",required=True,type=Path)
    p.add_argument("--latent-recovery-json",required=True,type=Path)
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()

    forcing_result=json.loads(a.forcing_json.read_text(encoding="utf-8"))
    forcing_units=pd.read_csv(a.forcing_csv)
    breeding_options=pd.read_csv(a.breeding_csv)
    latent_result=json.loads(a.latent_recovery_json.read_text(encoding="utf-8"))
    obs=_load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    metadata=build_frozen_observation_metadata(obs)
    if len(metadata)!=2100:
        raise ValueError(f"observation metadata drift: {len(metadata)} != 2100")

    result=run_support_audit(
        forcing_result,forcing_units,breeding_options,latent_result,metadata
    )
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
