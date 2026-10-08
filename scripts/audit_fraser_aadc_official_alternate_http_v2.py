"""AADC official EDS alternative metadata/byte-range pilot after v1 refused.

This reads a bounded publicly listed file manifest and at most 32 bytes
from each of 2011 & 2014 NetCDF objects on success. It never reads image
or physical ice raster cells, never downloads entire annual ~500MB files,
and never accesses sensitive credentials or biological response rows.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

DATASET_UUID = "f88a75e3-257f-4904-99ef-764e5cf9a064"
API = f"https://data.aad.gov.au/eds/api/dataset/{DATASET_UUID}"
LIST_URL = API + "/objects?recursive=true"
FILE_URL = API + "/object/download?prefix=fastice_v2_2/FastIce_70_{year}.nc"
YEARS = (2011, 2014)
READ_LIMIT = 32
MAX_METADATA = 150_000
TIMEOUT = 12


def check_magic(b: bytes) -> bool:
    return b.startswith(b"\x89HDF\r\n\x1a\n") or b[:4] in {
        b"CDF\x01", b"CDF\x02", b"CDF\x05",
    }


def manifest(*, opener=urllib.request.urlopen):
    req = urllib.request.Request(
        LIST_URL, headers={"Accept": "application/json",
                           "User-Agent": "mina-aadc-source-audit/1.0"}
    )
    try:
        with opener(req, timeout=TIMEOUT) as res:
            status = res.status
            content_type = res.headers.get("Content-Type", "")
            payload = res.read(MAX_METADATA + 1) if status == 200 else b""
        if status != 200:
            return {"status": "HOLD_HTTP_STATUS", "http_status": status}
        if len(payload) > MAX_METADATA:
            return {"status": "HOLD_UNEXPECTED_MANIFEST_SIZE"}
        decoded = json.loads(payload)
        if isinstance(decoded, dict):
            objs = decoded.get("objects", decoded.get("data", decoded.get("items", [])))
        else:
            objs = decoded
        if not isinstance(objs, list):
            return {"status": "HOLD_UNKNOWN_MANIFEST_SHAPE",
                    "root_type": type(decoded).__name__}
        paths = [str(x.get("name", x.get("key", ""))) for x in objs
                 if isinstance(x, dict)]
        year_matches = {
            str(year): [
                name for name in paths if name.endswith(f"FastIce_70_{year}.nc")
            ]
            for year in YEARS
        }
        return {
            "status": "PUBLIC_MANIFEST_READ",
            "format": content_type[:80],
            "objects_count": len(objs),
            "matched_frozen_years": year_matches,
            "exact_frozen_prefix_verified": all(
                year_matches[str(year)] == [
                    f"fastice_v2_2/FastIce_70_{year}.nc"
                ] for year in YEARS
            )
        }
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            OSError, ValueError, json.JSONDecodeError) as e:
        return {"status": "HOLD_METADATA_ROUTE_UNAVAILABLE",
                "error_type": type(e).__name__,
                "error_message": str(e)[:140]}


def range_check(year: int, *, opener=urllib.request.urlopen) -> dict:
    if year not in YEARS:
        raise ValueError("Year not in frozen source comparison")
    url = FILE_URL.format(year=year)
    report = {"year": year, "url": url, "head": "NOT_ATTEMPTED",
              "range_status": "NOT_ATTEMPTED", "physical_ice_values_read": 0,
              "bytes_read": 0}
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent":"mina-aadc-source-audit/1.0"})
        with opener(req, timeout=TIMEOUT) as res:
            code = res.status
            length = res.headers.get("Content-Length", "")
            media = res.headers.get("Content-Type", "")
        report["head_status_code"] = code
        report["head_content_length"] = int(length) if length.isdigit() else None
        report["head_media"] = media[:80]
        if code != 200 or not length.isdigit() or int(length) < 32:
            report["head"] = "HOLD_HEAD_INSUFFICIENT"
            return report
        report["head"] = "OK"
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            OSError, ValueError) as e:
        report["head"] = "HOLD_HEAD_UNAVAILABLE"
        report["head_error"] = str(e)[:140]
        return report
    try:
        req = urllib.request.Request(url, headers={
            "Range": f"bytes=0-{READ_LIMIT-1}",
            "Accept-Encoding": "identity",
            "User-Agent": "mina-aadc-source-audit/1.0",
        })
        with opener(req, timeout=TIMEOUT) as res:
            code = res.status
            cr = res.headers.get("Content-Range", "")
            report["range_http_status"] = code
            if code != 206 or not re.fullmatch(r"bytes 0-31/\d+", cr):
                report["range_status"] = "HOLD_NO_VALID_PARTIAL_RESPONSE"
                return report  # NEVER read full-body HTTP 200
            payload = res.read(READ_LIMIT + 1)
        report["bytes_read"] = len(payload)
        report["range_status"] = (
            "NETCDF_HEADER_CONFIRMED"
            if len(payload) == 32 and check_magic(payload)
            else "HOLD_BAD_NETCDF_MAGIC_OR_RANGE_LENGTH"
        )
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            OSError, ValueError) as e:
        report["range_status"] = "HOLD_RANGE_ACCESS_FAILED"
        report["range_error"] = str(e)[:140]
    return report


def run(*, opener=urllib.request.urlopen, offline=False) -> dict:
    if offline:
        index = {"status": "OFFLINE"}
        years = [{"year": y, "range_status": "OFFLINE", "bytes_read": 0,
                  "physical_ice_values_read": 0} for y in YEARS]
    else:
        index = manifest(opener=opener)
        years = [range_check(y, opener=opener) for y in YEARS]
    return {
        "source_kind": "OFFICIAL_AADC_EDS_V2_2_METADATA_ONLY",
        "source_doi": "10.26179/5d267d1ceb60c",
        "dataset_uuid": DATASET_UUID,
        "manifest_check": index,
        "frozen_years": list(YEARS),
        "files": years,
        "verified_frozen_year_remote_NC": sum(
            x["range_status"] == "NETCDF_HEADER_CONFIRMED" for x in years
        ),
        "source_readiness": (
            "READY_FOR_SEPARATE_FROZEN_PIXEL_EXTRACTION_DESIGN"
            if all(x["range_status"] == "NETCDF_HEADER_CONFIRMED" for x in years)
            else "HOLD_OFFICIAL_ALTERNATE_SOURCE_NOT_READABLE"
        ),
        "total_payload_bytes_read": sum(x["bytes_read"] for x in years),
        "physical_ice_class_values_read": 0,
        "penguin_response_values_read": 0,
        "fit_or_causal_inference_run": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--offline", action="store_true")
    a = p.parse_args()
    payload = json.dumps(run(offline=a.offline), indent=2) + "\n"
    a.out.write_text(payload, encoding="utf8")
    print(payload, end="")


if __name__ == "__main__":
    main()
