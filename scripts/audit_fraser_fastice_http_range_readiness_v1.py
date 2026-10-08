"""Read-only, bounded external-fast-ice archive readiness gate.

Frozen six years at Fraser/Massom v2.2 AADC direct annual NetCDF endpoints.
HEAD + exactly one bytes=0-31 HTTP Range per year (only after HEAD passes).
Do not download full ~500MB NetCDFs; no physical ice classes or bird outcomes.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

YEARS = (2009, 2010, 2011, 2012, 2013, 2014)
ARCHIVE_URL = (
    "https://public.services.aad.gov.au/datasets/science/"
    "AAS_4116_Fraser_fastice_circumantarctic/fastice_v2_2/"
    "FastIce_70_{year}.nc"
)
FROZEN_CONTRACT = (
    "contracts/EMPEROR_LEDDA_FRASER_FASTICE_INDEPENDENT_SOURCE_V1.json"
)
READ_BYTES = 32
MAX_ACCEPTABLE_FILE_BYTES = 2_000_000_000
TIMEOUT_SECONDS = 12

def classify_magic(start: bytes) -> str:
    if start.startswith(b"\x89HDF\r\n\x1a\n"):
        return "HDF5_NETCDF4"
    if start[:4] in (b"CDF\x01", b"CDF\x02", b"CDF\x05"):
        return "NETCDF_CLASSIC_OR_64_BIT"
    return "UNKNOWN_OR_NON_NC"


def _header(headers, key: str) -> str:
    return (headers.get(key, "") or "").strip()


def check_year(year: int, *, opener=urllib.request.urlopen) -> dict:
    if year not in YEARS:
        raise ValueError(f"year {year} is not in the frozen contract")
    url = ARCHIVE_URL.format(year=year)
    item = {
        "year": year, "original_url": url,
        "head_status": "NOT_ATTEMPTED", "byte_range_status": "NOT_ATTEMPTED",
        "read_payload_bytes": 0, "physical_fastice_values_read": 0,
    }

    try:
        req = urllib.request.Request(url, method="HEAD", headers={
            "User-Agent": "mina-antarctic-source-range-gate/1.0",
            "Accept-Encoding": "identity",
        })
        with opener(req, timeout=TIMEOUT_SECONDS) as response:
            code = response.status
            length_raw = _header(response.headers, "Content-Length")
            range_attr = _header(response.headers, "Accept-Ranges")
            etag = _header(response.headers, "ETag")
            modified = _header(response.headers, "Last-Modified")
        item.update({
            "http_head_status_code": code,
            "content_length_reported_bytes": int(length_raw) if length_raw.isdigit() else None,
            "accept_ranges_declared": range_attr,
            "etag_hint": etag[:100],
            "last_modified_hint": modified[:100],
            "head_status": "SUCCESS" if code == 200 else "UNEXPECTED_HTTP_STATUS",
        })
        if code != 200:
            return item
        if not length_raw.isdigit():
            item["head_status"] = "HOLD_UNKNOWN_FILE_SIZE"
            return item
        if not 0 < int(length_raw) <= MAX_ACCEPTABLE_FILE_BYTES:
            item["head_status"] = "HOLD_UNSAFE_FILE_SIZE"
            return item
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            OSError, ValueError) as exc:
        item["head_status"] = "HOLD_HEAD_UNAVAILABLE"
        item["head_error_type"] = type(exc).__name__
        item["head_error"] = str(exc)[:120]
        return item

    try:
        request = urllib.request.Request(
            url, headers={
                "User-Agent": "mina-antarctic-source-range-gate/1.0",
                "Range": f"bytes=0-{READ_BYTES-1}",
                "Accept-Encoding": "identity",
                "Cache-Control": "no-transform",
            },
        )
        # VERY IMPORTANT: examine HTTP status before calling read().
        # A server ignoring Range may return a multi-hundred MB 200 body;
        # we close such a response without reading a single body byte.
        with opener(request, timeout=TIMEOUT_SECONDS) as response:
            code = response.status
            content_range = _header(response.headers, "Content-Range")
            content_type = _header(response.headers, "Content-Type")
            item["range_response_code"] = code
            item["range_content_range"] = content_range[:120]
            item["range_content_type"] = content_type[:120]
            if code != 206:
                item["byte_range_status"] = (
                    "HOLD_FULL_BODY_NOT_READ" if code == 200
                    else "HOLD_RANGE_NOT_SUPPORTED"
                )
                return item
            if not re.match(r"^bytes 0-31/\d+$", content_range):
                item["byte_range_status"] = "HOLD_UNEXPECTED_CONTENT_RANGE"
                return item
            payload = response.read(READ_BYTES + 1)
        item["read_payload_bytes"] = len(payload)
        if len(payload) != READ_BYTES:
            item["byte_range_status"] = "HOLD_SHORT_OR_OVERLONG_RANGE"
            return item
        item["first32_format_signature"] = classify_magic(payload)
        item["byte_range_status"] = (
            "NETCDF_SIGNATURE_VERIFIED"
            if item["first32_format_signature"] != "UNKNOWN_OR_NON_NC"
            else "HOLD_INVALID_FILE_SIGNATURE"
        )
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            OSError, ValueError) as exc:
        item["byte_range_status"] = "HOLD_RANGE_FAILED"
        item["range_error_type"] = type(exc).__name__
        item["range_error"] = str(exc)[:120]
    return item


def run(*, offline=False, opener=urllib.request.urlopen) -> dict:
    checks = [
        ({"year": year, "head_status": "SKIPPED_OFFLINE",
          "byte_range_status": "SKIPPED_OFFLINE", "read_payload_bytes": 0,
          "physical_fastice_values_read": 0}
         if offline else check_year(year, opener=opener))
        for year in YEARS
    ]
    all_ok = all(
        c["byte_range_status"] == "NETCDF_SIGNATURE_VERIFIED"
        for c in checks
    )
    return {
        "audit_id": "pr195-fraser-fastice-2009to2014-yearly-range-readiness-v1",
        "stage": "EXTERNAL_SOURCE_READINESS_ONLY",
        "source": "https://doi.org/10.26179/5d267d1ceb60c",
        "contract": FROZEN_CONTRACT,
        "site": "LEDD",
        "target_site_coords_not_used_for_network_range_test": True,
        "all_six_files_remote_random_read_capable": all_ok,
        "checked_years": list(YEARS),
        "checks": checks,
        "total_downloaded_body_bytes": sum(c["read_payload_bytes"] for c in checks),
        "physical_class_values_read": 0,
        "biological_response_rows_read": 0,
        "effect_fitted": False,
        "decision": (
            "READY_FOR_SEPARATE_FROZEN_INDEPENDENT_POINT_EXTRACTION_DESIGN"
            if all_ok else "HOLD_RANGE_ACCESS_OR_SOURCE_IDENTITY"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    result = run(offline=args.offline)
    data = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    args.out.write_text(data, encoding="utf-8")
    print(data, end="")


if __name__ == "__main__":
    main()
