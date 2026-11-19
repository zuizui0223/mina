#!/usr/bin/env python3
"""Source-first schema audit of original AADC 2025 8-seabird and habitat-site files.

Fetches only original publisher XLS/XLSX; validates exact UUID, filename and
publisher-reported size before reading spreadsheet schema. Does not fit or
summarize bird occupation values, artificial A/P transitions or rock effects.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import quote,urlparse
import requests
import xlrd
from openpyxl import load_workbook

HOST="data.aad.gov.au"
SETS={
"2025_seabird":{"uuid":"b766a3e4-ae94-40c0-b340-9e544d8f5dc3",
    "name":"2_Site and search effort and occupancy data/occupancy_seabird.xls",
    "bytes":5259776,"eds_id":5959},
"2025_geographic_sites":{"uuid":"b766a3e4-ae94-40c0-b340-9e544d8f5dc3",
    "name":"2_Site and search effort and occupancy data/geog_sites_all.xlsx",
    "bytes":533501,"eds_id":5959},
"2025_certainty":{"uuid":"b766a3e4-ae94-40c0-b340-9e544d8f5dc3",
    "name":"2_Site and search effort and occupancy data/occupancy_certainty.xlsx",
    "bytes":21242,"eds_id":5959},
"2025_penguin":{"uuid":"b766a3e4-ae94-40c0-b340-9e544d8f5dc3",
    "name":"2_Site and search effort and occupancy data/occupancy_penguin.xlsx",
    "bytes":817591,"eds_id":5959},
"2016_icefree_site_atlas":{"uuid":"3F139A80-800D-46BD-A7C0-D29734DAE090",
    "name":"Potential habitat/Spatial reference systemn coastal East Antarctica.xlsx",
    "bytes":336800,"eds_id":4344}
}
PUBLISHER_EDS_MANIFESTS={
"5959":"c9f6f34ccffe66507beaa2af8eeccf29064af22608be362cabbe5f7011c6ba58",
"4344":"bb4020917338bf50f1c7155357d9899852699fde16d8ac207835e1166116968b",
}
MAX_DOWNLOAD=7_000_000
TEXT_FIELDS=("site","geog","season","species","region","subgroup","survey",
             "date","observer","method","effort","occup","state",
             "absence","certainty","precision","source","area","habitat",
             "latitude","longitude","lat","lon","presence","type","status")

def download_original(session,spec):
    url=(f"https://{HOST}/eds/api/dataset/{quote(spec['uuid'])}"
         f"/object/download?prefix={quote(spec['name'],safe='')}")
    if urlparse(url).hostname!=HOST:
        raise ValueError("not original AADC source host")
    with session.get(url,stream=True,timeout=(22,120),
                     headers={"User-Agent":"mina-2026-11-original-AADC-schema-audit"}) as r:
        r.raise_for_status()
        final=urlparse(r.url)
        if final.scheme!="https" or not (
            final.hostname==HOST or final.hostname.endswith(".data.aad.gov.au")
            or final.hostname.endswith(".amazonaws.com")):
            raise ValueError("unverified original AADC redirect")
        raw=bytearray()
        for b in r.iter_content(65536):
            raw.extend(b)
            if len(raw)>MAX_DOWNLOAD:
                raise ValueError("publisher object exceeds size cap")
    if len(raw)!=spec["bytes"]:
        raise ValueError(f"original byte-size drift {len(raw)} != {spec['bytes']}")
    return bytes(raw),{"url":url,"resolved_host":final.hostname,
                       "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}

def formatted_header(rows):
    report=[]
    for ridx,row in enumerate(rows):
        names=[]
        for cidx,val in enumerate(row):
            if val is None or val=="":
                continue
            # Avoid surfacing numerical animal counts; source TEXT headers only.
            if isinstance(val,str) and not re.fullmatch(r"[-+]?\d+(?:\.\d+)?",val.strip()):
                names.append({"column":cidx+1,"text":val.strip()[:95]})
            elif ridx==0:
                names.append({"column":cidx+1,"type":"NUMERIC_CELL_REDACTED"})
        if names:report.append({"source_row":ridx+1,"text_only_cells":names[:40]})
    return report[:7]

def inspect_workbook(raw,name):
    if name.lower().endswith(".xlsx"):
        if raw[:2]!=b"PK":raise ValueError("xlsx is not ZIP")
        wb=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
        out=[]
        try:
            for ws in wb.worksheets[:30]:
                preview=[]
                for idx,row in enumerate(ws.iter_rows(values_only=True)):
                    if idx>=7:break
                    preview.append(list(row))
                out.append({"name":ws.title,"rows":ws.max_row,
                            "columns":ws.max_column,"source_headers":formatted_header(preview),
                            "values_in_biological_rows_summarized":False})
        finally:
            wb.close()
        return out
    if name.lower().endswith(".xls"):
        if raw[:8]!=bytes.fromhex("D0CF11E0A1B11AE1"):
            raise ValueError("xls is not legacy Excel file")
        book=xlrd.open_workbook(file_contents=raw,on_demand=True)
        try:
            out=[]
            for ws in book.sheets()[:30]:
                preview=[ws.row_values(i) for i in range(min(7,ws.nrows))]
                out.append({"name":ws.name,"rows":ws.nrows,"columns":ws.ncols,
                            "source_headers":formatted_header(preview),
                            "values_in_biological_rows_summarized":False})
        finally:
            book.release_resources()
        return out
    raise ValueError("not whitelisted original source spreadsheet")

def audit():
    out={"status":"ORIGINAL_AADC_2025_EIGHT_SPECIES_SCHEMA_AUDIT",
         "origin_manifest_sha256":PUBLISHER_EDS_MANIFESTS,
         "data_source_doi":{"5959":"10.26179/5n29-r073",
                            "4344":"10.26179/53yk-8z83"},
         "original_bird_effect_fitted":False,
         "original_occupancy_counts_or_A_P_events_summarized":False,
         "files":{}}
    with requests.Session() as s:
        for tag,spec in SETS.items():
            item={"eds_id":spec["eds_id"],"uuid":spec["uuid"],
                  "original_name":spec["name"],"original_manifest_bytes":spec["bytes"]}
            try:
                raw,meta=download_original(s,spec)
                sheets=inspect_workbook(raw,spec["name"])
                item.update(meta)
                item["sheets"]=sheets
                item["status"]="ORIGINAL_PUBLISHER_SPREADSHEET_SCHEMA_VERIFIED"
            except Exception as e:
                item["status"]="HOLD_SOURCE_FILE"
                item["error"]=f"{type(e).__name__}: {str(e)}"[:300]
            out["files"][tag]=item
    out["all_source_schemas_verified"]=all(
        x["status"]=="ORIGINAL_PUBLISHER_SPREADSHEET_SCHEMA_VERIFIED"
        for x in out["files"].values())
    out["scientific_gate"]="No colonization or island effect until explicit survey effort with confirmed negative state and physical patch landmass are matched to independently time-verified substrate."
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True,type=Path)
    args=p.parse_args()
    try:r=audit()
    except Exception as e:
        r={"status":"HOLD_AADC_2025_MULTISOURCE_SCHEMA","error":f"{type(e).__name__}: {e}"[:340],
           "original_bird_effect_fitted":False}
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(r,indent=2,sort_keys=True,
                                       ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":r["status"],
                      "files":{tag:{"status":v["status"],"sha256":v.get("sha256"),
                                    "sheets":[{"name":s["name"],"rows":s["rows"],"columns":s["columns"]}
                                               for s in v.get("sheets",[])]}
                                  for tag,v in r.get("files",{}).items()}},sort_keys=True,
                     ensure_ascii=False))

if __name__=="__main__":
    main()
