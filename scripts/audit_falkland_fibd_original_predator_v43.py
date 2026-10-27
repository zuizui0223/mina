#!/usr/bin/env python3
"""V43: Falkland Islands Government native FIBDv8 XLS public-source QA.

Never infer rat absence from absence of an invasion record. Even explicit
FIBD rat-negative entries may be desktop assumptions for UNSURVEYED islands.
This program only reads PUBLIC FIRST-PARTY CKAN registry + XLS schemas and
reports aggregated source fields, not respondent/surveyor personal details,
animal/site coordinates, or raw biological rows.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
import math
from pathlib import Path
import re
from urllib.parse import urlparse
import requests
import xlrd

CKAN_HOST="dataportal.saeri.org"
CKAN_ROOT="https://dataportal.saeri.org"
ORIGINAL_DATASETS=(
    "fibdv8-20140601-invasives",
    "fibdv8-20140601-locations",
    "fibdv8-20140601-visits",
    "fibdv8-20140601-eradication",
    "fibdv8-20140601-birds",
)
MAX_XLS_BYTES=8_000_000
MAX_ROWS_PER_SHEET=160_000
MAX_COLUMNS=160
LICENCE="CC-BY-SA-4.0"
KEY_LIKELY=re.compile(r"\b(?:island\s*id|island[_ -]?no|location[_ -]?id|visit[_ -]?id|site[_ -]?id|island[_ -]?code)\b|^id$",re.I)
RAT_HEADER=re.compile(r"\brattus\b|\bnorway\s+rat\b|\bbrown\s+rat\b|\bblack\s+rat\b|\brat\s+status\b",re.I)
HEADER_WORDS=re.compile(r"island|visit|invasive|rat|mouse|species|survey|date|latitude|longitude|elevation|habitat|eradication",re.I)


def bounded_https(session,url,maxbytes):
    if urlparse(url).hostname!=CKAN_HOST:
        raise ValueError("NON_PUBLISHER_PUBLIC_RESOURCE_HOST")
    parsed=urlparse(url)
    if parsed.scheme=="http":
        url=parsed._replace(scheme="https").geturl()
    elif parsed.scheme!="https":
        raise ValueError("INSECURE_SOURCE_SCHEME")
    with session.get(url,stream=True,timeout=(15,75),
                     headers={"User-Agent":"mina-original-FIBD-UK-predator-niche-source-audit/1.0"},
                     allow_redirects=True) as response:
        response.raise_for_status()
        final=urlparse(response.url)
        if final.scheme!="https" or final.hostname!=CKAN_HOST:
            raise ValueError("SOURCE_HOST_REDIRECT_DENIED")
        raw=[]
        count=0
        for block in response.iter_content(chunk_size=65536):
            if not block:continue
            count+=len(block)
            if count>maxbytes:
                raise ValueError("SOURCE_SIZE_LIMIT")
            raw.append(block)
        return b"".join(raw)


def get_official_package(session,slug):
    if slug not in ORIGINAL_DATASETS:
        raise ValueError("UNREGISTERED_SOURCE_SLUG")
    payload=bounded_https(session,CKAN_ROOT+"/api/3/action/package_show?id="+slug,2_000_000)
    obj=json.loads(payload.decode("utf-8"))
    if obj.get("success") is not True or not isinstance(obj.get("result"),dict):
        raise ValueError("SOURCE_CKAN_PACKAGE_UNAVAILABLE")
    package=obj["result"]
    if package.get("name")!=slug or package.get("private") is not False:
        raise ValueError("SOURCE_DATASET_ID_OR_PRIVATE_RESTRICTED")
    if package.get("license_id")!=LICENCE:
        raise ValueError("SOURCE_LICENSE_NOT_CC_BY_SA_4_0")
    resources=[]
    for item in package.get("resources",[]):
        if str(item.get("format","")).lower() not in ("xls", "xlsx"):
            continue
        text=item.get("restricted","")
        access={}
        if isinstance(text,str) and text.strip():
            access=json.loads(text)
        if access and access.get("level") not in ("public",):
            continue
        if str(item.get("name","")).lower().endswith((".xls",".xlsx")) is False:
            continue
        if item.get("state") not in (None,"active"):
            continue
        original_size=item.get("size")
        if original_size and int(original_size)>MAX_XLS_BYTES:
            raise ValueError("SOURCE_RESOURCE_EXCEEDS_FIXED_SIZE_LIMIT")
        resources.append({
            "id":str(item["id"]),
            "url":str(item["url"]),
            "filename":str(item.get("name","")),
            "reported_bytes":original_size,
            "format":str(item.get("format")),
            "original_resource_restricted_state":access.get("level","PUBLIC_UNMARKED"),
            "modified_date":item.get("last_modified"),
        })
    if len(resources)!=1:
        raise ValueError("SOURCE_UNEXPECTED_PUBLIC_XLS_RESOURCE_COUNT="+str(len(resources)))
    return resources[0],{
        "CKAN_original_dataset_name":slug,
        "title":package.get("title"),
        "source_registry_resource_id":resources[0]["id"],
        "license":package.get("license_id"),
        "source_metadata_unique_resource_id":package.get("saeri_unique_resource_id"),
        "source_period_start":package.get("saeri_temporal_extent_start"),
        "source_period_end":package.get("saeri_temporal_extent_end"),
        "source_dataset_private":package.get("private"),
        "source_access":package.get("saeri_access_limitations"),
        "source_download_restricted_level":resources[0]["original_resource_restricted_state"],
        "original_publisher_disclaimer":str(package.get("saeri_lineage") or "")[:750],
    }


def literal_header(value):
    if value is None:return ""
    if isinstance(value,str):
        return re.sub(r"\s+"," ",value.replace("\x00"," ")).strip()[:92]
    return ""


def inspect_xls_sheets(data,slug):
    book=xlrd.open_workbook(file_contents=data,on_demand=True,ragged_rows=True)
    tables=[]
    try:
        if book.nsheets<1 or book.nsheets>14:raise ValueError("SOURCE_SHEET_COUNT_OUTSIDE_GUARD")
        for sheet in book.sheets():
            if sheet.nrows>MAX_ROWS_PER_SHEET or sheet.ncols>MAX_COLUMNS:
                raise ValueError("SOURCE_SHEET_DIMENSIONS_EXCEED_SAFE_BOUND")
            rows_head=[]
            for i in range(min(9,sheet.nrows)):
                row=[literal_header(sheet.cell_value(i,c)) for c in range(min(sheet.ncols,MAX_COLUMNS))]
                rows_head.append(row)
            # Header is picked based solely on column NAMES, not sightings.
            row_scores=[]
            for i,row in enumerate(rows_head):
                found=sum(bool(HEADER_WORDS.search(x)) for x in row if x)
                row_scores.append((found,i))
            index=max(row_scores)[1] if row_scores else 0
            source_headers=rows_head[index] if rows_head else []
            keys=[(j,x) for j,x in enumerate(source_headers) if KEY_LIKELY.search(x)]
            rat_cols=[(j,x) for j,x in enumerate(source_headers) if RAT_HEADER.search(x)]
            label_candidates=[x for x in source_headers if x and HEADER_WORDS.search(x)]
            key_stats=[]
            for col,name in keys[:12]:
                nonmissing=0;unique=set()
                # Enumerating keys is source QA only: do not expose original ID values.
                for rowi in range(index+1,sheet.nrows):
                    val=sheet.cell_value(rowi,col) if col<sheet.row_len(rowi) else ""
                    if val not in ("",None):
                        nonmissing+=1
                        unique.add(str(val).strip().casefold())
                key_stats.append({
                    "column":col+1,
                    "label":name,
                    "nonmissing_after_candidate_header":nonmissing,
                    "distinct_original_key_values":len(unique),
                    "source_key_duplicate_rows":nonmissing-len(unique),
                })
            taxon_codes={}
            for col,name in rat_cols[:6]:
                counter=Counter()
                # Do not infer field surveyed absences from blanks/negatives.
                for rowi in range(index+1,sheet.nrows):
                    val=sheet.cell_value(rowi,col) if col<sheet.row_len(rowi) else None
                    # no publication of island or animal coordinate rows
                    if isinstance(val,str):
                        cell=literal_header(val).casefold()
                    elif isinstance(val,(int,float)) and math.isfinite(val):
                        cell=str(int(val)) if float(val).is_integer() else "NONINTEGER_NUMBER"
                    else:
                        cell="<MISSING>"
                    counter[cell or "<MISSING>"]+=1
                # redact rare free-text entries potentially containing
                # individual locations or observer identities.
                taxon_codes[name]={
                    "nonempty":sum(n for v,n in counter.items() if v!="<MISSING>"),
                    "top_low_cardinality_statuses":[
                        {"literal":v if len(v)<32 and re.fullmatch(r"[a-z0-9 +./-]+",v) else "<OTHER_VALUE>",
                         "n":n}
                        for v,n in counter.most_common(10) if n>=10
                    ],
                    "rare_source_values_not_republished":True,
                }
            tables.append({
                "sheet_name":sheet.name[:100],
                "source_nonempty_sheet_rows":sheet.nrows,
                "source_max_columns":sheet.ncols,
                "candidate_header_row_index_0based":index,
                "column_header_candidates":[{"column":j+1,"label":x} for j,x in
                                            enumerate(source_headers) if x][:min(45,len(source_headers))],
                "literal_rat_header_candidates":[name for _,name in rat_cols],
                "original_key_name_candidates":[name for _,name in keys],
                "original_key_cardinality":key_stats,
                "rat_status_value_distributions_only_if_explicit_header":taxon_codes,
                "visit_rows_are_not_verified_predator_survey_effort":True,
            })
        return tables
    finally:
        book.release_resources()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    receipt={
        "status":"FIBD_V43_PRIMARY_PUBLISHER_SOURCE_AUDIT",
        "frozen_contract":"contracts/ISLAND_PREDATOR_FALKLAND_FIBD_V43_SOURCE_GATE.md",
        "source_catalogue":"https://dataportal.saeri.org",
        "five_original_falkland_government_dataset_slugs":ORIGINAL_DATASETS,
        "no_paper_reanalysis_or_predator_occupancy_fit":True,
        "no_public_raw_personal_surveyor_or_mammal_sensitive_location_rows_saved":True,
        "no_2014_UK_Stanbury_JNCC_or_V40_biological_outcomes_read":True,
        "Norway_rat_unsurveyed_source_status_does_not_mean_field_survey_negative":True,
    }
    # Keep the public publisher load bounded: at most 3 concurrent
    # official XLS requests instead of up to 10 sequential slow URL reads.
    # The five science/source slugs, licensing and source checks are unchanged.
    from concurrent.futures import ThreadPoolExecutor
    def read_original_dataset(slug):
        item={"status":"SOURCE_ACCESS_OR_SCHEMA_HOLD"}
        try:
            with requests.Session() as session:
                original,metadata=get_official_package(session,slug)
                item["metadata"]=metadata
                b=bounded_https(session,original["url"],MAX_XLS_BYTES)
            if b.startswith(b"<html") or b.startswith(b"<!DOC"):
                raise ValueError("SOURCE_RETURNED_HTML_NOT_XLS")
            item["original_binary_sha256"]=hashlib.sha256(b).hexdigest()
            item["original_bytes"]=len(b)
            item["original_source_filename"]=original["filename"]
            item["source_sheets"]=inspect_xls_sheets(b,slug)
            item["status"]="PUBLIC_ORIGINAL_SPREADSHEET_SCHEMA_VERIFIED"
        except Exception as e:
            item["status"]="SOURCE_ACCESS_OR_SCHEMA_HOLD"
            item["error"]=type(e).__name__+": "+str(e)[:350]
        return item
    with ThreadPoolExecutor(max_workers=3) as executor:
        outcomes=dict(zip(ORIGINAL_DATASETS,executor.map(read_original_dataset,ORIGINAL_DATASETS)))
    receipt["source_datasets"]=outcomes
    ok=[slug for slug,x in outcomes.items()
        if x["status"]=="PUBLIC_ORIGINAL_SPREADSHEET_SCHEMA_VERIFIED"]
    receipt["source_sheets_original_access_verified_n"]=len(ok)
    receipt["source_sheets_original_access_verified_slugs"]=ok
    core=all(x in ok for x in ("fibdv8-20140601-invasives","fibdv8-20140601-locations","fibdv8-20140601-visits"))
    receipt["status"]=(
        "FIBD_V43_PUBLIC_INVASIVE_LOCATION_VISIT_RAW_SCHEMAS_VERIFIED"
        if core
        else "FIBD_V43_PRIMARY_SOURCES_PARTIAL_ACCESS_HOLD"
    )
    receipt["ecological_occupancy_probability_fitted"]=False
    receipt["explicit_field_surveyed_non_detections_verified"]=False
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":receipt["status"],
        "verified_original_spreadsheets":len(ok),
        "by_dataset":{
            slug:{
                "status":item["status"],
                "sha":item.get("original_binary_sha256"),
                "bytes":item.get("original_bytes"),
                "sheets":item.get("source_sheets"),
                "error":item.get("error"),
            }
            for slug,item in outcomes.items()
        },
    },ensure_ascii=False))
    # Source unavailability is a valid scientific HOLD, not a raw data fabrication.
if __name__=="__main__":main()
