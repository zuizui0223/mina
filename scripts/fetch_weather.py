#!/usr/bin/env python3
"""Fetch the exact EDI Palmer Station daily weather entity used by Stage 4."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

PACKAGE = "knb-lter-pal.28.8"
DOI = "10.6073/pasta/cddd3985350334b876cd7d6d1a5bc7bf"
ENTITY = "375b34051b162d84516ec2d02f864675"
URL = (
    "https://pasta.lternet.edu/package/data/eml/"
    f"knb-lter-pal/28/8/{ENTITY}"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "mina-island-reassembly/0.4 (+https://github.com/zuizui0223/mina)"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read()
    if len(data) < 1000:
        raise RuntimeError("weather entity unexpectedly small")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"package={PACKAGE}")
    print(f"doi={DOI}")
    print(f"entity={ENTITY}")
    print(f"url={URL}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"bytes={len(data)}")
    print("first_lines=")
    for line in data.decode("utf-8-sig", errors="replace").splitlines()[:5]:
        print(line[:1000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
