#!/usr/bin/env python3
"""AADC V12: original public workbook COLUMN names and actual sheet relations.

Only reads the first row of each author-original worksheet and its
corresponding sharedStrings entries; no site/occupancy response rows parsed,
no ecological effects. Unlike the V11 reconnaissance, resolves worksheet
r:id relationship mapping rather than assuming sheet1/sheet2 by list order.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import posixpath
from urllib.parse import quote
import xml.etree.ElementTree as ET
import zipfile

import requests
import xlrd

from audit_aadc_original_workbook_headers_v11 import (
    HOST,DATASETS,SOURCE_FILES,
    trusted_response_get, public_dataset_manifests, MIME_LIMIT,
)

PINNED_FILES={
    "geographic_potential_sites":"ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294",
    "penguin_original_occupancy":"8b38aa86f0ef2a0a9fe8c5bb13da904a9f2431cd503644b962b6e116ac3187ac",
    "flying_seabird_original_occupancy":"4a03d8efc8f1579b2eafd982811c39edc00d2c87d49e990f93c6411db6860360",
    "occupancy_certainty_criteria":"b7aba52732102441b4edbe438b854cb9d2dbf39542fd6fbfcd62647ae9fdd156",
}
ADDITIONAL_GEO_NAME="Potential habitat/Spatial reference systemn coastal East Antarctica.xlsx"
ADDITIONAL_GEO_SIZE_LIMIT=10_000_000


def local_name(tag):
    return tag.rsplit("}",1)[-1]


def original_sheet_headers_xlsx(data: bytes):
    with zipfile.ZipFile(io.BytesIO(data)) as workbook:
        namelist=set(workbook.namelist())
        if "xl/workbook.xml" not in namelist or "xl/_rels/workbook.xml.rels" not in namelist:
            raise ValueError("SCHEMA_STOP required actual OOXML workbook/relationships missing")
        wroot=ET.fromstring(workbook.read("xl/workbook.xml"))
        links=ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        relationship={x.get("Id"):x.get("Target") for x in links
                      if local_name(x.tag)=="Relationship"}
        sheets=[]
        header_indices=set()
        for sheet in wroot.iter():
            if local_name(sheet.tag)!="sheet":
                continue
            nm=sheet.get("name")
            rid=sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            if rid not in relationship:
                raise ValueError("SCHEMA_STOP sheet r:id unresolved for "+str(nm))
            target=relationship[rid]
            if target.startswith("/"): filepath=target.lstrip("/")
            else: filepath=posixpath.normpath(posixpath.join("xl",target))
            if not filepath.startswith("xl/worksheets/") or filepath not in namelist:
                raise ValueError("SCHEMA_STOP original sheet relationship resolves outside worksheet")
            header=[]
            extent=None
            with workbook.open(filepath) as content:
                for event,node in ET.iterparse(content,events=("start","end")):
                    tag=local_name(node.tag)
                    if event=="start" and tag=="dimension":
                        extent=node.get("ref")
                    if event=="end" and tag=="row":
                        for c in node.iter():
                            if local_name(c.tag)!="c":
                                continue
                            type_=c.get("t")
                            raw=next((s.text for s in c.iter()
                                      if local_name(s.tag)=="v"),None)
                            inline="".join((s.text or "") for s in c.iter()
                                           if local_name(s.tag)=="t")
                            if type_=="s" and raw is not None:
                                idx=int(raw)
                                header_indices.add(idx)
                                value={"shared_id":idx}
                            else:
                                value={"plain_first_row":inline or raw}
                            header.append({"column_coordinate":c.get("r"),**value})
                        break
            sheets.append({
                "sheet_name":nm,
                "real_original_sheet_path":filepath,
                "declared_extent":extent,
                "raw_first_row_cells":header,
                "original_biological_rows_parsed":0,
            })
        if not sheets:
            raise ValueError("SCHEMA_STOP workbook has zero real worksheets")
        lookup={}
        if header_indices:
            if "xl/sharedStrings.xml" not in namelist:
                raise ValueError("SCHEMA_STOP XLSX header references nonexistent sharedStrings")
            # Parse only as far into the original *shared-string* sequence as
            # required by first-row indexes. No worksheet record row below
            # row 1 is opened.
            with workbook.open("xl/sharedStrings.xml") as stream:
                index=0
                for event,cell in ET.iterparse(stream,events=("end",)):
                    if local_name(cell.tag)=="si":
                        if index in header_indices:
                            lookup[index]="".join(
                                (x.text or "") for x in cell.iter()
                                if local_name(x.tag)=="t")
                        index+=1
                        if index>max(header_indices):
                            break
                        cell.clear()
            if set(lookup)!=header_indices:
                raise ValueError("SCHEMA_STOP original header shared string IDs out of range")
        for sheet in sheets:
            result=[]
            for cell in sheet.pop("raw_first_row_cells"):
                name=(lookup[cell["shared_id"]] if "shared_id" in cell
                      else cell["plain_first_row"])
                result.append(str(name).strip() if name is not None else "")
            sheet["original_first_row_headers"]=result
    return {"workbook_format":"XLSX_OOXML",
            "original_sheets":sheets,"original_biological_rows_parsed":0}


def original_sheet_headers_xls(data:bytes):
    if not data.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        raise ValueError("SCHEMA_STOP original legacy .xls not OLE2")
    try:
        book=xlrd.open_workbook(file_contents=data,on_demand=True)
    except Exception as exc:
        raise ValueError("SCHEMA_STOP invalid original binary BIFF Excel source") from exc
    sheets=[]
    try:
        for name in book.sheet_names():
            sheet=book.sheet_by_name(name)
            first=sheet.row_values(0) if sheet.nrows else []
            sheets.append({
                "sheet_name":name,
                "original_sheet_rows_including_header":sheet.nrows,
                "original_sheet_columns":sheet.ncols,
                "original_first_row_headers":[str(x).strip() for x in first][:70],
                "original_biological_rows_parsed":0
            })
    finally:
        book.release_resources()
    return {"workbook_format":"XLS_BIFF_OLE2",
            "original_sheets":sheets,"original_biological_rows_parsed":0}


def audit_original(session):
    found,index=public_dataset_manifests(session)
    out={}
    specs={**{key:("5959",fname) for key,fname in SOURCE_FILES.items()},
           "published_4884_spatial_reference_workbook":("4344",ADDITIONAL_GEO_NAME)}
    for label,(eds,path) in specs.items():
        expected=found[eds]["original_object_manifest"]["file_descriptors"]
        if path not in expected:
            raise ValueError("SOURCE_STOP archived publisher source object absent: "+path)
        uuid=found[eds]["uuid"]
        url=(f"https://{HOST}/eds/api/dataset/{quote(uuid)}/object/download?"
             f"prefix={quote(path,safe='')}")
        raw,receipt=trusted_response_get(
            session,url,ADDITIONAL_GEO_SIZE_LIMIT if label.startswith("published_") else MIME_LIMIT)
        if label in PINNED_FILES and receipt["source_sha256"]!=PINNED_FILES[label]:
            raise ValueError("SOURCE_STOP original author workbook SHA drift: "+label)
        if expected[path].get("bytes") is not None and int(expected[path]["bytes"])!=len(raw):
            raise ValueError("SOURCE_STOP official file manifest bytes differ from actual public file")
        if path.lower().endswith(".xlsx"):
            schema=original_sheet_headers_xlsx(raw)
        elif path.lower().endswith(".xls"):
            schema=original_sheet_headers_xls(raw)
        else:
            raise ValueError("SCHEMA_STOP unexpected original author table format")
        out[label]={
            "source_publisher_doi":DATASETS[eds]["doi"],
            "source_eds_id":eds,
            "original_filepath":path,
            "original_sha256":receipt["source_sha256"],
            "original_bytes":len(raw),
            "source_host":receipt["resolved_hostname"],
            **schema
        }
    return out,index


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",type=Path,required=True)
    args=p.parse_args()
    receipt={"status":"HOLD_AADC_ORIGINAL_HEADER_SEMANTICS",
             "original_bird_search_rows_opened":0,
             "effects_fitted":0}
    try:
        with requests.Session() as session:
            tables,public_index=audit_original(session)
        receipt={
            "status":"AADC_ORIGINAL_SITE_AND_OCCUPANCY_HEADERS_DECODED_NO_BIOLOGICAL_ROWS",
            "source_public_index_sha256":public_index["source_sha256"],
            "original_source_sheets":tables,
            "original_bird_search_rows_opened":0,
            "effects_fitted":0,
            "next_action":"Freeze site×species×season presence/verified absence eligibility and nesting-guild model before opening original search rows"
        }
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:550]
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
