#!/usr/bin/env python3
"""Fetch Palmer LTER chick-census metadata without the chick-count outcome."""
from __future__ import annotations

import argparse
import hashlib
import time
import urllib.error
import urllib.request
from pathlib import Path

DATASET_ID = "AdeliePenguinAdultandChickCounts"
DOI = "10.6073/pasta/9bf4588c02d6caa12a68133134ed4489"
BASE = "https://pallter-data.marine.rutgers.edu/erddap/tabledap"
PROJECTION = (
    "study_name,time,island_name,colony_code,"
    "num_breeding_pairs,census_time"
)
URL = f"{BASE}/{DATASET_ID}.csv?{PROJECTION}"
EXPECTED_HEADER = PROJECTION.encode("ascii")


def fetch(attempts: int = 4, timeout: int = 120) -> bytes:
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": (
                "mina-island-reassembly/0.15 "
                "(+https://github.com/zuizui0223/mina)"
            )
        },
    )
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt + 1 == attempts:
                break
            time.sleep(3 * (2**attempt))
    raise RuntimeError(
        f"failed to fetch outcome-blind chick metadata after {attempts} attempts"
    ) from last_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    data = fetch()
    if not data.startswith(EXPECTED_HEADER):
        raise RuntimeError("unexpected chick-metadata ERDDAP response header")
    if b"num_chicks" in data.splitlines()[0]:
        raise RuntimeError("outcome column num_chicks leaked into metadata projection")

    digest = hashlib.sha256(data).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"dataset_id={DATASET_ID}")
    print(f"doi={DOI}")
    print(f"url={URL}")
    print(f"sha256={digest}")
    print(f"bytes={len(data)}")
    print("outcome_column_present=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
