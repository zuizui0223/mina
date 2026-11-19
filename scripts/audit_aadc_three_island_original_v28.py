#!/usr/bin/env python3
"""V28: official AADC 1103/5516 original workbook schema, never bird count magnitudes."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from urllib.parse import quote,urlparse
import argparse
import csv
import hashlib
import io
import json
import re
import requests
from openpyxl import load_workbook
import xlrd

HOST="data.aad.gov.au"
URL=f"https://{HOST}/eds/api/dataset?size=10000"
TARGETS={
    "1103":{"title_token":"bechervaise", "metadata_id":"population_counts_BI"},
    "5516":{"title_token":"mac", "metadata_id":"AAS_4518_MacRobertson_Land_Adelie_Penguins"}
}
MAX_MANIFEST=28_000_000
MAX_OBJECTS=80
MAX_RAW=18_000_000

def exact_get(session,url,cap,expected_json=False):
    parsed=urlparse(url)
    if parsed.scheme!="https" or parsed.hostname!=HOST:
        raise ValueError("SOURCE_STOP untrusted original AADC endpoint")
    with session.get(url,stream=True,timeout=(22,95),
                     headers={"User-Agent":"mina-aadc-2026-three-island-original-schema-v28"}) as r:
        r.raise_for_status()
        end=urlparse(r.url)
        if end.scheme!="https" or not (
             end.hostname==HOST or end.hostname.endswith(".data.aad.gov.au")
             or end.hostname.endswith(".amazonaws.com")):
            raise ValueError("SOURCE_STOP original source redirected outside publisher transport")
        body=bytearray()
        for chunk in r.iter_content(32768):
            body.extend(chunk)
            if len(body)>cap:
                raise ValueError("SOURCE_STOP original source above bounded size")
        raw=bytes(body)
        if expected_json and not raw[:1] in (b"{",b"["):
            raise ValueError("SOURCE_STOP source API did not return JSON")
        if not expected_json and raw[:100].lstrip().lower().startswith((b"<html",b"<!doctype html")):
            raise ValueError("SOURCE_STOP original returned HTML portal")
        return raw,{"sha256":hashlib.sha256(raw).hexdigest(),
                    "source_bytes":len(raw),"resolved_source_hostname":end.hostname,
                    "publisher_content_type":r.headers.get("Content-Type","")}

def listed_datasets(raw):
    info=json.loads(raw)
    if not isinstance(info,list):
        raise ValueError("SCHEMA_STOP AADC dataset list not array")
    found={}
    for eds,required in TARGETS.items():
        item=[x for x in info if str(x.get("eds_id",""))==eds]
        if len(item)!=1:
            raise ValueError("SOURCE_STOP no exact one AADC eds_id "+eds)
        target=item[0]
        name=str(target.get("dataset_name",""))
        mid=str(target.get("metadata_entry_id",""))
        # Official frozen eds ID, title + metadata key, no fuzzy matches.
        if required["title_token"] not in name.lower() and required["metadata_id"].lower() not in mid.lower():
            raise ValueError("SOURCE_STOP AADC official dataset identity mismatch "+eds)
        if not re.fullmatch(r"[A-Fa-f0-9-]{36}",str(target.get("uuid",""))):
            raise ValueError("SCHEMA_STOP missing original AADC dataset UUID")
        found[eds]={"eds_id":eds,"uuid":str(target["uuid"]),"publisher_title":name,
                    "original_metadata_entry_id":mid,
                    "original_dataset_access_status":str(target.get("dataset_visibility_status",""))}
    return found

def object_candidates(eds,objects):
    if not isinstance(objects,list) or len(objects)>10000:
        raise ValueError("SCHEMA_STOP original publisher object index invalid")
    allowed=[]
    inventory=[]
    for entry in objects:
        if not isinstance(entry,dict) or not entry.get("name"):
            continue
        name=str(entry["name"])
        size=entry.get("size")
        if name.lower().endswith((".xls",".xlsx",".csv")):
            inventory.append({"name":name,"publisher_size":size})
            if eds=="1103" or (
               eds=="5516" and any(w in name.lower() for w in
               ("environment","time series","demograph","covariat"))):
                allowed.append(name)
    maximum=12 if eds=="1103" else 5
    if len(allowed)>maximum:
        raise ValueError("SOURCE_STOP too many source candidate spreadsheets; inspect metadata before selection")
    return sorted(allowed),inventory[:100]

def minimal_sheet_schema(header_rows,name,rows,cols):
    texts=[]
    for row in header_rows:
        headers=[str(v).strip() if isinstance(v,str) else "" for v in row]
        if any(headers):
            texts.append(headers[:35])
    return {"name":name,"sheet_rows":int(rows),"sheet_columns":int(cols),
            "first_five_source_text_header_rows":texts[:5],
            "original_animal_count_values_opened":0}

def spreadsheet_probe(raw,filename):
    lower=filename.lower()
    sheets=[]
    if lower.endswith(".xlsx"):
        if not raw.startswith(b"PK"):
            raise ValueError("SCHEMA_STOP publisher .xlsx is not ZIP format")
        wb=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
        try:
            for ws in wb.worksheets[:20]:
                top=[]
                for idx,row in enumerate(ws.iter_rows(values_only=True)):
                    if idx>=5:break
                    # Header text ONLY; numerical bird-count cells never emitted.
                    top.append(list(row))
                sheets.append(minimal_sheet_schema(top,ws.title,ws.max_row or 0,ws.max_column or 0))
        finally:
            wb.close()
    elif lower.endswith(".xls"):
        if not raw.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
            raise ValueError("SCHEMA_STOP publisher .xls not OLE2 legacy Excel")
        wb=xlrd.open_workbook(file_contents=raw,on_demand=True)
        try:
            for ws in wb.sheets()[:20]:
                first=[ws.row_values(i) for i in range(min(5,ws.nrows))]
                sheets.append(minimal_sheet_schema(first,ws.name,ws.nrows,ws.ncols))
        finally:
            wb.release_resources()
    elif lower.endswith(".csv"):
        try:
            text=raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text=raw.decode("latin-1")
        with io.StringIO(text,newline="") as f:
            reader=csv.reader(f)
            first=[]
            for index,row in enumerate(reader):
                if index>=5:break
                first.append(row)
        sheets=[minimal_sheet_schema(first,filename,0,max((len(row) for row in first),default=0))]
    else:raise ValueError("SCHEMA_STOP unsupported source format")
    return {"workbook_sheets":sheets,"original_occupied_nests_opened":0}

def audit(session):
    data,listing_meta=exact_get(session,URL,MAX_MANIFEST,True)
    datasets=listed_datasets(data)
    original={}
    for eds,base in datasets.items():
        uid=base["uuid"]
        list_url=f"https://{HOST}/eds/api/dataset/{quote(uid)}/objects?recursive=true&removeBasePath=true"
        content,ml=exact_get(session,list_url,MAX_MANIFEST,True)
        objects=json.loads(content)
        candidates,inventory=object_candidates(eds,objects)
        source={"original_dataset":base,"object_list_sha256":ml["sha256"],
                "source_spreadsheet_inventory":inventory,"selected_original_spreadsheets":candidates,
                "files":{}}
        for name in candidates:
            get=f"https://{HOST}/eds/api/dataset/{quote(uid)}/object/download?prefix={quote(name,safe='')}"
            try:
                raw,metadata=exact_get(session,get,MAX_RAW)
                structure=spreadsheet_probe(raw,name)
                source["files"][name]={"status":"ORIGINAL_SOURCE_READ_SCHEMA_ONLY",**metadata,**structure}
            except Exception as err:
                source["files"][name]={"status":"HOLD_SOURCE_FILE",
                                       "error_type":type(err).__name__,"error":str(err)[:550]}
        source["original_valid_file_count"]=sum(r.get("status")=="ORIGINAL_SOURCE_READ_SCHEMA_ONLY" for r in source["files"].values())
        original[eds]=source
    return {
        "status":"V28_AADC_ORIGINAL_THREE_ISLAND_AND_DEMOGRAPHY_SCHEMA_AUDIT",
        "official_publisher":"Australian Antarctic Data Centre",
        "original_dataset_catalog_sha256":listing_meta["sha256"],
        "dataset_sources":original,
        "original_occupied_nest_effects_fitted":0,
        "original_animal_count_values_opened":0,
        "datasets_have_independent_animal_observations_assumed":False,
        "meta_comparability_unknown_until_row_grain_and_season_QA":True,
        "decision":("READY_FOR_METADATA_ONLY_SEASON_SUPPORT" if
                    original["1103"]["original_valid_file_count"]>=1
                    else "HOLD_NO_VERIFIED_THREE_ISLAND_SOURCE")
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json",required=True,type=Path)
    args=ap.parse_args()
    receipt={"status":"HOLD_ORIGINAL_AADC_SOURCE","original_occupied_nest_effects_fitted":0}
    try:
        with requests.Session() as session:
            receipt=audit(session)
    except Exception as ex:
        receipt["error_type"]=type(ex).__name__
        receipt["error"]=str(ex)[:600]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_AADC_SOURCE":
        raise SystemExit(2)

if __name__=="__main__":
    main()
