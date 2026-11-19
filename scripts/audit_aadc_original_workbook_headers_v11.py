#!/usr/bin/env python3
"""AADC V11: download ORIGINAL published East Antarctic geography/occupancy
workbooks via verified official public REST API, then inspect HEADERS only.

Unlike legacy /eds/5959/download (generic HTML SPA), the public AADC browser
uses /eds/api/dataset and /eds/api/dataset/{uuid}/objects. File downloads use
the original AADC public /object/download?prefix= path. NO bird data rows,
site occupancies, slopes, p-values, or trait effects are opened here.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import quote,urlparse
import xml.etree.ElementTree as ET
import zipfile

import requests

HOST="data.aad.gov.au"
LIST_API=f"https://{HOST}/eds/api/dataset?size=10000"
DATASETS={
    "4344":{"uuid":"3F139A80-800D-46BD-A7C0-D29734DAE090",
            "doi":"10.26179/53yk-8z83"},
    "5959":{"uuid":"b766a3e4-ae94-40c0-b340-9e544d8f5dc3",
            "doi":"10.26179/5n29-r073"},
}
SOURCE_FILES={
    "geographic_potential_sites":
        "2_Site and search effort and occupancy data/geog_sites_all.xlsx",
    "penguin_original_occupancy":
        "2_Site and search effort and occupancy data/occupancy_penguin.xlsx",
    "flying_seabird_original_occupancy":
        "2_Site and search effort and occupancy data/occupancy_seabird.xls",
    "occupancy_certainty_criteria":
        "2_Site and search effort and occupancy data/occupancy_certainty.xlsx",
}
MIME_LIMIT=45_000_000
LIST_LIMIT=30_000_000


def trusted_response_get(session,url,cap,expected_json=False):
    if urlparse(url).scheme!="https" or urlparse(url).hostname!=HOST:
        raise ValueError("SOURCE_STOP original AADC URL not official HTTPS")
    with session.get(url,timeout=(20,95),stream=True,
                     headers={"User-Agent":"mina-original-AADC-public-Antarctic-source/1.0"}) as response:
        response.raise_for_status()
        resolved=urlparse(response.url)
        if resolved.scheme!="https" or not (
            resolved.hostname==HOST
            or resolved.hostname.endswith(".data.aad.gov.au")
            or resolved.hostname.endswith(".amazonaws.com")
        ):
            raise ValueError("SOURCE_STOP unexpected original publisher redirect: "+str(resolved.hostname))
        out=bytearray()
        for chunk in response.iter_content(chunk_size=32768):
            out.extend(chunk)
            if len(out)>cap:
                raise ValueError("SOURCE_STOP bounded public original AADC resource oversized")
        mime=response.headers.get("Content-Type","")
    raw=bytes(out)
    if expected_json:
        if not raw.startswith((b"[",b"{")):
            raise ValueError("SOURCE_STOP public dataset API returned non-JSON")
    elif raw[:120].lstrip().lower().startswith((b"<html",b"<!doctype html")):
        raise ValueError("SOURCE_STOP official AADC object download returned HTML SPA")
    return raw,{"resolved_hostname":resolved.hostname,"content_type":mime,
                "source_sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}


def public_dataset_manifests(session):
    raw,source=trusted_response_get(session,LIST_API,LIST_LIMIT,True)
    listing=json.loads(raw)
    if not isinstance(listing,list):
        raise ValueError("SCHEMA_STOP official public dataset API list not list")
    found={}
    for eds,expected in DATASETS.items():
        selected=[r for r in listing if str(r.get("eds_id",""))==eds]
        if len(selected)!=1:
            raise ValueError("SOURCE_STOP missing/duplicate requested released eds_id "+eds)
        r=selected[0]
        if str(r.get("uuid","")).casefold()!=expected["uuid"].casefold():
            raise ValueError("SOURCE_STOP public eds ID UUID changed "+eds)
        found[eds]={
            "uuid":r["uuid"],
            "eds_id":eds,
            "original_Doi":expected["doi"],
            "source_title":str(r.get("dataset_name",""))[:180],
            "original_metadata_entry_id":str(r.get("metadata_entry_id",""))[:180],
            "access_status":str(r.get("dataset_visibility_status",""))[:100],
        }
        u=f"https://{HOST}/eds/api/dataset/{quote(r['uuid'])}/objects?recursive=true&removeBasePath=true"
        content,meta=trusted_response_get(session,u,LIST_LIMIT,True)
        objects=json.loads(content)
        if not isinstance(objects,list):
            raise ValueError("SCHEMA_STOP publisher objects not array")
        keys=[str(x.get("name","")) for x in objects if isinstance(x,dict)]
        if not keys:
            raise ValueError("SCHEMA_STOP no public AADC archived files in dataset "+eds)
        found[eds]["original_object_manifest"]={
            "response_sha256":meta["source_sha256"],
            "original_listed_object_count":len(objects),
            "file_names":keys,
            "file_descriptors":{str(x["name"]):{"bytes":x.get("size"),
                                  "last_modified":x.get("lastModified")}
                              for x in objects if isinstance(x,dict) and x.get("name")},
        }
    return found,source


def _xml_local(tag):
    return tag.rsplit("}",1)[-1]


def original_xlsx_sheet_headers(raw):
    """Read original workbook metadata and first ROW only, no occupancy rows."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if "xl/workbook.xml" not in z.namelist():
            raise ValueError("SCHEMA_STOP ZIP but not XLSX")
        book=ET.fromstring(z.read("xl/workbook.xml"))
        sheets=[
            {"name":el.get("name"),"sheet_id":el.get("sheetId")}
            for el in book.iter() if _xml_local(el.tag)=="sheet"
        ]
        if not sheets:
            raise ValueError("SCHEMA_STOP XLSX has no worksheets")
        results=[]
        for index,item in enumerate(sheets):
            # All publisher workbooks observed so far include sequential sheets,
            # but do not silently invent an absent file.
            name=f"xl/worksheets/sheet{index+1}.xml"
            if name not in z.namelist():
                results.append({**item,"first_line_status":"HOLD_NO_SIMPLE_SEQUENTIAL_XML_SHEET"})
                continue
            with z.open(name) as stream:
                try:
                    header=[]
                    dimensions=None
                    for event,el in ET.iterparse(stream,events=("start","end")):
                        typ=_xml_local(el.tag)
                        if event=="start" and typ=="dimension":
                            dimensions=el.get("ref")
                        if event=="end" and typ=="row":
                            # Extract only first worksheet row XML; shared strings
                            # are reported as original indexes, not resolved to
                            # a full table including bird values.
                            for cell in el.iter():
                                if _xml_local(cell.tag)=="c":
                                    val=next((x.text for x in cell.iter()
                                              if _xml_local(x.tag)=="v"),None)
                                    text="".join((x.text or "") for x in cell.iter()
                                                 if _xml_local(x.tag)=="t")
                                    header.append({"cell":cell.get("r"),"type":cell.get("t"),
                                                   "raw_first_row_value":text or val})
                            break
                    results.append({**item,"worksheet_declared_extent":dimensions,
                                    "first_row_values_or_sharedString_indices":header[:35],
                                    "original_occupancy_rows_opened":0})
                except ET.ParseError as error:
                    raise ValueError("SCHEMA_STOP malformed original xlsx worksheet") from error
    return {"format":"xlsx","sheets":results,"original_biological_rows_opened":0}


