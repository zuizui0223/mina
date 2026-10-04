#!/usr/bin/env python3
"""Outcome-blind recovery of the frozen summer-exposure metric at Beaufort Island."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import planetary_computer
import rasterio
import requests
from pyproj import Transformer
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject
from rasterio.windows import from_bounds

PC_STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION = "landsat-c2-l2"
AEI_MD5 = "cde880d73f7f18b44aecf5690aa2dc92"
SITE_ID = "BEAU"
CRS = "EPSG:3031"
RES_M = 30.0
RADIUS_M = 2000.0
MIN_VALID_OBS = 2
PRIMARY_THRESHOLD = 0.50
SENSITIVITY_THRESHOLD = 0.67

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


def qa_flag(values: np.ndarray, bit: int) -> np.ndarray:
    return (values.astype(np.uint16) & np.uint16(1 << bit)) != 0


def grid_for_site(lon: float, lat: float):
    tx = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)
    x, y = tx.transform(float(lon), float(lat))
    n = int(math.ceil((2.0 * RADIUS_M) / RES_M))
    side = n * RES_M
    left = x - side / 2.0
    top = y + side / 2.0
    transform = from_origin(left, top, RES_M, RES_M)
    rows, cols = np.indices((n, n))
    xs = left + (cols + 0.5) * RES_M
    ys = top - (rows + 0.5) * RES_M
    circle = ((xs - x) ** 2 + (ys - y) ** 2) <= RADIUS_M ** 2
    return transform, (n, n), circle


def project_aei_support(aei, transform, shape, circle) -> np.ndarray:
    left = transform.c
    top = transform.f
    right = left + shape[1] * transform.a
    bottom = top + shape[0] * transform.e
    pad = 200.0
    window = from_bounds(
        min(left, right) - pad,
        min(bottom, top) - pad,
        max(left, right) + pad,
        max(bottom, top) + pad,
        transform=aei.transform,
    ).round_offsets().round_lengths()
    arr = aei.read(1, window=window, masked=True, boundless=True)
    src_support = (~np.ma.getmaskarray(arr)).astype(np.uint8)
    src_transform = aei.window_transform(window)
    dest = np.zeros(shape, dtype=np.uint8)
    reproject(
        source=src_support,
        destination=dest,
        src_transform=src_transform,
        src_crs=aei.crs,
        dst_transform=transform,
        dst_crs=CRS,
        src_nodata=0,
        dst_nodata=0,
        resampling=Resampling.nearest,
    )
    return (dest == 1) & circle


def fetch_item(item_id: str) -> dict:
    url = f"{PC_STAC}/collections/{COLLECTION}/items/{item_id}"
    last = None
    for attempt in range(4):
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": "mina-paper2d-exposure-recovery/1.0"})
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last = exc
            if attempt < 3:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to fetch STAC item {item_id}: {last!r}")


def read_qa_to_grid(item: dict, transform, shape) -> np.ndarray:
    asset = item.get("assets", {}).get("qa_pixel")
    if not asset or not asset.get("href"):
        raise ValueError(f"{item.get('id')} lacks qa_pixel")
    href = planetary_computer.sign(asset["href"])
    left = transform.c
    top = transform.f
    right = left + shape[1] * transform.a
    bottom = top + shape[0] * transform.e
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        GDAL_HTTP_MULTIRANGE="YES",
        GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
        GDAL_HTTP_TIMEOUT="30",
        GDAL_HTTP_MAX_RETRY="3",
    ):
        with rasterio.open(href) as src:
            # Reading the full remote raster is avoided; reproject only the target bounds.
            from rasterio.warp import transform_bounds
            qb = transform_bounds(CRS, src.crs, min(left,right), min(bottom,top), max(left,right), max(bottom,top), densify_pts=21)
            window = from_bounds(*qb, transform=src.transform).round_offsets().round_lengths()
            values = src.read(1, window=window, boundless=True, fill_value=np.uint16(1))
            src_transform = src.window_transform(window)
            dest = np.ones(shape, dtype=np.uint16)
            reproject(
                source=values,
                destination=dest,
                src_transform=src_transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=CRS,
                src_nodata=None,
                dst_nodata=np.uint16(1),
                resampling=Resampling.nearest,
            )
    return dest


def accumulate(scene_rows: pd.DataFrame, support: np.ndarray, transform, shape):
    valid_count = np.zeros(shape, dtype=np.uint16)
    exposed_count = np.zeros(shape, dtype=np.uint16)
    diagnostics = []
    for row in scene_rows.sort_values(["date", "item_id"]).itertuples(index=False):
        item = fetch_item(str(row.item_id))
        values = read_qa_to_grid(item, transform, shape)
        invalid = (
            qa_flag(values, BIT_FILL)
            | qa_flag(values, BIT_DILATED_CLOUD)
            | qa_flag(values, BIT_CLOUD)
            | qa_flag(values, BIT_CLOUD_SHADOW)
        )
        valid = support & (~invalid)
        exposed = valid & (~qa_flag(values, BIT_SNOW)) & (~qa_flag(values, BIT_WATER))
        valid_count += valid.astype(np.uint16)
        exposed_count += exposed.astype(np.uint16)
        diagnostics.append({
            "epoch": str(row.epoch),
            "item_id": str(row.item_id),
            "date": str(row.date),
            "valid_support_cells": int(valid.sum()),
            "exposed_support_cells": int(exposed.sum()),
        })
    return valid_count, exposed_count, diagnostics


def fraction_at_threshold(valid_count, exposed_count, paired, threshold: float) -> float:
    freq = np.divide(
        exposed_count.astype(float),
        valid_count,
        out=np.full(valid_count.shape, np.nan, dtype=float),
        where=valid_count > 0,
    )
    state = paired & (freq >= threshold)
    return float(state.sum() / paired.sum())


def run(sites_csv: Path, scenes_csv: Path, aei_raster: Path) -> dict:
    if md5(aei_raster) != AEI_MD5:
        raise ValueError("AEI raster md5 drift")
    sites = pd.read_csv(sites_csv)
    scenes = pd.read_csv(scenes_csv)
    site = sites[sites["site_id"].astype(str) == SITE_ID]
    if len(site) != 1:
        raise ValueError(f"expected one Beaufort site row, got {len(site)}")
    site = site.iloc[0]
    if not bool(site["site_pass"]):
        raise ValueError("Beaufort did not pass frozen full pixel QA")
    local = scenes[scenes["site_id"].astype(str) == SITE_ID].copy()
    if set(local["epoch"].astype(str)) != {"early", "late"}:
        raise ValueError("Beaufort frozen scene roster lacks one epoch")

    transform, shape, circle = grid_for_site(site["longitude"], site["latitude"])
    with rasterio.open(aei_raster) as aei:
        support = project_aei_support(aei, transform, shape, circle)
    if int(support.sum()) <= 0:
        raise ValueError("Beaufort has no projected AEI support")

    epoch_arrays = {}
    diagnostics = []
    for epoch in ("early", "late"):
        rows = local[local["epoch"].astype(str) == epoch]
        valid, exposed, diag = accumulate(rows, support, transform, shape)
        epoch_arrays[epoch] = (valid, exposed)
        diagnostics.extend(diag)

    early_valid, early_exposed = epoch_arrays["early"]
    late_valid, late_exposed = epoch_arrays["late"]
    paired = support & (early_valid >= MIN_VALID_OBS) & (late_valid >= MIN_VALID_OBS)
    n_paired = int(paired.sum())
    if n_paired <= 0:
        raise ValueError("no paired observable support cells")

    primary = {}
    for threshold in (PRIMARY_THRESHOLD, SENSITIVITY_THRESHOLD):
        ef = fraction_at_threshold(early_valid, early_exposed, paired, threshold)
        lf = fraction_at_threshold(late_valid, late_exposed, paired, threshold)
        primary[str(threshold)] = {
            "early_fraction": ef,
            "late_fraction": lf,
            "delta_late_minus_early": lf - ef,
        }

    def any_fraction(valid, exposed):
        state = paired & (valid > 0) & (exposed > 0)
        return float(state.sum() / paired.sum())

    early_any = any_fraction(early_valid, early_exposed)
    late_any = any_fraction(late_valid, late_exposed)
    result = {
        "schema_version": 1,
        "result_id": "mina-paper2d-summer-exposure-beaufort-recovery-v1",
        "site_id": SITE_ID,
        "site_name": str(site["site_name"]),
        "grid": {
            "crs": CRS,
            "resolution_m": RES_M,
            "radius_m": RADIUS_M,
            "aei_support_cells": int(support.sum()),
            "paired_observable_cells": n_paired,
            "paired_observable_area_ha": n_paired * RES_M * RES_M / 10000.0,
        },
        "epochs": {
            "early": [int(site["early_window_start"]), int(site["early_window_end"])],
            "late": [int(site["late_window_start"]), int(site["late_window_end"])],
            "early_scene_count": int((local["epoch"].astype(str) == "early").sum()),
            "late_scene_count": int((local["epoch"].astype(str) == "late").sum()),
        },
        "persistent_exposure": primary,
        "any_exposed_diagnostic": {
            "early_fraction": early_any,
            "late_fraction": late_any,
            "delta_late_minus_early": late_any - early_any,
        },
        "decision": {
            "positive_control_passed": bool(primary[str(PRIMARY_THRESHOLD)]["delta_late_minus_early"] > 0),
            "full_roster_measurement_authorized": bool(primary[str(PRIMARY_THRESHOLD)]["delta_late_minus_early"] > 0),
            "demographic_magnitudes_opened": False,
        },
        "scene_diagnostics": diagnostics,
        "boundary": [
            "This is an outcome-blind measurement-recovery control, not a penguin demographic result.",
            "The metric is persistent summer exposure within fixed current AEI support, not literal colony area.",
            "Thresholds and scenes are frozen independently of Beaufort direction.",
        ],
    }
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sites-csv", required=True, type=Path)
    p.add_argument("--scenes-csv", required=True, type=Path)
    p.add_argument("--aei-raster", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()
    result = run(a.sites_csv, a.scenes_csv, a.aei_raster)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["decision"]["positive_control_passed"]:
        raise SystemExit("Beaufort positive-direction recovery failed frozen primary metric")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
