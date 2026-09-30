#!/usr/bin/env python3
"""Outcome-blind support audit for the frozen Signy replication."""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import zipfile
from pathlib import Path

import pandas as pd

MIRROR_URL="https://polarbytes.umk.edu.my/adelie"
START_SEASON="1996-1997"
END_SEASON="2019-2020"


def _norm(x:str)->str:
    return re.sub(r"[^a-z0-9]+"," ",str(x).strip().lower()).strip()


def resolve_columns(frame:pd.DataFrame)->dict[str,str]:
    cols={_norm(c):str(c) for c in frame.columns}
    aliases={
        "colony":["colony","colony id","colony code","site","season"],
        "season":["breeding season","season year","year","season"],
        "pairs":["total number of nests","breeding pairs","pairs","total nests"],
        "chicks":["total number of chicks","chicks","fledglings","chicks expected to fledge"],
        "comments":["comments","comment"],
    }
    out={}
    for role,names in aliases.items():
        hits=[]
        for name in names:
            key=_norm(name)
            if key in cols:
                hits.append(cols[key])
        # "season" is ambiguous on the PolarBytes mirror: it may actually hold
        # colony labels. Resolve semantic roles later from values.
        out[role]=hits[0] if hits else None
    return out


def season_start(season:str)->int|None:
    s=str(season).strip()
    m=re.fullmatch(r"(\d{4})\s*[-/]\s*(\d{2,4})",s)
    if not m:
        return None
    return int(m.group(1))


def infer_semantics(frame:pd.DataFrame)->dict:
    """Resolve colony/season roles from names plus value patterns without outcomes."""
    columns=[str(c) for c in frame.columns]
    resolved=resolve_columns(frame)

    # Candidate season columns: majority of nonmissing values parse as YYYY-YYYY.
    season_scores={}
    colony_scores={}
    for c in columns:
        vals=frame[c].dropna().astype(str).str.strip()
        if len(vals)==0:
            continue
        parse=sum(season_start(v) is not None for v in vals)
        season_scores[c]=parse/len(vals)
        colony_scores[c]=sum(bool(re.fullmatch(r"A\d+(?:\s*\+\s*A\d+)?",v)) for v in vals)/len(vals)

    season_col=max(season_scores,key=season_scores.get) if season_scores else None
    colony_col=max(colony_scores,key=colony_scores.get) if colony_scores else None

    if season_col is None or season_scores.get(season_col,0)<0.5:
        season_col=None
    if colony_col is None or colony_scores.get(colony_col,0)<0.5:
        colony_col=None

    # Numeric count candidates are identified by header semantics only; support
    # audit never summarizes their values.
    pairs_col=None
    chicks_col=None
    nest_date_col=None
    chick_date_col=None
    for c in columns:
        n=_norm(c)
        if pairs_col is None and (
            "total number of nests" in n
            or "total number of pairs" in n
            or n in {"breeding pairs","pairs","total nests"}
        ):
            pairs_col=c
        if chicks_col is None and ("total number of chicks" in n or n in {"chicks","fledglings","chicks expected to fledge"}):
            chicks_col=c
        if nest_date_col is None and "date of nest count" in n:
            nest_date_col=c
        if chick_date_col is None and "date chick count" in n:
            chick_date_col=c

    comments_col=None
    for c in columns:
        if _norm(c) in {"comments","comment"}:
            comments_col=c
            break

    return {
        "columns":columns,
        "season_col":season_col,
        "colony_col":colony_col,
        "pairs_col":pairs_col,
        "chicks_col":chicks_col,
        "nest_date_col":nest_date_col,
        "chick_date_col":chick_date_col,
        "comments_col":comments_col,
        "season_scores":season_scores,
        "colony_scores":colony_scores,
    }




def season_from_date(value)->int|None:
    dt=pd.to_datetime(value,dayfirst=True,errors="coerce")
    if pd.isna(dt):
        return None
    year=int(dt.year)
    month=int(dt.month)
    return year if month>=7 else year-1


