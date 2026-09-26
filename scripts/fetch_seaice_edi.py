#!/usr/bin/env python3
"""Fetch the frozen EDI seasonal sea-ice package entity via PASTA API."""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

SCOPE = "knb-lter-pal"
IDENTIFIER = "151"
REVISION = "9"
NAMES_URL = (
    f"https://pasta.lternet.edu/package/name/eml/"
    f"{SCOPE}/{IDENTIFIER}/{REVISION}"
)
DATA_BASE = (
    f"https://pasta.lternet.edu/package/data/eml/"
    f"{SCOPE}/{IDENTIFIER}/{REVISION}"
)


def _get(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "mina-island-reassembly/0.4 (+https://github.com/zuizui0223/mina)"
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    names_text = _get(NAMES_URL).decode("utf-8").strip()
    rows = []
    for line in names_text.splitlines():
        if not line.strip() or "," not in line:
            continue
        entity, name = line.split(",", 1)
        rows.append((entity.strip(), name.strip()))
    print("entities=")
    for entity, name in rows:
        print(f"  {entity}\t{name}")

    candidates = [
        (entity, name)
        for entity, name in rows
        if name.lower().endswith((".csv", ".txt", ".tsv"))
        and ("ice" in name.lower() or len(rows) == 1)
    ]
    if len(candidates) != 1:
        raise RuntimeError(
            f"expected exactly one sea-ice tabular entity, candidates={candidates!r}"
        )

    entity, name = candidates[0]
    url = f"{DATA_BASE}/{entity}"
    data = _get(url)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    print(f"selected_entity={entity}")
    print(f"entity_name={name}")
    print(f"url={url}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"bytes={len(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
