#!/usr/bin/env python3
"""Outcome-blind local-pixel QA pilot for dynamic Antarctic breeding opportunity."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import planetary_computer
import rasterio
import requests
from pyproj import Transformer
from rasterio.warp import Resampling, reproject, transform_bounds
from rasterio.windows import from_bounds

PC_STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
LANDSAT = "landsat-c2-l2"
AEI_MD5 = "cde880d73f7f18b44aecf5690aa2dc92"
RADIUS_M = 2000.0
AUSTRAL_MONTHS = {11, 12, 1, 2, 3}
SCENE_CLOUD_MAX = 80.0
MAX_SCENES_PER_EPOCH = 5
LOCAL_VALID_THRESHOLD = 0.50
MIN_SELECTED_SCENES = 3
MIN_GOOD_SCENES = 2
QUERY_TIMEOUT_SECONDS = 45
QUERY_RETRIES = 3

PILOT_SITE_IDS = (
    "ORNE", "PALA", "LOUB",
    "PENG", "BART", "UCHA",
    "ANNE", "DOWN", "ROYD",
    "FISH", "PEPO", "PGEO", "STNK",
    "BEAU",
)
MAJOR_REGION_EXPECTED = {
    "Central-west Antarctic Peninsula": 3,
    "South Shetland Islands": 3,
    "Victoria Land": 3,
}

# Collection 2 QA_PIXEL bits used across Landsat 4-9.
BIT_FILL = 0
BIT_DILATED_CLOUD = 1
BIT_CLOUD = 3
BIT_CLOUD_SHADOW = 4
BIT_SNOW = 5
BIT_WATER = 7


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _date(feature: dict) -> datetime:
    value = feature.get("properties", {}).get("datetime")
    if not value:
        raise ValueError(f"STAC item {feature.get('id')} lacks datetime")
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _cloud(feature: dict) -> float:
    value = feature.get("properties", {}).get("eo:cloud_cover")
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def query_features(lon: float, lat: float, start: int, end: int) -> list[dict]:
    payload = {
        "collections": [LANDSAT],
        "intersects": {"type": "Point", "coordinates": [float(lon), float(lat)]},
        "datetime": f"{int(start)}-01-01T00:00:00Z/{int(end)}-12-31T23:59:59Z",
        "limit": 1000,
    }
    last = None
    for attempt in range(QUERY_RETRIES):
        try:
            response = requests.post(
                f"{PC_STAC}/search",
                json=payload,
                timeout=QUERY_TIMEOUT_SECONDS,
                headers={"User-Agent": "mina-outcome-blind-pixel-qa/1.0"},
            )
            response.raise_for_status()
            return list(response.json().get("features", []))
        except Exception as exc:
            last = exc
            if attempt + 1 < QUERY_RETRIES:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"STAC query failed: {last!r}")


def select_scenes(features: list[dict], max_scenes: int = MAX_SCENES_PER_EPOCH) -> list[dict]:
    """One lowest-cloud scene per year, then evenly spaced years across the epoch."""
    by_year: dict[int, dict] = {}
    for f in features:
        dt = _date(f)
        cloud = _cloud(f)
        if dt.month not in AUSTRAL_MONTHS:
            continue
        if math.isnan(cloud) or cloud > SCENE_CLOUD_MAX:
            continue
        current = by_year.get(dt.year)
        rank = (cloud, dt.isoformat(), str(f.get("id", "")))
        if current is None:
            by_year[dt.year] = f
        else:
            cur_dt = _date(current)
            cur_rank = (_cloud(current), cur_dt.isoformat(), str(current.get("id", "")))
            if rank < cur_rank:
                by_year[dt.year] = f

    years = sorted(by_year)
    if len(years) <= max_scenes:
        picked_years = years
    else:
        idx = np.rint(np.linspace(0, len(years) - 1, max_scenes)).astype(int)
        picked_years = [years[int(i)] for i in idx]
        if len(set(picked_years)) != max_scenes:
            raise RuntimeError("scene-year quantile selection produced duplicate years")
    return [by_year[y] for y in picked_years]


def qa_flag(values: np.ndarray, bit: int) -> np.ndarray:
    return (values.astype(np.uint16) & np.uint16(1 << bit)) != 0


def aei_support(src, lon: float, lat: float, radius: float = RADIUS_M):
    transformer = Transformer.from_crs(4326, src.crs, always_xy=True)
    x, y = transformer.transform(float(lon), float(lat))
    window = from_bounds(x - radius, y - radius, x + radius, y + radius, transform=src.transform)
    window = window.round_offsets().round_lengths()
    arr = src.read(1, window=window, masked=True, boundless=True)
    transform = src.window_transform(window)

    rows, cols = np.indices(arr.shape)
    xs = transform.c + (cols + 0.5) * transform.a + (rows + 0.5) * transform.b
    ys = transform.f + (cols + 0.5) * transform.d + (rows + 0.5) * transform.e
    circle = (xs - x) ** 2 + (ys - y) ** 2 <= radius ** 2
    support = circle & (~np.ma.getmaskarray(arr))
    return support.astype(np.uint8), transform, src.crs


def inspect_scene(feature: dict, support_mask: np.ndarray, support_transform, support_crs) -> dict:
    qa_asset = feature.get("assets", {}).get("qa_pixel")
    if not qa_asset or not qa_asset.get("href"):
        raise ValueError(f"{feature.get('id')} lacks qa_pixel asset")
    href = planetary_computer.sign(qa_asset["href"])
    src_h, src_w = support_mask.shape
    left = support_transform.c
    top = support_transform.f
    right = left + src_w * support_transform.a + src_h * support_transform.b
    bottom = top + src_w * support_transform.d + src_h * support_transform.e
    bounds = (
        min(left, right), min(bottom, top),
        max(left, right), max(bottom, top)
    )

    env_opts = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "GDAL_HTTP_MULTIRANGE": "YES",
        "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
        "GDAL_HTTP_TIMEOUT": "30",
        "GDAL_HTTP_MAX_RETRY": "3",
    }
    with rasterio.Env(**env_opts):
        with rasterio.open(href) as qa:
            qb = transform_bounds(support_crs, qa.crs, *bounds, densify_pts=21)
            window = from_bounds(*qb, transform=qa.transform).round_offsets().round_lengths()
            values = qa.read(1, window=window, boundless=True, fill_value=np.uint16(1))
            qtransform = qa.window_transform(window)
            projected_support = np.zeros(values.shape, dtype=np.uint8)
            reproject(
                source=support_mask,
                destination=projected_support,
                src_transform=support_transform,
                src_crs=support_crs,
                dst_transform=qtransform,
                dst_crs=qa.crs,
                src_nodata=0,
                dst_nodata=0,
                resampling=Resampling.nearest,
            )

    support = projected_support == 1
    n_support = int(support.sum())
    if n_support <= 0:
        raise ValueError("AEI support did not overlap QA raster after reprojection")

    invalid = (
        qa_flag(values, BIT_FILL)
        | qa_flag(values, BIT_DILATED_CLOUD)
        | qa_flag(values, BIT_CLOUD)
        | qa_flag(values, BIT_CLOUD_SHADOW)
    )
    valid = support & (~invalid)
    n_valid = int(valid.sum())
    valid_fraction = n_valid / n_support

    if n_valid > 0:
        snow_fraction = float((valid & qa_flag(values, BIT_SNOW)).sum() / n_valid)
        water_fraction = float((valid & qa_flag(values, BIT_WATER)).sum() / n_valid)
    else:
        snow_fraction = None
        water_fraction = None

    dt = _date(feature)
    return {
        "item_id": str(feature.get("id")),
        "date": dt.date().isoformat(),
        "year": int(dt.year),
        "scene_cloud_percent": _cloud(feature),
        "aei_support_pixels_on_landsat_grid": n_support,
        "locally_valid_pixels": n_valid,
        "locally_valid_fraction": float(valid_fraction),
        "snow_fraction_among_valid": snow_fraction,
        "water_fraction_among_valid": water_fraction,
        "local_valid_ge_0_50": bool(valid_fraction >= LOCAL_VALID_THRESHOLD),
    }


def representative_units(optical: pd.DataFrame, options: pd.DataFrame) -> pd.DataFrame:
    static = options[[
        "site_id", "site_name", "mapped_ice_free_pixel_count_2000m"
    ]].drop_duplicates("site_id")
    x = optical.merge(static, on="site_id", how="left", validate="many_to_one")
    x = x[
        x["catalog_gate_pass"].astype(bool)
        & (pd.to_numeric(x["mapped_ice_free_pixel_count_2000m"], errors="coerce").fillna(0) > 0)
    ].copy()
    if len(x) != 103 or x["site_id"].nunique() != 84:
        raise ValueError(
            f"combined candidate roster drift: units={len(x)}, sites={x['site_id'].nunique()}"
        )
    x = x.sort_values(["site_id", "early_landsat_n_scenes_le80", "unit_id"])
    reps = x.groupby("site_id", as_index=False).first()
    pilot = reps[reps["site_id"].isin(PILOT_SITE_IDS)].copy()
    missing = sorted(set(PILOT_SITE_IDS) - set(pilot["site_id"]))
    if missing:
        raise ValueError(f"pilot sites missing from combined roster: {missing}")
    if len(pilot) != len(PILOT_SITE_IDS):
        raise ValueError(f"pilot physical-site count drift: {len(pilot)}")
    return pilot.sort_values("site_id").reset_index(drop=True)


def summarize_epoch(scene_rows: list[dict], selected_count: int) -> dict:
    successful = [r for r in scene_rows if not r.get("read_error")]
    vals = [r["locally_valid_fraction"] for r in successful]
    good = [v for v in vals if v >= LOCAL_VALID_THRESHOLD]
    return {
        "selected_distinct_year_scenes": int(selected_count),
        "successful_scene_reads": int(len(successful)),
        "median_locally_valid_fraction": float(np.median(vals)) if vals else None,
        "min_locally_valid_fraction": float(np.min(vals)) if vals else None,
        "max_locally_valid_fraction": float(np.max(vals)) if vals else None,
        "scenes_locally_valid_ge_0_50": int(len(good)),
        "pass": bool(
            selected_count >= MIN_SELECTED_SCENES
            and len(successful) >= MIN_SELECTED_SCENES
            and len(good) >= MIN_GOOD_SCENES
        ),
    }


def program_pass(site_frame: pd.DataFrame) -> tuple[bool, dict]:
    passed = int(site_frame["site_pass"].sum())
    beau = site_frame.loc[site_frame["site_id"] == "BEAU", "site_pass"]
    beau_pass = bool(len(beau) == 1 and bool(beau.iloc[0]))
    regional = {}
    regional_ok = True
    for region, expected in MAJOR_REGION_EXPECTED.items():
        g = site_frame[site_frame["region"] == region]
        # BEAU is an added control and is not part of the 3-site Victoria stress set.
        if region == "Victoria Land":
            g = g[g["site_id"] != "BEAU"]
        n_pass = int(g["site_pass"].sum())
        regional[region] = {"selected": int(len(g)), "expected_selected": expected, "pass": n_pass}
        if len(g) != expected or n_pass < 2:
            regional_ok = False
    ok = bool(passed >= 11 and beau_pass and regional_ok)
    return ok, {"passing_sites": passed, "beaufort_pass": beau_pass, "major_regions": regional}


def audit(optical_csv: Path, options_csv: Path, aei_raster: Path):
    if md5(aei_raster) != AEI_MD5:
        raise ValueError("AEI raster md5 drift")

    optical = pd.read_csv(optical_csv)
    options = pd.read_csv(options_csv)
    pilot = representative_units(optical, options)

    scene_records: list[dict] = []
    site_records: list[dict] = []

    with rasterio.open(aei_raster) as aei:
        for row in pilot.to_dict(orient="records"):
            support_mask, support_transform, support_crs = aei_support(
                aei, float(row["longitude"]), float(row["latitude"])
            )
            n_aei = int(support_mask.sum())
            if n_aei <= 0:
                raise ValueError(f"pilot site {row['site_id']} unexpectedly has no AEI support")

            epoch_results = {}
            for epoch in ("early", "late"):
                start = int(row[f"{epoch}_window_start"])
                end = int(row[f"{epoch}_window_end"])
                features = query_features(float(row["longitude"]), float(row["latitude"]), start, end)
                selected = select_scenes(features)
                local_rows = []
                for feature in selected:
                    base = {
                        "site_id": row["site_id"],
                        "site_name": row["site_name"],
                        "unit_id": row["unit_id"],
                        "species_id": row["species_id"],
                        "region": row["region"],
                        "epoch": epoch,
                        "epoch_start": start,
                        "epoch_end": end,
                        "aei_support_cells_100m": n_aei,
                    }
                    try:
                        rec = {**base, **inspect_scene(
                            feature, support_mask, support_transform, support_crs
                        ), "read_error": None}
                    except Exception as exc:
                        rec = {
                            **base,
                            "item_id": str(feature.get("id")),
                            "date": _date(feature).date().isoformat(),
                            "year": int(_date(feature).year),
                            "scene_cloud_percent": _cloud(feature),
                            "aei_support_pixels_on_landsat_grid": None,
                            "locally_valid_pixels": None,
                            "locally_valid_fraction": None,
                            "snow_fraction_among_valid": None,
                            "water_fraction_among_valid": None,
                            "local_valid_ge_0_50": False,
                            "read_error": repr(exc),
                        }
                    scene_records.append(rec)
                    local_rows.append(rec)
                epoch_results[epoch] = summarize_epoch(local_rows, len(selected))

            site_pass = bool(epoch_results["early"]["pass"] and epoch_results["late"]["pass"])
            site_records.append({
                "site_id": row["site_id"],
                "site_name": row["site_name"],
                "unit_id": row["unit_id"],
                "species_id": row["species_id"],
                "region": row["region"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "aei_support_cells_100m": n_aei,
                "early_window_start": int(row["early_window_start"]),
                "early_window_end": int(row["early_window_end"]),
                "late_window_start": int(row["late_window_start"]),
                "late_window_end": int(row["late_window_end"]),
                "early_selected_scenes": epoch_results["early"]["selected_distinct_year_scenes"],
                "early_successful_reads": epoch_results["early"]["successful_scene_reads"],
                "early_median_valid_fraction": epoch_results["early"]["median_locally_valid_fraction"],
                "early_good_scenes": epoch_results["early"]["scenes_locally_valid_ge_0_50"],
                "early_pass": epoch_results["early"]["pass"],
                "late_selected_scenes": epoch_results["late"]["selected_distinct_year_scenes"],
                "late_successful_reads": epoch_results["late"]["successful_scene_reads"],
                "late_median_valid_fraction": epoch_results["late"]["median_locally_valid_fraction"],
                "late_good_scenes": epoch_results["late"]["scenes_locally_valid_ge_0_50"],
                "late_pass": epoch_results["late"]["pass"],
                "site_pass": site_pass,
            })

    sites = pd.DataFrame(site_records)
    scenes = pd.DataFrame(scene_records)
    overall, detail = program_pass(sites)
    result = {
        "schema_version": 1,
        "result_id": "mina-antarctic-island-ecology-paper2d-pixel-qa-pilot-v1",
        "status": "outcome_blind_local_pixel_qa",
        "pilot_sites": list(PILOT_SITE_IDS),
        "n_pilot_sites": int(len(sites)),
        "qa_rule": {
            "radius_m": RADIUS_M,
            "scene_cloud_max_percent": SCENE_CLOUD_MAX,
            "max_distinct_year_scenes_per_epoch": MAX_SCENES_PER_EPOCH,
            "invalid_qa_pixel_bits": [BIT_FILL, BIT_DILATED_CLOUD, BIT_CLOUD, BIT_CLOUD_SHADOW],
            "diagnostic_bits": {"snow_ice": BIT_SNOW, "water": BIT_WATER},
            "local_valid_threshold": LOCAL_VALID_THRESHOLD,
            "minimum_selected_scenes": MIN_SELECTED_SCENES,
            "minimum_good_scenes": MIN_GOOD_SCENES,
        },
        "decision": {
            "pilot_passed": overall,
            **detail,
            "full_84_site_pixel_qa_authorized": bool(overall),
            "demographic_magnitudes_opened": False,
            "habitat_change_classifier_opened": False,
        },
        "read_errors": int(scenes["read_error"].notna().sum()) if len(scenes) else 0,
        "boundary": [
            "This pilot tests local observation support over the fixed AEI mask; it does not estimate habitat change.",
            "QA_PIXEL snow/ice flags are diagnostic only at this stage.",
            "No penguin count magnitude, trend, E, kappa or concentration outcome is read.",
        ],
    }
    return result, sites, scenes


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--optical-csv", required=True, type=Path)
    p.add_argument("--options-csv", required=True, type=Path)
    p.add_argument("--aei-raster", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-sites-csv", required=True, type=Path)
    p.add_argument("--out-scenes-csv", required=True, type=Path)
    a = p.parse_args()

    result, sites, scenes = audit(a.optical_csv, a.options_csv, a.aei_raster)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sites.to_csv(a.out_sites_csv, index=False)
    scenes.to_csv(a.out_scenes_csv, index=False)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["decision"]["pilot_passed"]:
        raise SystemExit("Pixel-QA pilot failed frozen gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
