#!/usr/bin/env python3
"""V15 literal BAS Hart (2022) archive root folder metadata, no bird data values.

The V9 root manifest discovered 8 original entries but its generic directory
parser recorded only one CSV and missed apparent nested folders. This script
prints original publisher manifest ROW METADATA ONLY, and validates publisher
source identity. No arbitrary guessed file paths or biological rows opened.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import requests

from audit_multiisland_original_colony_sources_v9 import (
    BAS_ROOT_URL, BAS_ZAVO_URL, original_bas_manifest
)


def source_rows(rows):
    selected=[]
    for i,row in enumerate(rows):
        selected.append({
            "publisher_row_index":i,
            "original_row_values":{str(k):str(v)[:500] for k,v in row.items()},
            "is_source_filedescriptor_only":True
        })
    return selected


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result={"status":"HOLD_BAS_ORIGINAL_FOLDER_FORMAT_V15","biological_rows_opened":0}
    try:
        with requests.Session() as sess:
            rows,source=original_bas_manifest(sess,BAS_ROOT_URL)
            nest,nestsrc=original_bas_manifest(sess,BAS_ZAVO_URL)
        result={
            "status":"BAS_HART_2022_ORIGINAL_DIRECTORY_SCHEMA_V15",
            "original_dataset_doi":"10.5285/28222725-c53d-40f4-9350-49c368899f0b",
            "official_root":source,
            "official_root_original_directory_rows":source_rows(rows),
            "official_zavo_nest_folder":nestsrc,
            "official_zavo_original_directory_rows":source_rows(nest),
            "biological_rows_opened":0,
            "original_2022_ZAVO_chinstrap_survey_is_2020_simultaneous":False
        }
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:700]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
