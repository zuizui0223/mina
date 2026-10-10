#!/usr/bin/env python3
"""Metadata/CSV-column-only Dryad longitudinal penguin source verification.

Source first line ONLY is decoded. No subsequent individual ID, animal state
or outcome may be parsed, counted or fitted in this first source gate.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen, HTTPRedirectHandler, build_opener, HTTPSHandler

URL="https://datadryad.org/downloads/file_stream/532106"
KNOWN_COLUMNS={"ID","colony","season","success","breeder","age","afr","afrc","expt","expl","alr"}
FIRST_BYTES_LIMIT=4096
TOTAL_FILE_SIZE_LIMIT=2*1024*1024

class DryadRedirectOnly(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed=urlparse(newurl)
        if parsed.scheme!="https" or not (parsed.hostname=="datadryad.org"
                    or (parsed.hostname or "").endswith(".datadryad.org")):
            raise ValueError("Dryad redirect crossed unverified host or protocol")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def validate_url(url:str)->bool:
    p=urlparse(url)
    return p.scheme=="https" and (p.hostname=="datadryad.org" or
        (p.hostname or "").endswith(".datadryad.org"))

def header_only(chunk:bytes, content_type:str)->dict:
    """Decode only complete first CSV line, never the next penguin record."""
    result={
        "status":"HOLD_NO_COMPLETE_VERIFIED_CSV_HEADER",
        "source_header":[],
        "header_matches_original_metadata":False,
        "individual_identifiers_read":0,
        "individual_outcome_rows_read":0,
        "fit_performed":False
    }
    if not isinstance(chunk,bytes) or len(chunk)>FIRST_BYTES_LIMIT:
        return result
    first=chunk.split(b"\n",1)[0]
    if not chunk or b"\n" not in chunk:
        return result
    typ=content_type.lower()
    if "html" in typ or b"<html" in chunk[:200].lower() or b"<!doctype" in chunk[:200].lower():
        result["status"]="HOLD_HTML_INSTEAD_OF_OFFICIAL_CSV"
        return result
    try:
        decoded=first.decode("utf-8-sig").rstrip("\r")
        cols=next(csv.reader(io.StringIO(decoded)))
    except (UnicodeDecodeError,csv.Error,StopIteration):
        result["status"]="HOLD_UNKNOWN_CSV_HEADER_ENCODING"
        return result
    # Do not expose any values beyond dataset fields, even if first record.
    if not cols or len(cols)>60 or any(len(x)>100 for x in cols):
        result["status"]="HOLD_IMPLAUSIBLE_TABLE_SCHEMA"
        return result
    result["source_header"]=cols
    result["header_matches_original_metadata"]=KNOWN_COLUMNS.issubset(set(cols))
    result["status"]=("OFFICIAL_CSV_FIRST_HEADER_VERIFIED_NO_ANIMAL_RECORDS"
                      if result["header_matches_original_metadata"]
                      else "HOLD_DRYAD_SCHEMA_UNLIKE_METADATA")
    return result

def probe():
    report={
        "source":"Dryad 10.5061/dryad.s7h44j15w original author Kappes et al 2020",
        "source_url":URL,
        "status":"HOLD_OFFICIAL_DRYAD_ACCESS",
        "downloaded_data_bytes_to_disk":0,
        "individual_ids_read":0,
        "reproductive_outcome_rows_read":0,
        "not_same_ids_as_other_original_author_sources":True,
        "study_team_contact_recorded_not_sent":False,
        "paper_not_yet_claimed_as_new_higher_order_memory":True,
        "no_fit":True
    }
    try:
        if not validate_url(URL):
            raise ValueError("Only original official Dryad source URL allowed")
        req=Request(URL,headers={
            "Accept":"text/csv,text/plain,application/octet-stream",
            "Range":"bytes=0-4095",
            "User-Agent":"Penguin-study-public-metadata-schema-verification/1.0"})
        opener=build_opener(HTTPSHandler(),DryadRedirectOnly())
        with opener.open(req,timeout=17) as res:
            content_type=res.headers.get("Content-Type","")
            reported=res.headers.get("Content-Length","")
            total_size=int(reported) if reported.isdigit() else None
            if total_size is not None and total_size>TOTAL_FILE_SIZE_LIMIT:
                report["status"]="HOLD_SOURCE_OVER_EXPECTED_SIZE"
                report["declared_size_bytes"]=total_size
                return report
            final=res.geturl()
            if not validate_url(final):
                raise ValueError("Nonofficial final URL")
            sample=res.read(FIRST_BYTES_LIMIT)
            report["http_status"]=res.status
            report["declared_size_bytes"]=total_size
            report["response_content_type"]=content_type
            report["sample_bytes_read_not_saved"]=len(sample)
            report["final_host"]=urlparse(final).hostname
        z=header_only(sample,content_type)
        report["status"]=z["status"]
        report["source_header"]=z["source_header"]
        report["source_header_metadata_match"]=z["header_matches_original_metadata"]
        report["no_animal_rows_parsed"]=z["individual_outcome_rows_read"]==0
    except Exception as exc:
        report["status"]="HOLD_OFFICIAL_SOURCE_FETCH"
        report["error_type"]=type(exc).__name__
        report["error_message"]=str(exc)[:230]
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    p=ap.parse_args()
    r=probe()
    p.out.write_text(json.dumps(r,indent=2)+"\n")
    print("DRYAD_STATE_MEMORY_SOURCE_GATE",r["status"])
    print("SOURCE_COLUMN_SCHEMA",r.get("source_header",[]))
    print("FETCH_ERROR_CLASS",r.get("error_type","NONE"))
    # Report just a bounded HTTP/error type, never an author record or redirect token.
    print("FETCH_ERROR_SHORT",r.get("error_message","")[:90])
    print("READ_ANIMAL_OUTCOMES",r["reproductive_outcome_rows_read"])
    print("FITTED_SECOND_ORDER_MEMORY_EFFECT",False)

if __name__=="__main__":main()
