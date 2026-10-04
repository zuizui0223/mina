#!/usr/bin/env python3
"""Outcome-blind support audit for the Zenodo 1984-2024 emperor-penguin dataset."""
from __future__ import annotations

import argparse
import io
import json
import re
import tempfile
from pathlib import Path

import pandas as pd
import requests
import shapefile
from pyproj import CRS
from remotezip import RemoteZip


DATE_HINT = re.compile(r"(?i)(date|time|day|acq)")
COLONY_HINTS = {
    "astrid": "Astrid",
    "mertz": "Mertz",
    "sanae": "SANAE",
}


def _date_like_value(value) -> bool:
    if value is None or pd.isna(value):
        return False
    if isinstance(value, pd.Timestamp) or value.__class__.__name__ in {"datetime", "date"}:
        return True
    text = str(value).strip()
    if not text:
        return False
    patterns = (
        r"^\\d{4}[-/]\\d{1,2}[-/]\\d{1,2}",
        r"^\\d{1,2}[-/]\\d{1,2}[-/]\\d{2,4}",
        r"^\\d{1,2}[- ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[- ]\\d{2,4}",
        r"^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[ -]\\d{1,2}[, -]+\\d{4}",
    )
    return any(re.search(p, text, flags=re.I) for p in patterns)


def parse_date_series(s: pd.Series) -> dict:
    mask = s.map(_date_like_value)
    candidate = s[mask]
    d = pd.to_datetime(candidate, errors="coerce")
    good = d.dropna()
    return {
        "candidate_n": int(mask.sum()),
        "parsed_n": int(good.size),
        "parsed_fraction": float(good.size / int(mask.sum())) if int(mask.sum()) else 0.0,
        "distinct_dates": int(good.dt.date.nunique()) if good.size else 0,
        "min_date": good.min().date().isoformat() if good.size else None,
        "max_date": good.max().date().isoformat() if good.size else None,
        "min_year": int(good.min().year) if good.size else None,
        "max_year": int(good.max().year) if good.size else None,
    }


def audit_catalog(name: str, data: bytes) -> dict:
    xls = pd.ExcelFile(io.BytesIO(data))
    sheets = []
    best_date = None
    year_min = None
    year_max = None
    total_rows = 0
    label_tokens = set()

    for sheet_name in xls.sheet_names:
        raw = pd.read_excel(io.BytesIO(data), sheet_name=sheet_name, header=None)
        total_rows += len(raw)

        candidates = []
        for col_idx in raw.columns:
            info = parse_date_series(raw[col_idx])
            if info["parsed_n"] >= 2:
                candidates.append({"column_index": int(col_idx), **info})
        candidates.sort(
            key=lambda z: (z["distinct_dates"], z["parsed_n"], z["parsed_fraction"]),
            reverse=True,
        )

        for value in raw.iloc[: min(12, len(raw))].to_numpy().ravel():
            if value is None or pd.isna(value):
                continue
            text = str(value).strip()
            if text:
                label_tokens.add(text)

        top = candidates[0] if candidates else None
        if top is not None:
            if best_date is None or (
                top["distinct_dates"], top["parsed_n"], top["parsed_fraction"]
            ) > (
                best_date["distinct_dates"], best_date["parsed_n"], best_date["parsed_fraction"]
            ):
                best_date = {"sheet": sheet_name, **top}
            if top["min_year"] is not None:
                year_min = top["min_year"] if year_min is None else min(year_min, top["min_year"])
                year_max = top["max_year"] if year_max is None else max(year_max, top["max_year"])

        sheets.append({
            "sheet": sheet_name,
            "rows": int(len(raw)),
            "raw_columns": int(raw.shape[1]),
            "date_candidates": candidates,
        })

    low_labels = [x.lower() for x in label_tokens]
    return {
        "colony": name,
        "sheet_names": xls.sheet_names,
        "total_rows": int(total_rows),
        "header_tokens_sample": sorted(label_tokens)[:100],
        "best_date_field": best_date,
        "year_min": year_min,
        "year_max": year_max,
        "year_span": (year_max - year_min) if year_min is not None and year_max is not None else None,
        "has_guano_field": any("guano" in c for c in low_labels),
        "has_surface_field": any(
            any(k in c for k in ("surface", "fast ice", "ice shelf", "iceberg"))
            for c in low_labels
        ),
        "sheets": sheets,
    }


def classify_colony(path: str) -> str | None:
    low = path.lower()
    for token, colony in COLONY_HINTS.items():
        if token in low:
            return colony
    return None


