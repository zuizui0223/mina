#!/usr/bin/env python3
"""AADC Bechervaise source-only retrieval and same-ID reachability test.

The candidate joins are:
  (1) AAS_4086 unprocessed RFID gate crossings (2006–2018),
  (2) AAS_4518 tagged birds resighted at nests (1991–2019).
Only two specifically advertised original publisher DOWNLOAD links have
been verified: AAS_4518 data package 5516 and AAS_4086 TECHNICAL GUIDE
5228 (not the actual gate crossing data). HEAD is not assumed supported.
Read bounded initial bytes only; refuse insecure/other-host redirects, and
do not parse bird IDs, phenotypes or true breeding events.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import build_opener, HTTPRedirectHandler, HTTPSHandler, Request
from urllib.error import HTTPError,URLError

SOURCE_ENDPOINTS={
  "AAS_4518_1991_2019_DEMOGRAPHY_AND_RE-SIGHT_ARCHIVE":
      "https://data.aad.gov.au/eds/5516/download",
  "AAS_4086_2006_2018_WEIGHBRIDGE_TECHNICAL_GUIDE_ONLY":
      "https://data.aad.gov.au/eds/5228/download",
}
MAX_FIRST_BYTES=24576
ALLOWED_HOSTS={"data.aad.gov.au"}
SOURCE_METADATA={
  "AAS_4086_WEIGHBRIDGE":"https://data.aad.gov.au/metadata/records/AAS_4086_Weighbridge",
  "AAS_4518_NEST_RESIGHT":"https://researchdata.edu.au/population-counts-resights-1991-2019/3651220"
}

def official(url):
    p=urlparse(str(url))
    return p.scheme=="https" and p.hostname in ALLOWED_HOSTS

class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,url):
        if not official(url):
            p=urlparse(url)
            raise ValueError("unapproved original AADC redirection scheme="+p.scheme+
                             " hostname="+str(p.hostname))
        return super().redirect_request(req,fp,code,msg,headers,url)

def classify_head(raw,ctype,endpoint_label):
    report={
       "read_first_bytes_only":len(raw),
       "file_body_parsed":False,
       "penguin_identifiers_read":0,
       "unprocessed_weighbridge_records_opened":0,
       "record_state":"HOLD_UNKNOWN_SOURCE_FORMAT",
       "source_label":endpoint_label
    }
    if not raw:
        report["record_state"]="HOLD_EMPTY_RESPONSE"
        return report
    prefix=raw[:300].strip().lower()
    if "html" in ctype.lower() or prefix.startswith((b"<html",b"<!doctype")) or b"<html" in prefix:
        report["record_state"]="HOLD_JS_HTML_APPLICATION_OR_LOGIN_NOT_DATA"
        return report
    if raw.startswith(b"PK\x03\x04"):
        report["record_state"]="ZIP_ARCHIVE_HEADER_CANDIDATE_UNPARSED"
    elif raw.startswith(b"%PDF-"):
        report["record_state"]="PDF_DOCUMENT_PREFIX"
    elif raw.startswith(b"\xd0\xcf\x11\xe0"):
        report["record_state"]="LEGACY_XLS_BIFF_PREFIX_NOT_PARSED"
    elif raw.startswith(b"Rar!"):
        report["record_state"]="RAR_ARCHIVE_PREFIX_NOT_PARSED"
    elif b"," in raw[:150] and b"\n" in raw[:150]:
        report["record_state"]="TEXT_TABLE_PREFIX_DO_NOT_PARSE_ANIMAL_RECORDS"
    return report

def probe(url,label):
    report={
        "source_url":url,"source_label":label,
        "source_retrieval":"HOLD_SOURCE_NOT_READ",
        "actual_raw_gate_crossings_verified":False,
        "original_resight_nest_IDs_verified":False,
        "bird_records_opened":0
    }
    if not official(url):
        report["source_retrieval"]="HOLD_NOT_AN_OFFICIAL_HTTPS_AADC_ENDPOINT"
        return report
    opener=build_opener(HTTPSHandler(),SafeRedirect())
    try:
        req=Request(url,headers={
           "User-Agent":"Penguin causal source availability AADC probe/1.0",
           "Range":"bytes=0-24575",
           "Accept":"application/zip,application/octet-stream,application/pdf,text/html,*/*"
        })
        with opener.open(req,timeout=13) as response:
            report["http_status"]=response.status
            report["final_host"]=urlparse(response.geturl()).hostname
            report["reported_content_type"]=response.headers.get("Content-Type","")
            report["reported_content_length"]=response.headers.get("Content-Length")
            prefix=response.read(MAX_FIRST_BYTES)
        report["source_file_magic"]=classify_head(prefix,report["reported_content_type"],label)
        report["source_retrieval"]=report["source_file_magic"]["record_state"]
    except Exception as exc:
        report["source_retrieval"]="HOLD_OFFICIAL_DOWNLOAD_OR_REDIRECT"
        report["retrieval_error_type"]=type(exc).__name__
        report["retrieval_error_short"]=str(exc)[:160]
    return report

def audit():
    r={label:probe(url,label) for label,url in SOURCE_ENDPOINTS.items()}
    return {
      "status":"AADC_PUBLIC_METADATA_WITH_NO_SAME_ID_GATE_TO_NEST_BRIDGE_YET",
      "metadata_official":SOURCE_METADATA,
      "source_retrieval_checks":r,
      "calendar_year_overlap_2006_through_2018":True,
      "original_gate_data_url_is_missing_from_verified_publisher_source_links":True,
      "technical_guide_not_equivalent_to_original_gate_crossings":True,
      "original_bird_tag_IDs_read":0,
      "source_ID_format_and_quality_conversion_verified":False,
      "same_penguin_tag_ID_join_gate_to_nest_observation_verified":False,
      "at_risk_all_prospective_breeders_across_island_denominator_verified":False,
      "observed_first_egg_by_same_marked_gate_entrant_verified":False,
      "new_biological_causal_immigration_or_breeding_result":False,
      "Emmerson_Southwell_2022_cohort_size_demographic_feedback_ALREADY_PUBLISHED":True,
      "PR189_science_unchanged":True,
      "PR142_data_gate_unchanged":True,
      "PR195_emperor_georeference_unchanged":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=audit()
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    for label,x in report["source_retrieval_checks"].items():
        print("BECH_SOURCE",label,x["source_retrieval"],"HTTP",x.get("http_status"),
              "ERROR",x.get("retrieval_error_short",""))
        print("FILE_SIGNATURE",x.get("source_file_magic",{}).get("record_state"))
    print("ORIGINAL_ANIMAL_TAG_ROWS_READ",0)
    print("SAME_ID_GATE_TO_OWN_EGG_CROSSWALK_VERIFIED",False)
    print("NO_PENGUIN_BIOLOGICAL_CAUSAL_RESULT")

if __name__=="__main__": main()
