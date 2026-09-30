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
CHICKCOUNT_UID = "600007"
BASE = "https://www.usap-dc.org"
SWAGGER_URL = f"{BASE}/api/v2.0/swagger.json"


class NonCsvHeaderResponse(RuntimeError):
    pass


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "mina-island-reassembly/ross-schema-gate-v1"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read().decode("utf-8-sig", "replace")


def fetch_header(
    dataset_uid: str,
    file_name: str,
    token: str | None = None,
) -> str:
    url = (
        f"{BASE}/api/v2.0/datafiles/{dataset_uid}/"
        + urllib.parse.quote(file_name, safe="")
    )
    headers = {
        "User-Agent": "mina-island-reassembly/ross-schema-gate-v1",
        "Range": "bytes=0-65535",
    }
    if token:
        headers["X-Auth-Token"] = token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=90) as response:
        content_type = response.headers.get("Content-Type", "")
        final_url = response.geturl()
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
    header = bytes(buf).decode("utf-8-sig", "strict").rstrip("\r")
    if (
        "text/html" in content_type.lower()
        or header.lstrip().lower().startswith("<!doctype html")
        or header.lstrip().lower().startswith("<html")
    ):
        raise NonCsvHeaderResponse(
            f"non-CSV response content_type={content_type!r} "
            f"final_url={final_url!r}"
        )
    return header


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    readme_url = f"{BASE}/readme/{DATASET_UID}"
    readme = fetch_text(readme_url)
    if not readme.strip():
        raise RuntimeError("empty USAP-DC resight README")
    banding_readme_url = f"{BASE}/readme/{BANDING_UID}"
    banding_readme = fetch_text(banding_readme_url)
    if not banding_readme.strip():
        raise RuntimeError("empty USAP-DC banding README")
    chickcount_readme_url = f"{BASE}/readme/{CHICKCOUNT_UID}"
    chickcount_readme = fetch_text(chickcount_readme_url)
    if not chickcount_readme.strip():
        raise RuntimeError("empty USAP-DC chick-count README")

    swagger = json.loads(fetch_text(SWAGGER_URL))
    datafile_doc = (
        swagger.get("paths", {})
        .get("/datafiles/{dataset_uid}/{file_name}", {})
        .get("get", {})
    )
    datafile_description = str(datafile_doc.get("description", ""))
    datafile_responses = datafile_doc.get("responses", {})
    documented_api_key_required = bool(
        "X-Auth-Token" in datafile_description
        and "API key" in datafile_description
        and "401" in datafile_responses
    )

    token = os.environ.get("USAP_DC_API_KEY", "").strip()
    result: dict[str, object] = {
        "schema_version": 1,
        "audit_id": "mina-ross-island-resight-schema-audit-v1",
        "dataset_uid": DATASET_UID,
        "resight_file": RESIGHT_FILE,
        "readme_url": readme_url,
        "readme_retrieved": True,
        "readme_text": readme,
        "banding_readme_url": banding_readme_url,
        "banding_readme_retrieved": True,
        "banding_readme_text": banding_readme,
        "chickcount_readme_url": chickcount_readme_url,
        "chickcount_readme_retrieved": True,
        "chickcount_readme_text": chickcount_readme,
        "api_key_present": bool(token),
        "swagger_url": SWAGGER_URL,
        "swagger_datafile_endpoint_found": bool(datafile_doc),
        "swagger_documents_api_key_required": documented_api_key_required,
        "swagger_datafile_description": datafile_description,
        "anonymous_header_attempted": False,
        "anonymous_header_http_status": None,
        "authenticated_header_attempted": False,
        "resight_header": None,
        "banding_header": None,
        "behavioral_rows_read": 0,
        "status": "README_ONLY",
    }

    # First use the documented public API endpoint without credentials. This
    # is not an authentication bypass: it simply tests whether public datasets
    # expose schema/header access anonymously. Read stops at the first newline.
    try:
        result["anonymous_header_attempted"] = True
        result["resight_header"] = fetch_header(
            DATASET_UID, RESIGHT_FILE, None
        )
        result["banding_header"] = fetch_header(
            BANDING_UID, BANDING_FILE, None
        )
        result["anonymous_header_http_status"] = 200
        result["status"] = "README_AND_HEADERS_ANONYMOUS"
    except urllib.error.HTTPError as exc:
        result["anonymous_header_http_status"] = exc.code
        result["anonymous_header_error"] = str(exc)
    except NonCsvHeaderResponse as exc:
        result["anonymous_header_http_status"] = 200
        result["anonymous_header_non_csv"] = True
        result["anonymous_header_error"] = str(exc)

    # Only if anonymous schema access fails and an explicit repository secret
    # is present, retry the same header-only request with the API token.
    if (
        result["resight_header"] is None
        and result["banding_header"] is None
        and token
    ):
        try:
            result["authenticated_header_attempted"] = True
            result["resight_header"] = fetch_header(
                DATASET_UID, RESIGHT_FILE, token
            )
            result["banding_header"] = fetch_header(
                BANDING_UID, BANDING_FILE, token
            )
            result["status"] = "README_AND_HEADERS_AUTHENTICATED"
        except urllib.error.HTTPError as exc:
            result["status"] = f"HEADER_FETCH_HTTP_{exc.code}"
            result["header_error"] = str(exc)
        except NonCsvHeaderResponse as exc:
            result["status"] = "HEADER_FETCH_NON_CSV"
            result["header_error"] = str(exc)

    if result["resight_header"] is None and not token:
        result["status"] = (
            "README_ONLY_API_KEY_REQUIRED"
            if documented_api_key_required
            else "README_ONLY_HEADER_UNAVAILABLE"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("status=", result["status"])
    print("readme_retrieved=", result["readme_retrieved"])
    print("banding_readme_retrieved=", result["banding_readme_retrieved"])
    print("chickcount_readme_retrieved=", result["chickcount_readme_retrieved"])
    print("api_key_present=", result["api_key_present"])
    print(
        "swagger_documents_api_key_required=",
        result["swagger_documents_api_key_required"],
    )
    print("anonymous_header_attempted=", result["anonymous_header_attempted"])
    print(
        "anonymous_header_http_status=",
        result["anonymous_header_http_status"],
    )
    print(
        "authenticated_header_attempted=",
        result["authenticated_header_attempted"],
    )
    print("behavioral_rows_read=0")
    if result["resight_header"]:
        print("resight_header=", result["resight_header"])
    if result["banding_header"]:
        print("banding_header=", result["banding_header"])
    # Intentionally do not print the README: it is uploaded as an audit artifact.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
