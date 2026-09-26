#!/usr/bin/env python3
"""Fetch the pinned public mirror of Palmer LTER seasonal sea-ice indices.

The mirror file was generated from EDI package knb-lter-pal.151.9 by the
published Diou-Cass et al. reproducibility workflow. The EDI package currently
denies anonymous direct entity reads, so mina pins both the original DOI/entity
ID and the public Git-LFS content hash used as the transport mirror.
"""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

REPO_COMMIT="aa11abacdd3a9d64a9d6a7574d6ee12f073cf62c"
LFS_SHA256="8a310b2af2abd5b27604100cc082b65c38f1274f0f6eb689514a2ffb8c2f7393"
EXPECTED_SIZE=2418
URL=(
    "https://media.githubusercontent.com/media/qdioucass/"
    "pallter_decadalpigmentindices/"
    f"{REPO_COMMIT}/data_code_analysis/local%20data/"
    "PALLTER_EDISeaIceDataframe.csv"
)
EDI_ENTITY="13bb2b05f1e930574150d9cd8ab04b8a"
EDI_DOI="10.6073/pasta/4207e529832840db2282498d9f4f4f05"


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("out",type=Path)
    args=p.parse_args()
    req=urllib.request.Request(URL,headers={"User-Agent":"mina-island-reassembly/0.4"})
    with urllib.request.urlopen(req,timeout=90) as r:
        data=r.read()
    sha=hashlib.sha256(data).hexdigest()
    if sha!=LFS_SHA256:
        raise RuntimeError(f"sea-ice mirror hash mismatch: {sha}")
    if len(data)!=EXPECTED_SIZE:
        raise RuntimeError(f"sea-ice mirror size mismatch: {len(data)}")
    if not data.startswith(b"Year,"):
        raise RuntimeError("unexpected sea-ice mirror header")
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(data)
    print(f"edi_doi={EDI_DOI}")
    print(f"edi_entity={EDI_ENTITY}")
    print(f"mirror_commit={REPO_COMMIT}")
    print(f"sha256={sha}")
    print(f"bytes={len(data)}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
