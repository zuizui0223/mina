#!/usr/bin/env python3
"""Outcome-blind optical-scene support audit for Antarctic island-ecology Paper 2."""
from __future__ import annotations

import argparse
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

PC_STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
LANDSAT = "landsat-c2-l2"
SENTINEL = "sentinel-2-l2a"
AUSTRAL_MONTHS = {11, 12, 1, 2, 3}
PRIMARY_CLOUD_MAX = 80.0
DIAGNOSTIC_CLOUD_MAX = 50.0
WINDOW_RADIUS = 4
MIN_SCENES = 3
MIN_YEARS = 2
MIN_SEPARATION = 8
LOWER_YEAR = 1984
UPPER_YEAR = 2025
QUERY_TIMEOUT_SECONDS = 45
QUERY_RETRIES = 3
MAX_WORKERS = 12
STAC_LIMIT = 1000


def epoch_window(anchor: int) -> tuple[int, int]:
    """Return a fixed-width 9-year window, shifted inward at archive edges."""
    width = 2 * WINDOW_RADIUS
    start, end = anchor - WINDOW_RADIUS, anchor + WINDOW_RADIUS
    if start < LOWER_YEAR:
        start = LOWER_YEAR
        end = min(UPPER_YEAR, start + width)
    if end > UPPER_YEAR:
        end = UPPER_YEAR
        start = max(LOWER_YEAR, end - width)
    return int(start), int(end)


def _item_properties(item) -> dict:
    if isinstance(item, dict):
        return item.get("properties", {})
    return getattr(item, "properties", {}) or {}


def _item_datetime(item):
    if isinstance(item, dict):
        value = _item_properties(item).get("datetime")
        if not value:
            return None
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return getattr(item, "datetime", None)


def _cloud(item) -> float:
    value = _item_properties(item).get("eo:cloud_cover")
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def summarize_items(items: list) -> dict:
    rows = []
    for item in items:
        dt = _item_datetime(item)
        if dt is None or dt.month not in AUSTRAL_MONTHS:
            continue
        cloud = _cloud(item)
        if math.isnan(cloud) or cloud > PRIMARY_CLOUD_MAX:
            continue
        rows.append((dt.date().isoformat(), dt.year, cloud))
    rows.sort()
    clouds = [r[2] for r in rows]
    years = sorted({r[1] for r in rows})
    return {
        "n_scenes_cloud_le80": len(rows),
        "n_scenes_cloud_le50": sum(c <= DIAGNOSTIC_CLOUD_MAX for c in clouds),
        "n_distinct_years": len(years),
        "years": years,
        "first_scene": rows[0][0] if rows else None,
        "last_scene": rows[-1][0] if rows else None,
        "cloud_median": float(pd.Series(clouds).median()) if clouds else None,
        "catalog_support": len(rows) >= MIN_SCENES and len(years) >= MIN_YEARS,
    }


def query_catalog(collection: str, lon: float, lat: float, start: int, end: int,
                  retries: int = QUERY_RETRIES) -> dict:
    """Query one point/epoch with explicit timeout; errors remain distinguishable from no data."""
    payload = {
        "collections": [collection],
        "intersects": {"type": "Point", "coordinates": [float(lon), float(lat)]},
        "datetime": f"{start}-01-01T00:00:00Z/{end}-12-31T23:59:59Z",
        "limit": STAC_LIMIT,
    }
    last = None
    for attempt in range(retries):
        try:
            response = requests.post(
                f"{PC_STAC}/search",
                json=payload,
                timeout=QUERY_TIMEOUT_SECONDS,
                headers={"User-Agent": "mina-outcome-blind-optical-support-audit/1.0"},
            )
            response.raise_for_status()
            body = response.json()
            features = body.get("features", [])
            summary = summarize_items(features)
            matched = body.get("numberMatched")
            summary["n_returned_items"] = len(features)
            summary["number_matched"] = matched
            summary["catalog_truncated"] = bool(
                isinstance(matched, int) and matched > len(features)
            )
            return summary
        except Exception as exc:
            last = repr(exc)
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    return {
        "n_scenes_cloud_le80": 0,
        "n_scenes_cloud_le50": 0,
        "n_distinct_years": 0,
        "years": [],
        "first_scene": None,
        "last_scene": None,
        "cloud_median": None,
        "catalog_support": False,
        "n_returned_items": 0,
        "number_matched": None,
        "catalog_truncated": False,
        "query_error": last,
    }


