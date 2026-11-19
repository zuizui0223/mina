#!/usr/bin/env python3
"""Retrieve BAS official SCAR ADD 7.13 high-resolution polygon SHP archive.

This is SOURCE QA ONLY. No raster, rock, penguin, or ecological calculations.
BAS archive is a publisher dataset, not the gigantic ArcGIS GeoJSON endpoint.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile
import requests

DOI = "10.5285/1c81cf24-576f-43df-be72-a5c7dbb51ffb"
ARCHIVE_URL = (
    "https://ramadda.data.bas.ac.uk/repository/entry/get/"
    "add_coastline_high_res_polygon_v7_13.shp.zip?"
    "entryid=synth%3A1c81cf24-576f-43df-be72-a5c7dbb51ffb"
    "%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N18xMy5zaHAuemlw"
)
MAX_ZIP_BYTES = 110_000_000
MAX_UNPACKED = 350_000_000

def download_archive() -> tuple[bytes, dict]:
    total = 0
    h = hashlib.sha256()
    out = io.BytesIO()
    with requests.get(
        ARCHIVE_URL, headers={"User-Agent": "mina-source-provenance-gate/1.0"},
        timeout=(20, 120), stream=True, allow_redirects=True
    ) as resp:
        resp.raise_for_status()
        parsed = urlparse(resp.url)
        if parsed.scheme != "https" or parsed.hostname not in {
            "ramadda.data.bas.ac.uk", "194.66.5.50"
        }:
            raise RuntimeError("Unverified BAS archive redirect")
        ct = resp.headers.get("Content-Type", "")
        for b in resp.iter_content(chunk_size=262144):
            if not b:
                continue
            total += len(b)
            if total > MAX_ZIP_BYTES:
                raise RuntimeError("BAS archive exceeded fixed 110MB maximum")
            h.update(b)
            out.write(b)
    blob = out.getvalue()
    if blob[:2] != b"PK":
        raise RuntimeError("BAS response is not ZIP")
    with ZipFile(io.BytesIO(blob)) as z:
        names = z.namelist()
        if len(names) > 80 or z.testzip() is not None:
            raise RuntimeError("unexpected archive entries or CRC error")
        if sum(i.file_size for i in z.infolist()) > MAX_UNPACKED:
            raise RuntimeError("BAS archive decompressed contents exceed cap")
        for name in names:
            p = Path(name)
            if p.is_absolute() or ".." in p.parts or len(p.parts) > 5:
                raise RuntimeError("unsafe archive pathname")
        shp = [n for n in names if n.lower().endswith(".shp")]
        prj = [n for n in names if n.lower().endswith(".prj")]
        dbf = [n for n in names if n.lower().endswith(".dbf")]
        shx = [n for n in names if n.lower().endswith(".shx")]
        if len(shp) != 1 or not (len(prj) == len(dbf) == len(shx) == 1):
            raise RuntimeError("archive does not have exactly one SHP/DBF/SHX/PRJ layer")
        project = z.read(prj[0]).decode("utf-8", errors="replace")
        if "3031" not in project and "Polar_Stereographic" not in project:
            raise RuntimeError("unrecognized source CRS; no source geometry fit")
        meta = {
            "zip_sha256": h.hexdigest(), "zip_bytes": total,
            "file_names": names, "shp_uncompressed_bytes": z.getinfo(shp[0]).file_size,
            "source_wkt_excerpt": project[:240],
            "archive_format_valid": True,
            "publisher_url_host": parsed.hostname,
            "content_type": ct,
        }
    return blob, meta

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-zip", required=False, type=Path)
    a = ap.parse_args()
    receipt = {"source": ARCHIVE_URL, "doi": DOI, "version": "7.13",
               "source_only": True, "biology_opened": False,
               "time_utc": datetime.now(timezone.utc).isoformat()}
    try:
        raw, audit = download_archive()
        receipt.update(audit)
        receipt["status"] = "ORIGINAL_PUBLISHER_ZIP_VERIFIED"
        if a.out_zip:
            a.out_zip.parent.mkdir(parents=True, exist_ok=True)
            a.out_zip.write_bytes(raw)
    except Exception as exc:
        receipt["status"] = "HOLD_OFFICIAL_ZIP_SOURCE"
        receipt["reason"] = f"{type(exc).__name__}: {str(exc)}"[:320]
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: receipt.get(k) for k in ("status","reason","zip_sha256","zip_bytes")}, sort_keys=True))

if __name__ == "__main__":
    main()
