#!/usr/bin/env python3
"""Outcome-blind source discovery/audit for East Antarctic Adelie expansion route."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

PAGES = {
    "occupancy": "https://data.aad.gov.au/metadata/records/AAS_4088_Adelie_Occupancy",
    "potential_habitat": "https://data.aad.gov.au/metadata/records/AAS_4088_Adelie_Potential_Habitats",
    "plos_article": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0139877",
}
PLOS_S1 = "https://journals.plos.org/plosone/article/file?type=supplementary&id=info:doi/10.1371/journal.pone.0139877.s001"

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "mina-source-audit/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def extract_download_links(html: str, base: str) -> list[str]:
    # Keep only explicit AADC EDS direct-download links surfaced by the official page.
    found = set()
    pats = [
        r'https?://data\.aad\.gov\.au/eds/\d+/download[^"\'<> ]*',
        r'["\'](/eds/\d+/download[^"\'<> ]*)["\']',
    ]
    for pat in pats:
        for m in re.finditer(pat, html, flags=re.I):
            value = m.group(1) if m.lastindex else m.group(0)
            found.add(urljoin(base, value))
    return sorted(found)

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path)
    a=p.parse_args()

    pages={}
    all_links={}
    for key,url in PAGES.items():
        raw=fetch(url)
        text=raw.decode("utf-8", errors="replace")
        links=extract_download_links(text,url)
        pages[key]={
            "url":url,
            "http_bytes":len(raw),
            "sha256":sha(raw),
            "direct_download_links":links,
        }
        all_links[key]=links

    # Accessibility only; do not inspect S1 biological values.
    s1_raw=fetch(PLOS_S1)
    result={
        "schema_version":1,
        "analysis_id":"east-antarctica-expansion-source-link-audit-v1",
        "status":"outcome_blind_source_gate",
        "pages":pages,
        "plos_s1":{
            "url":PLOS_S1,
            "http_bytes":len(s1_raw),
            "sha256":sha(s1_raw),
            "content_prefix_hex":s1_raw[:16].hex(),
            "download_accessible":len(s1_raw)>0,
        },
        "gate":{
            "occupancy_direct_link_found":bool(all_links["occupancy"]),
            "potential_habitat_direct_link_found":bool(all_links["potential_habitat"]),
            "plos_s1_accessible":len(s1_raw)>0,
        },
        "effect_computed":False,
        "occupancy_values_inspected":False,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
