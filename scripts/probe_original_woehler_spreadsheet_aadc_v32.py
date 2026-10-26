#!/usr/bin/env python3
"""V32 first-party AADC Woehler original source Excel access and byte receipt.

No count values parsed, no observed bird records, no personal registration.
Official portal original spreadsheet link was supplied in AADC metadata and
retained by the national Australian Research Data catalogue.
"""
from __future__ import annotations
import argparse,hashlib,io,json
from pathlib import Path,PurePosixPath
from urllib.parse import urlparse,urljoin
import zipfile
import requests

SOURCE="https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216"
MAX_SOURCE_BYTES=15_000_000
MAX_ARCHIVE_MEMBER_COUNT=30
MAX_UNPACKED_BYTES=40_000_000


def trusted_official_url(url):
    parsed=urlparse(url)
    return parsed.scheme=="https" and (
        parsed.hostname=="data.aad.gov.au"
        or (parsed.hostname or "").endswith(".aad.gov.au"))


def identify_source_binary(data:bytes):
    if data.startswith(b"PK\x03\x04"):return "ZIP_OR_XLSX"
    if data.startswith(bytes.fromhex("d0cf11e0a1b11ae1")):return "EXCEL_OLD_XLS_OLE"
    if data.lstrip().lower().startswith((b"<!doctype",b"<html",b"<?xml")):return "HTML_XML_NOT_ORIGINAL_EXCEL"
    if data.startswith(b"%PDF"):return "PDF_NOT_ORIGINAL_EXCEL"
    return "UNKNOWN_SOURCE_BINARY"


