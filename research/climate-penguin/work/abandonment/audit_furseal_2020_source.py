#!/usr/bin/env python3
"""Original-public-source audit of 2020 Palmer fur seal locations.

Retrieves Dryad 10.5061/dryad.qv9s4mwp0 from public fixed file ids.
Only field availability, origin and survey support are reported.
Fur seal positions in Jan-Mar 2020 do not reconstruct 2001 or 2007
seal abundance, and are not a penguin nesting map or a vegetation outcome.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import time
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DOI = "10.5061/dryad.qv9s4mwp0"
DOI_PATH = "doi%3A10.5061%2Fdryad.qv9s4mwp0"
BASE = "https://datadryad.org"
FILE_IDS = {
    "drone_survey_dates_times.csv": 3801883,
    "fur_seal_locations_all_surveys.csv": 3801884,
    "fur_seal_locations_d72_d46.csv": 3801885,
}
LABELS = ("litchfield", "torgersen", "humble", "christine", "cormorant")


def read_url(url: str, attempts: int = 2) -> bytes:
    last = None
    for i in range(attempts):
        try:
            req = Request(url, headers={"User-Agent": "mina-source-audit/1.0 (academic reproducibility)",
                                        "Accept": "text/csv, application/json, */*"})
            with urlopen(req, timeout=40) as r:
                data = r.read(2_000_001)
                if len(data) > 2_000_000:
                    raise ValueError("unexpected oversized response")
                return data
        except (HTTPError, URLError, OSError, ValueError) as e:
            last = e
            if i + 1 < attempts:
                time.sleep(2)
    raise RuntimeError(f"{type(last).__name__}: {str(last)[:200]}")


def download_public_csv(name: str, file_id: int, getter=read_url):
    urls = (f"{BASE}/api/v2/files/{file_id}/download",
            f"{BASE}/downloads/file_stream/{file_id}")
    errors = []
    for url in urls:
        try:
            raw = getter(url)
            if raw[:20].lstrip().lower().startswith((b"<!doctype", b"<html", b"{\"error\"")):
                raise ValueError("response not CSV")
            decoded = raw.decode("utf-8-sig")
            parsed = list(csv.DictReader(io.StringIO(decoded)))
            head = decoded.splitlines()[0] if decoded.splitlines() else ""
            if not parsed or len(parsed[0]) < 2 or "," not in head:
                raise ValueError("no valid CSV records")
            return {"name": name, "id": file_id, "source_url": url,
                    "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                    "columns": list(parsed[0]), "rows": parsed}, raw
        except (RuntimeError, ValueError, UnicodeError, csv.Error) as e:
            errors.append({"url": url, "error": str(e)[:220]})
    return {"name": name, "id": file_id, "error": errors}, None


def field_support(rows: list[dict[str, str]]):
    if not rows:
        return {}
    cols = list(rows[0])
    matched = {}
    for label in LABELS:
        matched[label] = sum(any(label in (str(value or "").lower()) for value in r.values())
                             for r in rows)
    numeric = {}
    lower = {x.lower().strip(): x for x in cols}
    for pair in (("x", "y"), ("easting", "northing"), ("utm_x", "utm_y"),
                 ("longitude", "latitude"), ("lon", "lat")):
        if all(x in lower for x in pair):
            coords = []
            for r in rows:
                try:
                    x, y = (float(r[lower[k]]) for k in pair)
                    if abs(x) != float("inf") and abs(y) != float("inf") and x == x and y == y:
                        coords.append((x, y))
                except (TypeError, ValueError):
                    continue
            numeric = {"columns": [lower[k] for k in pair],
                       "n_numeric": len(coords),
                       "bounds": [min(x for x, _ in coords), min(y for _, y in coords),
                                  max(x for x, _ in coords), max(y for _, y in coords)] if coords else None}
            break
    datecols = [x for x in cols if "date" in x.lower() or "time" in x.lower()]
    sitecols = [x for x in cols if any(y in x.lower() for y in ("site", "island", "region", "loc"))]
    categorical = {col: dict(Counter(str(r.get(col, "")).strip() for r in rows).most_common(30))
                   for col in sitecols[:3]}
    return {"total_rows": len(rows), "coordinate_support": numeric,
            "site_label_columns": sitecols, "site_values_top30": categorical,
            "date_columns": datecols, "named_island_record_matches": matched}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("furseal_source_audit"))
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    report = {"schema_version": 1, "dataset_doi": DOI, "year": 2020,
              "basis": "Larsen et al. 2025 Dryad public drone survey",
              "dryad_dataset_url": f"{BASE}/dataset/doi:{DOI}",
              "download_status": {}, "files": {},
              "limits": [
                 "One 2020 austral season: historical 2001/2007 seal pressure not measured",
                 "Repeat drone surveys and multiple seal rows are not independent islands",
                 "No historic penguin nesting polygons; MAPPPD site centroid is not footprint",
                 "No longitudinal plant-cover response; no causal attribution",
              ]}
    for name, file_id in FILE_IDS.items():
        obj, raw = download_public_csv(name, file_id)
        if raw is None:
            report["files"][name] = obj
            report["download_status"][name] = "ERROR"
        else:
            rows = obj.pop("rows")
            report["files"][name] = {**obj, "support": field_support(rows)}
            report["download_status"][name] = "OK"
            (args.out / name).write_bytes(raw)
    report["all_three_source_files_verified"] = all(x == "OK" for x in report["download_status"].values())
    (args.out / "source_audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"all_three_source_files_verified": report["all_three_source_files_verified"],
                      "files": {name: {
                         "status": report["download_status"][name],
                         "rows": report["files"][name].get("support", {}).get("total_rows"),
                         "columns": report["files"][name].get("columns"),
                         "island_matches": report["files"][name].get("support", {}).get("named_island_record_matches"),
                         "coordinate_support": report["files"][name].get("support", {}).get("coordinate_support"),
                         "source_errors": report["files"][name].get("error"),
                       } for name in FILE_IDS}}, ensure_ascii=False))
    return 0 if report["all_three_source_files_verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
