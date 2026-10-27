#!/usr/bin/env python3
"""V48b: public original Dryad FILE SCHEMA only, never passerine effect reanalysis.

Exact 2 file IDs and source MD5 are fixed from V48 successful original Dryad
REST metadata. Goal: is a dated, island-linked original RAT SURVEILLANCE
exposure actually present to identify Paper2 Falklands H_M? No FIBD birds
or source-site names in outputs. No data login or private protected access.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import urljoin,urlparse

import requests

SOURCE={
 "DetectedS.csv":{
     "id":55543,"md5":"5b63de46da026644dc2b9a4ebe518a48",
     "size":16256
 },
 "Relative_Abunance.csv":{
     "id":55544,"md5":"6ccd0b6fb24ab3a1efad0be30d489ad6",
     "size":12000
 },
}
HOST="datadryad.org"
MAX_REDIRECTS=3
MAX_COLS=100
MAX_ROWS=20000
COL_PATTERN=re.compile(
 r"(?:\b|\W)(?:island|location|locality|site|region|latitude|longitude|"
 r"rat|rattus|eradication|eradicated|trap|survey|visit|sampling|effort|"
 r"year|date|predator|mammal|invasive|presence|status)(?:\b|\W)",
 re.I
)
S3_PATTERN=re.compile(
 r"^(?:[a-z0-9-]+\.)*s3(?:[.-][a-z0-9-]+)?\.amazonaws\.com$",re.I
)


def safe_download_host(url):
    parsed=urlparse(url)
    if parsed.scheme!="https" or not parsed.hostname:
        return False
    host=parsed.hostname.casefold()
    return host==HOST or bool(S3_PATTERN.fullmatch(host))


def original_download(name):
    if name not in SOURCE:
        raise ValueError("UNKNOWN_DRYAD_ORIGINAL_FILE")
    meta=SOURCE[name]
    url=f"https://{HOST}/api/v2/files/{meta['id']}/download"
    with requests.Session() as session:
        for n in range(MAX_REDIRECTS+1):
            if not safe_download_host(url):
                raise ValueError("UNSAFE_DRYAD_DOWNLOAD_REDIRECT_HOST")
            with session.get(
                url,stream=True,timeout=(12,45),allow_redirects=False,
                headers={"User-Agent":"mina-Paper2-Dryad-original-source-V48b/1.0"},
            ) as result:
                if result.status_code in (301,302,303,307,308):
                    if n==MAX_REDIRECTS:
                        raise ValueError("DRYAD_TOO_MANY_SOURCE_REDIRECTS")
                    loc=result.headers.get("Location")
                    if not loc:
                        raise ValueError("DRYAD_MISSING_SOURCE_REDIRECT_LOCATION")
                    url=urljoin(url,loc)
                    if not safe_download_host(url):
                        raise ValueError("UNSAFE_DRYAD_DOWNLOAD_REDIRECT_HOST")
                    continue
                result.raise_for_status()
                if result.status_code!=200:
                    raise ValueError("DRYAD_ORIGINAL_FILE_UNEXPECTED_STATUS")
                chunks=[];bytes_count=0
                for blob in result.iter_content(chunk_size=8192):
                    if not blob:continue
                    bytes_count+=len(blob)
                    if bytes_count>meta["size"]+1024:
                        raise ValueError("SOURCE_FILE_SIZE_MAX_EXCEEDED")
                    chunks.append(blob)
                payload=b"".join(chunks)
                if len(payload)!=meta["size"]:
                    raise ValueError("SOURCE_FILE_ORIGINAL_SIZE_MISMATCH")
                if hashlib.md5(payload).hexdigest()!=meta["md5"]:
                    raise ValueError("SOURCE_FILE_ORIGINAL_PUBLISHED_MD5_MISMATCH")
                return payload,{
                    "source_filename":name,"published_file_id":meta["id"],
                    "original_bytes":len(payload),
                    "publisher_original_md5":meta["md5"],
                    "public_Dryad_dataset_license":"CC0-1.0",
                    "download_original_content_verified":True,
                    "source_file_original_data_rows_exported":False,
                }
    raise ValueError("SOURCE_DOWNLOAD_FAILED_UNEXPECTED")


def interpret_header(header):
    cleaned=" ".join(str(header or "").strip().split())[:100]
    if not cleaned or not COL_PATTERN.search(cleaned):
        return None
    if len(cleaned)>80 or re.search(r"[^A-Za-z0-9 _.,()/#-]",cleaned):
        return None
    return cleaned


def inspect_csv_schema(raw,name):
    try:body=raw.decode("utf-8-sig")
    except UnicodeDecodeError:body=raw.decode("latin-1")
    # Original files are bounded <17kb. No raw source rows returned.
    try:dialect=csv.Sniffer().sniff(body[:2048],delimiters=",;\t")
    except csv.Error:dialect=csv.excel
    rows=list(csv.reader(io.StringIO(body),dialect))
    if not rows or len(rows)>MAX_ROWS+1:
        raise ValueError("DRYAD_ORIGINAL_CSV_ROW_BOUND")
    cols=len(rows[0])
    if cols<1 or cols>MAX_COLS:
        raise ValueError("DRYAD_ORIGINAL_CSV_COLUMN_BOUND")
    if any(len(row)!=cols for row in rows[1:] if row):
        raise ValueError("DRYAD_ORIGINAL_CSV_RAGGED_ROWS")
    labels=[]
    for i,h in enumerate(rows[0]):
        name_safe=interpret_header(h)
        if name_safe is not None:
            labels.append({"col_1based":i+1,"original_safe_header":name_safe})
    indicators={}
    for item in labels:
        index=item["col_1based"]-1
        content=[r[index].strip() for r in rows[1:] if r]
        vals=[v for v in content if v]
        indicators[item["original_safe_header"]]={
            "column_1based":index+1,
            "original_nonempty_cells":len(vals),
            "original_distinct_nonempty_values_n":len(set(vals)),
            "values_or_individual_island_names_published":False,
        }
    keys={"island_name_or_ID":r"\b(?:island|location|site|locality)\b",
          "dated_effort":r"\b(?:year|date|visit|trap|survey|sampling|effort)\b",
          "rat_observed_status_or_eradication":r"\b(?:rat|rattus|mammal|invasive|predator|eradication|eradicated|status)\b"}
    found={k:[i["col_1based"] for i in labels if re.search(p,i["original_safe_header"],re.I)]
           for k,p in keys.items()}
    return {
      "source_original_filename":name,
      "original_csv_rows_including_header":len(rows),
      "original_csv_columns":cols,
      "candidate_original_source_field_names_without_row_values":labels,
      "sensitive_source_field_values_never_exported":True,
      "original_candidate_columns_completeness":indicators,
      "original_header_keyword_support_by_source_role":found,
      "original_headers_support_all_three_mammal_predictor_requirements":
          all(len(found[k])>0 for k in keys),
      "not_a_verified_negative_survey_history_even_if_columns_named_rat":True,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r={
      "status":"V48B_DRYAD_ORIGINAL_CSV_SOURCE_SCHEMA_HOLD",
      "contract":"contracts/PAPER2_DRYAD_RAT_STATUS_ORIGINAL_CSV_V48B.md",
      "date":"2026-10-28",
      "source_Dryad_published_dataset":"doi:10.5061/dryad.dj524",
      "published_version":15582,
      "no_original_passserine_detection_or_abundance_effect_computed":True,
      "no_FIBD_bird_response_or_raw_island_name_read":True,
      "true_field_rat_surveyed_positive_and_negative_gates_pass":False,
    }
    results={}
    for file in SOURCE:
        try:
            raw,meta=original_download(file)
            results[file]={"status":"SOURCE_FILE_ORIGINAL_SHA_VERIFIED",**meta,
                           "schema":inspect_csv_schema(raw,file)}
        except Exception as exc:
            results[file]={"status":"SOURCE_DATA_ACCESS_OR_SCHEMA_HOLD",
                           "error":type(exc).__name__+": "+str(exc)[:450]}
    r["source_files"]=results
    successful=[n for n,x in results.items() if x["status"]=="SOURCE_FILE_ORIGINAL_SHA_VERIFIED"]
    r["source_files_verified_original_MD5_n"]=len(successful)
    r["source_metadata_predictor_possible"]={
        n:results[n].get("schema",{}).get(
            "original_headers_support_all_three_mammal_predictor_requirements",False)
        for n in SOURCE
    }
    r["status"]=(
        "V48B_DRYAD_ORIGINAL_TWO_FILE_SOURCE_SCHEMAS_AUDITED"
        if len(successful)==2 else "V48B_DRYAD_SOURCE_PARTIAL_OR_ACCESS_HOLD"
    )
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False))
    if r["status"]!="V48B_DRYAD_ORIGINAL_TWO_FILE_SOURCE_SCHEMAS_AUDITED":
        raise SystemExit(2)


if __name__=="__main__":
    main()
