#!/usr/bin/env python3
"""Fetch a pinned public mirror of the frozen EDI Palmer daily weather table."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import urllib.parse
import urllib.request
from pathlib import Path

SCIENTIFIC_PACKAGE="knb-lter-pal.28.8"
SCIENTIFIC_DOI="10.6073/pasta/cddd3985350334b876cd7d6d1a5bc7bf"
SCIENTIFIC_ENTITY="375b34051b162d84516ec2d02f864675"

MIRROR_REPO="coding-for-reproducible-research/CfRR_Courses"
MIRROR_COMMIT="de62ff56db79f75c2a63e737f3cc4f63c9363a2c"
MIRROR_PATH="individual_modules/working_with_data_in_R/data/PalmerStation_Daily_Weather.csv"
MIRROR_BLOB_SHA="4b7a462346eef71ebfab1c2ca9a935a66de8886c"
URL=(
    "https://raw.githubusercontent.com/"
    f"{MIRROR_REPO}/{MIRROR_COMMIT}/"
    + urllib.parse.quote(MIRROR_PATH,safe="/")
)
UA="Mozilla/5.0 mina-island-reassembly/0.5"


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("out",type=Path)
    args=p.parse_args()
    req=urllib.request.Request(URL,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=90) as r:
        data=r.read()
    if len(data)<1_000_000:
        raise RuntimeError(f"weather mirror unexpectedly small: {len(data)} bytes")

    text=data.decode("utf-8-sig","strict")
    reader=csv.DictReader(io.StringIO(text))
    rows=list(reader)
    fields=reader.fieldnames or []
    expected={"Date","Rainfall..mm.","Precipitation.Snow..cm."}
    missing=sorted(expected-set(fields))
    if missing:
        raise RuntimeError(f"weather mirror missing expected EDI columns: {missing}")
    if len(rows)!=10674:
        raise RuntimeError(f"expected 10674 daily rows, observed {len(rows)}")
    if rows[0]["Date"]!="1989-04-01":
        raise RuntimeError(f"unexpected first date: {rows[0]['Date']!r}")
    if rows[0]["Rainfall..mm."] not in {"0","0.0"}:
        raise RuntimeError("first rainfall value disagrees with published EDI structure")
    if rows[0]["Precipitation.Snow..cm."] not in {"0","0.0"}:
        raise RuntimeError("first snow-precipitation value disagrees with published EDI structure")

    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(data)
    print(f"scientific_package={SCIENTIFIC_PACKAGE}")
    print(f"scientific_doi={SCIENTIFIC_DOI}")
    print(f"scientific_entity={SCIENTIFIC_ENTITY}")
    print(f"transport_repo={MIRROR_REPO}")
    print(f"transport_commit={MIRROR_COMMIT}")
    print(f"transport_path={MIRROR_PATH}")
    print(f"transport_blob_sha={MIRROR_BLOB_SHA}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"bytes={len(data)}")
    print(f"rows={len(rows)}")
    print("fields=" + ",".join(fields))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
