#!/usr/bin/env python3
"""Bounded official geodoi landing-page metadata/download-link audit.

Only reads HTML/response headers from official public publication page.
No RAR or biological record downloaded, no credentials or account login.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen

OFFICIAL="https://www.geodoi.ac.cn/WebEn/doi.aspx?Id=1540"
TARGET_NAME="PanAnta.PenguinColony.rar"
MAX_HTML_BYTES=350000

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.active=None
        self.forms=0
        self.postbacks=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="form":self.forms+=1
        if tag=="a":
            self.active={"href":attrs.get("href",""),
                         "onclick":attrs.get("onclick",""),"text":""}
    def handle_data(self,txt):
        if self.active is not None:self.active["text"]+=txt
    def handle_endtag(self,tag):
        if tag=="a" and self.active is not None:
            if "__doPostBack" in self.active["href"] or "__doPostBack" in self.active["onclick"]:
                self.postbacks+=1
            self.links.append(self.active)
            self.active=None


def inspect_page(html, page_url=OFFICIAL):
    p=LinkParser()
    p.feed(html)
    items=[]
    for link in p.links:
        values=link["href"]+" "+link["onclick"]+" "+link["text"]
        if TARGET_NAME.lower() in values.lower() or "download" in values.lower():
            url=urljoin(page_url,link["href"]) if link["href"] else None
            parsed=urlparse(url) if url else None
            is_direct=bool(url and (parsed.scheme=="https" and parsed.hostname in
                                   ("www.geodoi.ac.cn","geodoi.ac.cn")) and
                           parsed.path.lower().endswith(".rar"))
            items.append({
                "text":link["text"].strip()[:90],
                "href":link["href"][:220],
                "onclick":link["onclick"][:220],
                "verified_static_official_rar_href":is_direct,
                "url":url if is_direct else None
            })
    known=TARGET_NAME.lower() in html.lower()
    return {
        "archive_literal_on_page":known,
        "official_page_download_anchor_matches":items[:30],
        "forms_count":p.forms,
        "postback_anchors_count":p.postbacks,
        "verified_direct_archive_urls":[x["url"] for x in items if x["verified_static_official_rar_href"]],
        "status":("STATIC_OFFICIAL_ARCHIVE_HREF_FOUND" if any(x["verified_static_official_rar_href"] for x in items)
                  else "HOLD_NO_STATIC_VERIFIED_OFFICIAL_ARCHIVE_HREF"),
        "no_archive_download_or_biology_executed":True,
    }


def run():
    report={
        "source_publication":"Zhang and Li 2020 doi:10.3974/geodb.2020.05.06.V1",
        "official_page":OFFICIAL,
        "target_listed_archive":TARGET_NAME,
        "status":"HOLD_SOURCE_PAGE_INACCESSIBLE",
        "source_access_not_equivalent_to_2014_footprint_recovered":True,
        "source_2014_Ledda_site_table_listed_NOT_verification_of_live_birds":True,
        "raw_downloaded_bytes":0,
        "biological_feature_records_read":0,
        "causal_mechanism_fitted":False
    }
    try:
        req=Request(OFFICIAL,headers={"User-Agent":"mina-2014-external-geolocation-audit/1.0",
                                     "Accept":"text/html"})
        with urlopen(req,timeout=15) as res:
            http_status=res.status
            html_bytes=res.read(MAX_HTML_BYTES+1)
            content_type=res.headers.get("Content-Type","")
        if http_status!=200 or len(html_bytes)>MAX_HTML_BYTES or "html" not in content_type.lower():
            raise ValueError("Official landing page unexpected status, content type or size")
        doc=html_bytes.decode("utf-8","replace")
        report.update(inspect_page(doc))
        report["HTML_bytes_read"]=len(html_bytes)
        report["site_HTTP_status"]=http_status
    except Exception as e:
        report["error_type"]=type(e).__name__
        report["error_message"]=str(e)[:240]
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    d=run()
    a.out.write_text(json.dumps(d,indent=2)+"\n",encoding="utf8")
    print("OFFICIAL_ZHANG2014_ARCHIVE_LINK_STATUS",d["status"])
    print("OFFICIAL_ARCHIVE_DOWNLOAD_FOUND",len(d.get("verified_direct_archive_urls",[])))
    print("NO_2014_POLYGON_READ_OR_BIOLOGICAL_INFERENCE")


if __name__=="__main__":main()
