#!/usr/bin/env python3
"""Recover Palmer Adélie census ver.8 via EDI PASTA or DataONE replication.

Source recovery only. The target DOI is fixed. A candidate is accepted only
when recovered metadata explicitly contains that DOI token.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DOI_MD5 = "805f6b97593c60cfdfd02266db9ab4b6"
DOI = f"10.6073/pasta/{DOI_MD5}"
PASTA_DOI_URL = (
    f"https://pasta.lternet.edu/package/doi/doi:10.6073/pasta/{DOI_MD5}"
)
DATAONE_BASE = "https://cn.dataone.org/cn/v2"
TITLE_QUERY = '"Adelie penguin area-wide breeding population census"'
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0 Safari/537.36"
)


def fetch(url: str, attempts: int = 3, timeout: int = 120) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "*/*"}
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


def urls_from_text(data: bytes) -> list[str]:
    text = html.unescape(data.decode("utf-8", "strict"))
    urls = re.findall(r"https?://[^\s<\"']+", text)
    out = []
    seen = set()
    for url in urls:
        url = url.rstrip(").,;")
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def save_entities(
    out_dir: Path,
    entity_urls: list[str],
    *,
    prefix: str,
) -> list[tuple[int, str, str, int, str]]:
    manifest = []
    for idx, url in enumerate(entity_urls, start=1):
        data = fetch(url)
        digest = hashlib.sha256(data).hexdigest()
        suffix = ".dat"
        if b"," in data[:500]:
            suffix = ".csv"
        elif b"\t" in data[:500]:
            suffix = ".tsv"
        path = out_dir / f"{prefix}_entity_{idx:02d}{suffix}"
        path.write_bytes(data)
        preview = data[:300].decode("utf-8", "replace").replace("\n", "\\n")
        print(
            f"{prefix}_entity_{idx:02d}_url={url}\n"
            f"{prefix}_entity_{idx:02d}_sha256={digest}\n"
            f"{prefix}_entity_{idx:02d}_bytes={len(data)}\n"
            f"{prefix}_entity_{idx:02d}_preview={preview}"
        )
        manifest.append((idx, url, digest, len(data), path.name))
    return manifest


def recover_pasta(out_dir: Path):
    resource_map = fetch(PASTA_DOI_URL)
    (out_dir / "doi_resource_map.txt").write_bytes(resource_map)
    urls = urls_from_text(resource_map)
    metadata_urls = [u for u in urls if "/package/metadata/eml/" in u]
    data_urls = [u for u in urls if "/package/data/eml/" in u]
    if not metadata_urls or not data_urls:
        raise RuntimeError("PASTA DOI resource map lacks metadata/data URLs")
    metadata = fetch(metadata_urls[0])
    if DOI_MD5 not in metadata.decode("utf-8", "replace").lower():
        raise RuntimeError("PASTA metadata does not contain target DOI")
    (out_dir / "metadata.xml").write_bytes(metadata)
    package_match = re.search(
        r"/package/metadata/eml/([^/]+)/([^/]+)/(newest|oldest|\d+)",
        metadata_urls[0],
    )
    package_id = ".".join(package_match.groups()) if package_match else None
    if not package_id:
        raise RuntimeError("cannot parse PASTA package id")
    print("transport=pasta")
    print(f"resolved_package_id={package_id}")
    print(f"metadata_url={metadata_urls[0]}")
    print(f"metadata_sha256={hashlib.sha256(metadata).hexdigest()}")
    return package_id, save_entities(out_dir, data_urls, prefix="pasta")


def dataone_query() -> dict:
    params = {
        "q": f"title:{TITLE_QUERY} AND documents:*",
        "fl": "identifier,title,documents,dataUrl,formatId,seriesId,obsoletes,obsoletedBy",
        "rows": "100",
        "wt": "json",
    }
    url = f"{DATAONE_BASE}/query/solr/?" + urllib.parse.urlencode(params)
    raw = fetch(url)
    return json.loads(raw.decode("utf-8"))


def dataone_object_url(pid: str) -> str:
    # CN resolve is the documented public path used for EDI replicated objects.
    return f"{DATAONE_BASE}/resolve/" + urllib.parse.quote(pid, safe="")


def recover_dataone(out_dir: Path):
    search = dataone_query()
    (out_dir / "dataone_search.json").write_text(
        json.dumps(search, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    docs = search.get("response", {}).get("docs", [])
    print(f"dataone_candidate_metadata_count={len(docs)}")
    matches = []
    for doc in docs:
        identifier = str(doc.get("identifier", ""))
        if not identifier:
            continue
        try:
            metadata = fetch(dataone_object_url(identifier))
        except RuntimeError:
            continue
        text = metadata.decode("utf-8", "replace").lower()
        if DOI_MD5 not in text:
            continue
        matches.append((doc, metadata))
    if len(matches) != 1:
        raise RuntimeError(
            f"DataONE DOI-verified metadata matches={len(matches)}; expected exactly one"
        )

    doc, metadata = matches[0]
    identifier = str(doc["identifier"])
    (out_dir / "metadata.xml").write_bytes(metadata)
    print("transport=dataone")
    print(f"metadata_identifier={identifier}")
    print(f"metadata_sha256={hashlib.sha256(metadata).hexdigest()}")
    print(f"metadata_title={doc.get('title')}")

    documents = doc.get("documents", [])
    if isinstance(documents, str):
        documents = [documents]
    if not documents:
        raise RuntimeError("DOI-verified DataONE metadata has no documented data entities")

    entity_urls = [dataone_object_url(str(pid)) for pid in documents]
    manifest = save_entities(out_dir, entity_urls, prefix="dataone")

    package_match = re.search(
        r"/package/metadata/eml/([^/]+)/([^/]+)/(\d+)",
        identifier,
    )
    package_id = ".".join(package_match.groups()) if package_match else "unparsed"
    print(f"resolved_package_id={package_id}")
    return package_id, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"target_doi={DOI}")
    try:
        package_id, manifest = recover_pasta(args.out_dir)
    except RuntimeError as pasta_error:
        print(f"pasta_recovery_warning={pasta_error}")
        package_id, manifest = recover_dataone(args.out_dir)

    if not manifest:
        raise RuntimeError("no census v8 data entities recovered")

    (args.out_dir / "manifest.tsv").write_text(
        "index\turl\tsha256\tbytes\tfilename\n"
        + "".join(
            f"{idx}\t{url}\t{digest}\t{size}\t{name}\n"
            for idx, url, digest, size, name in manifest
        ),
        encoding="utf-8",
    )
    (args.out_dir / "resolved_package_id.txt").write_text(
        package_id + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
