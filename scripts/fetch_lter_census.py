#!/usr/bin/env python3
"""Fetch the frozen Palmer LTER five-island Adélie breeding census."""
from __future__ import annotations

import argparse
import hashlib
import time
import urllib.error
import urllib.request
from pathlib import Path

DATASET_ID = "AdeliePenguinCensus"
DOI = "10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e"
BASE = "https://pallter-data.marine.rutgers.edu/erddap/tabledap"
PROJECTION = "study_name,time,island_name,colony_code,num_breeding_pairs"
URL = f"{BASE}/{DATASET_ID}.csv?{PROJECTION}"
EXPECTED_SHA256 = "b4ef04e2275ea779fc8fe54fa13528dc2052d37dd88a60c811d54c7601f67b16"
EXPECTED_HEADER = b"study_name,time,island_name,colony_code,num_breeding_pairs"


def fetch(attempts: int = 4, timeout: int = 120) -> bytes:
    request = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "mina-island-reassembly/0.15 (+https://github.com/zuizui0223/mina)"
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
        f"failed to fetch frozen Palmer census after {attempts} attempts"
    ) from last_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    data = fetch()
    if not data.startswith(EXPECTED_HEADER):
        raise RuntimeError("unexpected ERDDAP response header")

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(
            "Palmer census source drifted from frozen analysis bytes: "
            f"{digest} != {EXPECTED_SHA256}"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"dataset_id={DATASET_ID}")
    print(f"doi={DOI}")
    print(f"url={URL}")
    print(f"sha256={digest}")
    print(f"bytes={len(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
