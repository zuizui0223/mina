#!/usr/bin/env python3
"""Outcome-blind schema audit for East Antarctic penguin expansion sources.

This script may inspect archive structure, table/sheet names, headers and row
counts. It must not summarize biological values or occupancy-state frequencies.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

try:
    import openpyxl
except ImportError:
    openpyxl = None


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def csv_schema(raw: bytes, name: str) -> dict:
    text=None
    encoding=None
    for enc in ("utf-8-sig","utf-8","latin-1"):
        try:
            text=raw.decode(enc)
            encoding=enc
            break
        except UnicodeDecodeError:
            pass
    if text is None:
        return {"name":name,"kind":"csv","readable":False}
    rows=csv.reader(io.StringIO(text))
    try:
        header=next(rows)
    except StopIteration:
        header=[]
        n=0
    else:
        n=sum(1 for _ in rows)
    return {
        "name":name,
        "kind":"csv",
        "encoding":encoding,
        "columns":[str(x).strip() for x in header],
        "data_rows":int(n),
    }


def xlsx_schema(raw: bytes, name: str) -> dict:
    if openpyxl is None:
        return {"name":name,"kind":"xlsx","readable":False,"reason":"openpyxl_missing"}
    wb=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    sheets=[]
    for ws in wb.worksheets:
        it=ws.iter_rows(values_only=True)
        try:
            first=next(it)
        except StopIteration:
            first=()
        sheets.append({
            "sheet":ws.title,
            "columns":[None if v is None else str(v).strip() for v in first],
            "max_row":int(ws.max_row or 0),
            "max_column":int(ws.max_column or 0),
        })
    return {"name":name,"kind":"xlsx","sheets":sheets}


def inspect(path: Path) -> dict:
    raw=path.read_bytes()
    out={
        "path":str(path),
        "bytes":len(raw),
        "sha256":sha256(path),
        "prefix_hex":raw[:16].hex(),
    }
    if zipfile.is_zipfile(io.BytesIO(raw)):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names=z.namelist()
            # Distinguish a top-level XLSX from a bundle ZIP.
            if "[Content_Types].xml" in names and any(n.startswith("xl/") for n in names):
                out["container"]="xlsx"
                out["tables"]=[xlsx_schema(raw,path.name)]
                return out
            tables=[]
            for name in names:
                low=name.lower()
                if low.endswith(".csv"):
                    tables.append(csv_schema(z.read(name),name))
                elif low.endswith(".xlsx"):
                    tables.append(xlsx_schema(z.read(name),name))
            out["container"]="zip"
            out["members"]=names
            out["tables"]=tables
            return out
    out["container"]="opaque"
    return out


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--occupancy-2025",required=True,type=Path)
    p.add_argument("--occupancy-2016",required=True,type=Path)
    p.add_argument("--plos-s1",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result={
        "schema_version":1,
        "analysis_id":"east-antarctica-expansion-schema-audit-v1",
        "status":"outcome_blind_schema_only",
        "sources":{
            "occupancy_2025":inspect(a.occupancy_2025),
            "occupancy_2016":inspect(a.occupancy_2016),
            "plos_s1":inspect(a.plos_s1),
        },
        "biological_values_summarized":False,
        "occupancy_state_frequencies_computed":False,
        "colonization_events_counted":False,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
