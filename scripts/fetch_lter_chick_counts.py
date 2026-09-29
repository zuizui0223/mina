#!/usr/bin/env python3
"""Fetch Palmer LTER colony-specific Adelie chick-production counts."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

DATASET_ID = "AdeliePenguinAdultandChickCounts"
DOI = "10.6073/pasta/9bf4588c02d6caa12a68133134ed4489"
BASE = "https://pallter-data.marine.rutgers.edu/erddap/tabledap"
PROJECTION = (
    "study_name,time,island_name,colony_code,"
    "num_breeding_pairs,num_chicks,census_time"
)
URL = f"{BASE}/{DATASET_ID}.csv?{PROJECTION}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": (
                "mina-island-reassembly/0.15 "
                "(+https://github.com/zuizui0223/mina)"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read()
    expected = (
        b"study_name,time,island_name,colony_code,"
        b"num_breeding_pairs,num_chicks,census_time"
    )
    if not data.startswith(expected):
        raise RuntimeError("unexpected chick-census ERDDAP response header")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"dataset_id={DATASET_ID}")
    print(f"doi={DOI}")
    print(f"url={URL}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"bytes={len(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
