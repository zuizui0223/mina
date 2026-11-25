#!/usr/bin/env python3
"""V56a: diagnose original AADC PUBLIC EDS download landing pages, not animal data.

V56 original four official AADC source urls returned HTML rather than GIS.
This one source-access diagnostic checks just the 2023-24 modern guild dataset
and independent coastline dataset, without clicking forms, accepting licences,
authenticating or following non-first-party content URLs. Only page STRUCTURE
and safe official link classification retained, never full HTML / token URLs.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests

SOURCES={
    "2023_24_wildlife_both_flight_guilds":"https://data.aad.gov.au/eds/6113/download",
    "original_Macquarie_1_to_50k_coast":"https://data.aad.gov.au/eds/2812/download",
}
DOMAIN_SUFFIXES=("aad.gov.au","antarctica.gov.au")
MAX_HTML_BYTES=200000
MAX_REDIRECTS=4
MIN_TITLE=0


def official(url):
    p=urlparse(url)
    if p.scheme!="https" or not p.hostname:
        return False
    h=p.hostname.lower().rstrip(".")
    return any(h==x or h.endswith("."+x) for x in DOMAIN_SUFFIXES)


class PublicPageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title=False
        self.title_parts=[]
        self.anchor_targets=[]
        self.forms=0
        self.inputs_by_type={}
        self.buttons=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="title":
            self.in_title=True
        if tag=="a" and attrs.get("href"):
            self.anchor_targets.append(attrs["href"])
        if tag=="form":
            self.forms+=1
        if tag=="input":
            typ=str(attrs.get("type") or "text").casefold()
            if typ not in ("text","hidden","submit","checkbox","radio",
                           "email","password","button","search"):
                typ="other"
            self.inputs_by_type[typ]=self.inputs_by_type.get(typ,0)+1
        if tag=="button":
            self.buttons+=1
    def handle_endtag(self,tag):
        if tag=="title":
            self.in_title=False
    def handle_data(self,data):
        if self.in_title and len(self.title_parts)<30:
            self.title_parts.append(data)
    @property
    def safe_title(self):
        title=re.sub(r"\s+"," "," ".join(self.title_parts)).strip()
        # For safety only classify common site UI title, never echo HTML
        # potentially containing tokens or accidental user identity strings.
        if re.search("login|sign.?in|log.?in",title,re.I):
            return "LOGIN_TITLE"
        if re.search("download",title,re.I):
            return "DOWNLOAD_PAGE_TITLE"
        if re.search("Antarctic|Australian",title,re.I):
            return "AADC_PUBLISHER_TITLE"
        if re.search("error|not found|unavailable",title,re.I):
            return "ERROR_PAGE_TITLE"
        return "OTHER_OR_EMPTY_PAGE_TITLE"


def source_page_structure(raw,original_url):
    head=raw[:MAX_HTML_BYTES].lstrip()
    if not head.lower().startswith((b"<!doctype",b"<html",b"<head",b"<body")):
        return {"response_kind":"NON_HTML_BINARY_OR_OTHER","html_form_count":0,
                "direct_official_public_file_links_n":0}
    p=PublicPageMetadata()
    p.feed(head.decode("utf-8","replace"))
    safe_links=[]
    for href in p.anchor_targets[:250]:
        full=urljoin(original_url,href)
        if not official(full):continue
        up=urlparse(full)
        # URLs with query params may carry session tokens; never save them.
        if re.search(r"\.(?:zip|shp|csv|geojson|gpkg|xlsx|kml|tar\.gz)$",
                     up.path,re.I):
            safe_links.append({
                "official_link_file_extension":up.path.rsplit(".",1)[-1].lower()[:10],
                "link_hostname":up.hostname,
                "html_link_has_query_string_redacted":bool(up.query),
            })
    # Do not return raw link paths or text values to avoid leaking sensitive
    # wildlife sites or session params; the host pattern suffices for workflow.
    return {
      "response_kind":"HTML_OFFICIAL_LANDING_PAGE",
      "classified_page_title":p.safe_title,
      "html_form_count":p.forms,
      "html_input_type_counts":p.inputs_by_type,
      "html_button_count":p.buttons,
      "all_HTML_anchor_links_n":len(p.anchor_targets),
      "direct_official_public_file_links_n":len(safe_links),
      "direct_official_file_link_types":safe_links[:16],
      "user_consents_forms_submitted":False,
      "linked_original_bird_file_bytes_downloaded":False,
    }


def metadata_only(url):
    if url not in SOURCES.values() or not official(url):
        raise ValueError("NOT_EXACT_FROZEN_AADC_PUBLIC_ENDPOINT")
    now=url
    with requests.Session() as session:
        for hops in range(MAX_REDIRECTS+1):
            if not official(now):
                raise ValueError("CROSS_DOMAIN_ORIGINAL_PUBLISHER_REDIRECT_NOT_AUTHORIZED")
            with session.get(now,headers={
                "User-Agent":"mina-Paper2-original-AADC-landing-diagnostic-V56a/1.0",
                "Accept":"text/html,application/octet-stream,*/*",
            },stream=True,allow_redirects=False,timeout=(12,35)) as r:
                status=r.status_code
                if status in (301,302,303,307,308):
                    h=r.headers.get("Location")
                    if not h or hops==MAX_REDIRECTS:
                        raise ValueError("AADC_REDIRECT_LIMIT_OR_MISSING_LOCATION")
                    nxt=urljoin(now,h)
                    if not official(nxt):
                        raise ValueError("AADC_DOWNLOAD_CROSS_DOMAIN_REDIRECT")
                    now=nxt
                    continue
                if status in (401,403):
                    return {
                        "source_transport_HTTP_status":status,
                        "source_access_status":"AUTHENTICATION_OR_ACCESS_RESTRICTION",
                        "response_body_read":False,
                    }
                # Read only the first small public HTML page; never follow
                # a form or download animal data from embedded links.
                buf=bytearray()
                for chunk in r.iter_content(32768):
                    if not chunk:continue
                    remaining=MAX_HTML_BYTES-len(buf)
                    buf.extend(chunk[:remaining])
                    if len(buf)>=MAX_HTML_BYTES:break
                result=source_page_structure(bytes(buf),now)
                result.update({
                    "source_transport_HTTP_status":status,
                    "source_content_type_reported":str(r.headers.get("Content-Type",""))[:95],
                    "source_final_official_AADC_host":urlparse(now).hostname,
                    "source_redirect_count":hops,
                    "source_diagnostic_max_html_bytes":MAX_HTML_BYTES,
                    "source_gis_data_published_from_this_diagnostic":False,
                })
                return result
    raise ValueError("AADC_SOURCE_UNEXPECTED_REDIRECT_END")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result={
        "schema":"PAPER2_V56A_AADC_ORIGINAL_DOWNLOAD_LANDING_PAGE_DIAGNOSTIC",
        "date":"2026-10-29",
        "source_V56_job":"https://github.com/zuizui0223/mina/actions/runs/40854775052",
        "source_HTML_NOT_ORIGINAL_GIS_is_known":True,
        "original_AADC_source_urls_compared":SOURCES,
        "no_private_or_credentialed_source_access_attempted":True,
        "source_checks":{},
    }
    for tag,url in SOURCES.items():
        try:
            result["source_checks"][tag]=metadata_only(url)
        except Exception as e:
            result["source_checks"][tag]={
                "status":"SOURCE_LANDING_DIAGNOSTIC_HOLD",
                "error":type(e).__name__+": "+str(e)[:240],
            }
    result["status"]="V56A_ORIGINAL_AADC_PUBLIC_LANDING_DIAGNOSTIC_RECORDED"
    result["source_original_GIS_and_animal_model_fitted"]=False
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