def binary_xls_source_structure(raw):
    # Legacy Excel 97-2003 OLE binary file. xlrd is required for *later*
    # content; at Stage 1 do not decode biological rows or assign absences.
    if not raw.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        raise ValueError("SCHEMA_STOP original legacy seabird XLS is not OLE2")
    return {"format":"legacy_xls_ole2","original_biological_rows_opened":0,
            "header_gate":"HOLD_BINARY_SHEET_HEADER_NEEDS_DOCUMENTED_LEGACY_READER"}


def get_original_source_headers(session,found):
    manifest=found["5959"]["original_object_manifest"]["file_descriptors"]
    result={}
    for label,path in SOURCE_FILES.items():
        if path not in manifest:
            raise ValueError("SOURCE_STOP published 5959 source object missing: "+path)
        url=(f"https://{HOST}/eds/api/dataset/{quote(DATASETS['5959']['uuid'])}"
             f"/object/download?prefix={quote(path,safe='')}")
        raw,meta=trusted_response_get(session,url,MIME_LIMIT)
        if path.lower().endswith(".xlsx"):
            if not raw.startswith(b"PK"):
                raise ValueError("SOURCE_STOP original Excel workbook not OOXML ZIP: "+path)
            schema=original_xlsx_sheet_headers(raw)
        elif path.lower().endswith(".xls"):
            schema=binary_xls_source_structure(raw)
        else:
            raise ValueError("SOURCE_STOP unexpected source format")
        result[label]={"source_original_name":path,
                       "expected_source_manifest_size":manifest[path]["bytes"],
                       **meta,**schema}
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True,type=Path)
    args=p.parse_args()
    result={"status":"HOLD_AADC_OFFICIAL_PUBLIC_DATASET_API",
            "original_search_or_occupancy_rows_opened":0}
    try:
        with requests.Session() as session:
            sources,origin=public_dataset_manifests(session)
            headers=get_original_source_headers(session,sources)
        # Small public results only; no full 258-map file roster echoed to GitHub
        for item in sources.values():
            item["original_object_manifest"]["file_names"]=[
                name for name in item["original_object_manifest"]["file_names"]
                if name.endswith((".xls",".xlsx",".csv",".zip",".shp",".dbf"))
            ][:70]
            item["original_object_manifest"].pop("file_descriptors",None)
        result={"status":"AADC_PUBLIC_4844_SITES_AND_8_SEABIRDS_ORIGINAL_WORKBOOK_SCHEMAS",
                "source_datasets":sources,
                "source_public_index_sha256":origin["source_sha256"],
                "source_workbook_headers":headers,
                "source_site_occupancy_rows_opened":0,
                "ecological_effects_computed":0,
                "next_stage_requires":"Explicit original survey-site join and presence/absence certainty schema before trait×island effects"}
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:500]
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
