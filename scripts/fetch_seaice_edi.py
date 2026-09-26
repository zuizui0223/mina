#!/usr/bin/env python3
"""Fetch the frozen EDI seasonal sea-ice package entity via PASTA API.

PASTA exposes registry and data hosts separately. Some runners receive 403 from
registry convenience endpoints, so this fetcher first reads the package
resource map and follows the concrete pasta-d data URL. It fails closed if the
package has more than one readable data entity and no unambiguous tabular name.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import urllib.error
import urllib.request
from pathlib import Path

SCOPE = "knb-lter-pal"
IDENTIFIER = "151"
REVISION = "9"
REGISTRY_BASES = (
    "https://pasta-d.lternet.edu",
    "https://pasta.lternet.edu",
)


def _get(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 mina-island-reassembly/0.4 "
                "(+https://github.com/zuizui0223/mina)"
            ),
            "Accept": "text/plain,application/xml,text/xml,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def _try(urls: list[str]) -> tuple[str, bytes]:
    errors = []
    for url in urls:
        try:
            return url, _get(url)
        except Exception as exc:
            errors.append(f"{url}: {exc!r}")
    raise RuntimeError("all EDI endpoints failed:\n" + "\n".join(errors))


def _resource_map() -> tuple[str, list[str]]:
    urls = [
        f"{base}/package/eml/{SCOPE}/{IDENTIFIER}/{REVISION}"
        for base in REGISTRY_BASES
    ]
    source, raw = _try(urls)
    text = raw.decode("utf-8", errors="replace")
    data_urls = []
    for token in re.split(r"\s+", text):
        token = token.strip()
        if "/package/data/eml/" in token and token.startswith("http"):
            data_urls.append(token)
    # De-duplicate while preserving order.
    data_urls = list(dict.fromkeys(data_urls))
    if not data_urls:
        raise RuntimeError(
            f"resource map contained no data URLs; source={source}; body={text[:1000]!r}"
        )
    return source, data_urls


def _entity_names() -> dict[str, str]:
    urls = [
        f"{base}/package/name/eml/{SCOPE}/{IDENTIFIER}/{REVISION}"
        for base in REGISTRY_BASES
    ]
    try:
        _, raw = _try(urls)
    except RuntimeError:
        return {}
    result = {}
    text = raw.decode("utf-8", errors="replace")
    for line in text.splitlines():
        if "," not in line:
            continue
        entity, name = line.split(",", 1)
        result[entity.strip()] = name.strip()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    map_source, data_urls = _resource_map()
    names = _entity_names()
    print(f"resource_map_source={map_source}")
    print("data_entities=")
    candidates = []
    for url in data_urls:
        entity = url.rstrip("/").split("/")[-1]
        name = names.get(entity, "")
        print(f"  {entity}\t{name}\t{url}")
        if name:
            lower = name.lower()
            if lower.endswith((".csv", ".txt", ".tsv", ".dat")) and (
                "ice" in lower or len(data_urls) == 1
            ):
                candidates.append((url, entity, name))

    if not candidates and len(data_urls) == 1:
        url = data_urls[0]
        entity = url.rstrip("/").split("/")[-1]
        candidates = [(url, entity, names.get(entity, ""))]

    if len(candidates) != 1:
        raise RuntimeError(
            f"expected one unambiguous tabular sea-ice entity; candidates={candidates!r}"
        )

    url, entity, name = candidates[0]
    # Convert registry-host URLs to the concrete data host where possible.
    url = url.replace("https://pasta.lternet.edu/", "https://pasta-d.lternet.edu/")
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
