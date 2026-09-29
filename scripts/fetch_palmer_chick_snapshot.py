#!/usr/bin/env python3
"""Fetch the frozen public Palmer chick-production snapshot used for v1."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

REPO_COMMIT = "d782d30e5d28c468d53390abf86eb77eec685826"
URL = (
    "https://raw.githubusercontent.com/"
    "robitalec/2023-CSEE-reproducible-workflows-workshop/"
    + REPO_COMMIT
    + "/raw-data/adelie-adult-chick-counts.csv"
)
EXPECTED_HEADER = b"studyName,Date GMT,Time GMT,Island,Colony,Adults,Chicks"

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("out",type=Path)
    a=p.parse_args()
    req=urllib.request.Request(URL,headers={"User-Agent":"mina-island-reassembly/0.15"})
    with urllib.request.urlopen(req,timeout=90) as r:
        data=r.read()
    if not data.startswith(EXPECTED_HEADER):
        raise RuntimeError("unexpected Palmer chick snapshot header")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_bytes(data)
    print("source_url=",URL)
    print("repo_commit=",REPO_COMMIT)
    print("sha256=",hashlib.sha256(data).hexdigest())
    print("bytes=",len(data))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
