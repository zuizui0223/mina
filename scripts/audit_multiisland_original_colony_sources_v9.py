#!/usr/bin/env python3
"""Discover genuine original multi-island breeding boundary data, no animal rows.

Two official archive indices only: AADC public dataset registry (Adelie polygon
boundary time series) and BAS RAMADDA publisher CSV manifests (SSI nest GIS).
No biological observations or boundary polygons are opened in this script.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import csv
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlparse, parse_qs, quote, urljoin

import requests

from audit_aadc_original_workbook_headers_v11 import HOST as AADC_HOST, LIST_API, trusted_response_get

AADC_TARGET="aas_4088_adelie_breeding_colony_boundaries"
AADC_PREFIX="aas_4088_adelie_occupancy_"
BAS_HOST="ramadda.data.bas.ac.uk"
BAS_ENTRY_ID="28222725-c53d-40f4-9350-49c368899f0b"
BAS_ROOT_URL=(f"https://{BAS_HOST}/repository/entry/show?entryid="
              f"{BAS_ENTRY_ID}&output=default.csv")
# The prior PR #196 actually verified this publisher's ZAVO original folder,
# but it is only a source-first fallback if listing the real archive root fails.
BAS_KNOWN_ZAVO_FOLDER="synth:"+BAS_ENTRY_ID+":L1phdm9kb3Zza2kvY29vcmRpbmF0ZXM="
BAS_ZAVO_URL=(f"https://{BAS_HOST}/repository/entry/show?entryid="
              f"{quote(BAS_KNOWN_ZAVO_FOLDER,safe='')}&output=default.csv")
BAS_ALLOWED={"ramadda.data.bas.ac.uk","194.66.5.50"}
MAX_AADC_DATASETS=75
MAX_AADC_OBJECT_METADATA_BYTES=18_000_000
MAX_BAS_FOLDERS=150
MAX_BAS_ROWS_TOTAL=6500
MAX_BAS_DOCUMENT_BYTES=2_000_000
SOURCE_SEASON=re.compile(r"(?:19|20)\d{2}[-_/]?(?:\d{2,4})?")


def is_target_aadc(entry:dict):
    mid=str(entry.get("metadata_entry_id","")).casefold().strip()
    # Source parent plus its documented nested 32 regional child accounts only.
    return mid==AADC_TARGET or mid.startswith(AADC_PREFIX)


def aadc_catalogue(records:list):
    matches=[x for x in records if isinstance(x,dict) and is_target_aadc(x)]
    summary={"registry_records_examined":len(records),"parent_metadata_id":AADC_TARGET,
             "source_registry_matching_parent_and_children":len(matches),
             "potential_polygon_parent_records":sum(
                 str(x.get("metadata_entry_id","")).casefold()==AADC_TARGET
                 for x in matches),
             "metadata_original_registry_entries":[{
                 "metadata_entry_id":x.get("metadata_entry_id"),
                 "eds_id":str(x.get("eds_id","")),
                 "uuid":str(x.get("uuid","")),
                 "dataset_name":str(x.get("dataset_name",""))[:210],
                 "dataset_visibility_status":str(x.get("dataset_visibility_status",""))[:90],
             } for x in matches[:MAX_AADC_DATASETS]],
             "publisher_breeding_data_rows_opened":0}
    return matches,summary


def aadc_source_index(session):
    original,manifest=trusted_response_get(session,LIST_API,30_000_000,True)
    records=json.loads(original)
    if not isinstance(records,list):
        raise ValueError("SCHEMA_STOP original public AADC index not an array")
    selected,result=aadc_catalogue(records)
    result["publisher_registry_source_sha256"]=manifest["source_sha256"]
    if not selected:
        return {"status":"HOLD_AADC_PARENT_CHILD_NOT_IN_PUBLIC_API_INDEX",**result}
    if len(selected)>MAX_AADC_DATASETS:
        raise ValueError("SOURCE_STOP excessive AADC matching source datasets")
    views=[]
    for source in selected:
        uid=str(source.get("uuid",""))
        if not re.fullmatch(r"[0-9a-fA-F-]{36}",uid):
            views.append({"metadata_entry_id":source.get("metadata_entry_id"),
                          "source_status":"HOLD_INVALID_OR_MISSING_OFFICIAL_UUID"})
            continue
        url=f"https://{AADC_HOST}/eds/api/dataset/{quote(uid)}/objects?recursive=true&removeBasePath=true"
        try:
            payload,response=trusted_response_get(
                session,url,MAX_AADC_OBJECT_METADATA_BYTES,True)
            records=json.loads(payload)
            if not isinstance(records,list):
                raise ValueError("SCHEMA_STOP AADC object index not a list")
            paths=[str(x.get("name","")) for x in records
                   if isinstance(x,dict) and x.get("name")]
            relevant=[p for p in paths if p.lower().endswith(
                (".shp",".shx",".dbf",".prj",".gpkg",".geojson",".zip",
                 ".csv",".xlsx",".xls",".gdb",".pdf",".txt"))]
            exts=Counter(Path(x).suffix.lower() for x in relevant)
            geography_id_hints=[
                x for x in relevant if re.search(
                    r"IS_\d{3,}|(?:19|20)\d{2}[-_](?:19|20)?\d{2}|(?:19|20)\d{2}",
                    x,re.IGNORECASE)]
            views.append({
                "metadata_entry_id":source.get("metadata_entry_id"),
                "source_uuid":uid,
                "source_eds_id":source.get("eds_id"),
                "source_status":"PUBLISHER_MANIFEST_SUCCESS",
                "original_file_object_count":len(records),
                "original_spatial_document_by_extension":dict(sorted(exts.items())),
                "original_site_or_season_filename_hints":geography_id_hints[:35],
                "original_source_file_paths_and_bytes":[{
                    "original_path":str(x.get("name",""))[:400],
                    "publisher_declared_bytes":x.get("size")
                 } for x in records if isinstance(x,dict) and
                    str(x.get("name","")).lower().endswith((".shp",".zip",".gpkg",".geojson",".csv"))
                 ][:150],
                "source_index_json_sha256":response["source_sha256"],
                "biological_polygon_rows_read":0
            })
        except Exception as exc:
            views.append({
                "metadata_entry_id":source.get("metadata_entry_id"),
                "source_uuid":uid,
                "source_status":"HOLD_ORIGINAL_OBJECT_MANIFEST_ACCESS",
                "error_type":type(exc).__name__,
                "error":str(exc)[:220],
            })
    n_ok=sum(v["source_status"]=="PUBLISHER_MANIFEST_SUCCESS" for v in views)
    return {"status":"AADC_ORIGINAL_BOUNDARY_MANIFESTS_PARTIAL_OR_COMPLETE" if n_ok else
            "HOLD_AADC_BOUNDARY_MANIFESTS_UNAVAILABLE",
            **result,"original_dataset_object_receipts":views,
            "successful_publisher_dataset_object_manifest_n":n_ok}


def bas_validate_source(url:str):
    parsed=urlparse(url)
    if parsed.scheme!="https" or parsed.hostname not in BAS_ALLOWED or parsed.port not in (None,443):
        raise ValueError("SOURCE_STOP nonpublisher BAS URL")
    if parsed.path!="/repository/entry/show":
        raise ValueError("SOURCE_STOP not an original RAMADDA directory show URL")
    qs=parse_qs(parsed.query)
    if "entryid" not in qs or len(qs["entryid"])!=1:
        raise ValueError("SOURCE_STOP original RAMADDA entry ID missing")
    identity=qs["entryid"][0]
    if identity!=BAS_ENTRY_ID and not identity.startswith("synth:"+BAS_ENTRY_ID+":"):
        raise ValueError("SOURCE_STOP RAMADDA entryid outside verified dataset")
    return identity


def bas_file_row_is_publisher(row:dict):
    url=str(row.get("url",""))
    parsed=urlparse(url)
    if parsed.scheme not in ("https","http") or parsed.hostname not in BAS_ALLOWED:
        return False
    return parsed.path.startswith(("/repository/entry/get/","/repository/entry/show"))


def bas_folder_target(row:dict):
    target=row.get("url","")
    if not target:
        return None
    parsed=urlparse(str(target))
    if parsed.hostname!=BAS_HOST or parsed.path!="/repository/entry/show":
        return None
    try:
        identity=bas_validate_source("https://"+BAS_HOST+parsed.path+"?"+parsed.query)
    except ValueError:
        return None
    return f"https://{BAS_HOST}/repository/entry/show?entryid={quote(identity,safe='')}&output=default.csv"


def original_bas_manifest(session, url):
    bas_validate_source(url)
    with session.get(url,timeout=(20,90),stream=True,
                     headers={"User-Agent":"mina-original-multiisland-BAS-manifest-only/1.0"}) as r:
        r.raise_for_status()
        resolved=urlparse(r.url)
        if resolved.scheme!="https" or resolved.hostname not in BAS_ALLOWED:
            raise ValueError("SOURCE_STOP off-publisher RAMADDA redirect")
        contents=bytearray()
        for block in r.iter_content(16384):
            contents.extend(block)
            if len(contents)>MAX_BAS_DOCUMENT_BYTES:
                raise ValueError("SOURCE_STOP RAMADDA source listing exceeds bound")
        ctype=r.headers.get("Content-Type","")
    raw=bytes(contents)
    if raw.lstrip()[:100].lower().startswith((b"<!doctype",b"<html")):
        raise ValueError("SOURCE_STOP publisher served HTML, not manifest CSV")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if not rows and b"name" not in raw.lower():
        raise ValueError("SCHEMA_STOP original RAMADDA CSV list has no name column")
    if rows and ("name" not in rows[0] or "url" not in rows[0]):
        raise ValueError("SCHEMA_STOP RAMADDA CSV manifest missing name/url")
    return rows,{"source_url":url,"source_bytes":len(raw),
                 "source_csv_sha256":hashlib.sha256(raw).hexdigest(),
                 "content_type":ctype,"original_publisher_file_biological_rows_opened":0}


def bas_source_tree(session):
    pending=deque([BAS_ROOT_URL])
    visited=set()
    all_files=[]
    folders=[]
    unresolved=[]
    while pending and len(visited)<MAX_BAS_FOLDERS:
        url=pending.popleft()
        folder_id=bas_validate_source(url)
        if folder_id in visited:continue
        visited.add(folder_id)
        try:
            rows,receipt=original_bas_manifest(session,url)
        except Exception as exc:
            unresolved.append({"folder":folder_id,"error_type":type(exc).__name__,
                               "error":str(exc)[:210]})
            continue
        folders.append({"folder":folder_id,"row_count":len(rows),**receipt})
        for r in rows:
            if len(all_files)>MAX_BAS_ROWS_TOTAL:
                raise ValueError("SOURCE_STOP too many publisher original metadata rows")
            name=str(r.get("name",""))
            child=bas_folder_target(r)
            if child and child!=url:
                if bas_validate_source(child) not in visited:
                    pending.append(child)
            elif bas_file_row_is_publisher(r):
                all_files.append({
                    "folder":folder_id,
                    "original_file_name":name,
                    "original_publisher_url":str(r.get("url",""))[:650],
                    "source_declared_size":r.get("size",r.get("file size")),
                    "source_row_type":str(r.get("type",""))[:100],
                })
    if len(folders)==0 and BAS_KNOWN_ZAVO_FOLDER not in visited:
        # Independently preserve the known original ZAVO folder from PR196.
        try:
            rows,receipt=original_bas_manifest(session,BAS_ZAVO_URL)
            folders.append({"folder":BAS_KNOWN_ZAVO_FOLDER,"row_count":len(rows),
                            "fallback_prior_verified_ZAVO_only":True,**receipt})
            for r in rows:
                if bas_file_row_is_publisher(r):
                    all_files.append({"folder":BAS_KNOWN_ZAVO_FOLDER,
                                      "original_file_name":str(r.get("name","")),
                                      "original_publisher_url":str(r.get("url",""))[:650],
                                      "source_declared_size":r.get("size"),
                                      "source_row_type":str(r.get("type",""))[:100]})
        except Exception as exc:
            unresolved.append({"folder":BAS_KNOWN_ZAVO_FOLDER,
                               "error_type":type(exc).__name__,
                               "error":str(exc)[:210]})
    csvfiles=[x for x in all_files if x["original_file_name"].lower().endswith(".csv")]
    tiffs=[x for x in all_files if x["original_file_name"].lower().endswith((".tif",".tiff"))]
    allsitecounts=Counter()
    for f in csvfiles:
        p=f["original_file_name"]
        for site in ("ZAVO","CAND","BELL","THUL","HERD","HEWI","ASHEN","BEACH"):
            if site in p.upper() or site in f["folder"].upper():
                allsitecounts[site]+=1
    return {
        "status":"BAS_ORIGINAL_MULTIISLAND_MANIFEST_DISCOVERED" if folders else "HOLD_BAS_ARCHIVE_MANIFEST",
        "original_hart_2022_dataset_DOI":"10.5285/28222725-c53d-40f4-9350-49c368899f0b",
        "publisher_ramadda_original_folder_count":len(folders),
        "original_source_directory_receipts":folders[:MAX_BAS_FOLDERS],
        "original_source_access_holds":unresolved[:50],
        "original_CSV_file_count":len(csvfiles),
        "original_TIF_file_count":len(tiffs),
        "original_source_CSV_filenames_and_direct_urls":csvfiles[:130],
        "original_source_site_name_file_hints":dict(sorted(allsitecounts.items())),
        "listed_source_file_total_count":len(all_files),
        "publisher_original_biological_rows_opened":0,
        "imputed_ZAVO_2022_chinstrap_not_2020_observation":True,
        "multiple_original_locality_files_not_proof_distinct_physical_islands":True
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result={"status":"V9_ORIGINAL_MULTIISLAND_SOURCE_DISCOVERY", "animal_rows_opened":0}
    try:
        with requests.Session() as session:
            result["AADC_EAST_ANTARCTIC_BOUNDARIES"]=aadc_source_index(session)
    except Exception as exc:
        result["AADC_EAST_ANTARCTIC_BOUNDARIES"]={"status":"HOLD_AADC_SOURCE_INDEX",
                                                   "error_type":type(exc).__name__,
                                                   "error":str(exc)[:450],
                                                   "animal_rows_opened":0}
    try:
        with requests.Session() as session:
            result["BAS_SOUTH_SANDWICH_UAV"]=bas_source_tree(session)
    except Exception as exc:
        result["BAS_SOUTH_SANDWICH_UAV"]={"status":"HOLD_BAS_SOURCE_INDEX",
                                         "error_type":type(exc).__name__,
                                         "error":str(exc)[:450],
                                         "animal_rows_opened":0}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if all(x.get("status","").startswith("HOLD") for x in (
        result["AADC_EAST_ANTARCTIC_BOUNDARIES"],result["BAS_SOUTH_SANDWICH_UAV"]
    )):
        raise SystemExit(2)


if __name__=="__main__":
    main()
