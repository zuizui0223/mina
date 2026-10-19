#!/usr/bin/env python3
"""Locate original AADC East Antarctic potential-site and seabird search-event data.

Source/format/schema discovery ONLY, before opening records or fitting ecology.
Reproduce every official URL, redirect, original bytes and SHA256. No invented
source-site zeros; no assumed PDF/Excel content; no private authentication.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse
import zipfile
import xml.etree.ElementTree as ET

import requests

DATASETS = {
    "all_potential_icefree_sites_4884": {
        "doi": "10.26179/53yk-8z83",
        "url": "https://data.aad.gov.au/eds/4344/download"
    },
    "eight_seabirds_effort_occupancy": {
        "doi": "10.26179/5n29-r073",
        "url": "https://data.aad.gov.au/eds/5959/download"
    },
}
MAX_BYTES = 100_000_000
MAX_TOTAL_UNCOMPRESSED = 350_000_000
MAX_ITEMS = 120
HEADERS_PER_CONTAINER = 15


def download_source(src, dest):
    with requests.get(src["url"], timeout=(20, 100), stream=True,
                      headers={"User-Agent":"Antarctic-island-original-AADC-scientific-data-audit/1.0"},
                      allow_redirects=True) as resp:
        resp.raise_for_status()
        u=urlparse(resp.url)
        if u.scheme!="https" or not (u.hostname=="data.aad.gov.au" or u.hostname.endswith(".aad.gov.au")):
            raise ValueError("SOURCE_STOP unverified AADC download redirect to "+str(u.hostname))
        sha=hashlib.sha256()
        n=0
        with dest.open("wb") as out:
            for chunk in resp.iter_content(chunk_size=65536):
                if not chunk:continue
                n+=len(chunk)
                if n>MAX_BYTES:
                    raise ValueError("SOURCE_STOP original data payload larger than bounded source download")
                sha.update(chunk);out.write(chunk)
        return {
            "doi":src["doi"],"source_url":src["url"],
            "resolved_host":u.hostname,"resolved_path":u.path,
            "content_type":resp.headers.get("Content-Type"),
            "content_disposition":resp.headers.get("Content-Disposition"),
            "source_bytes":n,"source_sha256":sha.hexdigest(),
        }


def is_excel(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        return "[Content_Types].xml" in z.namelist() and "xl/workbook.xml" in z.namelist()


def workbook_structure(blob):
    """Read XML sheet metadata ONLY; never read biological spreadsheet rows."""
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        w=ET.fromstring(z.read("xl/workbook.xml"))
        sheets=[]
        for e in w.findall(".//{*}sheets/{*}sheet"):
            sheets.append({"sheet_name":e.attrib.get("name"),
                           "sheet_index_metadata":e.attrib.get("sheetId"),
                           "has_sheet_data_opened":False})
        return {"format":"xlsx_zip","sheets":sheets,
                "source_record_rows_opened":0}


def payload_structure(blob, source_name):
    if blob.startswith((b"PK\x03\x04",b"PK\x05\x06")):
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            infos=z.infolist()
            if len(infos)>MAX_ITEMS:
                raise ValueError("SCHEMA_STOP unexpectedly many archive members")
            if sum(i.file_size for i in infos)>MAX_TOTAL_UNCOMPRESSED:
                raise ValueError("SCHEMA_STOP uncompressed AADC archive too large")
            if z.testzip() is not None:
                raise ValueError("SCHEMA_STOP source archive CRC failure")
            if "[Content_Types].xml" in z.namelist():
                return {"format":"xlsx_zip","workbook":workbook_structure(blob),
                        "original_archive_member_count":len(infos)}
            members=[]
            for i in infos:
                if i.is_dir():continue
                if i.filename.startswith("/") or ".." in Path(i.filename).parts:
                    raise ValueError("SOURCE_STOP unsafe AADC archive member name")
                meta={"original_member_name":i.filename,"original_member_bytes":i.file_size,
                      "original_member_type":Path(i.filename).suffix.lower()}
                # Original table *header* only; do not select records based on
                # observed occupancy effect or reclassify absence.
                if i.filename.lower().endswith(".csv"):
                    with z.open(i) as f:
                        first=f.readline(5000)
                    if b"\n" in first and b"<html" not in first.lower():
                        meta["first_line_column_headers"]=next(
                            csv.reader(io.StringIO(first.decode("utf-8-sig").strip())))
                if i.filename.lower().endswith(".xlsx"):
                    # Handle inner Excel ZIP structure without reading biological rows.
                    if i.file_size<MAX_BYTES:
                        meta["workbook_schema_only"]=workbook_structure(z.read(i))
                members.append(meta)
            return {"format":"zip_archive","original_archive_member_count":len(infos),
                    "original_archived_member_schema":members[:MAX_ITEMS],
                    "biological_record_rows_opened":0}
    if blob[:100].lstrip().lower().startswith((b"<html",b"<!doctype")):
        raise ValueError("SOURCE_STOP AADC supplied HTML not data archive")
    if blob.startswith(b"%PDF"):
        return {"format":"pdf","note":"PDF is not a machine-readable site/event table; further raw structured source required",
                "original_record_rows_opened":0}
    if blob.startswith(b"\xd0\xcf\x11\xe0"):
        return {"format":"legacy_xls_OLE2","note":"Legacy binary workbook needs a documented reader; no rows opened",
                "original_record_rows_opened":0}
    if blob[:400].count(b",")>=2 or blob[:400].count(b"\t")>=2:
        first=blob.split(b"\n",1)[0]
        line=first.decode("utf-8-sig").strip()
        return {"format":"text_table","first_line_columns":next(csv.reader(
            io.StringIO(line),delimiter="\t" if "\t" in line else ",")),
            "original_record_rows_opened":0}
    raise ValueError("SOURCE_STOP unknown AADC original payload type")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True)
    args=p.parse_args()
    result={"status":"HOLD_AADC_SOURCE_SCHEMA","original_breeding_occurrences_read":0,
            "ecological_effects_fitted":0,"records":{}}
    ok=True
    import tempfile
    with tempfile.TemporaryDirectory(prefix="aadc-macro-v9-") as temp:
        for key,src in DATASETS.items():
            dest=Path(temp)/(key+".payload")
            try:
                provenance=download_source(src,dest)
                details=payload_structure(dest.read_bytes(),key)
                result["records"][key]={**provenance,**details}
            except Exception as e:
                ok=False
                result["records"][key]={
                    "source_doi":src["doi"],"source_url":src["url"],
                    "status":"HOLD_SOURCE_ACCESS_OR_SCHEMA",
                    "error_type":type(e).__name__,
                    "error":str(e)[:300],
                    "original_breeding_occurrences_read":0,
                }
    result["status"]=(
        "AADC_ORIGINAL_POTENTIAL_SITES_AND_SURVEY_SCHEMA_VERIFIED"
        if ok else "HOLD_AADC_SOURCE_ACCESS_OR_SCHEMA")
    Path(args.out_json).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,ensure_ascii=False))
    if not ok:
        raise SystemExit(2)


if __name__=="__main__":
    main()
