#!/usr/bin/env python3
"""Auditable official AADC potential-site / breeding-occupancy file probe.

Only verify remote source shape, binary fingerprint and ZIP member filenames.
Do NOT parse any penguin occupancy records or construct biological negatives.
A coastal rock/island geographic site is not a 3-10 m nest site.
"""
from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,build_opener,HTTPSHandler,HTTPRedirectHandler
from urllib.error import HTTPError,URLError
from zipfile import ZipFile,is_zipfile

FILES={
    "potential_island_outcrop_sites":"https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=4598",
    "historical_geographic_site_occupancy":"https://data.aad.gov.au/eds/4345/download",
}
MAX_SOURCE_BYTES=12*1024*1024
ALLOWED_HOSTS={"data.aad.gov.au"}
READ_TIMEOUT_SECONDS=19

class OnlyOfficialHTTPSRedirects(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        parsed=urlparse(newurl)
        if parsed.scheme!="https" or parsed.hostname not in ALLOWED_HOSTS:
            # Report origin only, not query parameters or any token-bearing URI.
            raise ValueError("Unofficial or non-HTTPS AADC redirect blocked: "+
                             parsed.scheme+"://"+str(parsed.hostname or ""))
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def _official(uri):
    p=urlparse(uri)
    return p.scheme=="https" and p.hostname in ALLOWED_HOSTS

def classify_archive(payload:bytes,content_type:str,source_url:str)->dict:
    if not isinstance(payload,bytes):
        raise TypeError("Expected raw source bytes, not decoded records")
    result={
        "bytes_fetched":len(payload),
        "sha256":hashlib.sha256(payload).hexdigest(),
        "content_type":content_type,
        "source_url":source_url,
        "type":"UNKNOWN",
        "record_rows_opened":0,
        "source_file_valid":False,
        "archive_members":[],
        "sample_rows_read":0
    }
    if not _official(source_url):
        result["type"]="HOLD_UNVERIFIED_OFFICIAL_URL"
        return result
    if not payload or len(payload)>MAX_SOURCE_BYTES:
        result["type"]="HOLD_EMPTY_OR_OVERSIZED_INPUT"
        return result
    head=payload[:8192].lstrip().lower()
    if b"<!doctype html" in head[:200] or head.startswith(b"<html") or (
        "html" in content_type.lower()):
        result["type"]="HOLD_HTML_APPLICATION_NOT_SOURCE_DATA"
        return result
    if payload[:2]==b"PK" and is_zipfile(BytesIO(payload)):
        try:
            with ZipFile(BytesIO(payload)) as z:
                members=z.infolist()
                if len(members)>1000:
                    result["type"]="HOLD_TOO_MANY_ARCHIVE_MEMBERS"
                    return result
                result["archive_members"]=[
                    {"name":m.filename[:200],"size_uncompressed":m.file_size,
                     "bytes_compressed":m.compress_size,"is_dir":m.is_dir()}
                    for m in members
                ]
                result["type"]="STRUCTURALLY_VALID_ZIP_OR_XLSX"
                result["source_file_valid"]=True
                return result
        except Exception as e:
            result["type"]="HOLD_ZIP_MEMBER_STRUCTURE_ERROR"
            result["error_type"]=type(e).__name__
            return result
    if payload[:8]==b"Rar!\x1a\x07\x00" or payload[:8]==b"Rar!\x1a\x07\x01":
        result["type"]="BINARY_RAR_ARCHIVE_NOT_PARSED"
        result["source_file_valid"]=True
        return result
    if payload[:4]==b"\x50\x41\x52\x31":
        result["type"]="PARQUET_UNOPENED"
        result["source_file_valid"]=True
        return result
    if payload[:6].startswith(b"%PDF-"):
        result["type"]="PDF_NOT_TABULAR_SOURCE"
        return result
    # CSV headers may contain sensitive/meaningful field values; do not read
    # or expose even first row until a separate authorized schema gate.
    if b"\0" not in payload[:1000] and (b"," in payload[:200] or b"\t" in payload[:200]):
        result["type"]="TEXT_TABULAR_CANDIDATE_UNREAD"
        result["source_file_valid"]=True
        return result
    result["type"]="HOLD_UNKNOWN_UNOPENED_SOURCE"
    return result

def probe(url:str)->dict:
    report={"url":url,"status":"HOLD_AADC_SOURCE_UNREACHABLE","no_animal_records_read":True,
            "do_not_equate_geographic_sites_with_nests":True}
    if not _official(url):
        report["status"]="HOLD_UNAPPROVED_SOURCE_URL"
        return report
    opener=build_opener(HTTPSHandler(),OnlyOfficialHTTPSRedirects())
    req=Request(url,headers={
        "User-Agent":"Antarctic penguin open-data archive provenance audit (github.com/zuizui0223/mina)",
        "Accept":"application/zip,application/octet-stream,text/csv,application/vnd.ms-excel,*/*"})
    try:
        with opener.open(req,timeout=READ_TIMEOUT_SECONDS) as stream:
            response_url=stream.geturl()
            if not _official(response_url):
                raise ValueError("Nonofficial final response endpoint")
            clen=stream.headers.get("Content-Length","")
            n=int(clen) if clen.isdigit() else None
            report["declared_content_length"]=n
            report["http_status"]=stream.status
            report["final_url"]=response_url
            if n and n>MAX_SOURCE_BYTES:
                report["status"]="HOLD_OFFICIAL_FILE_OVER_12MIB"
                return report
            payload=stream.read(MAX_SOURCE_BYTES+1)
            result=classify_archive(payload,stream.headers.get("Content-Type",""),response_url)
            report["source_manifest"]=result
            report["status"]=("OFFICIAL_FILE_STRUCTURALLY_RETRIEVED_NOT_BIOLOGY" if
                              result["source_file_valid"] else result["type"])
    except Exception as err:
        report["status"]="HOLD_OFFICIAL_ENDPOINT_ACCESS"
        report["error_type"]=type(err).__name__
        report["error_message"]=str(err)[:320]
    return report

def run()->dict:
    d={key:probe(url) for key,url in FILES.items()}
    return {
        "status":"STRUCTURAL_OFFICIAL_SOURCE_ARCHIVE_ONLY",
        "source_records":d,
        "both_source_files_retrieved":all(x["status"]=="OFFICIAL_FILE_STRUCTURALLY_RETRIEVED_NOT_BIOLOGY"
                                          for x in d.values()),
        "potential_sites_are_islands_or_rock_outcrops_not_individual_nests":True,
        "historic_absence_requires_observed_search_date_effort":True,
        "source_rows_read":0,
        "cross_site_occupancy_join_verified":False,
        "subcolony_or_nest_success_data_joined":False,
        "colonization_extinction_results_not_new_prior_art_southwell2017":True,
        "new_causal_island_biogeography_test_completed":False,
        "frozen_Ecology_PR189_untouched":True,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    report=run()
    args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    for name,row in report["source_records"].items():
        print("AADC_ARCHIVE",name,row["status"],
              "BYTES",row.get("source_manifest",{}).get("bytes_fetched"),
              "TYPE",row.get("source_manifest",{}).get("type"))
        print("AADC_ARCHIVE_NAMES",name,[m["name"] for m in
              row.get("source_manifest",{}).get("archive_members",[])][:30])
        if row["status"].startswith("HOLD"):
            print("AADC_ARCHIVE_HOLD_REASON",name,
                  row.get("error_type",""),row.get("error_message",""))
    print("TWO_ARCHIVES_PRESENT",report["both_source_files_retrieved"])
    print("NO_BIRD_RECORDS_OR_CAUSAL_TEST_PERFORMED")

if __name__=="__main__":
    main()
