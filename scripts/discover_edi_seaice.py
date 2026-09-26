#!/usr/bin/env python3
"""Discover and download the exact EDI sea-ice table without opening values manually.

The mechanism contract is frozen before this script is executed. This utility
fetches EML metadata for knb-lter-pal.151.9, records entity names/URLs, and
downloads tabular entities. The analysis script decides which entity/columns
match the frozen PAL DSR Grid + ice-season-duration definition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PACKAGE="knb-lter-pal"
DATASET="151"
VERSION="9"
META=f"https://pasta.lternet.edu/package/metadata/eml/{PACKAGE}/{DATASET}/{VERSION}"
UA="mina-island-reassembly/0.4 (+https://github.com/zuizui0223/mina)"


def fetch(url: str) -> bytes:
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=90) as r:
        return r.read()


def local(tag: str) -> str:
    return tag.split("}")[-1]


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("out_dir",type=Path)
    args=p.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)

    xml=fetch(META)
    (args.out_dir/"metadata.xml").write_bytes(xml)
    root=ET.fromstring(xml)

    entities=[]
    for node in root.iter():
        if local(node.tag)!="dataTable":
            continue
        name=None
        obj=None
        urls=[]
        attrs=[]
        for child in node.iter():
            key=local(child.tag)
            text=(child.text or "").strip()
            if key=="entityName" and text and name is None:
                name=text
            elif key=="objectName" and text and obj is None:
                obj=text
            elif key=="url" and text.startswith("http"):
                urls.append(text)
            elif key=="attributeName" and text:
                attrs.append(text)
        entities.append({"entity_name":name,"object_name":obj,"urls":urls,"attributes":attrs})

    downloaded=[]
    for i,e in enumerate(entities):
        candidates=[u for u in e["urls"] if "package/data/" in u or "download" in u]
        for j,url in enumerate(candidates):
            try:
                data=fetch(url)
            except Exception as exc:
                downloaded.append({"entity_index":i,"url":url,"error":repr(exc)})
                continue
            suffix=Path(urllib.request.urlparse(url).path).suffix if False else ""
            filename=f"entity_{i}_{j}.dat"
            path=args.out_dir/filename
            path.write_bytes(data)
            downloaded.append({
                "entity_index":i,
                "url":url,
                "filename":filename,
                "bytes":len(data),
                "sha256":hashlib.sha256(data).hexdigest(),
                "head":data[:300].decode("utf-8","replace"),
            })

    manifest={
        "metadata_url":META,
        "metadata_sha256":hashlib.sha256(xml).hexdigest(),
        "entities":entities,
        "downloads":downloaded,
    }
    (args.out_dir/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