def read_prj_epsg(prj_bytes: bytes | None) -> dict:
    if not prj_bytes:
        return {"prj_present": False, "epsg": None, "crs_name": None, "error": None}
    try:
        text = prj_bytes.decode("utf-8", errors="ignore")
        crs = CRS.from_wkt(text)
        return {"prj_present": True, "epsg": crs.to_epsg(), "crs_name": crs.name, "error": None}
    except Exception as exc:
        return {"prj_present": True, "epsg": None, "crs_name": None, "error": f"{type(exc).__name__}: {exc}"}


def audit_remote_zip(url: str) -> dict:
    rz = RemoteZip(url)
    names = rz.namelist()
    shp_names = sorted([n for n in names if n.lower().endswith(".shp")])
    rows = []
    complete_components = 0

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for shp_name in shp_names:
            base = shp_name[:-4]
            components = {}
            for ext in (".shp",".dbf",".shx",".prj",".cpg"):
                member = base + ext
                if member in names:
                    components[ext] = rz.read(member)
            complete = all(ext in components for ext in (".shp",".dbf",".shx"))
            if complete:
                complete_components += 1
            feature_count = None
            shape_type = None
            fields = []
            if complete:
                local_base = root / f"f_{len(rows)}"
                for ext, blob in components.items():
                    (local_base.with_suffix(ext)).write_bytes(blob)
                reader = shapefile.Reader(str(local_base.with_suffix(".shp")))
                feature_count = int(len(reader))
                shape_type = str(reader.shapeTypeName)
                fields = [
                    {"name": str(f[0]), "type": str(f[1]), "size": int(f[2]), "decimals": int(f[3])}
                    for f in reader.fields[1:]
                ]
            crs = read_prj_epsg(components.get(".prj"))
            rows.append({
                "archive_path": shp_name,
                "colony": classify_colony(shp_name),
                "component_complete": bool(complete),
                "feature_count": feature_count,
                "shape_type": shape_type,
                "fields": fields,
                "crs": crs,
            })
    rz.close()
    return {
        "archive_members": int(len(names)),
        "shapefiles": int(len(shp_names)),
        "complete_shapefiles": int(complete_components),
        "colonies_in_paths": sorted({r["colony"] for r in rows if r["colony"]}),
        "schema_rows": rows,
    }


def download(session: requests.Session, url: str) -> bytes:
    r = session.get(url, timeout=120)
    r.raise_for_status()
    return r.content


def audit(contract: dict) -> dict:
    session = requests.Session()
    session.headers.update({"User-Agent":"mina-paper3-zenodo-support/1.0"})
    catalogs = {}
    errors = []
    for colony, url in contract["source"]["catalog_files"].items():
        try:
            catalogs[colony] = audit_catalog(colony, download(session, url))
        except Exception as exc:
            errors.append(f"{colony}: {type(exc).__name__}: {exc}")

    try:
        routes = audit_remote_zip(contract["source"]["route_zip"])
        route_error = None
    except Exception as exc:
        routes = {"archive_members":0,"shapefiles":0,"complete_shapefiles":0,"colonies_in_paths":[],"schema_rows":[]}
        route_error = f"{type(exc).__name__}: {exc}"

    gate = contract["continuation_gate"]
    catalog_colonies = sum(1 for x in catalogs.values() if x.get("best_date_field") is not None)
    catalog_long = sum(1 for x in catalogs.values() if (x.get("year_span") or 0) >= int(gate["minimum_catalog_year_span"]))
    route_colonies = len(routes["colonies_in_paths"])
    route_machine = any(
        str(r.get("shape_type","")).upper().startswith(("POINT","POLYLINE","LINE"))
        for r in routes["schema_rows"]
        if r.get("component_complete")
    )
    passed = bool(
        catalog_colonies >= int(gate["minimum_catalog_colonies"])
        and catalog_long >= int(gate["minimum_catalog_colonies"])
        and routes["complete_shapefiles"] >= int(gate["minimum_route_shapefiles"])
        and route_colonies >= int(gate["minimum_route_colonies"])
        and (route_machine if gate["machine_readable_route_geometry_required"] else True)
    )

    return {
        "schema_version":1,
        "result_id":"mina-paper3-zenodo-longterm-support-v1",
        "contract_id":contract["contract_id"],
        "catalogs":catalogs,
        "catalog_errors":errors,
        "route_archive":{k:v for k,v in routes.items() if k!="schema_rows"},
        "route_error":route_error,
        "route_schema_rows":routes["schema_rows"],
        "decision":{
            "support_gate_passed":passed,
            "semantic_route_start_validation_authorized":passed,
            "movement_outcomes_opened":False
        },
        "boundary":[
            "No coordinate distances or movement outcomes are calculated.",
            "Route shapefiles are not yet assumed to encode colony positions.",
            "No abundance, breeding success or environmental covariates are read."
        ]
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    c=json.loads(a.contract.read_text(encoding="utf-8"))
    r=audit(c)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in r.items() if k!="route_schema_rows"},indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
