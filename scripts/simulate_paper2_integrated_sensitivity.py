#!/usr/bin/env python3
"""Outcome-blind support filters for integrated observation-source sensitivities."""
from __future__ import annotations

import pandas as pd


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
