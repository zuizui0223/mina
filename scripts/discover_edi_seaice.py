#!/usr/bin/env python3
"""Discover public PASTA resources for the frozen Palmer sea-ice package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

SCOPE="knb-lter-pal"
IDENTIFIER="151"
REVISION="9"
UA="Mozilla/5.0 mina-island-reassembly/0.4"
BASE="https://pasta.lternet.edu"

ENDPOINTS={
    "resource_map":f"{BASE}/package/eml/{SCOPE}/{IDENTIFIER}/{REVISION}",
    "entity_list":f"{BASE}/package/data/eml/{SCOPE}/{IDENTIFIER}/{REVISION}",
    "entity_names":f"{BASE}/package/name/eml/{SCOPE}/{IDENTIFIER}/{REVISION}",
    "metadata":f"{BASE}/package/metadata/eml/{SCOPE}/{IDENTIFIER}/{REVISION}",
    "doi":f"{BASE}/package/doi/eml/{SCOPE}/{IDENTIFIER}/{REVISION}",
}


def fetch(url: str) -> tuple[int, bytes, dict[str,str]]:
    req=urllib.request.Request(
        url,
        headers={
            "User-Agent":UA,
            "Accept":"text/plain, application/xml;q=0.9, */*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(req,timeout=90) as r:
            return int(r.status),r.read(),dict(r.headers.items())
    except urllib.error.HTTPError as exc:
        return int(exc.code),exc.read(),dict(exc.headers.items())


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("out_dir",type=Path)
    args=p.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)

    probes={}
    for name,url in ENDPOINTS.items():
        status,data,headers=fetch(url)
        path=args.out_dir/f"{name}.txt"
        path.write_bytes(data)
        probes[name]={
            "url":url,
            "status":status,
            "bytes":len(data),
            "sha256":hashlib.sha256(data).hexdigest(),
            "content_type":headers.get("Content-Type"),
            "head":data[:1000].decode("utf-8","replace"),
        }

    urls=[]
    for source in ("resource_map","entity_list"):
        text=(args.out_dir/f"{source}.txt").read_text("utf-8","replace")
        urls.extend(re.findall(r"https?://[^\s<>\"]+",text))
    entity_urls=[]
    seen=set()
    for url in urls:
        if "/package/data/" not in url:
            continue
        clean=url.strip().rstrip(",")
        if clean in seen:
            continue
        seen.add(clean)
        entity_urls.append(clean)

    downloads=[]
    for i,url in enumerate(entity_urls):
        status,data,headers=fetch(url)
        filename=f"entity_{i}.dat"
        (args.out_dir/filename).write_bytes(data)
        downloads.append({
            "url":url,
            "status":status,
            "filename":filename,
            "bytes":len(data),
            "sha256":hashlib.sha256(data).hexdigest(),
            "content_type":headers.get("Content-Type"),
            "head":data[:1000].decode("utf-8","replace"),
        })

    manifest={
        "package_id":f"{SCOPE}.{IDENTIFIER}.{REVISION}",
        "probes":probes,
        "entity_urls":entity_urls,
        "downloads":downloads,
    }
    (args.out_dir/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))

    # PASTA revision 9 currently denies anonymous entity reads despite the
    # published DOI. Fall back to the Palmer LTER ERDDAP catalog and record
    # matching public mirrors without changing the frozen scientific endpoint.
    erddap_search=(
        "https://pallter-data.marine.rutgers.edu/erddap/search/index.csv"
        "?page=1&itemsPerPage=1000&searchFor=sea%20ice"
    )
    status,data,headers=fetch(erddap_search)
    (args.out_dir/"erddap_search.csv").write_bytes(data)
    manifest["erddap_search"]={
        "url":erddap_search,
        "status":status,
        "bytes":len(data),
        "sha256":hashlib.sha256(data).hexdigest(),
        "head":data[:5000].decode("utf-8","replace"),
    }
    (args.out_dir/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("ERDDAP_SEARCH")
    print(manifest["erddap_search"]["head"])

    # Exact entity identifier independently recoverable from the public
    # Diou-Cass 2026 reproducibility repository, which documents this same
    # knb-lter-pal.151.9 package and reads it over plain HTTP.
    exact_entity=(
        "http://pasta.lternet.edu/package/data/eml/"
        "knb-lter-pal/151/9/13bb2b05f1e930574150d9cd8ab04b8a"
    )
    exact_status,exact_data,exact_headers=fetch(exact_entity)
    (args.out_dir/"seasonal_seaice.csv").write_bytes(exact_data)
    manifest["exact_entity"]={
        "url":exact_entity,
        "entity_id":"13bb2b05f1e930574150d9cd8ab04b8a",
        "status":exact_status,
        "bytes":len(exact_data),
        "sha256":hashlib.sha256(exact_data).hexdigest(),
        "content_type":exact_headers.get("Content-Type"),
        "head":exact_data[:3000].decode("utf-8","replace"),
        "provenance_mirror":"qdioucass/pallter_decadalpigmentindices:data_code_analysis/dataset curation/3_PALLTER_EDISeaIceDataImport.py"
    }
    (args.out_dir/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("EXACT_ENTITY")
    print(json.dumps(manifest["exact_entity"],indent=2))

    if exact_status!=200 or len(exact_data)<100:
        raise SystemExit("exact frozen EDI sea-ice entity was not readable")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