def reconstruct_season_start(frame:pd.DataFrame,sem:dict)->pd.Series:
    if sem["season_col"] is not None:
        return frame[sem["season_col"]].map(season_start)
    candidates=[]
    for key in ("nest_date_col","chick_date_col"):
        col=sem.get(key)
        if col is not None:
            candidates.append(frame[col].map(season_from_date))
    if not candidates:
        return pd.Series([None]*len(frame),index=frame.index,dtype="object")
    out=candidates[0].copy()
    for other in candidates[1:]:
        mismatch=out.notna() & other.notna() & out.ne(other)
        if bool(mismatch.any()):
            bad=frame.loc[mismatch].index.tolist()
            raise ValueError(f"nest/chick dates imply conflicting seasons at rows {bad[:10]}")
        out=out.where(out.notna(),other)
    return out

def audit_table(frame:pd.DataFrame)->dict:
    sem=infer_semantics(frame)
    required=("colony_col","pairs_col","chicks_col")
    missing=[k for k in required if sem[k] is None]
    date_support=sem.get("nest_date_col") is not None or sem.get("chick_date_col") is not None
    if sem["season_col"] is None and not date_support:
        missing.append("season_or_date_metadata")
    if missing:
        return {
            "status":"schema_unresolved",
            "missing_roles":missing,
            "semantics":sem,
            "row_count":int(len(frame)),
            "effect_computed":False,
        }

    colony_col=sem["colony_col"]
    pairs_col=sem["pairs_col"]; chicks_col=sem["chicks_col"]
    x=frame.copy()
    x["_season_start"]=reconstruct_season_start(x,sem)
    x["_colony"]=x[colony_col].astype(str).str.strip()
    x["_literal_atomic"]=~x["_colony"].str.contains(r"\+",regex=True)
    x["_pairs_present"]=x[pairs_col].notna()
    x["_chicks_present"]=x[chicks_col].notna()
    x=x[x["_season_start"].between(1996,2019,inclusive="both")].copy()

    seasons=sorted(int(v) for v in x["_season_start"].dropna().unique())
    colonies=sorted(x["_colony"].dropna().unique().tolist())

    # Support only: a performance row requires pair + chick fields in t.
    perf=x[x["_pairs_present"] & x["_chicks_present"]].copy()

    # Lag-2 row requires S_t plus pair counts for same literal colony at t+1,t+2.
    pair_keys=set(
        (int(r["_season_start"]),str(r["_colony"]))
        for _,r in x[x["_pairs_present"]].iterrows()
    )
    lag2=[]
    for _,r in perf.iterrows():
        t=int(r["_season_start"]); c=str(r["_colony"])
        if (t+1,c) in pair_keys and (t+2,c) in pair_keys:
            lag2.append((t,c))

    eligible_seasons=sorted({t for t,_ in lag2})
    eligible_colonies=sorted({c for _,c in lag2})

    atomic_lag2=[(t,c) for t,c in lag2 if "+" not in c]
    result={
        "status":"support_audited",
        "row_count":int(len(frame)),
        "primary_window_rows":int(len(x)),
        "semantics":sem,
        "primary_window":{
            "start":START_SEASON,
            "end":END_SEASON,
            "seasons_present":seasons,
            "n_seasons_present":len(seasons),
            "literal_colonies":colonies,
            "n_literal_colonies":len(colonies),
        },
        "nonmissing_support":{
            "pair_rows":int(x["_pairs_present"].sum()),
            "chick_rows":int(x["_chicks_present"].sum()),
            "performance_rows":int(len(perf)),
            "lag2_rows":int(len(lag2)),
            "lag2_predictor_seasons":eligible_seasons,
            "n_lag2_predictor_seasons":len(eligible_seasons),
            "lag2_colonies":eligible_colonies,
            "n_lag2_colonies":len(eligible_colonies),
            "atomic_only_lag2_rows":int(len(atomic_lag2)),
            "pooled_label_enters_primary":bool(any("+" in c for _,c in lag2)),
        },
        "gate":{
            "required_primary_seasons":8,
            "required_primary_colonies":4,
            "required_lag2_rows":40,
            "passes":bool(
                len(eligible_seasons)>=8
                and len(eligible_colonies)>=4
                and len(lag2)>=40
            ),
        },
        "effect_computed":False,
    }
    return result