def bounded_zip_members(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        entries=z.infolist()
        if len(entries)>MAX_ARCHIVE_MEMBER_COUNT:
            raise ValueError("SOURCE_STOP original Excel archive unexpected member count")
        if sum(n.file_size for n in entries)>MAX_UNPACKED_BYTES:
            raise ValueError("SOURCE_STOP original Excel source archive expands beyond 40 MiB")
        if z.testzip() is not None:
            raise ValueError("SOURCE_STOP original Excel source ZIP CRC failure")
        out=[]
        for n in entries:
            path=PurePosixPath(n.filename)
            if path.is_absolute() or ".." in path.parts or len(path.parts)>5:
                raise ValueError("SOURCE_STOP unsafe AADC original Excel archive path")
            out.append({
                "source_original_member_name":n.filename,
                "original_source_member_uncompressed_size":n.file_size,
                "candidate_original_Excel_not_census_replicate":
                    path.suffix.lower() in (".xls",".xlsx")
            })
        return out


def fetch_original_excel(session):
    if not trusted_official_url(SOURCE):
        raise ValueError("SOURCE_STOP original AADC metadata URL outside publisher")
    headers_in={
        "User-Agent":"mina-original-AADC-penguin-fieldcount-quality-recovery-v32/1.0",
        "Accept":"application/octet-stream,application/zip,application/vnd.ms-excel,*/*",
    }
    # Stop *before* following any downgrade to HTTP, even on the AADC host.
    with session.get(SOURCE,timeout=(20,100),stream=True,headers=headers_in,
                     allow_redirects=False) as first:
        origin_status=first.status_code
        destination=SOURCE
        upgraded=False
        if origin_status in (301,302,303,307,308):
            loc=first.headers.get("Location","")
            candidate=urlparse(urljoin(SOURCE,loc))
            if (candidate.hostname!="data.aad.gov.au" or
                candidate.path!="/dataset/file/2216" or
                candidate.query or candidate.fragment or
                candidate.scheme not in ("http","https")):
                raise ValueError(
                    f"ACCESS_HOLD unexpected first-party original redirect host={candidate.hostname}, "
                    f"scheme={candidate.scheme}, path={candidate.path[:180]}, "
                    f"query_parameter_names={[x.split('=',1)[0] for x in candidate.query.split('&') if x][:10]}"
                )
            # The publisher's original HTTPS metadata endpoint currently
            # redirects to the *same* host over HTTP. Do not transmit cookies
            # or fetch original census bytes over insecure HTTP; upgrade the
            # exact authoritative disclosed path to HTTPS instead.
            destination="https://data.aad.gov.au/dataset/file/2216"
            upgraded=(candidate.scheme=="http")
        elif origin_status!=200:
            return None,{
                "original_Metadata_Source_HTTP_status":origin_status,
                "HTTP_status":origin_status,
                "response_final_URL":first.url,
            }
    with session.get(destination,timeout=(20,100),stream=True,headers=headers_in,
                     allow_redirects=False) as res:
        if not trusted_official_url(res.url):
            raise ValueError("ACCESS_HOLD upgraded original URL not first-party publisher HTTPS")
        if res.status_code in (301,302,303,307,308):
            jump=urlparse(urljoin(destination,res.headers.get("Location","")))
            raise ValueError(
                f"ACCESS_HOLD secondary publisher redirect: scheme={jump.scheme}, "
                f"host={jump.hostname}, path={jump.path[:160]}, "
                f"query_parameter_names={[x.split('=',1)[0] for x in jump.query.split('&') if x][:10]}"
            )
        status=res.status_code
        headers={
            "original_Metadata_Source_HTTP_status":origin_status,
            "original_AADC_redirect_rewritten_to_same_host_HTTPS":upgraded,
            "HTTP_status":status,
            "response_final_URL":res.url,
            "source_MIME_type":res.headers.get("Content-Type"),
            "source_content_disposition":res.headers.get("Content-Disposition"),
            "source_declared_content_length":res.headers.get("Content-Length"),
        }
        if status!=200:
            return None,headers
        raw=bytearray()
        for fragment in res.iter_content(1<<15):
            raw.extend(fragment)
            if len(raw)>MAX_SOURCE_BYTES:
                raise ValueError("SOURCE_STOP original spreadsheet response exceeds bounded 15MiB")
    return bytes(raw),headers


def diagnose_original_response(raw,headers):
    if raw is None:
        return {
            "status":"ACCESS_HOLD_FIRST_PARTY_SOURCE_HTTP",
            "original_publisher_HTTP_receipt":headers,
            "source_original_spreadsheet_obtained":False,
            "original_Woehler_quality_code_rows_read":0,
        }
    signature=identify_source_binary(raw)
    available=signature in ("ZIP_OR_XLSX","EXCEL_OLD_XLS_OLE")
    report={
        "status":"ACCESS_PASS_FIRST_PARTY_ORIGINAL_SPREADSHEET_BINARY"
                 if available else "ACCESS_HOLD_FIRST_PARTY_NOT_SPREADSHEET",
        "original_publisher_HTTP_receipt":headers,
        "original_AADC_source_metadata_record":"FAUNA_PENGUIN_COLONY",
        "original_publisher_unmodified_and_corrected_source_file_ID":2216,
        "original_AADC_original_source_size_bytes":len(raw),
        "original_AADC_response_SHA256":hashlib.sha256(raw).hexdigest(),
        "original_file_signature":signature,
        "source_original_spreadsheet_obtained":available,
        "original_Woehler_quality_code_rows_read":0,
        "original_census_Stage_NA_CB_recovered":False,
        "source_new_biological_island_model_fitted":False,
    }
    if signature=="ZIP_OR_XLSX":
        report["original_source_zip_member_names"]=bounded_zip_members(raw)
    elif signature=="HTML_XML_NOT_ORIGINAL_EXCEL":
        report["source_HTML_page_excerpt_no_secrets"]=raw.decode(
            "utf-8",errors="replace")[:850]
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    output={"status":"ACCESS_HOLD_AADC_WOEHLER_EXCEL_SOURCE_V32"}
    try:
        with requests.Session() as s:
            raw,headers=fetch_original_excel(s)
        output=diagnose_original_response(raw,headers)
    except Exception as e:
        output["error_type"]=type(e).__name__
        output["error"]=str(e)[:550]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",
                     encoding="utf-8")
    print(json.dumps(output,ensure_ascii=False))


if __name__=="__main__":
    main()