def build_units(forcing_csv: Path, options_csv: Path) -> pd.DataFrame:
    f = pd.read_csv(forcing_csv)
    o = pd.read_csv(options_csv)
    required_f = {
        "unit_id", "site_id", "species_id", "region",
        "first_observed_season", "last_observed_season", "n_observed_seasons"
    }
    required_o = {"site_id", "latitude", "longitude"}
    missing = required_f - set(f.columns)
    if missing:
        raise ValueError(f"forcing csv missing {sorted(missing)}")
    missing = required_o - set(o.columns)
    if missing:
        raise ValueError(f"options csv missing {sorted(missing)}")

    # Explicit outcome-blind guard.
    forbidden = [c for c in f.columns if c.lower() in {
        "count", "abundance", "trend", "effective_component_number", "kappa",
        "delta_kappa", "p_value"
    }]
    if forbidden:
        raise ValueError(f"forbidden demographic fields present: {forbidden}")

    coords = o[["site_id", "latitude", "longitude"]].drop_duplicates("site_id")
    x = f[list(required_f)].merge(coords, on="site_id", how="left", validate="many_to_one")
    if x[["latitude", "longitude"]].isna().any().any():
        bad = x.loc[x[["latitude", "longitude"]].isna().any(axis=1), "site_id"].tolist()
        raise ValueError(f"missing coordinates: {bad}")
    if len(x) != 107:
        raise ValueError(f"frozen cohort drift: {len(x)} != 107")
    return x.sort_values(["species_id", "site_id"]).reset_index(drop=True)


def _task_key(collection: str, row, window: tuple[int, int]) -> tuple:
    return (
        collection,
        str(row.site_id),
        float(row.longitude),
        float(row.latitude),
        int(window[0]),
        int(window[1]),
    )


def _collect_tasks(units: pd.DataFrame) -> dict[tuple, tuple]:
    tasks = {}
    for _, row in units.iterrows():
        early = epoch_window(int(row.first_observed_season))
        late = epoch_window(int(row.last_observed_season))
        for collection, window in ((LANDSAT, early), (LANDSAT, late)):
            key = _task_key(collection, row, window)
            tasks[key] = (collection, row.longitude, row.latitude, *window)
        s2_start = max(2016, late[0])
        if s2_start <= late[1]:
            window = (s2_start, late[1])
            key = _task_key(SENTINEL, row, window)
            tasks[key] = (SENTINEL, row.longitude, row.latitude, *window)
    return tasks


