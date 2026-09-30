#!/usr/bin/env python3
"""Recover Palmer Adélie census ver.8 from the public EDI PASTA API.

Fail closed unless the candidate package metadata contains the DOI cited by
Cimino et al. (2025). This script performs source recovery only; it does not
fit ecological models.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

SCOPE = "knb-lter-pal"
IDENTIFIER = "87"
REVISION = "8"
EXPECTED_DOI_TOKEN = "805f6b97593c60cfdfd02266db9ab4b6"
METADATA_URL = (
    f"https://pasta.lternet.edu/package/metadata/eml/"
    f"{SCOPE}/{IDENTIFIER}/{REVISION}"
)
UA = "mina-palmer-census-audit/1.0 (+https://github.com/zuizui0223/mina)"


def fetch(url: str, attempts: int = 4, timeout: int = 120) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt + 1 == attempts:
                break
            time.sleep(2 * (2**attempt))
    raise RuntimeError(f"failed to fetch {url}") from last_error


def entity_urls(metadata: bytes) -> list[str]:
    text = html.unescape(metadata.decode("utf-8", "strict"))
    urls = re.findall(r"https?://[^<\s\"']+", text)
    out = []
    seen = set()
    for url in urls:
        url = url.rstrip(").,;")
        if "/package/data/eml/" not in url:
            continue
        if url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    metadata = fetch(METADATA_URL)
    metadata_text = metadata.decode("utf-8", "strict").lower()
    if EXPECTED_DOI_TOKEN not in metadata_text:
        raise RuntimeError(
            "candidate knb-lter-pal.87.8 metadata does not contain expected "
            f"DOI token {EXPECTED_DOI_TOKEN}; refusing to use guessed package"
        )

    metadata_path = args.out_dir / "knb-lter-pal.87.8.xml"
    metadata_path.write_bytes(metadata)
    print(f"metadata_url={METADATA_URL}")
    print(f"metadata_sha256={hashlib.sha256(metadata).hexdigest()}")
    print(f"metadata_bytes={len(metadata)}")

    urls = entity_urls(metadata)
    if not urls:
        raise RuntimeError("verified metadata contains no PASTA data entity URLs")
    print(f"entity_url_count={len(urls)}")

    manifest = []
    for idx, url in enumerate(urls, start=1):
        data = fetch(url)
        digest = hashlib.sha256(data).hexdigest()
        suffix = ".dat"
        lower = data[:500].lower()
        if b"," in data[:500]:
            suffix = ".csv"
        elif b"\t" in data[:500]:
            suffix = ".tsv"
        path = args.out_dir / f"entity_{idx:02d}{suffix}"
        path.write_bytes(data)
        preview = data[:250].decode("utf-8", "replace").replace("\n", "\\n")
        print(
            f"entity_{idx:02d}_url={url}\n"
            f"entity_{idx:02d}_sha256={digest}\n"
            f"entity_{idx:02d}_bytes={len(data)}\n"
            f"entity_{idx:02d}_preview={preview}"
        )
        manifest.append((idx, url, digest, len(data), path.name))

    manifest_path = args.out_dir / "manifest.tsv"
    manifest_path.write_text(
        "index\turl\tsha256\tbytes\tfilename\n"
        + "".join(
            f"{idx}\t{url}\t{digest}\t{size}\t{name}\n"
            for idx, url, digest, size, name in manifest
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
