#!/usr/bin/env python3
"""Schema-only audit for USAP-DC Ross Island Adelie resight data.

This script deliberately avoids reading behavioral outcome rows. It fetches the
public README without authentication and, only when an API key is supplied,
opens the CSV stream long enough to read the UTF-8 header line before closing.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DATASET_UID = "601444"
RESIGHT_FILE = "band_resighting_1997-2021.csv"
BANDING_UID = "601443"
BANDING_FILE = "band_inv_1994-2021.csv"
BASE = "https://www.usap-dc.org"


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "mina-island-reassembly/ross-schema-gate-v1"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read().decode("utf-8-sig", "replace")


def fetch_header(dataset_uid: str, file_name: str, token: str) -> str:
    url = (
        f"{BASE}/api/v2.0/datafiles/{dataset_uid}/"
        + urllib.parse.quote(file_name, safe="")
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "mina-island-reassembly/ross-schema-gate-v1",
            "X-Auth-Token": token,
            "Range": "bytes=0-65535",
        },
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        # Read only through the first newline. Do not materialize any data row.
        buf = bytearray()
        while True:
            chunk = response.read(1)
            if not chunk:
                break
            if chunk == b"\n":
                break
            buf.extend(chunk)
            if len(buf) > 65535:
                raise RuntimeError("CSV header exceeded 65535 bytes")
    return bytes(buf).decode("utf-8-sig", "strict").rstrip("\r")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    readme_url = f"{BASE}/readme/{DATASET_UID}"
    readme = fetch_text(readme_url)
    if not readme.strip():
        raise RuntimeError("empty USAP-DC README")

    token = os.environ.get("USAP_DC_API_KEY", "").strip()
    result: dict[str, object] = {
        "schema_version": 1,
        "audit_id": "mina-ross-island-resight-schema-audit-v1",
        "dataset_uid": DATASET_UID,
        "resight_file": RESIGHT_FILE,
        "readme_url": readme_url,
        "readme_retrieved": True,
        "readme_text": readme,
        "api_key_present": bool(token),
        "resight_header": None,
        "banding_header": None,
        "behavioral_rows_read": 0,
        "status": "README_ONLY",
    }

    if token:
        try:
            result["resight_header"] = fetch_header(
                DATASET_UID, RESIGHT_FILE, token
            )
            result["banding_header"] = fetch_header(
                BANDING_UID, BANDING_FILE, token
            )
            result["status"] = "README_AND_HEADERS"
        except urllib.error.HTTPError as exc:
            result["status"] = f"HEADER_FETCH_HTTP_{exc.code}"
            result["header_error"] = str(exc)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("status=", result["status"])
    print("readme_retrieved=", result["readme_retrieved"])
    print("banding_readme_retrieved=", result["banding_readme_retrieved"])
    print("api_key_present=", result["api_key_present"])
    print("behavioral_rows_read=0")
    if result["resight_header"]:
        print("resight_header=", result["resight_header"])
    if result["banding_header"]:
        print("banding_header=", result["banding_header"])
    # Intentionally do not print the README: it is uploaded as an audit artifact.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
