#!/usr/bin/env python3
"""Outcome-blind AADC EDS asset resolver.

Uses the same public EDS API endpoints as bowerbird::bb_aadc_datasource_meta().
It records dataset/object metadata and optionally downloads schema-inspectable
files, but never summarizes biological values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://data.aad.gov.au/eds/api"
ALLOW_EXT = {".csv", ".tsv", ".xlsx", ".xls", ".zip", ".json", ".geojson", ".gpkg"}
MAX_OBJECT_BYTES = 100 * 1024 * 1024
MAX_TOTAL_BYTES = 250 * 1024 * 1024

CTX = ssl.create_default_context()


def get_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "mina-aadc-schema-audit/1.0"})
    with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
        return r.read()


def get_json(url: str):
    return json.loads(get_bytes(url).decode("utf-8"))


def safe_name(name: str) -> str:
    p = Path(name)
    parts = [x for x in p.parts if x not in {"", ".", "..", "/"}]
    return "__".join(parts) if parts else "unnamed"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--metadata-id", required=True)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--download-dir", required=True, type=Path)
    a = p.parse_args()

    meta_url = f"{API}/metadata/{urllib.parse.quote(a.metadata_id)}?format=json"
    meta = get_json(meta_url)
    rows = meta if isinstance(meta, list) else [meta]

    datasets = []
    total_downloaded = 0
    a.download_dir.mkdir(parents=True, exist_ok=True)

    for row in rows:
        uuid = row.get("uuid")
        if not uuid:
            continue
        obj_url = f"{API}/dataset/{urllib.parse.quote(str(uuid))}/objects?recursive=true"
        objs = get_json(obj_url)
        if not isinstance(objs, list):
            objs = []
        ds = {
            "eds_id": row.get("eds_id"),
            "uuid": uuid,
            "dataset_name": row.get("dataset_name"),
            "objects_url": obj_url,
            "objects": [],
        }
        for obj in objs:
            name = str(obj.get("name", ""))
            size = int(obj.get("size") or 0)
            suffix = Path(name).suffix.lower()
            inspectable = suffix in ALLOW_EXT
            rec = {
                "name": name,
                "size": size,
                "suffix": suffix,
                "schema_inspectable": inspectable,
                "downloaded": False,
                "sha256": None,
                "local_file": None,
            }
            if (
                inspectable
                and size <= MAX_OBJECT_BYTES
                and total_downloaded + size <= MAX_TOTAL_BYTES
            ):
                q = urllib.parse.urlencode({"prefix": name})
                dl_url = f"{API}/dataset/{urllib.parse.quote(str(uuid))}/object/download?{q}"
                raw = get_bytes(dl_url)
                local = a.download_dir / f"{uuid}__{safe_name(name)}"
                local.write_bytes(raw)
                rec["downloaded"] = True
                rec["sha256"] = hashlib.sha256(raw).hexdigest()
                rec["local_file"] = str(local)
                rec["download_url"] = dl_url
                rec["downloaded_bytes"] = len(raw)
                total_downloaded += len(raw)
            ds["objects"].append(rec)
        datasets.append(ds)

    result = {
        "schema_version": 1,
        "analysis_id": "aadc-eds-asset-resolver-v1",
        "status": "outcome_blind_asset_and_schema_access",
        "metadata_id": a.metadata_id,
        "metadata_url": meta_url,
        "metadata_rows": rows,
        "datasets": datasets,
        "downloaded_total_bytes": total_downloaded,
        "biological_values_summarized": False,
        "occupancy_state_frequencies_computed": False,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
