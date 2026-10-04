#!/usr/bin/env python3
"""Outcome-blind optical-scene support audit for Antarctic island-ecology Paper 2."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import pandas as pd
from pystac_client import Client

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


def epoch_window(anchor: int) -> tuple[int, int]:
    return max(LOWER_YEAR, anchor - WINDOW_RADIUS), min(UPPER_YEAR, anchor + WINDOW_RADIUS)


def _cloud(item) -> float:
    value = item.properties.get("eo:cloud_cover")
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def summarize_items(items: list) -> dict:
    rows = []
    for item in items:
        dt = item.datetime
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


def query_catalog(client: Client, collection: str, lon: float, lat: float, start: int, end: int,
                  retries: int = 3) -> dict:
    last = None
    for attempt in range(retries):
        try:
            search = client.search(
                collections=[collection],
                intersects={"type": "Point", "coordinates": [float(lon), float(lat)]},
                datetime=f"{start}-01-01/{end}-12-31",
            )
            return summarize_items(list(search.items()))
        except Exception as exc:  # network/catalog errors are recorded, not silently passed
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
        "count", "abundance", "trend", "effective_component_number", "kappa", "delta_kappa", "p_value"
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


def audit(forcing_csv: Path, options_csv: Path) -> tuple[dict, pd.DataFrame]:
    units = build_units(forcing_csv, options_csv)
    client = Client.open(PC_STAC)
    cache: dict[tuple, dict] = {}
    out = []

    def q(collection, site, lon, lat, start, end):
        key = (collection, site, start, end)
        if key not in cache:
            cache[key] = query_catalog(client, collection, lon, lat, start, end)
        return cache[key]

    for _, r in units.iterrows():
        early = epoch_window(int(r.first_observed_season))
        late = epoch_window(int(r.last_observed_season))
        early_ls = q(LANDSAT, r.site_id, r.longitude, r.latitude, *early)
        late_ls = q(LANDSAT, r.site_id, r.longitude, r.latitude, *late)

        late_s2 = None
        s2_start = max(2016, late[0])
        if s2_start <= late[1]:
            late_s2 = q(SENTINEL, r.site_id, r.longitude, r.latitude, s2_start, late[1])

        early_mid = sum(early) / 2
        late_mid = sum(late) / 2
        sep = late_mid - early_mid
        primary = bool(
            early_ls.get("catalog_support")
            and late_ls.get("catalog_support")
            and sep >= MIN_SEPARATION
        )
        reason = []
        if not early_ls.get("catalog_support"):
            reason.append("early_landsat_catalog_support")
        if not late_ls.get("catalog_support"):
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

    result = {
        "schema_version": 1,
        "audit_id": "mina-antarctic-island-ecology-paper2-optical-catalog-v1",
        "status": "outcome_blind_scene_catalog_support",
        "planetary_computer_stac": PC_STAC,
        "collections": {"landsat": LANDSAT, "sentinel2": SENTINEL},
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
            "all_queries_error_free": bool(
                df[["early_query_error", "late_query_error", "sentinel_query_error"]]
                .fillna("").eq("").all().all()
            ),
            "pixel_qa_opened": False,
            "demographic_magnitudes_opened": False,
        },
        "interpretation_boundary": [
            "This is a scene-catalog support audit, not a habitat-change result.",
            "Scene-level cloud cover is not local clear-pixel fraction.",
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
