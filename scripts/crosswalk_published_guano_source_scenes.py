#!/usr/bin/env python3
"""Crosswalk published PANGAEA Adelie guano pixels to USGS C2 L1 source scenes."""
from __future__ import annotations

import argparse
import io
import json
import math
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests


def strip_metaheader(text: str) -> str:
    if "*/" in text:
        return text.split("*/", 1)[1].lstrip("\r\n ")
    return text


def read_pangaea_table(text: str) -> pd.DataFrame:
    body = strip_metaheader(text)
    df = pd.read_csv(io.StringIO(body), sep="\t")
    if len(df) == 0:
        raise ValueError("empty PANGAEA table")
    if df.shape[1] < 10:
        raise ValueError(f"unexpected PANGAEA column count: {df.shape[1]}")
    # Use published parameter order rather than fragile translated header labels.
    out = pd.DataFrame({
        "colony_id": df.iloc[:, 0],
        "source_file": df.iloc[:, 1].astype(str),
        "published_d": pd.to_numeric(df.iloc[:, 2], errors="coerce"),
        "pixel_row": pd.to_numeric(df.iloc[:, 3], errors="coerce"),
        "pixel_col": pd.to_numeric(df.iloc[:, 4], errors="coerce"),
        "latitude": pd.to_numeric(df.iloc[:, 7], errors="coerce"),
        "longitude": pd.to_numeric(df.iloc[:, 8], errors="coerce"),
    })
    if out[["source_file","latitude","longitude"]].isna().any().any():
        raise ValueError("missing required published reference fields")
    return out


def parse_source_file(name: str) -> dict:
    s = str(name).strip()
    if len(s) < 16 or not s.startswith("L"):
        raise ValueError(f"unexpected source_file: {s}")
    path = int(s[3:6])
    row = int(s[6:9])
    year = int(s[9:13])
    doy = int(s[13:16])
    date = datetime(year, 1, 1) + timedelta(days=doy - 1)
    if date.year != year:
        raise ValueError(f"invalid day-of-year in {s}")
    return {
        "wrs_path": path,
        "wrs_row": row,
        "year": year,
        "doy": doy,
        "date": date.date().isoformat(),
    }


def _int_prop(props: dict, keys: list[str]):
    for key in keys:
        value = props.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def search_exact_date(session, endpoint, collection, lon, lat, date):
    payload = {
        "collections": [collection],
        "intersects": {"type": "Point", "coordinates": [float(lon), float(lat)]},
        "datetime": f"{date}T00:00:00Z/{date}T23:59:59Z",
        "limit": 100,
    }
    url = endpoint.rstrip("/") + "/search"
    last = None
    for attempt in range(5):
        try:
            r = session.post(url, json=payload, timeout=60)
            r.raise_for_status()
            return r.json().get("features", [])
        except Exception as exc:
            last = exc
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise last


def choose_match(items: list[dict], parsed: dict) -> tuple[str | None, str]:
    candidates = []
    for item in items:
        props = item.get("properties", {}) or {}
        if str(props.get("platform", "")).upper() not in {"LANDSAT_7", "LANDSAT-7"}:
            continue
        path = _int_prop(props, ["landsat:wrs_path", "wrs:path", "landsat:path"])
        row = _int_prop(props, ["landsat:wrs_row", "wrs:row", "landsat:row"])
        if path == parsed["wrs_path"] and row == parsed["wrs_row"]:
            candidates.append((str(item.get("id")), "property_path_row"))
            continue
        token = f"{parsed['wrs_path']:03d}{parsed['wrs_row']:03d}"
        iid = str(item.get("id", ""))
        if token in iid:
            candidates.append((iid, "id_path_row_token"))
    if not candidates:
        return None, "no_match"
    candidates.sort()
    return candidates[0]


def audit(reference: pd.DataFrame, contract: dict) -> tuple[pd.DataFrame, dict]:
    expected = int(contract["published_reference"]["expected_classified_pixels"])
    if len(reference) != expected:
        raise ValueError(f"published pixel count drift: {len(reference)} != {expected}")

    parsed_rows = []
    for source_file, local in reference.groupby("source_file", sort=True):
        parsed = parse_source_file(source_file)
        first = local.iloc[0]
        parsed_rows.append({
            "source_file": source_file,
            **parsed,
            "representative_latitude": float(first.latitude),
            "representative_longitude": float(first.longitude),
            "published_pixel_count": int(len(local)),
        })
    scenes = pd.DataFrame(parsed_rows)
    session = requests.Session()
    session.headers.update({"User-Agent": "mina-published-guano-scene-crosswalk/1.0"})
    endpoint = contract["landsat"]["stac_endpoint"]
    collection = contract["landsat"]["collection"]

    results = []
    for i, row in scenes.iterrows():
        try:
            items = search_exact_date(
                session, endpoint, collection,
                row.representative_longitude, row.representative_latitude, row.date
            )
            item_id, method = choose_match(items, row.to_dict())
            error = None
        except Exception as exc:
            item_id, method, error = None, "query_error", f"{type(exc).__name__}: {exc}"
        rec = row.to_dict()
        rec.update({
            "collection2_item_id": item_id,
            "crosswalk_method": method,
            "crosswalked": item_id is not None,
            "query_error": error,
        })
        results.append(rec)
        print(f"[{i+1}/{len(scenes)}] {row.source_file}: {item_id or method}", flush=True)
        time.sleep(0.03)

    out = pd.DataFrame(results)
    n_scenes = len(out)
    n_cross = int(out["crosswalked"].sum())
    pixels_cross = int(out.loc[out["crosswalked"], "published_pixel_count"].sum())
    scene_frac = n_cross / n_scenes if n_scenes else 0.0
    pixel_frac = pixels_cross / len(reference) if len(reference) else 0.0
    gate = contract["pass_gate"]
    passed = (
        scene_frac >= float(gate["minimum_fraction_unique_source_scenes_crosswalked"])
        and pixel_frac >= float(gate["minimum_fraction_published_pixels_represented"])
    )
    receipt = {
        "schema_version": 1,
        "result_id": "mina-paper2-published-guano-scene-crosswalk-v1-result",
        "contract_id": contract["contract_id"],
        "published_reference": {
            "pixels": int(len(reference)),
            "unique_source_scenes": int(n_scenes),
        },
        "crosswalk": {
            "source_scenes_crosswalked": n_cross,
            "source_scene_fraction": scene_frac,
            "published_pixels_represented": pixels_cross,
            "published_pixel_fraction": pixel_frac,
            "query_errors": int(out["query_error"].notna().sum()),
            "failed_source_files": out.loc[~out["crosswalked"], "source_file"].astype(str).tolist(),
        },
        "decision": {
            "crosswalk_gate_passed": bool(passed),
            "published_d_value_recovery_authorized": bool(passed),
            "demographic_magnitudes_opened": False,
        },
        "boundary": [
            "This is a source-scene identity audit, not a classifier accuracy result.",
            "No published d-value is used to select or drop source scenes.",
            "No penguin demographic outcome is read."
        ]
    }
    return out, receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-csv", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    args = p.parse_args()

    c = json.loads(args.contract.read_text(encoding="utf-8"))
    url = c["published_reference"]["download"]
    headers = {"Accept": c["published_reference"]["accept"], "User-Agent": "mina-pangaea-crosswalk/1.0"}
    r = requests.get(url, headers=headers, timeout=120, allow_redirects=True)
    r.raise_for_status()
    ref = read_pangaea_table(r.text)
    table, receipt = audit(ref, c)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out_csv, index=False)
    args.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
