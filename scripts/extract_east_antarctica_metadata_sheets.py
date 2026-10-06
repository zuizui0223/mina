#!/usr/bin/env python3
"""Extract documentation sheets only from AADC xlsx files.

Outcome-blind by construction: sheets whose names contain metadata/readme are
read; event/data sheets are never iterated.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import openpyxl

def extract_dir(path: Path):
    out=[]
    for f in sorted(path.rglob("*.xlsx")):
        wb=openpyxl.load_workbook(f,read_only=True,data_only=True)
        fs={"file":f.name,"documentation_sheets":[]}
        for ws in wb.worksheets:
            low=ws.title.lower()
            if "metadata" not in low and "readme" not in low:
                continue
            rows=[]
            for row in ws.iter_rows(values_only=True):
                vals=[None if v is None else str(v) for v in row]
                while vals and vals[-1] is None: vals.pop()
                if any(v not in (None,"") for v in vals): rows.append(vals)
            fs["documentation_sheets"].append({"sheet":ws.title,"rows":rows})
        out.append(fs)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result={"schema_version":1,"status":"documentation_sheets_only",
            "event_data_sheets_read":False,"files":extract_dir(a.source_dir)}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
