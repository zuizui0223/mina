#!/usr/bin/env python3
"""Outcome-blind breeding-option trait extraction from Antarctic Ecosystem Inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr
import rasterio
from pyproj import Transformer
from rasterio.windows import from_bounds

MAPPPDR_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"
PRIMARY_SPECIES = ("ADPE", "CHPE", "GEPE")
RADII_M = (500, 1000, 2000, 5000)
PRIMARY_RADIUS_M = 2000
EXPECTED_TIF_MD5 = "cde880d73f7f18b44aecf5690aa2dc92"
EXPECTED_DBF_MD5 = "fa5363b1c0d882b4343e239d03dc2ba4"


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rda(path: Path, expected: str) -> pd.DataFrame:
    result = pyreadr.read_r(str(path))
    if expected in result:
        frame = result[expected]
    elif len(result) == 1:
        frame = next(iter(result.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(result)}")
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(expected)
    return frame


def candidate_sites(root: Path) -> pd.DataFrame:
    sites = load_rda(root / "data" / "sites.rda", "sites")
    obs = load_rda(root / "data" / "penguin_obs.rda", "penguin_obs")

    nest = obs[
        obs["species_id"].isin(PRIMARY_SPECIES)
        & (obs["type"] == "nests")
        & obs["count"].notna()
    ].copy()
    nest["year"] = pd.to_numeric(nest["year"], errors="coerce")
    nest = nest.dropna(subset=["year"])

    units = []
    for (site_id, species_id), local in nest.groupby(["site_id", "species_id"]):
        years = sorted(set(int(y) for y in local["year"]))
        if len(years) >= 5 and max(years) - min(years) >= 10:
            units.append((str(site_id), str(species_id)))

    if len(units) != 152:
        raise ValueError(f"candidate unit drift: {len(units)} != 152")

    site_ids = sorted({site_id for site_id, _ in units})
    out = sites[sites["site_id"].isin(site_ids)].copy()
    if len(out) != 122:
        raise ValueError(f"candidate site drift: {len(out)} != 122")
    return out[["site_id", "site_name", "region", "ccamlr_id", "latitude", "longitude"]]


def shannon(values: np.ndarray) -> float:
    if values.size == 0:
        return float("nan")
    _, counts = np.unique(values, return_counts=True)
    p = counts / counts.sum()
    return float(-(p * np.log(p)).sum())


def extract_circle(src, x: float, y: float, radius: float) -> dict[str, float | int | None]:
    window = from_bounds(x - radius, y - radius, x + radius, y + radius, transform=src.transform)
    window = window.round_offsets().round_lengths()
    arr = src.read(1, window=window, masked=True, boundless=True)

    transform = src.window_transform(window)
    rows, cols = np.indices(arr.shape)
    xs = transform.c + (cols + 0.5) * transform.a + (rows + 0.5) * transform.b
    ys = transform.f + (cols + 0.5) * transform.d + (rows + 0.5) * transform.e
    circle = (xs - x) ** 2 + (ys - y) ** 2 <= radius ** 2

    total = int(circle.sum())
    if total == 0:
        return {
            "circle_pixel_count": 0,
            "mapped_ice_free_pixel_count": 0,
            "mapped_ice_free_area_ha": 0.0,
            "mapped_ice_free_fraction_of_circle": 0.0,
            "ecosystem_value_richness": 0,
            "ecosystem_value_shannon": None,
            "dominant_ecosystem_value_fraction": None,
        }

    valid = circle & (~np.ma.getmaskarray(arr))
    values = np.asarray(arr.data[valid])
    values = values[np.isfinite(values)]

    count = int(values.size)
    pixel_area_m2 = abs(float(src.transform.a * src.transform.e - src.transform.b * src.transform.d))
    area_ha = count * pixel_area_m2 / 10000.0
    fraction = count / total

    if count:
        unique, counts = np.unique(values, return_counts=True)
        richness = int(unique.size)
        dominant = float(counts.max() / counts.sum())
        entropy = shannon(values)
    else:
        richness = 0
        dominant = None
        entropy = None

    return {
        "circle_pixel_count": total,
        "mapped_ice_free_pixel_count": count,
        "mapped_ice_free_area_ha": float(area_ha),
        "mapped_ice_free_fraction_of_circle": float(fraction),
        "ecosystem_value_richness": richness,
        "ecosystem_value_shannon": entropy,
        "dominant_ecosystem_value_fraction": dominant,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir", required=True, type=Path)
    p.add_argument("--raster", required=True, type=Path)
    p.add_argument("--vat-dbf", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-csv", required=True, type=Path)
    a = p.parse_args()

    tif_md5 = md5(a.raster)
    dbf_md5 = md5(a.vat_dbf)
    if tif_md5 != EXPECTED_TIF_MD5:
        raise ValueError(f"raster md5 drift: {tif_md5}")
    if dbf_md5 != EXPECTED_DBF_MD5:
        raise ValueError(f"VAT md5 drift: {dbf_md5}")

    sites = candidate_sites(a.mapppdr_dir)
    records = []

    with rasterio.open(a.raster) as src:
        if src.crs is None:
            raise ValueError("ecosystem inventory raster has no CRS")
        transformer = Transformer.from_crs(4326, src.crs, always_xy=True)

        for row in sites.to_dict(orient="records"):
            x, y = transformer.transform(float(row["longitude"]), float(row["latitude"]))
            rec = {
                "site_id": str(row["site_id"]),
                "site_name": str(row["site_name"]),
                "region": str(row["region"]),
                "ccamlr_id": None if pd.isna(row["ccamlr_id"]) else str(row["ccamlr_id"]),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "x_raster_crs": float(x),
                "y_raster_crs": float(y),
            }
            for radius in RADII_M:
                metrics = extract_circle(src, x, y, radius)
                for key, value in metrics.items():
                    rec[f"{key}_{radius}m"] = value
            records.append(rec)

        raster_meta = {
            "crs": str(src.crs),
            "width": int(src.width),
            "height": int(src.height),
            "count": int(src.count),
            "dtype": str(src.dtypes[0]),
            "nodata": None if src.nodata is None else float(src.nodata),
            "resolution": [float(abs(src.transform.a)), float(abs(src.transform.e))],
            "bounds": [
                float(src.bounds.left),
                float(src.bounds.bottom),
                float(src.bounds.right),
                float(src.bounds.top),
            ],
        }

    frame = pd.DataFrame(records)
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(a.out_csv, index=False)

    coverage = {}
    for radius in RADII_M:
        col = f"mapped_ice_free_pixel_count_{radius}m"
        matched = int((frame[col] > 0).sum())
        coverage[str(radius)] = {
            "radius_m": radius,
            "sites_with_any_mapped_ice_free_pixel": matched,
            "coverage_fraction": matched / len(frame),
            "missing_site_ids": frame.loc[frame[col] <= 0, "site_id"].tolist(),
        }

    primary_coverage = coverage[str(PRIMARY_RADIUS_M)]["coverage_fraction"]
    result = {
        "schema_version": 1,
        "result_id": "mina-antarctic-breeding-options-atlas-gate1-result-v1",
        "mapppdr_commit": MAPPPDR_COMMIT,
        "candidate_site_species_units": 152,
        "distinct_candidate_sites": len(frame),
        "ecosystem_inventory": {
            "doi": "10.5281/zenodo.11629115",
            "raster_file": a.raster.name,
            "raster_md5": tif_md5,
            "vat_dbf_file": a.vat_dbf.name,
            "vat_dbf_md5": dbf_md5,
            "raster_metadata": raster_meta,
        },
        "radii_m": list(RADII_M),
        "primary_radius_m": PRIMARY_RADIUS_M,
        "coverage_by_radius": coverage,
        "gate_passed": bool(primary_coverage >= 0.90),
        "primary_radius_coverage_fraction": float(primary_coverage),
        "derived_csv": a.out_csv.name,
        "boundary": [
            "Valid raster cells are mapped ice-free ecosystem cells, not observed occupied nesting area.",
            "Raster-class richness and Shannon diversity are site-centered breeding-option proxies only.",
            "No penguin demographic outcome is used in this extraction."
        ],
    }
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result["gate_passed"]:
        raise SystemExit("Breeding-option Gate 1 failed frozen >=90% primary-radius coverage rule")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
