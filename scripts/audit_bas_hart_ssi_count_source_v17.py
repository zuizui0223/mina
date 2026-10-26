#!/usr/bin/env python3
"""V17 verified BAS Hart original South Sandwich all-site nest-count CSV audit.

Opens actual first-party original summary count rows; no GIS, satellite TIFF,
or coordinate-level nest records. Outcome analysis not yet fitted.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,math,re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT="28222725-c53d-40f4-9350-49c368899f0b"
MAX_ORIGINAL_CSV_BYTES=5_000_000
EXPECTED_CURRENT_FILES=164
ALLOWED={"ramadda.data.bas.ac.uk","194.66.5.50"}
EXPECTED_ARCHIVE_STATUS="VERIFIED_ORIGINAL_SOURCE_FILES_PUBLISHER_SUMMARY_COUNT_DISCREPANCY"


def choose_source(manifest:dict):
    if manifest.get("status")!=EXPECTED_ARCHIVE_STATUS:
        raise ValueError("SOURCE_STOP publisher 2026 verified 164-file live manifest not supplied")
    files=manifest["original_all_file_metadata_only"]
    if len(files)!=EXPECTED_CURRENT_FILES or len({
        a["original_archive_relative_path"] for a in files})!=len(files):
        raise ValueError("SOURCE_STOP original BAS live archive file count or source IDs drift")
    candidates=[f for f in files if f["original_archive_relative_path"]=="SSI_count_results.csv"]
    if len(candidates)!=1:
        raise ValueError("SOURCE_STOP original BAS root SSI_count_results not unique")
    f=candidates[0]
    parsed=urlparse(f["source_file_url_https"])
    if (parsed.scheme!="https" or parsed.hostname not in ALLOWED
        or parsed.path!="/repository/entry/get/SSI_count_results.csv"):
        raise ValueError("SOURCE_STOP source download URL not genuine BAS count CSV")
    return f


def obtain_source_count_bytes(url):
    parsed=urlparse(url)
    if parsed.scheme!="https" or parsed.hostname not in ALLOWED:
        raise ValueError("SOURCE_STOP count source not original publisher HTTPS")
    with requests.Session() as sess:
        with sess.get(url,timeout=(20,110),stream=True,headers={
            "User-Agent":"mina-original-Hart-BAS-publisher-count-source-v17/1.0"}) as resp:
            resp.raise_for_status()
            actual=urlparse(resp.url)
            if actual.scheme!="https" or actual.hostname not in ALLOWED:
                raise ValueError("SOURCE_STOP unexpected original BAS file redirect")
            chunks=bytearray()
            for p in resp.iter_content(chunk_size=16384):
                chunks.extend(p)
                if len(chunks)>MAX_ORIGINAL_CSV_BYTES:
                    raise ValueError("SOURCE_STOP original first-party nested census CSV unexpectedly large")
    source=bytes(chunks)
    if source.lstrip()[:100].lower().startswith((b"<html",b"<!doctype")):
        raise ValueError("SOURCE_STOP original publisher served HTML, not CSV")
    if not source:
        raise ValueError("SOURCE_STOP original BAS nest count table empty")
    return source


def parse_original_counts(raw):
    try:
        text=raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise ValueError("SCHEMA_STOP original BAS counts CSV not UTF-8") from e
    f=io.StringIO(text,newline="")
    reader=csv.DictReader(f)
    columns=list(reader.fieldnames or [])
    if not columns or len(set(columns))!=len(columns) or not all(columns):
        raise ValueError("SCHEMA_STOP source original CSV header absent/ambiguous")
    if len(columns)>200:
        raise ValueError("SCHEMA_STOP implausibly wide original counts table")
    rows=list(reader)
    if len(rows)>5000 or not rows:
        raise ValueError("SOURCE_STOP original BAS summary CSV unexpected row count")
    if any(None in row for row in rows):
        raise ValueError("SCHEMA_STOP BAS source row has more values than header")
    per_column={}
    for col in columns:
        vals=[str(r.get(col,"") or "").strip() for r in rows]
        nonempty=[v for v in vals if v]
        numbers=[]
        for v in nonempty:
            try:
                n=float(v.replace(",",""))
                if math.isfinite(n):numbers.append(n)
            except ValueError:pass
        per_column[col]={
            "nonempty_source_rows":len(nonempty),
            "numeric_source_cell_count":len(numbers),
            "unique_literal_source_values":len(set(nonempty)),
            "up_to_8_original_literal_values":list(dict.fromkeys(nonempty))[:8],
        }
    return rows,{
        "status":"BAS_HART_ORIGINAL_SSI_COUNTS_CSV_SOURCE_SCHEMA_V17",
        "first_party_source_nest_count_rows":len(rows),
        "source_column_names":columns,
        "source_column_shape_and_literal_values":per_column,
        "original_record_examples":rows[:min(6,len(rows))],
        "source_species_or_site_missing_values_recoded_as_zero":False,
        "source_2022_ZAVO_chinstrap_observation_misreported_as_2020":False,
        "original_nest_point_coordinate_csv_records_opened":0,
        "new_ecological_statistical_fit_performed":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--publisher-manifest",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    output={"status":"HOLD_ORIGINAL_BAS_NEST_COUNT_SOURCE_V17","new_ecological_statistical_fit_performed":False}
    try:
        manifest=json.loads(a.publisher_manifest.read_text(encoding="utf-8"))
        file=choose_source(manifest)
        original=obtain_source_count_bytes(file["source_file_url_https"])
        _values,output=parse_original_counts(original)
        output["original_publisher_root_count_file_SHA256"]=hashlib.sha256(original).hexdigest()
        output["original_publisher_root_count_file_bytes"]=len(original)
        output["original_source_file_id"]=file["original_publisher_archive_id"]
        output["original_source_manifest_folder_SHA256"]={
           r["source_path"]:r["original_publisher_manifest_SHA256"]
           for r in manifest["publisher_directory_manifest_SHA_receipts"] if r["source_path"]==""
        }
    except Exception as e:
        output["error_type"]=type(e).__name__
        output["error"]=str(e)[:900]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # This is the actual original published short summary table; examples permit
    # author to identify actual count vs estimated count fields for V18.
    print(json.dumps(output,ensure_ascii=False))
    if output["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
