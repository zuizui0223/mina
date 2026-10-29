#!/usr/bin/env python3
"""V29 bounded official AADC legacy download endpoints source probe.

No biological count cells, raw colony GIS, photographs or actual original
source binary downloaded in full; at most first 128 KiB per first-party URL.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from urllib.parse import urlparse
import requests

SOURCE_ITEMS={
 "VESTFOLD_CAPE_PETREL_ISLAND_SURVEY":"https://data.aad.gov.au/eds/5210/download",
 "BECHERVAISE_ADELIE_FIELD_NEST_LOCATIONS":"https://data.aad.gov.au/eds/1354/download",
 "WINDMILL_MULTITAXON_FIELD_BIRD_GIS":"https://data.aad.gov.au/eds/4670/download",
}
CAP=131072
ALLOWED_HOST_SUFFIX=".aad.gov.au"

def final_host_ok(url):
    u=urlparse(url)
    return u.scheme=="https" and (u.hostname=="data.aad.gov.au" or
            (u.hostname or "").endswith(ALLOWED_HOST_SUFFIX))

def probe(session,url):
    if not url.startswith("https://data.aad.gov.au/eds/") or not url.endswith("/download"):
        raise ValueError("SOURCE_STOP source URL must be exact official EDS download endpoint")
    redirects=[]
    # Permit just publisher-owned redirects. Requests' history reflects every hop.
    with session.get(url,timeout=(20,100),stream=True,headers={
        "User-Agent":"mina-original-AADC-legacy-data-publisher-source-probe-v29/1.0"
    },allow_redirects=True) as resp:
        for item in [*resp.history,resp]:
            redirects.append({
                "HTTP_status":item.status_code,
                "host":urlparse(item.url).hostname,
                "path":urlparse(item.url).path,
            })
            if not final_host_ok(item.url):
                raise ValueError("SOURCE_HOLD original EDS source redirects outside AADC-owned host")
        length=resp.headers.get("Content-Length")
        declared=int(length) if length and length.isdecimal() else None
        snippet=resp.raw.read(CAP+1,decode_content=True)
        if len(snippet)>CAP:
            snippet=snippet[:CAP]
        if snippet.startswith(b"PK\x03\x04"):kind="POSSIBLE_ZIP_OR_XLSX"
        elif snippet.startswith(b"%PDF"):kind="PDF"
        elif snippet.startswith((b"II*\x00",b"MM\x00*")):kind="TIFF"
        elif snippet.lstrip().lower().startswith((b"<!doctype",b"<html",b"<?xml")):kind="HTML_OR_XML"
        elif b"," in snippet[:1000] and b"\n" in snippet[:1000]:kind="POSSIBLE_CSV"
        else:kind="UNKNOWN_BINARY_OR_TEXT"
        return {
            "source_first_party_HTTP_status":resp.status_code,
            "source_final_content_type":resp.headers.get("Content-Type"),
            "source_final_content_disposition":resp.headers.get("Content-Disposition"),
            "source_declared_original_binary_length_bytes":declared,
            "source_response_is_attachment_or_binary":bool(
                kind in ("POSSIBLE_ZIP_OR_XLSX","PDF","TIFF") or
                "attachment" in (resp.headers.get("Content-Disposition") or "").lower()),
            "source_first_128KiB_signature":kind,
            "publisher_html_source_visible_content":(
                snippet.decode("utf-8",errors="replace")[:2400]
                if kind=="HTML_OR_XML" else None
            ),
            "source_first_128KiB_probe_bytes":len(snippet),
            "source_probe_SHA256_NOT_FULL_DATA_FILE":hashlib.sha256(snippet).hexdigest(),
            "original_EDS_HTTP_redirect_chain":redirects,
            "original_data_file_hash_verified":False,
            "biological_data_values_read":0,
            "full_original_binary_downloaded":False,
        }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    report={
       "status":"AADC_LEGACY_ORIGINAL_FIELD_SURVEY_SOURCE_PROBE_V29",
       "original_source_links_as_published_on_AADC_full_metadata":SOURCE_ITEMS,
       "original_EDS_source_probe_by_dataset":{},
       "biological_field_species_counts_or_GIS_opened":0,
       "ecological_effects_fit":0,
    }
    with requests.Session() as s:
        for name,url in SOURCE_ITEMS.items():
            try:
                report["original_EDS_source_probe_by_dataset"][name]={
                    "status":"ORIGINAL_EDS_SOURCE_HTTP_PROBED",
                    **probe(s,url)
                }
            except Exception as e:
                report["original_EDS_source_probe_by_dataset"][name]={
                    "status":"HOLD_ORIGINAL_EDS_SOURCE_ACCESS",
                    "error_type":type(e).__name__,
                    "error":str(e)[:400],
                    "biological_data_values_read":0
                }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

if __name__=="__main__":
    main()
