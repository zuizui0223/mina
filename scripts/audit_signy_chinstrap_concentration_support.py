#!/usr/bin/env python3
"""Outcome-blind support audit for cross-species Signy chinstrap concentration."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from scripts.audit_signy_replication_support import (
    infer_semantics,
    read_official_zip,
    reconstruct_season_start,
)

WINDOW_START=1996
WINDOW_END=2019


def numeric_available(value: object) -> bool:
    if value is None or pd.isna(value):
        return False
    text=str(value).strip()
    if text in {"","NA","NaN","nan"}:
        return False
    try:
        float(text)
    except (TypeError,ValueError):
        return False
    return True


def audit_frame(frame: pd.DataFrame) -> dict[str,object]:
    sem=infer_semantics(frame)
    if sem.get("colony_col") is None or sem.get("pairs_col") is None:
        return {
            "schema_version":1,
            "audit_id":"mina-signy-chinstrap-concentration-support-v1",
            "status":"schema_unresolved",
            "semantics":sem,
            "effect_computed":False,
        }

    x=frame.copy()
    x["_season"]=reconstruct_season_start(x,sem)
    x["_colony"]=x[sem["colony_col"]].astype(str).str.strip()
    x["_numeric"]=x[sem["pairs_col"]].map(numeric_available)
    x=x[x["_season"].between(WINDOW_START,WINDOW_END,inclusive="both")].copy()

    seasons=list(range(WINDOW_START,WINDOW_END+1))
    labels=sorted(
        c for c in x["_colony"].dropna().astype(str).unique().tolist()
        if c and c.lower() not in {"nan","none","na"}
    )
    support={}
    for c in labels:
        local=x[x["_colony"]==c]
        row_seasons=sorted(int(v) for v in local["_season"].dropna().unique())
        numeric_seasons=sorted(
            int(v) for v in local.loc[local["_numeric"],"_season"].dropna().unique()
        )
        support[c]={
            "first_row_season":min(row_seasons) if row_seasons else None,
            "last_row_season":max(row_seasons) if row_seasons else None,
            "n_row_seasons":len(row_seasons),
            "n_numeric_pair_seasons":len(numeric_seasons),
            "row_seasons":row_seasons,
            "numeric_pair_seasons":numeric_seasons,
        }

    first_third_end=WINDOW_START+7
    last_third_start=WINDOW_END-7
    candidates=[]
    for c,info in support.items():
        rows=set(info["row_seasons"])
        nums=set(info["numeric_pair_seasons"])
        spans=(
            any(s<=first_third_end for s in rows)
            and any(s>=last_third_start for s in rows)
        )
        if spans and len(nums)>=12:
            candidates.append(c)

    season_support={}
    complete=[]
    for s in seasons:
        numeric=set(
            str(r["_colony"])
            for _,r in x[(x["_season"]==s)&x["_numeric"]].iterrows()
        )
        season_support[str(s)]={
            "numeric_candidate_units":sorted(set(candidates)&numeric),
            "n_numeric_candidate_units":len(set(candidates)&numeric),
        }
        if candidates and set(candidates).issubset(numeric):
            complete.append(s)

    return {
        "schema_version":1,
        "audit_id":"mina-signy-chinstrap-concentration-support-v1",
        "status":"support_audited",
        "window":[WINDOW_START,WINDOW_END],
        "effect_computed":False,
        "numeric_pair_magnitudes_recorded_or_summarized":False,
        "numeric_parseability_only":True,
        "semantics":sem,
        "literal_colony_labels":labels,
        "label_support":support,
        "structural_candidate_rule":(
            "literal colony label spans both first and last thirds of 1996-2019 "
            "and has numerically parseable pair counts in >=12 seasons"
        ),
        "structural_candidates":sorted(candidates),
        "complete_candidate_seasons":complete,
        "n_complete_candidate_seasons":len(complete),
        "season_support":season_support,
        "support_gate":{
            "required_candidate_units":4,
            "required_complete_seasons":12,
            "passes":bool(len(candidates)>=4 and len(complete)>=12),
        },
        "boundary":[
            "No breeding-pair magnitude is recorded, summarized, compared, transformed or modeled.",
            "No total-abundance trend, effective-patch number, concentration slope or p-value is computed.",
            "No label pooling or reconciliation is introduced after effect inspection."
        ],
    }


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--official-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    frame,source=read_official_zip(a.official_zip)
    result=audit_frame(frame)
    result["source"]={
        "doi":"10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9",
        "selected_csv":source["selected_csv"],
        "selected_csv_sha256":source["selected_csv_sha256"],
        "rows":int(len(frame)),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
