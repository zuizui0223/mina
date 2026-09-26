#!/usr/bin/env python3
"""Fetch frozen Palmer seasonal sea-ice data.

Primary source is EDI package knb-lter-pal.151.9. Some CI networks receive HTTP
403 from PASTA. In that case, use the published PalPhenology Zenodo associated
data (record 7520769) as a transport fallback. File selection is mechanical:
exactly one public file whose name contains "ice" or "sea" and is tabular, or
the script fails closed after printing all available files.

The ecological predictor definition remains the frozen one in
PALMER_REGIONAL_LOCAL_MECHANISM_V1.json; this script only solves transport.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

SCOPE = "knb-lter-pal"
IDENTIFIER = "151"
REVISION = "9"
ZENODO_RECORD = "7520769"


def _get(url: str, *, accept: str = "*/*") -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 mina-island-reassembly/0.4 "
                "(+https://github.com/zuizui0223/mina)"
            ),
            "Accept": accept,
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def _try_edi() -> tuple[bytes, dict[str, str]] | None:
    bases = ("https://pasta-d.lternet.edu", "https://pasta.lternet.edu")
    errors = []
    for base in bases:
        url = f"{base}/package/eml/{SCOPE}/{IDENTIFIER}/{REVISION}"
        try:
            raw = _get(url, accept="application/xml,text/xml,text/plain,*/*")
        except Exception as exc:
            errors.append(f"{url}: {exc!r}")
            continue
        text = raw.decode("utf-8", errors="replace")
        data_urls = list(dict.fromkeys(
            token.strip()
            for token in re.split(r"\s+", text)
            if token.strip().startswith("http") and "/package/data/eml/" in token
        ))
        if len(data_urls) != 1:
            errors.append(f"{url}: expected one data entity, got {data_urls!r}")
            continue
        data_url = data_urls[0].replace(
            "https://pasta.lternet.edu/", "https://pasta-d.lternet.edu/"
        )
        try:
            data = _get(data_url)
        except Exception as exc:
            errors.append(f"{data_url}: {exc!r}")
            continue
        return data, {
            "transport": "edi_pasta",
            "url": data_url,
            "package": f"{SCOPE}.{IDENTIFIER}.{REVISION}",
        }
    print("edi_transport_errors=")
    for error in errors:
        print("  " + error)
    return None


def _zenodo_fallback() -> tuple[bytes, dict[str, str]]:
    api = f"https://zenodo.org/api/records/{ZENODO_RECORD}"
    record = json.loads(_get(api, accept="application/json").decode("utf-8"))
    files = record.get("files", [])
    print("zenodo_files=")
    candidates = []
    for item in files:
        key = str(item.get("key") or item.get("filename") or "")
        links = item.get("links", {})
        download = links.get("content") or links.get("self")
        print(f"  {key}\t{download}")
        lower = key.lower()
        if (
            download
            and lower.endswith((".csv", ".txt", ".tsv", ".dat"))
            and ("ice" in lower or "sea" in lower)
        ):
            candidates.append((key, download))
    if len(candidates) != 1:
        raise RuntimeError(
            "Zenodo fallback requires exactly one mechanically selected "
            f"sea/ice tabular file; candidates={candidates!r}"
        )
    key, url = candidates[0]
    data = _get(url)
    return data, {
        "transport": "zenodo_palphenology_fallback",
        "url": url,
        "record": ZENODO_RECORD,
        "file": key,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    fetched = _try_edi()
    if fetched is None:
        data, provenance = _zenodo_fallback()
    else:
        data, provenance = fetched

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    for key, value in provenance.items():
        print(f"{key}={value}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"bytes={len(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
