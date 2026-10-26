#!/usr/bin/env python3
"""V16 traverse BAS Hart publisher's original nested group-ID archive manifest.

Only publisher directory/file metadata; no penguin nest observations or values.
Fixes V9 omission of original RAMADDA \`id\`+type=group entries.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter,deque,defaultdict
import hashlib
import json
from pathlib import Path
from urllib.parse import quote,urlparse,unquote

import requests
from audit_multiisland_original_colony_sources_v9 import (
    BAS_ROOT_URL,BAS_ENTRY_ID,BAS_HOST,MAX_BAS_FOLDERS,
    original_bas_manifest
)

EXPECTED_CSV=31
EXPECTED_TIFF=127
MAX_ENTRIES=800
MAX_GROUPS=150
MAIN_ROOT=BAS_ENTRY_ID
ALLOWED=("ramadda.data.bas.ac.uk","194.66.5.50")
PUBLISHER_ROOT_PREFIX="synth:"+BAS_ENTRY_ID+":"
TOP_LOCALITIES={
    "Ashen_Hills","Beach_Point","Bellingshausen","Candlemas_Island",
    "Herd_Point","Hewison_Point","Zavodovski"
}


def validate_group_id(source_id:str,allow_root=True):
    if source_id==MAIN_ROOT and allow_root:return source_id
    if not source_id.startswith(PUBLISHER_ROOT_PREFIX):
        raise ValueError("SOURCE_STOP archive group outside verified dataset root")
    tail=source_id[len(PUBLISHER_ROOT_PREFIX):]
    try:
        content=base64.b64decode(tail,validate=True).decode("utf-8")
    except Exception as e:
        raise ValueError("SOURCE_STOP invalid publisher folder base64 identity") from e
    if not content.startswith("/") or "//" in content or "/../" in content or "\\" in content:
        raise ValueError("SOURCE_STOP unexpected publisher folder path")
    return source_id


def decode_publisher_relative(source_id):
    if source_id==MAIN_ROOT:return ""
    validate_group_id(source_id)
    return base64.b64decode(source_id[len(PUBLISHER_ROOT_PREFIX):],validate=True).decode("utf-8").lstrip("/")


def original_entry_url(source_id):
    validate_group_id(source_id)
    return (
        f"https://{BAS_HOST}/repository/entry/show?"
        f"entryid={quote(source_id,safe='')}&output=default.csv"
    )


def canonical_file_row(row,group_id):
    identity=row.get("id","")
    validate_group_id(identity)
    if str(row.get("type",""))!="file":
        raise ValueError("SCHEMA_STOP canonical original file not publisher type=file")
    src=str(row.get("url",""))
    parsed=urlparse(src)
    if parsed.hostname not in ALLOWED or parsed.scheme not in ("https","http"):
        raise ValueError("SOURCE_STOP original published file URL hostname outside BAS")
    if unquote(parsed.path)!=f"/repository/entry/get/{str(row.get('name',''))}":
        raise ValueError("SOURCE_STOP original filename and publisher file URL mismatch")
    rel=decode_publisher_relative(identity)
    parent=decode_publisher_relative(group_id)
    if not rel.startswith(parent+("/" if parent else "")):
        raise ValueError("SOURCE_STOP original file outside publisher folder")
    filebase=rel.rsplit("/",1)[-1]
    if filebase!=str(row["name"]):
        raise ValueError("SOURCE_STOP original publisher name != encoded file basename")
    folder=rel.split("/")[0]
    if folder not in TOP_LOCALITIES and rel!="SSI_count_results.csv":
        raise ValueError("SOURCE_STOP original file unrecognized top-level locality")
    # Canonical source URL copied semantically from original publisher (HTTPS
    # and original query preserved); no data bytes are fetched in this stage.
    final=f"https://{BAS_HOST}{parsed.path}?{parsed.query}"
    return {
        "original_publisher_archive_id":identity,
        "original_archive_relative_path":rel,
        "top_level_source_locality_folder":folder if rel!="SSI_count_results.csv" else "ROOT_COUNT_RESULTS",
        "source_parent_original_group_id":group_id,
        "original_publisher_file_name":filebase,
        "source_file_url_https":final,
        "original_source_file_type":filebase.lower().rsplit(".",1)[-1] if "." in filebase else "none",
        "biological_rows_read":0
    }


def traverse_publisher_archives(session):
    queue=deque([(MAIN_ROOT,None)])
    visited=set()
    receipts=[]
    files=[]
    pending_failed=[]
    while queue:
        if len(visited)>=MAX_GROUPS:
            raise ValueError("SOURCE_STOP original publisher folder tree unexpectedly large")
        group,_parent=queue.popleft()
        if group in visited:continue
        validate_group_id(group)
        visited.add(group)
        path=decode_publisher_relative(group)
        try:
            rows,source=original_bas_manifest(session,original_entry_url(group))
        except Exception as e:
            pending_failed.append({
                "original_publisher_group_id":group,"source_path":path,
                "error_type":type(e).__name__,"error":str(e)[:300]})
            continue
        receipts.append({
            "original_publisher_group_id":group,
            "source_path":path,
            "source_manifest_row_count":len(rows),
            "original_publisher_manifest_SHA256":source["source_csv_sha256"],
            "source_manifest_bytes":source["source_bytes"],
        })
        for row in rows:
            if len(files)>MAX_ENTRIES:
                raise ValueError("SOURCE_STOP original source manifest has too many files")
            typ=str(row.get("type",""))
            origin=row.get("id","")
            if typ=="group":
                validate_group_id(origin)
                parent=decode_publisher_relative(group)
                child=decode_publisher_relative(origin)
                if (parent and not child.startswith(parent+"/")) or child==parent:
                    raise ValueError("SOURCE_STOP original child group escaped folder")
                queue.append((origin,group))
            elif typ=="file":
                files.append(canonical_file_row(row,group))
            else:
                raise ValueError("SCHEMA_STOP original publisher directory row type unexpected")
    allgroups=Counter(x["top_level_source_locality_folder"] for x in files)
    counts=Counter(x["original_source_file_type"] for x in files)
    duplicate_paths=len(files)-len({
        x["original_archive_relative_path"] for x in files})
    if duplicate_paths:
        raise ValueError("SOURCE_STOP duplicate original publisher file paths")
    original_current_complete=(
        len(files)>=EXPECTED_CSV+EXPECTED_TIFF and
        counts["csv"]>=EXPECTED_CSV and
        counts["tif"]+counts["tiff"]>=EXPECTED_TIFF and not pending_failed
    )
    exact_catalogue_counts=(
        counts["csv"]==EXPECTED_CSV and
        counts["tif"]+counts["tiff"]==EXPECTED_TIFF and
        len(files)==EXPECTED_CSV+EXPECTED_TIFF
    )
    state=(
        "VERIFIED_ORIGINAL_SOURCE_FILES_MATCH_PUBLISHED_INVENTORY"
        if original_current_complete and exact_catalogue_counts else
        "VERIFIED_ORIGINAL_SOURCE_FILES_PUBLISHER_SUMMARY_COUNT_DISCREPANCY"
        if original_current_complete else
        "HOLD_INCOMPLETE_ORIGINAL_SOURCE_FILE_MANIFEST"
    )
    return {
       "status":state,
       "original_BAS_Hart_DOI":"10.5285/28222725-c53d-40f4-9350-49c368899f0b",
       "original_archive_source_root_id":BAS_ENTRY_ID,
       "original_publisher_group_manifest_count":len(receipts),
       "publisher_directory_manifest_SHA_receipts":receipts,
       "original_filename_inventory_total":len(files),
       "original_file_types":dict(sorted(counts.items())),
       "original_published_metadata_expected_CSV":EXPECTED_CSV,
       "original_published_metadata_expected_TIFF":EXPECTED_TIFF,
       "original_file_manifest_exactly_equals_published_2022_summary":exact_catalogue_counts,
       "original_file_archive_recursively_complete_under_source_count_gate":original_current_complete,
       "source_inventory_discrepancy_explained_by_2022_paper_metadata":False,
       "original_top_locality_folder_file_counts":dict(sorted(allgroups.items())),
       "original_all_file_metadata_only":files,
       "unavailable_official_publisher_nested_group_ids":pending_failed,
       "original_penguin_nest_coordinate_rows_read":0,
       "original_SSI_count_values_read":0,
       "south_sandwich_island_localities_are_independent_physical_islands_verified":False,
       "original_2022_chinstrap_Zavodovski_recount_is_true_2020_simultaneous":False,
       "actual_original_field_observation_data_loaded":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    summary={"status":"HOLD_BAS_NESTED_GROUP_SOURCE_MANIFEST_V16",
             "original_penguin_nest_coordinate_rows_read":0}
    try:
        with requests.Session() as s:
            summary=traverse_publisher_archives(s)
    except Exception as e:
        summary["error_type"]=type(e).__name__
        summary["error"]=str(e)[:1000]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    # Avoid dumping all 158 publisher file URLs in public CI logs, keep receipt.
    print(json.dumps({k:v for k,v in summary.items()
                      if k not in ("original_all_file_metadata_only",
                                   "publisher_directory_manifest_SHA_receipts")},ensure_ascii=False))
    if summary["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
