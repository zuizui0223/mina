"""Source header audit only for original 2011 ground-observed chinstrap nest counts.

Never read, display, count or decode original biological data rows.
Underlying density denominator used digitized area, so ground density itself
is NOT independent spatial map validation.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from urllib.parse import quote, urlparse

import requests

ROOT = "96febb5d-1821-4f49-9b5f-32e489ae3839"
SOURCE_NAME = "zavodovski_chinstrap_density_2011.csv"
SOURCE_ID = "synth:" + ROOT + ":L3phdm9kb3Zza2lfY2hpbnN0cmFwX2RlbnNpdHlfMjAxMS5jc3Y="
HOST = "ramadda.data.bas.ac.uk"


def source_url():
    return ("https://" + HOST + "/repository/entry/get/" + SOURCE_NAME +
            "?entryid=" + quote(SOURCE_ID, safe="") + "&fileinline=true")


def schema_gate(names):
    norm = [re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_") for name in names]
    # Real-world CSV exports may have repeated or blank column headings.
    # Preserve the header as evidence, but do not pretend it is joinable.
    if len(norm) < 2 or any(not name for name in norm) or len(norm) != len(set(norm)):
        return {
            "status": "HOLD_AMBIGUOUS_FIRST_CSV_HEADER",
            "original_columns": names,
            "normalized_columns": norm,
            "original_biological_rows_parsed": 0,
            "original_count_values_parsed": 0,
            "spatial_join_eligible": False,
            "explanation": "Blank, duplicate or non-tabular initial header; no positional join allowed.",
        }
    latitude = {"latitude", "lat", "gps_latitude", "gps_lat", "decimal_latitude"}
    longitude = {"longitude", "long", "lon", "gps_longitude", "gps_lon", "decimal_longitude"}
    east = {"easting", "utm_easting", "utm_e", "x", "x_utm", "coordinate_x"}
    north = {"northing", "utm_northing", "utm_n", "y", "y_utm", "coordinate_y"}
    coord_pairs = {
        "latitude_longitude": bool(set(norm)&latitude and set(norm)&longitude),
        "projected_xy": bool(set(norm)&east and set(norm)&north),
    }
    site_cols = [v for v in norm if re.search(r"(?:^|_)(?:subcolony|site|colony|patch|plot|location)(?:_|$)", v) or v.endswith("_id")]
    has_location = any(coord_pairs.values())
    return {
        "original_columns": names,
        "normalized_columns": norm,
        "candidate_georeference_columns": {k:bool(v) for k,v in coord_pairs.items()},
        "candidate_site_ID_columns_no_verified_polygon_crosswalk": site_cols,
        "status": ("POTENTIAL_COORDINATE_HEADER_REQUIRES_ACTUAL_SOURCE_FIELD_PROVENANCE"
                   if has_location else "HOLD_NO_COORDINATE_COLUMNS_IN_THIS_CSV"),
        "original_biological_rows_parsed": 0,
        "original_count_values_parsed": 0,
    }


def first_line_only():
    with requests.get(source_url(), timeout=(20,40), stream=True,
                      headers={"User-Agent": "mina-source-header-only/1.0"}) as response:
        response.raise_for_status()
        final = urlparse(response.url)
        if final.scheme != "https" or final.hostname not in {HOST,"194.66.5.50"}:
            raise ValueError("SOURCE_STOP nonofficial redirect")
        first = response.raw.readline(2049)
        if len(first)>2048 or b"\n" not in first:
            raise ValueError("SOURCE_STOP CSV header too long or no line boundary")
        if first.lstrip().lower().startswith(b"<html"):
            raise ValueError("SOURCE_STOP source is HTML")
        header = first.decode("utf-8-sig").strip("\r\n")
        cols = next(csv.reader(io.StringIO(header)))
        result = schema_gate(cols)
        result["publisher_source_uri"] = source_url()
        result["source_doi"] = "10.5285/96febb5d-1821-4f49-9b5f-32e489ae3839"
        result["response_content_length_declared_bytes"] = response.headers.get("content-length")
        result["original_header_sha256"] = hashlib.sha256(first).hexdigest()
        result["original_header_bytes_read"] = len(first)
        return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    a=p.parse_args()
    try:
        result=first_line_only()
    except Exception as exc:
        result={"status":"HOLD_SOURCE_OR_SCHEMA_FAILED",
                "error":f"{type(exc).__name__}: {str(exc)[:220]}",
                "original_biological_rows_parsed":0}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result))
    if result["status"]=="HOLD_SOURCE_OR_SCHEMA_FAILED":
        raise SystemExit(2)


if __name__=="__main__":
    main()
