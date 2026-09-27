#!/usr/bin/env python3
"""Fetch a pinned public mirror of the frozen EDI Palmer daily weather table."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import urllib.parse
import urllib.request
from pathlib import Path

SCIENTIFIC_PACKAGE="Palmer LTER daily weather ver.9"
SCIENTIFIC_DOI="10.6073/pasta/3eefb45dbfb784c3cabe3690ea46fe9e"
SCIENTIFIC_ENTITY="public ver.9 snapshot"

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
    def norm(value: str) -> str:
        return re.sub(r"[^a-z0-9]+","",value.lower())

    normalized={norm(field):field for field in fields}
    date_field=normalized.get("date")
    melted_field=next(
        (
            field for field in fields
            if "precip" in norm(field) and "melted" in norm(field)
        ),
        None,
    )
    snow_field=next(
        (
            field for field in fields
            if "precip" in norm(field) and "snow" in norm(field)
        ),
        None,
    )
    if date_field is None or snow_field is None:
        raise RuntimeError(
            "weather mirror lacks normalized Date/Snow-precipitation fields; "
            f"observed fields={fields!r}"
        )
    if len(rows)!=10674:
        raise RuntimeError(f"expected 10674 daily rows, observed {len(rows)}")
    if rows[0][date_field]!="1989-04-01" or rows[-1][date_field]!="2023-06-30":
        raise RuntimeError(f"unexpected date coverage: {rows[0][date_field]!r}..{rows[-1][date_field]!r}")
    if rows[0][snow_field] not in {"0","0.0","0.00"}:
        raise RuntimeError("first snow-precipitation value disagrees with published EDI structure")
    if melted_field is not None and rows[0][melted_field] not in {"0","0.0","0.00"}:
        raise RuntimeError("first melted-precipitation value disagrees with published EDI structure")

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
    print(f"validated_date_field={date_field}")
    print(f"validated_melted_precipitation_field={melted_field}")
    print(f"validated_snow_field={snow_field}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
