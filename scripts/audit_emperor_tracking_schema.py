#!/usr/bin/env python3
"""Schema-only audit of the public emperor-penguin colony tracking archive.

This script intentionally does not calculate movement distances or expose
coordinate-derived outcomes. It inspects only archive/file structure,
shapefile schema, geometry family, CRS, feature counts and date parseability.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import tempfile
import time
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests
import shapefile
from pyproj import CRS


FILE_RE = re.compile(r"(?i)(Atka|Coulman|Washington)[ _-]?(20(?:17|18|19|20|21|22|23|24))")


def download_archive(urls: list[str], timeout: int = 120) -> tuple[bytes, str]:
    session = requests.Session()
    session.headers.update({"User-Agent": "mina-paper3-schema-audit/1.0"})
    errors = []
    for url in urls:
        for attempt in range(4):
            try:
                r = session.get(url, timeout=timeout, allow_redirects=True)
                r.raise_for_status()
                data = r.content
                if not zipfile.is_zipfile(io.BytesIO(data)):
                    raise ValueError(
                        f"download is not ZIP: content-type={r.headers.get('content-type')} bytes={len(data)}"
                    )
                return data, r.url
            except Exception as exc:
                errors.append(f"{url} attempt {attempt+1}: {type(exc).__name__}: {exc}")
                time.sleep(2 ** attempt)
    raise RuntimeError("All archive download routes failed: " + " | ".join(errors[-8:]))


def parse_colony_year(path: str) -> tuple[str, int] | None:
    m = FILE_RE.search(Path(path).stem)
    if not m:
        return None
    colony = m.group(1).capitalize()
    if colony == "Washington":
        colony = "Washington"
    return colony, int(m.group(2))


def _candidate_date_fields(reader: shapefile.Reader) -> list[str]:
    out = []
    for f in reader.fields[1:]:
        name, ftype = str(f[0]), str(f[1])
        low = name.lower()
        semantic = any(k in low for k in ("date", "time", "acq", "day"))
        if ftype.upper() == "D" or semantic:
            out.append(name)
    return out


def _parse_one_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text or text.lower() in {"none", "nan", "na"}:
        return None
    dt = pd.to_datetime(text, errors="coerce", utc=False)
    if pd.isna(dt):
        return None
    if hasattr(dt, "date"):
        return dt.date()
    return None


def choose_date_field(reader: shapefile.Reader) -> dict:
    fields = [str(f[0]) for f in reader.fields[1:]]
    candidates = _candidate_date_fields(reader)
    records = reader.records()
    scored = []
    for name in candidates:
        idx = fields.index(name)
        parsed = [_parse_one_date(rec[idx]) for rec in records]
        good = [d for d in parsed if d is not None]
        scored.append({
            "field": name,
            "parsed_n": len(good),
            "parsed_fraction": (len(good) / len(records)) if records else 0.0,
            "distinct_dates": len(set(good)),
            "min_date": min(good).isoformat() if good else None,
            "max_date": max(good).isoformat() if good else None,
            "_dates": good,
        })
    scored.sort(key=lambda x: (x["parsed_fraction"], x["distinct_dates"], x["parsed_n"]), reverse=True)
    if not scored:
        return {"selected": None, "candidates": []}
    best = scored[0]
    public = [{k: v for k, v in x.items() if k != "_dates"} for x in scored]
    dates = best["_dates"]
    counts = Counter(dates)
    return {
        "selected": best["field"],
        "parsed_n": best["parsed_n"],
        "parsed_fraction": best["parsed_fraction"],
        "distinct_dates": best["distinct_dates"],
        "min_date": best["min_date"],
        "max_date": best["max_date"],
        "dates_with_multiple_records": sum(v > 1 for v in counts.values()),
        "max_records_one_date": max(counts.values()) if counts else 0,
        "candidates": public,
    }


def read_epsg(prj_path: Path) -> dict:
    if not prj_path.exists():
        return {"prj_present": False, "epsg": None, "error": "missing .prj"}
    text = prj_path.read_text(encoding="utf-8", errors="ignore")
    try:
        crs = CRS.from_wkt(text)
        epsg = crs.to_epsg()
        return {"prj_present": True, "epsg": epsg, "crs_name": crs.name, "error": None}
    except Exception as exc:
        return {
            "prj_present": True,
            "epsg": None,
            "crs_name": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def inspect_shapefile(shp_path: Path) -> dict:
    reader = shapefile.Reader(str(shp_path))
    fields = [
        {
            "name": str(f[0]),
            "type": str(f[1]),
            "size": int(f[2]),
            "decimals": int(f[3]),
        }
        for f in reader.fields[1:]
    ]
    date_info = choose_date_field(reader)
    crs = read_epsg(shp_path.with_suffix(".prj"))
    return {
        "path": shp_path.as_posix(),
        "feature_count": int(len(reader)),
        "shape_type": str(reader.shapeTypeName),
        "fields": fields,
        "date": date_info,
        "crs": crs,
        "dbf_present": shp_path.with_suffix(".dbf").exists(),
        "shx_present": shp_path.with_suffix(".shx").exists(),
    }


def inspect_archive(data: bytes, contract: dict) -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(root)
            names = z.namelist()
        shp_paths = sorted(root.rglob("*.shp"))

        rows = []
        unmapped = []
        for shp in shp_paths:
            rel = shp.relative_to(root).as_posix()
            parsed = parse_colony_year(rel)
            if parsed is None:
                unmapped.append(rel)
                continue
            colony, year = parsed
            info = inspect_shapefile(shp)
            info["archive_path"] = rel
            info["colony"] = colony
            info["season"] = year
            rows.append(info)

    by_colony: dict[str, dict] = {}
    for colony in ("Atka", "Coulman", "Washington"):
        local = [x for x in rows if x["colony"] == colony]
        years = sorted({int(x["season"]) for x in local})
        good_date_years = sorted({
            int(x["season"]) for x in local
            if x["date"].get("selected")
            and float(x["date"].get("parsed_fraction", 0.0)) >= 0.95
            and int(x["date"].get("distinct_dates", 0)) >= int(
                contract["pass_gate"]["minimum_dates_in_at_least_n_seasons"]
            )
        })
        point_years = sorted({
            int(x["season"]) for x in local
            if str(x["shape_type"]).upper().startswith("POINT")
        })
        epsg4326_years = sorted({
            int(x["season"]) for x in local
            if x["crs"].get("epsg") == 4326
        })
        by_colony[colony] = {
            "shapefiles": len(local),
            "years": years,
            "n_years": len(years),
            "years_with_3plus_dates": good_date_years,
            "n_years_with_3plus_dates": len(good_date_years),
            "point_geometry_years": point_years,
            "epsg4326_years": epsg4326_years,
            "date_fields_selected": sorted({
                str(x["date"]["selected"]) for x in local if x["date"].get("selected")
            }),
            "field_name_sets": sorted({
                "|".join(f["name"] for f in x["fields"]) for x in local
            }),
        }

    gate = contract["pass_gate"]
    colony_pass = {}
    for colony, x in by_colony.items():
        colony_pass[colony] = bool(
            x["n_years"] >= int(gate["minimum_seasons_per_colony"])
            and x["n_years_with_3plus_dates"] >= int(gate["seasons_meeting_minimum_dates_per_colony"])
            and len(x["point_geometry_years"]) == x["n_years"]
        )
    named_colonies_passing = sum(colony_pass.values())
    passed = bool(
        named_colonies_passing >= int(gate["minimum_named_colonies"])
        and all(colony_pass.values())
    )

    return {
        "archive_members": len(names),
        "shapefiles_total": len(shp_paths),
        "mapped_tracking_shapefiles": len(rows),
        "unmapped_shapefiles": unmapped,
        "by_colony": by_colony,
        "colony_pass": colony_pass,
        "schema_gate_passed": passed,
        "schema_rows": rows,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--archive", type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    args = p.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    if args.archive:
        data = args.archive.read_bytes()
        source_url = None
    else:
        data, source_url = download_archive(contract["archive"]["preferred_urls"])

    result = inspect_archive(data, contract)
    output = {
        "schema_version": 1,
        "result_id": "mina-paper3-mobile-node-schema-audit-v1",
        "archive_source_url": source_url,
        **{k: v for k, v in result.items() if k != "schema_rows"},
        "decision": {
            "schema_gate_passed": bool(result["schema_gate_passed"]),
            "movement_metric_execution_authorized": bool(result["schema_gate_passed"]),
            "movement_outcomes_opened": False,
        },
        "schema_rows": result["schema_rows"],
        "boundary": [
            "No coordinate distance or displacement is calculated.",
            "Feature counts and date multiplicity are schema/support facts only.",
            "No abundance, breeding success or environmental covariates are used."
        ],
    }
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k != "schema_rows"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