def audit(forcing_csv: Path, options_csv: Path) -> tuple[dict, pd.DataFrame]:
    units = build_units(forcing_csv, options_csv)
    tasks = _collect_tasks(units)
    cache: dict[tuple, dict] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(query_catalog, collection, lon, lat, start, end): key
            for key, (collection, lon, lat, start, end) in tasks.items()
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                cache[key] = future.result()
            except Exception as exc:
                cache[key] = {
                    "n_scenes_cloud_le80": 0,
                    "n_scenes_cloud_le50": 0,
                    "n_distinct_years": 0,
                    "years": [],
                    "first_scene": None,
                    "last_scene": None,
                    "cloud_median": None,
                    "catalog_support": False,
                    "n_returned_items": 0,
                    "number_matched": None,
                    "catalog_truncated": False,
                    "query_error": repr(exc),
                }

    out = []
    for _, r in units.iterrows():
        early = epoch_window(int(r.first_observed_season))
        late = epoch_window(int(r.last_observed_season))
        early_ls = cache[_task_key(LANDSAT, r, early)]
        late_ls = cache[_task_key(LANDSAT, r, late)]

        late_s2 = None
        s2_start = max(2016, late[0])
        if s2_start <= late[1]:
            late_s2 = cache[_task_key(SENTINEL, r, (s2_start, late[1]))]

        early_mid = sum(early) / 2
        late_mid = sum(late) / 2
        sep = late_mid - early_mid
        query_ok = not early_ls.get("query_error") and not late_ls.get("query_error")
        primary = bool(
            query_ok
            and early_ls.get("catalog_support")
            and late_ls.get("catalog_support")
            and sep >= MIN_SEPARATION
        )
        reason = []
        if early_ls.get("query_error"):
            reason.append("early_catalog_query_error")
        elif not early_ls.get("catalog_support"):
            reason.append("early_landsat_catalog_support")
        if late_ls.get("query_error"):
            reason.append("late_catalog_query_error")
        elif not late_ls.get("catalog_support"):
            reason.append("late_landsat_catalog_support")
        if sep < MIN_SEPARATION:
            reason.append("epoch_separation")

        row = {
            **r.to_dict(),
            "early_window_start": early[0],
            "early_window_end": early[1],
            "late_window_start": late[0],
            "late_window_end": late[1],
            "epoch_midpoint_separation_years": sep,
            "early_landsat_n_scenes_le80": early_ls["n_scenes_cloud_le80"],
            "early_landsat_n_scenes_le50": early_ls["n_scenes_cloud_le50"],
            "early_landsat_n_years": early_ls["n_distinct_years"],
            "early_landsat_first_scene": early_ls["first_scene"],
            "early_landsat_last_scene": early_ls["last_scene"],
            "late_landsat_n_scenes_le80": late_ls["n_scenes_cloud_le80"],
            "late_landsat_n_scenes_le50": late_ls["n_scenes_cloud_le50"],
            "late_landsat_n_years": late_ls["n_distinct_years"],
            "late_landsat_first_scene": late_ls["first_scene"],
            "late_landsat_last_scene": late_ls["last_scene"],
            "late_sentinel_n_scenes_le80": None if late_s2 is None else late_s2["n_scenes_cloud_le80"],
            "late_sentinel_n_scenes_le50": None if late_s2 is None else late_s2["n_scenes_cloud_le50"],
            "late_sentinel_n_years": None if late_s2 is None else late_s2["n_distinct_years"],
            "catalog_gate_pass": primary,
            "catalog_gate_reason": ";".join(reason),
            "early_query_error": early_ls.get("query_error"),
            "late_query_error": late_ls.get("query_error"),
            "sentinel_query_error": None if late_s2 is None else late_s2.get("query_error"),
            "early_catalog_truncated": bool(early_ls.get("catalog_truncated", False)),
            "late_catalog_truncated": bool(late_ls.get("catalog_truncated", False)),
        }
        out.append(row)

    df = pd.DataFrame(out)
    by_species = {}
    for sp, g in df.groupby("species_id"):
        by_species[sp] = {
            "units": int(len(g)),
            "pass": int(g.catalog_gate_pass.sum()),
            "pass_fraction": float(g.catalog_gate_pass.mean()),
            "distinct_sites": int(g.site_id.nunique()),
        }
    by_region = {}
    for region, g in df.groupby("region", dropna=False):
        by_region[str(region)] = {
            "units": int(len(g)),
            "pass": int(g.catalog_gate_pass.sum()),
            "pass_fraction": float(g.catalog_gate_pass.mean()),
        }

    query_error_rows = df[
        df["early_query_error"].notna() | df["late_query_error"].notna()
    ]
    result = {
        "schema_version": 1,
        "audit_id": "mina-antarctic-island-ecology-paper2-optical-catalog-v1",
        "status": "outcome_blind_scene_catalog_support",
        "planetary_computer_stac": PC_STAC,
        "collections": {"landsat": LANDSAT, "sentinel2": SENTINEL},
        "execution": {
            "unique_catalog_queries": len(tasks),
            "max_workers": MAX_WORKERS,
            "query_timeout_seconds": QUERY_TIMEOUT_SECONDS,
            "stac_limit": STAC_LIMIT,
        },
        "gate": {
            "window_radius_years": WINDOW_RADIUS,
            "year_bounds": [LOWER_YEAR, UPPER_YEAR],
            "austral_months": sorted(AUSTRAL_MONTHS),
            "primary_scene_cloud_max_percent": PRIMARY_CLOUD_MAX,
            "diagnostic_scene_cloud_max_percent": DIAGNOSTIC_CLOUD_MAX,
            "minimum_scenes_per_epoch": MIN_SCENES,
            "minimum_distinct_years_per_epoch": MIN_YEARS,
            "minimum_epoch_midpoint_separation_years": MIN_SEPARATION,
        },
        "cohort": {
            "site_species_units": int(len(df)),
            "distinct_sites": int(df.site_id.nunique()),
            "species": by_species,
            "regions": by_region,
        },
        "decision": {
            "passing_units": int(df.catalog_gate_pass.sum()),
            "passing_fraction": float(df.catalog_gate_pass.mean()),
            "query_error_units": int(len(query_error_rows)),
            "all_queries_error_free": bool(len(query_error_rows) == 0),
            "any_catalog_truncation": bool(
                df["early_catalog_truncated"].any() or df["late_catalog_truncated"].any()
            ),
            "pixel_qa_opened": False,
            "demographic_magnitudes_opened": False,
        },
        "interpretation_boundary": [
            "This is a scene-catalog support audit, not a habitat-change result.",
            "Scene-level cloud cover is not local clear-pixel fraction.",
            "Catalog query failure is reported separately and is never classified as ecological data absence.",
            "Failure of the Level-2 catalog gate does not prove that no usable Level-1/TOA imagery exists, especially at high latitude.",
            "No count magnitudes, abundance trends, effective-component outcomes, or concentration statistics are read.",
        ],
    }
    return result, df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forcing-csv", required=True, type=Path)
    ap.add_argument("--options-csv", required=True, type=Path)
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-csv", required=True, type=Path)
    args = ap.parse_args()
    result, df = audit(args.forcing_csv, args.options_csv)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    df.to_csv(args.out_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
