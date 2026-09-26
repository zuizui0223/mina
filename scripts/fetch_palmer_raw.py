#!/usr/bin/env python3
"""Fetch the exact Palmer Penguins raw table used by mina."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

COMMIT = "8957207b78d6ccd1b4654a9dd9c9041b657478ab"
GIT_BLOB = "ba99fbd527f0bb983b3d9615ef5c81a5917ab7d9"
URL = (
    "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/"
    f"{COMMIT}/inst/extdata/penguins_raw.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    with urllib.request.urlopen(URL) as response:
        data = response.read()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"commit={COMMIT}")
    print(f"git_blob={GIT_BLOB}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"bytes={len(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
