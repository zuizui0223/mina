#!/usr/bin/env python3
"""Fetch the published Santora et al. (2020) Adélie 5-km colony shapefile from Dryad."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

FILES = {
    "ADPE-5km.dbf": "https://datadryad.org/downloads/file_stream/578664",
    "ADPE-5km.prj": "https://datadryad.org/downloads/file_stream/578663",
    "ADPE-5km.shp": "https://datadryad.org/downloads/file_stream/578667",
    "ADPE-5km.shx": "https://datadryad.org/downloads/file_stream/578669",
}
DOI = "10.7291/D1NT0S"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for name, url in FILES.items():
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "mina-island-reassembly/0.15 (+https://github.com/zuizui0223/mina)"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        target = args.out_dir / name
        target.write_bytes(data)
        print(f"{name} bytes={len(data)} sha256={hashlib.sha256(data).hexdigest()}")
    print(f"doi={DOI}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
