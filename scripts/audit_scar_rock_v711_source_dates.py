#!/usr/bin/env python3
"""Official 2025 SCAR rock-outcrop high-res SHP source and acquisition-date gate.

Reads original DBF dates without loading the large SHP geometry. No claim of
new rock, penguin A/P, or island-replicate independence.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile
import requests
import shapefile

ARCHIVE_URL = (
    "https://ramadda.data.bas.ac.uk/repository/entry/get/"
    "add_rock_outcrop_high_res_polygon_v7_11.shp.zip?"
    "entryid=synth%3A815525ca-cefe-4fbf-9224-3ee784e7de4e"
    "%3AL2FkZF9yb2NrX291dGNyb3BfaGlnaF9yZXNfcG9seWdvbl92N18xMS5zaHAuemlw"
)
SOURCE_DOI = "10.5285/815525ca-cefe-4fbf-9224-3ee784e7de4e"
MAX_BYTES = 205_000_000
MAX_UNPACKED = 850_000_000

def fetch_archive():
    h = hashlib.sha256()
    out = io.BytesIO()
    total = 0
    with requests.get(ARCHIVE_URL,stream=True,timeout=(25,150),
                      headers={"User-Agent":"mina-scar-rock-source-gate/1.0"}) as resp:
        resp.raise_for_status()
        final = urlparse(resp.url)
        if final.scheme != "https" or final.hostname not in {
            "ramadda.data.bas.ac.uk", "194.66.5.50"
        }:
            raise ValueError("unexpected BAS download redirect")
        for b in resp.iter_content(chunk_size=262144):
            if not b:
                continue
            total += len(b)
            if total > MAX_BYTES:
                raise ValueError("BAS rock archive >205MB source cap")
            h.update(b)
            out.write(b)
    return out.getvalue(), {"zip_sha256":h.hexdigest(),"zip_bytes":total}

def analyze(data:bytes,meta:dict)->dict:
    if not data.startswith(b"PK"):
        raise ValueError("BAS source response is not zipped shapefile")
    with ZipFile(io.BytesIO(data)) as z:
        infos=z.infolist()
        if len(infos)>80 or z.testzip() is not None:
            raise ValueError("bad ZIP entries or checksum")
        if sum(i.file_size for i in infos)>MAX_UNPACKED:
            raise ValueError("unpacked SHP exceeds source cap")
        for info in infos:
            p=Path(info.filename)
            if p.is_absolute() or ".." in p.parts or len(p.parts)>6:
                raise ValueError("unexpected ZIP file path")
        entries={}
        for suffix in (".shp",".shx",".dbf",".prj"):
            found=[f.filename for f in infos if f.filename.lower().endswith(suffix)]
            if len(found)!=1:
                raise ValueError("source archive does not contain exactly one "+suffix)
            entries[suffix]=found[0]
        prj=z.read(entries[".prj"]).decode("utf-8",errors="replace")
        if "Polar_Stereographic" not in prj and "3031" not in prj:
            raise ValueError("rock archive has unrecognized projection")
        raw_dbf=z.read(entries[".dbf"])
        dbf=shapefile.Reader(dbf=io.BytesIO(raw_dbf), encoding="latin1")
        names=[str(f[0]).lower() for f in dbf.fields[1:]]
        if "sourcedate" not in names or "sourceprec" not in names:
            raise ValueError("No paired sourcedate/sourceprec fields: cannot assess source timing")
        date_idx=names.index("sourcedate")
        prec_idx=names.index("sourceprec")
        dates=Counter()
        precs=Counter()
        missing=0
        for row in dbf.iterRecords():
            val=str(row[date_idx]).strip() if row[date_idx] is not None else ""
            prec=str(row[prec_idx]).strip() if row[prec_idx] is not None else ""
            precs[prec or "<missing>"]+=1
            if len(val)>=4 and val[:4].isdigit():
                dates[val[:4]]+=1
            else:
                missing+=1
        n=dbf.numRecords
        dbf.close()
        return {
            **meta,"source_id":SOURCE_DOI, "archive_url":ARCHIVE_URL,
            "file_names":[i.filename for i in infos],
            "raw_shp_bytes":z.getinfo(entries[".shp"]).file_size,
            "raw_dbf_bytes":len(raw_dbf),
            "source_projection_excerpt":prj[:200],
            "source_dbf_fields":names,
            "original_rock_polygon_records":n,
            "records_without_parseable_source_year":missing,
            "source_precisions":dict(sorted(precs.items())),
            "source_year_counts":dict(sorted(dates.items())),
            "records_source_2000plus":sum(n for y,n in dates.items() if int(y)>=2000),
            "records_source_2005plus":sum(n for y,n in dates.items() if int(y)>=2005),
            "records_source_2019plus":sum(n for y,n in dates.items() if int(y)>=2019),
            "original_source_rock_geometries_loaded":False,
            "status":"ROCK_DBFSOURCE_DATE_VERIFIED",
            "date_utc":datetime.now(timezone.utc).isoformat(),
        }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    receipt={"status":"HOLD_OFFICIAL_ROCK_SOURCE","source_doi":SOURCE_DOI,
             "source_only":True,"penguin_count_opened":False}
    try:
        raw,meta=fetch_archive()
        receipt.update(analyze(raw,meta))
    except Exception as e:
        receipt["reason"]=f"{type(e).__name__}: {str(e)}"[:400]
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:receipt.get(k) for k in
                      ("status","reason","zip_sha256","original_rock_polygon_records",
                       "records_source_2019plus")},sort_keys=True))

if __name__=="__main__":
    main()
