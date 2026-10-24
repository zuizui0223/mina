#!/usr/bin/env python3
"""V21: original BAS Bird Island and Maiviken source schemas, NO count values."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlparse
import requests

SOURCES={
  "bird_island_v1":{
      "doi":"10.5285/c8d5a7a4-e19b-497f-b7ae-56f9a2b15a56",
      "url":"https://ramadda.data.bas.ac.uk/repository/entry/get/Gentoo_BI_nest_chick_counts.csv?entryid=synth%3Ac8d5a7a4-e19b-497f-b7ae-56f9a2b15a56%3AL0dlbnRvb19CSV9uZXN0X2NoaWNrX2NvdW50cy5jc3Y%3D","description":"Historical v1 1982-2020 only, not BAS 2026 v2",
  },
  "south_georgia_maiviken":{
      "doi":"10.5285/1fd5bc8a-96b5-4f53-aa15-33e5330e7705",
      "url":"https://ramadda.data.bas.ac.uk/repository/entry/get/Gentoo_SG_nest_chick_counts.csv?entryid=synth%3A1fd5bc8a-96b5-4f53-aa15-33e5330e7705%3AL0dlbnRvb19TR19uZXN0X2NoaWNrX2NvdW50cy5jc3Y%3D","description":"Maiviken monitoring site on main South Georgia island",
  },
}
MAX_BYTES=1024*1024

def get_raw(url,session=None):
    if urlparse(url).scheme!="https" or urlparse(url).hostname!="ramadda.data.bas.ac.uk":
        raise ValueError("SOURCE_STOP unexpected source publisher URL")
    s=session or requests.Session()
    try:
        r=s.get(url,headers={"User-Agent":"mina-BAS-gentoo-source-metadata-v21"},
                stream=True,timeout=35,allow_redirects=True)
        p=urlparse(r.url)
        if p.scheme!="https" or not (p.hostname or "").endswith(".bas.ac.uk"):
            raise ValueError("SOURCE_STOP untrusted published redirect")
        r.raise_for_status()
        n=0; data=[]
        for part in r.iter_content(chunk_size=16384):
            n+=len(part)
            if n>MAX_BYTES:
                raise ValueError("SOURCE_STOP original exceeds 1MiB")
            data.append(part)
        raw=b"".join(data)
        if not raw or raw.lstrip().lower().startswith((b"<!doctype",b"<html",b"<script")):
            raise ValueError("SOURCE_STOP BAS original download returned HTML or empty")
        if b"\x00" in raw[:128]:
            raise ValueError("SOURCE_STOP binary/non-CSV publisher response")
        return raw,{"url":r.url,"mime":r.headers.get("Content-Type",""),
                    "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
    finally:
        if session is None:s.close()

def parse_source(raw):
    try: text=raw.decode("utf-8-sig")
    except UnicodeDecodeError: text=raw.decode("latin-1")
    rd=csv.DictReader(io.StringIO(text,newline=""))
    fields=rd.fieldnames
    if not fields or len(fields)<3 or len([f for f in fields if f])<3:
        raise ValueError("SCHEMA_STOP fewer than 3 declared columns")
    if len(set(fields))!=len(fields):
        raise ValueError("SCHEMA_STOP duplicate CSV headers")
    if len(fields)>120:
        raise ValueError("SCHEMA_STOP unexpectedly wide original")
    records=list(rd)
    if not records or len(records)>30000:
        raise ValueError("SCHEMA_STOP empty or unexpectedly long original CSV")
    presence={}
    for f in fields:
        if f is None:continue
        presence[f]=sum(1 for row in records if row.get(f) is not None and str(row[f]).strip()!="")
    year_candidates=[f for f in fields if f and re.search(r"season|year",f,re.I)]
    stage_names=[f for f in fields if f and re.search(r"nest|egg|chick|fledg|pair",f,re.I)]
    # Only declared textual season label uniqueness, no outcomes or value ranges.
    years={}
    for name in year_candidates:
        years[name]=len({str(r[name]).strip() for r in records if r.get(name) is not None
                         and str(r[name]).strip()})
    return {"headers":fields,
            "original_rows":len(records),
            "per_column_nonempty":presence,
            "source_year_column_candidates":year_candidates,
            "distinct_nonempty_year_labels_by_candidate":years,
            "potential_reproductive_stage_field_names":stage_names,
            "original_breeding_count_values_read":0}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json",type=Path,required=True)
    args=ap.parse_args()
    report={"status":"V21_SOURCE_CHECK_PERFORMED","sources":{},"ecological_effects_fit":0}
    for name,spec in SOURCES.items():
        try:
            raw,receipt=get_raw(spec["url"])
            report["sources"][name]={"status":"ORIGINAL_PUBLISHER_FILE_VERIFIED",
                "doi":spec["doi"],"description":spec["description"],
                "receipt":receipt,"structural_metadata":parse_source(raw)}
        except Exception as exc:
            report["sources"][name]={"status":"HOLD_ORIGINAL_SOURCE",
                "doi":spec["doi"],"error_type":type(exc).__name__,
                "error":str(exc)[:300]}
    good=sum(s["status"]=="ORIGINAL_PUBLISHER_FILE_VERIFIED" for s in report["sources"].values())
    report["files_validated"]=good
    report["scientific_decision"]="PASS_BOTH_ORIGINAL_SCHEMAS_NO_EFFECT" if good==2 else "HOLD_INCOMPLETE_ORIGINAL_SOURCE"
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":
    main()
