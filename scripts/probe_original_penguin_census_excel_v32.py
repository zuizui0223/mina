#!/usr/bin/env python3
"""V32 genuine AADC old Woehler Excel original spreadsheet source probe.

Only first 128KiB; no original count values or imaginary quality ranks.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from urllib.parse import urlparse,urljoin,urlunparse
import requests

SOURCE_URL="https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216"
SOURCE_ID="FAUNA_PENGUIN_COLONY"
MAX_PROBE_BYTES=131072
ALLOWED_HOST={"data.aad.gov.au","www.aad.gov.au"}


def response_kind(first:bytes):
    if first.startswith(b"PK\x03\x04"):return "POSSIBLE_XLSX_OR_ZIP"
    if first.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):return "LEGACY_XLS_COMPOUND_BINARY"
    if first.startswith(b"%PDF"):return "PDF_NOT_ORIGINAL_EXCEL"
    if first.lstrip().lower().startswith((b"<!doctype",b"<html",b"<?xml")):
        return "HTML_OR_XML_NOT_EXCEL"
    if first.startswith(b"{\n") or first.startswith(b"{"):
        return "JSON_NOT_EXCEL"
    return "UNKNOWN"


def fetch_bounded_source():
    chain=[]
    headers={"User-Agent":"mina-AADC-original-Woehler-xls-literal-fileID-original-redirect-QA/1.0"}
    url=SOURCE_URL
    with requests.Session() as session:
        for _ in range(5):
            with session.get(url,stream=True,timeout=(20,90),allow_redirects=False,headers=headers) as res:
                current=urlparse(res.url)
                if current.scheme!="https" or current.hostname not in ALLOWED_HOST:
                    raise ValueError("SOURCE_STOP original source route not AADC HTTPS")
                chain.append({"status":res.status_code,
                              "first_party_host":current.hostname,
                              "first_party_path":current.path})
                if res.status_code in (301,302,303,307,308):
                    relative=res.headers.get("Location","")
                    if not relative:raise ValueError("SOURCE_STOP original AADC redirect without Location")
                    dest=urljoin(res.url,relative)
                    u=urlparse(dest)
                    # Never log or forward signed query strings to a third-party.
                    if u.hostname in ALLOWED_HOST and u.scheme=="http":
                        # Publisher's old HTTP legacy file endpoint: never send
                        # the browser request over plaintext. Instead resolve
                        # the same canonical original host/path directly by
                        # HTTPS; this is not an off-publisher source fallback.
                        dest=urlunparse(u._replace(scheme="https"))
                        u=urlparse(dest)
                        chain[-1]["source_HTTP_legacy_same_host_link_canonicalized_to_HTTPS"]=True
                    if u.scheme!="https" or u.hostname not in ALLOWED_HOST:
                        return {
                            "status":"HOLD_ORIGINAL_AADC_REDIRECT_TO_NONAPPROVED_HOST",
                            "original_AADC_metadata_identifier":SOURCE_ID,
                            "first_party_exact_download_link":SOURCE_URL,
                            "original_publisher_HTTP_redirect_chain":chain,
                            "publisher_issued_external_redirect_host":u.hostname,
                            "publisher_issued_external_redirect_path":u.path[:400],
                            "publisher_issued_external_redirect_query_redacted":bool(u.query),
                            "original_nest_count_rows_fetched":0,
                            "original_survey_quality_type_code_values_fetched":0,
                            "full_original_spreadsheet_SHA256_verified":False,
                            "off_publisher_file_data_downloaded":False,
                        }
                    url=dest
                    continue
                code=res.status_code
                length=res.headers.get("Content-Length")
                declared=int(length) if length and length.isdecimal() else None
                raw=res.raw.read(MAX_PROBE_BYTES+1,decode_content=True)
                raw=raw[:MAX_PROBE_BYTES]
                kind=response_kind(raw)
                return {
                    "status":"FIRST_PARTY_ORIGINAL_EXCEL_BINARY_SOURCE_CANDIDATE"
                             if code==200 and kind in (
                                "POSSIBLE_XLSX_OR_ZIP","LEGACY_XLS_COMPOUND_BINARY")
                             else "HOLD_FIRST_PARTY_ORIGINAL_EXCEL_NOT_AVAILABLE",
                    "original_AADC_metadata_identifier":SOURCE_ID,
                    "first_party_exact_download_link":SOURCE_URL,
                    "HTTP_status":code,
                    "original_publisher_HTTP_redirect_chain":chain,
                    "original_source_final_path":urlparse(res.url).path,
                    "original_source_final_content_type":res.headers.get("Content-Type"),
                    "original_source_content_disposition":res.headers.get("Content-Disposition"),
                    "original_source_reported_total_bytes":declared,
                    "bounded_128KiB_binary_source_signature":kind,
                    "bounded_bytes_fetched":len(raw),
                    "bounded_first_chunk_SHA256_NOT_FULL_XLS":hashlib.sha256(raw).hexdigest(),
                    "HTML_or_XML_original_publisher_response_preview":
                        raw.decode("utf-8",errors="replace")[:1500] if kind=="HTML_OR_XML_NOT_EXCEL" else None,
                    "original_nest_count_rows_fetched":0,
                    "original_survey_quality_type_code_values_fetched":0,
                    "full_original_spreadsheet_SHA256_verified":False,
                    "can_original_N_C_A_B_quality_be_joined_to_OBIS":False,
                }
    raise ValueError("SOURCE_STOP original AADC redirects exceed 5 safe first-party hops")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result={"status":"HOLD_FIRST_PARTY_ORIGINAL_EXCEL_NOT_AVAILABLE",
            "original_nest_count_rows_fetched":0}
    try:result=fetch_bounded_source()
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:700]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
