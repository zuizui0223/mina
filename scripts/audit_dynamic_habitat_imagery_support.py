#!/usr/bin/env python3
"""Outcome-blind STAC availability audit for dynamic Antarctic breeding habitat."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
from pystac_client import Client

ENDPOINT = "https://earth-search.aws.element84.com/v1"
MAX_ITEMS = 5000
SUMMER_MONTHS = {11, 12, 1, 2, 3}
WINDOWS = {
    "landsat_early": {
        "collection": "landsat-c2-l2",
        "start": "1984-01-01",
        "end": "1994-12-31",
    },
    "landsat_late": {
        "collection": "landsat-c2-l2",
        "start": "2018-01-01",
        "end": "2025-12-31",
    },
    "sentinel2_validation": {
        "collection": "sentinel-2-l2a",
        "start": "2018-01-01",
        "end": "2025-12-31",
    },
}
MIN_SUMMER_DATES = 3
MIN_SUMMER_YEARS = 2


def _item_datetime(item) -> datetime | None:
    dt = getattr(item, "datetime", None)
    if dt is not None:
        return dt
    props = getattr(item, "properties", {}) or {}
    value = props.get("datetime") or props.get("start_datetime")
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def summarize_items(items: Iterable, max_items: int = MAX_ITEMS) -> dict:
    rows = []
    total = 0
    for item in items:
        total += 1
        dt = _item_datetime(item)
        if dt is None:
            continue
        props = getattr(item, "properties", {}) or {}
        cloud = props.get("eo:cloud_cover")
        try:
            cloud = float(cloud) if cloud is not None else None
        except (TypeError, ValueError):
            cloud = None
        rows.append((dt.date().isoformat(), dt.year, dt.month, cloud))

    summer = [r for r in rows if r[2] in SUMMER_MONTHS]
    dates = sorted({r[0] for r in summer})
    years = sorted({r[1] for r in summer})
    cloudy = [(r[0], r[3]) for r in summer if r[3] is not None]

    def date_count_below(threshold: float) -> int:
        return len({date for date, cloud in cloudy if cloud < threshold})

    return {
        "n_items": total,
        "n_items_with_datetime": len(rows),
        "n_summer_dates": len(dates),
        "n_summer_years": len(years),
        "first_summer_date": dates[0] if dates else None,
        "last_summer_date": dates[-1] if dates else None,
        "n_summer_dates_cloud_lt20": date_count_below(20),
        "n_summer_dates_cloud_lt40": date_count_below(40),
        "n_summer_dates_cloud_lt60": date_count_below(60),
        "n_summer_dates_with_cloud_metadata": len({date for date, _ in cloudy}),
        "query_hit_max_items": total >= max_items,
        "catalog_support": (
            len(dates) >= MIN_SUMMER_DATES
            and len(years) >= MIN_SUMMER_YEARS
            and total < max_items
        ),
    }


def query_window(
    client: Client,
    lon: float,
    lat: float,
    collection: str,
    start: str,
    end: str,
    max_items: int = MAX_ITEMS,
    retries: int = 3,
) -> dict:
    point = {"type": "Point", "coordinates": [float(lon), float(lat)]}
    last_error = None
    for attempt in range(retries):
        try:
            search = client.search(
                collections=[collection],
                intersects=point,
                datetime=f"{start}/{end}",
                max_items=max_items,
            )
            return summarize_items(search.items(), max_items=max_items)
        except Exception as exc:  # network/API boundary
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(
        f"STAC query failed after {retries} attempts for {collection} "
        f"{start}/{end} at {lat},{lon}: {last_error}"
    )


def audit(seed_csv: Path, endpoint: str = ENDPOINT, max_items: int = MAX_ITEMS) -> tuple[dict, pd.DataFrame]:
    seed = pd.read_csv(seed_csv)
    required = {
        "site_id", "site_name", "species_ids", "region",
        "latitude", "longitude", "first_record_season", "last_record_season",
    }
    missing = sorted(required - set(seed.columns))
    if missing:
        raise ValueError(f"seed missing required columns: {missing}")
    if seed["site_id"].duplicated().any():
        dup = seed.loc[seed["site_id"].duplicated(), "site_id"].tolist()
        raise ValueError(f"seed must contain one row per site; duplicates: {dup}")
    if len(seed) != 88:
        raise ValueError(f"frozen site roster drift: {len(seed)} != 88")

    client = Client.open(endpoint)
    out_rows = []
    for _, row in seed.sort_values("site_id").iterrows():
        out = row.to_dict()
        for name, spec in WINDOWS.items():
            summary = query_window(
                client,
                lon=float(row["longitude"]),
                lat=float(row["latitude"]),
                collection=spec["collection"],
                start=spec["start"],
                end=spec["end"],
                max_items=max_items,
            )
            for key, value in summary.items():
                out[f"{name}_{key}"] = value

        out["catalog_support_all"] = all(
            bool(out[f"{name}_catalog_support"]) for name in WINDOWS
        )
        out_rows.append(out)

    table = pd.DataFrame(out_rows)
    by_region = {}
    for region, local in table.groupby("region", dropna=False):
        by_region[str(region)] = {
            "n_sites": int(len(local)),
            "n_catalog_supported": int(local["catalog_support_all"].sum()),
            "fraction_catalog_supported": float(local["catalog_support_all"].mean()),
        }

    result = {
        "schema_version": 1,
        "audit_id": "mina-dynamic-habitat-imagery-support-audit-v1",
        "stac_endpoint": endpoint,
        "seed_csv": str(seed_csv),
        "n_sites": int(len(table)),
        "windows": WINDOWS,
        "austral_summer_months": sorted(SUMMER_MONTHS),
        "gate": {
            "minimum_summer_dates": MIN_SUMMER_DATES,
            "minimum_summer_years": MIN_SUMMER_YEARS,
            "all_windows_required": True,
            "catalog_only": True,
        },
        "summary": {
            "n_catalog_supported_all": int(table["catalog_support_all"].sum()),
            "fraction_catalog_supported_all": float(table["catalog_support_all"].mean()),
            "by_region": by_region,
            "window_support": {
                name: {
                    "n_supported": int(table[f"{name}_catalog_support"].sum()),
                    "fraction_supported": float(table[f"{name}_catalog_support"].mean()),
                    "median_summer_dates": float(table[f"{name}_n_summer_dates"].median()),
                    "min_summer_dates": int(table[f"{name}_n_summer_dates"].min()),
                    "max_summer_dates": int(table[f"{name}_n_summer_dates"].max()),
                }
                for name in WINDOWS
            },
        },
        "boundary": [
            "No demographic count magnitudes or derived increase/decline labels are read.",
            "Catalog support is not pixel-quality support.",
            "Cloud-cover metadata are descriptive only at this gate because snow/ice can complicate scene-level cloud metadata in polar environments.",
            "The next gate must inspect local QA pixels and classification feasibility before any ecological outcome model is authorized.",
        ],
    }
    return result, table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-csv", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--endpoint", default=ENDPOINT)
    parser.add_argument("--max-items", type=int, default=MAX_ITEMS)
    args = parser.parse_args()

    result, table = audit(args.seed_csv, endpoint=args.endpoint, max_items=args.max_items)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    table.to_csv(args.out_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
