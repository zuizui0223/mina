#!/usr/bin/env python3
"""Fetch the pinned official PAL-LTER Humble Adelie arrival chronology CSV."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

REPOSITORY = "PAL-LTER/pal-seabirds"
COMMIT = "523e74a064e2f1153704a32731631cbff4395e73"
PATH = (
    "station/formatted/Adelie_Humble_Population_Arrival/"
    "Adelie_Humble_Population_Arrival_1992_2020.csv"
)
GIT_BLOB_SHA = "98cbe512be3899f108c22f44a3ff985ef890a3ff"
URL = f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/{PATH}"
EXPECTED_HEADER = b"studyName,Date,Island,Colony,Adults"


def _git_blob_sha(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data).hexdigest()


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

    if not data.startswith(EXPECTED_HEADER):
        raise RuntimeError("unexpected PAL-LTER arrival CSV header")
    observed_blob = _git_blob_sha(data)
    if observed_blob != GIT_BLOB_SHA:
        raise RuntimeError(
            f"arrival Git blob SHA mismatch: {observed_blob} != {GIT_BLOB_SHA}"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"repository={REPOSITORY}")
    print(f"commit={COMMIT}")
    print(f"path={PATH}")
    print(f"git_blob_sha={observed_blob}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"bytes={len(data)}")
    print(f"rows={max(0, data.count(b'\\n') - 1)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
