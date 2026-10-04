#!/usr/bin/env python3
"""Outcome-blind optical-imagery support audit for Antarctic island-ecology Paper 2.

This script NEVER reads penguin count magnitudes or derived demographic outcomes.
It reconstructs the frozen bridged site roster from support-only metadata, joins
site coordinates, then queries public STAC metadata for repeat optical coverage.
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path
from typing import Iterable

import pandas as pd
import pyreadr
import requests

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
SUMMER_MONTHS = {11, 12, 1, 2, 3}
WINDOWS = {
    "landsat_early": {
        "collection": "landsat-c2-l2",
        "datetime": "1984-01-01/1994-12-31",
    },
    "landsat_late": {
        "collection": "landsat-c2-l2",
        "datetime": "2018-01-01/2025-12-31",
    },
    "sentinel2_validation": {
        "collection": "sentinel-2-l2a",
        "datetime": "2018-01-01/2025-12-31",
    },
}
MIN_DISTINCT_DATES = 5
MIN_DISTINCT_YEARS = 3
MAX_ITEMS = 250


def _load_rda(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        value = result[expected]
    elif len(result) == 1:
        value = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(value, pd.DataFrame):
        raise TypeError(expected)
    return value


def parse_seasons(value: object) -> list[int]:
    if pd.isna(value):
        return []
    return sorted({int(v) for v in str(value).split(";") if str(v).strip()})


def collapse_sites(forcing: pd.DataFrame, sites: pd.DataFrame) -> pd.DataFrame:
    """Collapse frozen site x species support rows to one outcome-blind site roster."""
    required = {"site_id", "species_id", "seasons"}
    missing = required - set(forcing.columns)
    if missing:
        raise ValueError(f"forcing CSV missing columns: {sorted(missing)}")

    site_meta = sites.copy()
    site_meta["site_id"] = site_meta["site_id"].astype(str)
    site_meta = site_meta.drop_duplicates("site_id").set_index("site_id")

    rows: list[dict] = []
    for site_id, local in forcing.groupby(forcing["site_id"].astype(str), sort=True):
        if site_id not in site_meta.index:
            raise ValueError(f"missing site metadata: {site_id}")
        m = site_meta.loc[site_id]
        seasons = sorted({
            season
            for raw in local["seasons"]
            for season in parse_seasons(raw)
        })
        species = sorted({str(v) for v in local["species_id"]})
        rows.append({
            "site_id": site_id,
            "site_name": str(m.get("site_name", site_id)),
            "species_ids": ";".join(species),
            "n_species": len(species),
            "region": None if pd.isna(m.get("region")) else str(m.get("region")),
            "ccamlr_id": None if pd.isna(m.get("ccamlr_id")) else str(m.get("ccamlr_id")),
            "latitude": float(m["latitude"]),
            "longitude": float(m["longitude"]),
            "first_record_season": min(seasons),
            "last_record_season": max(seasons),
            "n_site_species_units": int(len(local)),
        })
    return pd.DataFrame(rows).sort_values("site_id").reset_index(drop=True)


def _item_datetime(feature: dict) -> pd.Timestamp | None:
    props = feature.get("properties", {})
    raw = props.get("datetime") or props.get("start_datetime")
    if not raw:
        return None
    try:
        return pd.Timestamp(raw)
    except Exception:
        return None


def summarize_features(features: Iterable[dict], capped: bool = False) -> dict:
    dates = []
    platforms = Counter()
    cloud = []
    for f in features:
        dt = _item_datetime(f)
        if dt is None or dt.month not in SUMMER_MONTHS:
            continue
        dates.append(dt.date().isoformat())
        p = f.get("properties", {})
        if p.get("platform"):
            platforms[str(p["platform"])] += 1
        cc = p.get("eo:cloud_cover")
        if cc is not None:
            try:
                cloud.append(float(cc))
            except Exception:
                pass
    unique_dates = sorted(set(dates))
    years = sorted({int(d[:4]) for d in unique_dates})
    return {
        "summer_distinct_dates": len(unique_dates),
        "summer_distinct_years": len(years),
        "first_summer_date": unique_dates[0] if unique_dates else None,
        "last_summer_date": unique_dates[-1] if unique_dates else None,
        "platform_counts": dict(sorted(platforms.items())),
        "scene_cloud_cover_median": (float(pd.Series(cloud).median()) if cloud else None),
        "search_capped": bool(capped),
        "support_pass": (
            len(unique_dates) >= MIN_DISTINCT_DATES
            and len(years) >= MIN_DISTINCT_YEARS
        ),
    }


def stac_search_point(
    session: requests.Session,
    *,
    lon: float,
    lat: float,
    collection: str,
    datetime_range: str,
    max_items: int = MAX_ITEMS,
    retries: int = 4,
) -> tuple[list[dict], bool]:
    """Fetch STAC item metadata at a point, with bounded pagination."""
    payload = {
        "collections": [collection],
        "intersects": {"type": "Point", "coordinates": [lon, lat]},
        "datetime": datetime_range,
        "limit": min(100, max_items),
    }
    features: list[dict] = []
    url = STAC_URL
    body = payload
    while url and len(features) < max_items:
        response = None
        for attempt in range(retries):
            try:
                response = session.post(url, json=body, timeout=60)
                response.raise_for_status()
                break
            except requests.RequestException:
                if attempt + 1 == retries:
                    raise
                time.sleep(2 ** attempt)
        data = response.json()
        features.extend(data.get("features", []))
        next_link = next(
            (link for link in data.get("links", []) if link.get("rel") == "next"),
            None,
        )
        if not next_link:
            url = None
            break
        url = next_link.get("href")
        method = str(next_link.get("method", "GET")).upper()
        if method == "POST":
            body = next_link.get("body", body)
        else:
            body = None
            # Planetary Computer currently paginates search with POST. Fail
            # explicitly rather than silently changing request semantics.
            if method != "GET":
                raise RuntimeError(f"unsupported STAC pagination method: {method}")
            response = session.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()
            features.extend(data.get("features", []))
            url = None
    capped = len(features) >= max_items
    return features[:max_items], capped


def audit_site(session: requests.Session, row: pd.Series) -> dict:
    out = row.to_dict()
    for label, spec in WINDOWS.items():
        features, capped = stac_search_point(
            session,
            lon=float(row["longitude"]),
            lat=float(row["latitude"]),
            collection=spec["collection"],
            datetime_range=spec["datetime"],
        )
        summary = summarize_features(features, capped=capped)
        for key, value in summary.items():
            if isinstance(value, dict):
                value = json.dumps(value, sort_keys=True)
            out[f"{label}_{key}"] = value
    out["metadata_support_pass"] = bool(
        out["landsat_early_support_pass"]
        and out["landsat_late_support_pass"]
        and out["sentinel2_validation_support_pass"]
    )
    return out


def summarize_audit(df: pd.DataFrame) -> dict:
    by_region = {}
    for region, local in df.groupby("region", dropna=False):
        label = "NA" if pd.isna(region) else str(region)
        by_region[label] = {
            "sites": int(len(local)),
            "metadata_support_pass": int(local["metadata_support_pass"].sum()),
        }
    return {
        "schema_version": 1,
        "audit_id": "mina-paper2-dynamic-habitat-imagery-support-v1",
        "mapppdr_commit": MAPPPDR_COMMIT,
        "stac_endpoint": STAC_URL,
        "summer_months": sorted(SUMMER_MONTHS),
        "windows": WINDOWS,
        "thresholds": {
            "minimum_distinct_summer_dates": MIN_DISTINCT_DATES,
            "minimum_distinct_summer_years": MIN_DISTINCT_YEARS,
            "maximum_items_per_search": MAX_ITEMS,
        },
        "sites": int(len(df)),
        "metadata_support_pass_sites": int(df["metadata_support_pass"].sum()),
        "metadata_support_fraction": float(df["metadata_support_pass"].mean()),
        "by_region": by_region,
        "no_demographic_outcomes_opened": True,
        "interpretation_boundary": [
            "This gate measures catalogued repeat optical-image availability only.",
            "Scene-level cloud metadata is descriptive and is not used for eligibility.",
            "Pixel-level cloud, shadow, snow, illumination and rock/ice classification quality remain unopened.",
            "Passing this gate does not establish that ice-free breeding-opportunity change is estimable.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forcing-csv", required=True, type=Path)
    ap.add_argument("--mapppdr-dir", required=True, type=Path)
    ap.add_argument("--out-csv", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    args = ap.parse_args()

    forcing = pd.read_csv(args.forcing_csv, dtype={"site_id": str, "species_id": str})
    sites = _load_rda(args.mapppdr_dir / "data" / "sites.rda", "sites")
    roster = collapse_sites(forcing, sites)

    session = requests.Session()
    session.headers.update({"User-Agent": "mina-outcome-blind-imagery-audit/1.0"})
    rows = []
    for i, (_, row) in enumerate(roster.iterrows(), start=1):
        print(f"[{i}/{len(roster)}] {row['site_id']} {row['site_name']}", flush=True)
        rows.append(audit_site(session, row))
    result = pd.DataFrame(rows)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out_csv, index=False)
    summary = summarize_audit(result)
    args.out_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
