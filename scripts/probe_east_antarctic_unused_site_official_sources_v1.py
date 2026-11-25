#!/usr/bin/env python3
"""Check bounded response metadata from three KNOWN OFFICIAL AADC dataset links.

No downloaded biological outcome rows, no user credentials, no inferred
site-level controls, and no unbounded remote archive downloads. Publication
identifiers and paths fixed before opening remote source endpoints.

The 2016 and 2025 AADC data do not geographically overlap Cox's Cape Crozier
solo nests and cannot supply unseen nest-scale controls there.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError,URLError

SOURCES=(
    ("AADC_2016_COASTAL_POTENTIAL_SITES","https://data.aad.gov.au/eds/4344/download"),
    ("AADC_2016_ADELIE_OCCUPANCY","https://data.aad.gov.au/eds/4345/download"),
    ("AADC_2025_EIGHT_SPECIES_OCCUPANCY","https://data.aad.gov.au/eds/5959/download"),
)
MAX_BYTES=65536
TIMEOUT=12

def valid_official_url(url):
    u=urlsplit(url)
    return u.scheme=="https" and u.hostname in ("data.aad.gov.au", "www.data.aad.gov.au")

class BoundedOfficialRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not valid_official_url(newurl):
            raise ValueError("HOLD_REDIRECT_OUTSIDE_OFFICIAL_AADC_DOMAIN")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def classify_signature(prefix):
    if prefix.startswith(b"PK\x03\x04"):
        return "ZIP_ARCHIVE_MAGIC"
    if prefix.startswith(b"\x1f\x8b"):
        return "GZIP_MAGIC"
    if prefix.startswith(b"Rar!\x1a\x07"):
        return "RAR_ARCHIVE_MAGIC"
    if prefix.startswith(b"\x50\x41\x52\x31"):
        return "PARQUET_MAGIC"
    if prefix.lstrip().lower().startswith((b"<!doctype html",b"<html",b"<!doctype")):
        return "HTML_NOT_DATA_ARCHIVE"
    if prefix.startswith(b"\xd0\xcf\x11\xe0"):
        return "LEGACY_OLE_OFFICE_DOCUMENT"
    return "UNRECOGNIZED_PREFIX_NOT_DATA_CONFIRMED"

def probe_url(name,url,opener=None):
    if not valid_official_url(url):
        raise ValueError("Unapproved source URL")
    if opener is None:
        opener=build_opener(BoundedOfficialRedirect())
    out={"dataset":name,"published_official_url":url,
         "status":"HOLD_NO_ARCHIVE_MAGIC_CHECKED",
         "source_biological_columns_read":0,"source_occupancy_rows_read":0,
         "new_causal_model_run":False}
    for method in ("HEAD","GET"):
        try:
            req=Request(url,headers={
                "User-Agent":"mina-source-structure-audit/1.0",
                "Accept":"application/octet-stream,application/zip,*/*;q=0.5",
                "Range":f"bytes=0-{MAX_BYTES-1}",
            },method=method)
            with opener.open(req,timeout=TIMEOUT) as resp:
                final_url=resp.geturl()
                if not valid_official_url(final_url):
                    raise ValueError("UNVERIFIED_NONOFFICIAL_FINAL_URL")
                status=resp.status
                kind=resp.headers.get("Content-Type","")
                length=resp.headers.get("Content-Length","")
                disposition=resp.headers.get("Content-Disposition","")
                if method=="HEAD":
                    out.update({"head_status":status,"content_type":kind[:120],
                        "content_length_declared":length[:32],
                        "content_disposition":disposition[:130],
                        "verified_final_official_url":final_url})
                    continue
                prefix=resp.read(32)
                magic=classify_signature(prefix)
                out.update({"get_status":status,"response_magic":magic,
                    "content_type":kind[:120],
                    "content_length_declared":length[:32],
                    "content_disposition":disposition[:130],
                    "verified_final_official_url":final_url})
                out["status"]=("OFFICIAL_BYTE_PREFIX_AVAILABLE_NOT_TABLE_READ"
                    if magic not in ("HTML_NOT_DATA_ARCHIVE","UNRECOGNIZED_PREFIX_NOT_DATA_CONFIRMED")
                    else "HOLD_NO_VERIFIED_TABULAR_ARCHIVE")
                break
        except (HTTPError,URLError,TimeoutError,ValueError,ConnectionError,OSError) as e:
            out[f"{method.lower()}_error_type"]=type(e).__name__
            out[f"{method.lower()}_error_message"]=str(e)[:220]
    return out

def audit():
    results=[probe_url(name,url) for name,url in SOURCES]
    return {
        "status":"ONLY_ORIGINAL_OFFICIAL_AADC_SOURCE_STRUCTURE_PROBED",
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "source_records":results,
        "n_known_official_source_endpoints":len(results),
        "n_prefix_read":sum(x.get("get_status") in (200,206) for x in results),
        "Cape_Crozier169E_overlaps_East_Antarctic_sites":False,
        "East_Antarctic_potential_habitat_is_exact_nest_3_10m_risk_set":False,
        "source_occupancy_outcome_rows_read":0,
        "original_site_geometries_materialized":False,
        "cause_of_failed_pioneer_colonization_identified":False,
        "PR189_modified":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    d=audit()
    args.out.write_text(json.dumps(d,indent=2)+"\n",encoding="utf8")
    for x in d["source_records"]:
        print("AADC_SOURCE",x["dataset"],x["status"],x.get("head_status"),
              x.get("get_status"),x.get("response_magic"),
              "HEAD_ERROR",x.get("head_error_type"),"GET_ERROR",x.get("get_error_type"))
    print("AADC_AUTHOR_SITE_COVERAGE_NOT_CROZIER_NEST_PATCHES")
    print("NO_NEW_NEST_OR_CAUSAL_OUTCOMES_READ")

if __name__=="__main__":
    main()
