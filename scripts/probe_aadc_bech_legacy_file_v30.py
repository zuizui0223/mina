#!/usr/bin/env python3
"""V30 inspect one literal publisher first-party archived original field file.

Bechervaise Island original metadata linked file_id=1363; this fetch reads
at most first 128 KiB to verify binary vs JS-shell availability. No birds.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from urllib.parse import urlparse
import requests
from probe_aadc_legacy_public_downloads_v29 import CAP,final_host_ok
OFFICIAL_AADC_LINK="https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=1363"

def source_probe(sess):
    redirects=[]
    with sess.get(OFFICIAL_AADC_LINK,timeout=(20,100),stream=True,headers={
        "User-Agent":"mina-official-Bechervaise-GIS-legacy-source-1363-v30/1.0"
    }) as res:
        res.raise_for_status()
        for item in [*res.history,res]:
            if not final_host_ok(item.url):
                raise ValueError("SOURCE_STOP original legacy file redirected outside authorized AADC publisher")
            redirects.append({"http_code":item.status_code,"host":urlparse(item.url).hostname,"path":urlparse(item.url).path})
        first=res.raw.read(CAP+1,decode_content=True)[:CAP]
        kind=("ZIP" if first.startswith(b"PK\x03\x04") else
              "JPEG" if first.startswith(b"\xff\xd8\xff") else
              "HTML" if first.lstrip().lower().startswith((b"<!doctype",b"<html")) else
              "PNG" if first.startswith(b"\x89PNG") else
              "SOURCE_UNKNOWN_FORMAT")
        return {
            "status":"ORIGINAL_BECHERVAISE_PUBLISHER_LEGACY_FILE_PROBED",
            "original_AADC_metadata_link":OFFICIAL_AADC_LINK,
            "actual_HTTP_status":res.status_code,
            "original_source_final_content_type":res.headers.get("Content-Type"),
            "original_source_content_disposition":res.headers.get("Content-Disposition"),
            "source_Content_Length":res.headers.get("Content-Length"),
            "original_response_signature":kind,
            "initial_read_bytes":len(first),
            "partial_probe_SHA256_NOT_FULL_SOURCE_HASH":hashlib.sha256(first).hexdigest(),
            "original_publisher_HTTP_chain":redirects,
            "original_html_v2_JS_shell_identified":bool(kind=="HTML" and b"/assets/index-" in first),
            "raw_penguin_nest_coordinate_observations_read":0,
            "one_original_field_source_file_downloaded_in_full":False,
        }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    obj={"status":"HOLD_ORIGINAL_BECHERVAISE_LEGACY_SOURCE_V30","raw_penguin_nest_coordinate_observations_read":0}
    try:
        with requests.Session() as sess:obj=source_probe(sess)
    except Exception as e:
        obj["error_type"]=type(e).__name__
        obj["error"]=str(e)[:450]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(obj,ensure_ascii=False))
if __name__=="__main__":main()
