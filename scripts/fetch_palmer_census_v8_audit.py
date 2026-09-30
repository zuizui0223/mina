#!/usr/bin/env python3
"""Recover Palmer Adélie census ver.8 through the public EDI DOI resource map.

This is source recovery only. The DOI is the authority: no package scope,
identifier, revision, or data entity is guessed.
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

DOI_MD5 = "805f6b97593c60cfdfd02266db9ab4b6"
DOI = f"10.6073/pasta/{DOI_MD5}"
RESOURCE_MAP_URL = (
    f"https://pasta.lternet.edu/package/doi/doi:10.6073/pasta/{DOI_MD5}"
)
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0 Safari/537.36"
)


def fetch(url: str, attempts: int = 4, timeout: int = 120) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "*/*",
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
            time.sleep(2 * (2**attempt))
    raise RuntimeError(f"failed to fetch {url}") from last_error


def resource_urls(resource_map: bytes) -> list[str]:
    text = html.unescape(resource_map.decode("utf-8", "strict"))
    urls = re.findall(r"https?://[^\s<\"']+", text)
    out: list[str] = []
    seen: set[str] = set()
    for url in urls:
        url = url.rstrip(").,;")
        if "pasta" not in url or url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    resource_map = fetch(RESOURCE_MAP_URL)
    map_path = args.out_dir / "doi_resource_map.txt"
    map_path.write_bytes(resource_map)
    print(f"doi={DOI}")
    print(f"resource_map_url={RESOURCE_MAP_URL}")
    print(f"resource_map_sha256={hashlib.sha256(resource_map).hexdigest()}")
    print(f"resource_map_bytes={len(resource_map)}")

    urls = resource_urls(resource_map)
    package_urls = [u for u in urls if "/package/eml/" in u]
    metadata_urls = [u for u in urls if "/package/metadata/eml/" in u]
    data_urls = [u for u in urls if "/package/data/eml/" in u]
    if not package_urls:
        raise RuntimeError("DOI resource map did not expose a package resource URL")
    if not data_urls:
        raise RuntimeError("DOI resource map did not expose any data entity URL")

    package_ids = set()
    for url in package_urls + metadata_urls + data_urls:
        match = re.search(
            r"/package/(?:data/|metadata/)?eml/([^/]+)/([^/]+)/(newest|oldest|\d+)",
            url,
        )
        if match:
            package_ids.add(".".join(match.groups()))
    if len(package_ids) != 1:
        raise RuntimeError(f"DOI resource map is ambiguous: package_ids={package_ids!r}")
    package_id = next(iter(package_ids))
    print(f"resolved_package_id={package_id}")
    print(f"resource_url_count={len(urls)}")
    print(f"data_entity_count={len(data_urls)}")

    metadata_recovered = False
    if metadata_urls:
        try:
            metadata = fetch(metadata_urls[0])
            (args.out_dir / "metadata.xml").write_bytes(metadata)
            print(f"metadata_url={metadata_urls[0]}")
            print(f"metadata_sha256={hashlib.sha256(metadata).hexdigest()}")
            print(f"metadata_bytes={len(metadata)}")
            metadata_recovered = True
        except RuntimeError as exc:
            print(f"metadata_recovery_warning={exc}")
    print(f"metadata_recovered={str(metadata_recovered).lower()}")

    manifest = []
    for idx, url in enumerate(data_urls, start=1):
        data = fetch(url)
        digest = hashlib.sha256(data).hexdigest()
        suffix = ".dat"
        if b"," in data[:500]:
            suffix = ".csv"
        elif b"\t" in data[:500]:
            suffix = ".tsv"
        path = args.out_dir / f"entity_{idx:02d}{suffix}"
        path.write_bytes(data)
        preview = data[:300].decode("utf-8", "replace").replace("\n", "\\n")
        print(
            f"entity_{idx:02d}_url={url}\n"
            f"entity_{idx:02d}_sha256={digest}\n"
            f"entity_{idx:02d}_bytes={len(data)}\n"
            f"entity_{idx:02d}_preview={preview}"
        )
        manifest.append((idx, url, digest, len(data), path.name))

    (args.out_dir / "manifest.tsv").write_text(
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
