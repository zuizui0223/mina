#!/usr/bin/env python3
"""Locate actual UK Polar Data Centre Cook/Fox/Thomson 2021 historic Antarctic
Peninsula glacier/coastline features from the official RAMADDA entry.

A metadata source record does not prove underlying data files were downloaded.
Do not fabricate file dates or imply that coastline frontal outlines measure
new rock, colony counts or inland glacier extent. This probe tries only
authoritative, fixed source entry URLs and reports failures plainly.
"""
from __future__ import annotations
import argparse,hashlib,html.parser,json,urllib.parse,urllib.request
from pathlib import Path

ENTRY="07727663-9b94-4069-a486-67e4d82177d3"
BASE="https://ramadda.data.bas.ac.uk/repository/entry/show"
TARGETS=[
 BASE+"?"+urllib.parse.urlencode({"entryid":ENTRY}),
 BASE+"?"+urllib.parse.urlencode({"entryid":ENTRY,"output":"json"}),
]
class Links(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.items=[]
    def handle_starttag(self,tag,attrs):
        if tag not in ("a","link"):return
        a=dict(attrs)
        if a.get("href"):self.items.append(a["href"])
def main(out):
    out.mkdir(parents=True,exist_ok=True)
    r=[]
    for url in TARGETS:
        try:
            req=urllib.request.Request(url,headers={
               "User-Agent":"mina-penguin-historical-BAS-source-probe-20261117",
               "Accept":"text/html,application/json;q=0.9,*/*;q=0.3"})
            with urllib.request.urlopen(req,timeout=20) as f:
                code=f.status;kind=f.headers.get("Content-Type","")
                raw=f.read(1_000_000)
            source=raw.decode("utf-8",errors="replace")
            p=Links();p.feed(source) if "<html" in source.lower() else None
            files=[u for u in p.items if
                   any(w in u.lower() for w in (".gpkg",".zip",".shp","entryid","download","get?"))]
            res={"url":url,"http_status":code,"mime":kind,"n_bytes_sampled":len(raw),
                "response_sha256_sampled":hashlib.sha256(raw).hexdigest(),
                "anchor_links_total":len(p.items),
                "possible_download_links":files[:45],
                "seems_official_cook_record":ENTRY in source or "coastal change" in source.lower(),
                "is_full_file_downloaded":False}
        except Exception as e:
            res={"url":url,"status":"NOT_RETRIEVED","error":f"{type(e).__name__}: {str(e)[:240]}",
                 "is_full_file_downloaded":False}
        r.append(res)
    rec={"status":"COOK_2021_HISTORIC_COASTLINE_OFFICIAL_REPOSITORY_SOURCE_GATE",
         "original_DOI":"10.5285/07727663-9b94-4069-a486-67e4d82177d3",
         "original_source_years":"1843-2008 irregular glacier fronts, not annual glacier map",
         "n_official_repository_urls_tested":len(TARGETS),
         "n_successful_page_metadata_reads":sum(z.get("http_status")==200 for z in r),
         "full_glacier_front_geometries_downloaded":False,
         "no_new_bare_rock_or_colony_state_inference":True,
         "results":r}
    (out/"cook2021_historical_front_repository_discovery.json").write_text(
       json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    print("COOK2021_OFFICIAL_SOURCE="+json.dumps(
        {"status":rec["status"],"successful":rec["n_successful_page_metadata_reads"],
         "urls":[{"http_status":z.get("http_status"),"error":z.get("error"),
                  "links":z.get("possible_download_links",[])[:8]} for z in r]},
        ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();main(a.out)