def read_official_zip(path:Path)->tuple[pd.DataFrame,dict]:
    """Select the breeding-success CSV from the official RAMADDA zip tree."""
    with zipfile.ZipFile(path) as z:
        csvs=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if not csvs:
            raise ValueError("official zip contains no CSV files")
        candidates=[]
        for name in csvs:
            raw=z.read(name)
            text=None
            used_encoding=None
            last=None
            for enc in ("utf-8-sig","utf-8","latin-1"):
                try:
                    text=raw.decode(enc)
                    used_encoding=enc
                    break
                except Exception as exc:
                    last=exc
            if text is None:
                raise ValueError(f"cannot decode {name}: {last}")

            rows=list(csv.reader(io.StringIO(text)))
            if not rows:
                raise ValueError(f"empty CSV: {name}")
            header=[str(x).strip() for x in rows[0]]
            width=len(header)
            repaired_overflow=0
            padded_short=0
            fixed=[]
            for line_no,row in enumerate(rows[1:],start=2):
                if len(row)==0 or all(str(v).strip()=="" for v in row):
                    continue
                if len(row)>width:
                    # Official files occasionally contain unquoted commas in
                    # the final free-text Comments field. Preserve the first
                    # width-1 fields exactly and join only the overflow back
                    # into the final field.
                    row=row[:width-1]+[",".join(row[width-1:])]
                    repaired_overflow+=1
                elif len(row)<width:
                    row=row+[""]*(width-len(row))
                    padded_short+=1
                if len(row)!=width:
                    raise ValueError(
                        f"cannot normalize {name} line {line_no}: "
                        f"{len(row)} fields for {width}-column header"
                    )
                fixed.append(row)
            frame=pd.DataFrame(fixed,columns=header)
            headers=" ".join(_norm(x) for x in frame.columns)
            score=(
                4*("chick" in headers)
                +4*(("nest" in headers) or ("pair" in headers))
                +2*("season" in headers)
                +len(frame)/10000
            )
            candidates.append(
                (score,name,frame,len(raw),used_encoding,repaired_overflow,padded_short)
            )
        candidates.sort(key=lambda x:x[0],reverse=True)
        score,name,frame,size,encoding,repaired_overflow,padded_short=candidates[0]
        manifest=[
            {
                "name":n,
                "rows":int(len(df)),
                "columns":[str(x) for x in df.columns],
                "bytes":int(sz),
                "encoding":enc,
                "overflow_comment_rows_repaired":int(over),
                "short_rows_padded":int(short),
                "selection_score":float(sc),
            }
            for sc,n,df,sz,enc,over,short in candidates
        ]
        return frame,{
            "selected_csv":name,
            "selected_score":float(score),
            "selected_encoding":encoding,
            "selected_overflow_comment_rows_repaired":int(repaired_overflow),
            "selected_short_rows_padded":int(padded_short),
            "zip_members":z.namelist(),
            "csv_manifest":manifest,
        }

def fetch_mirror()->pd.DataFrame:
    tables=pd.read_html(MIRROR_URL)
    if not tables:
        raise RuntimeError("no HTML tables found")
    # Select table containing the largest overlap with expected semantic headers.
    def score(df):
        names=" ".join(_norm(c) for c in df.columns)
        return (
            ("chick" in names)*3
            +("nest" in names)*3
            +len(df)/1000
        )
    return max(tables,key=score)


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--official-zip",type=Path)
    a=p.parse_args()
    if a.official_zip is not None:
        frame,zip_meta=read_official_zip(a.official_zip)
        result=audit_table(frame)
        result["source"]={
            "role":"official NERC/BAS RAMADDA zip-tree support audit",
            "official_doi":"10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
            "ramadda_entryid":"daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
            "zip_metadata":zip_meta,
            "effect_execution_requires_official_or_byte_verified_source":False,
        }
    else:
        frame=fetch_mirror()
        result=audit_table(frame)
        result["source"]={
            "role":"schema/support mirror only",
            "url":MIRROR_URL,
            "official_doi":"10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
            "effect_execution_requires_official_or_byte_verified_source":True,
        }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result.get("status") else 1


if __name__=="__main__":
    raise SystemExit(main())
