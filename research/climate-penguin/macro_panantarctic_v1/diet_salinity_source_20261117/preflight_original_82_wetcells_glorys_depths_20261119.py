#!/usr/bin/env python3
"""Original 860-cohort 82-cell GLORYS depth availability WITHOUT testing isotope outcomes.

Contract:
MECHANISM_ABC_PREFLIGHT_FROZEN_CONTRACT_20261119_JA.md
Source model: frozen original GLORYS12V1 202311 Zarr, same indexed wet cell.
No nearest-deep-point substitution and no outcome-dependent depth selection.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

import fsspec
import numpy as np
import pandas as pd
import xarray as xr

SOURCE_SHA256 = "dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
SOURCE_CSV = "matched_860_original_isotope_ocean_ice_site_seasons.csv"
ZARR_URL = (
    "https://s3.waw3-1.cloudferro.com/mdl-arco-time-025/arco/"
    "GLOBAL_MULTIYEAR_PHY_001_030/"
    "cmems_mod_glo_phy_my_0.083deg_P1M-m_202311/timeChunked.zarr"
)
TARGET_DEPTHS_M = (0, 50, 200, 400)
MONTHS = (
    (1996, 7), (2003, 7), (2005, 7),
    (2010, 7), (2005, 12), (2006, 2),
)
MAIN_PROBE_MONTH = "2005-12"
PRIOR_REGIONS = (
    "Victoria Land",
    "Wilkes Land",
    "Southwest Antarctic Peninsula",
)
# Chosen by source physical completeness / independent geography, not isotope.
MIN_DEPTH_VALID = {"0m": 80, "50m": 70, "200m": 58}
MIN_200M_REGIONS = 8
MIN_200M_PER_TARGET_REGION = 3


def source_cohort(src):
    b = Path(src).read_bytes()
    hashv = hashlib.sha256(b).hexdigest()
    if hashv != SOURCE_SHA256:
        raise ValueError(f"Original 860 source archive SHA256 changed: {hashv}")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip() is not None:
            raise ValueError("Source 860 ZIP CRC failed")
        d = pd.read_csv(io.BytesIO(z.read(SOURCE_CSV)))
    required = {"site_id", "season", "source_region",
                "source_wet_grid_y", "source_wet_grid_x"}
    if not required.issubset(d.columns):
        raise ValueError(f"Required original geocoordinates absent: {required - set(d)}")
    if (len(d), d.site_id.nunique(), d.source_region.nunique()) != (860, 88, 13):
        raise ValueError("Original 860 cohort denominator drift")
    if d.duplicated(["site_id", "season"]).any():
        raise ValueError("Original cohort contains duplicated site×season")
    known_years = sorted(d.season.astype(int).unique())
    if known_years != [1996, *range(1999, 2013)]:
        raise ValueError(f"Original years changed: {known_years}")
    cells = (d[["source_wet_grid_y", "source_wet_grid_x"]]
             .drop_duplicates()
             .sort_values(["source_wet_grid_y", "source_wet_grid_x"])
             .reset_index(drop=True))
    if len(cells) != 82:
        raise ValueError(f"Expected 82 original ocean wet cells, found {len(cells)}")
    grouped = d[["source_region", "source_wet_grid_y",
                 "source_wet_grid_x"]].drop_duplicates()
    return d, cells, grouped, hashv


def select_levels(ds):
    for coord in ("time", "elevation", "latitude", "longitude"):
        if coord not in ds.coords:
            raise ValueError(f"Frozen GLORYS original coordinate missing: {coord}")
    for v in ("so", "thetao"):
        if v not in ds.data_vars:
            raise ValueError(f"Frozen GLORYS original variable missing: {v}")
    depths = np.asarray(ds.elevation.values, dtype=float)
    if np.any(~np.isfinite(depths)):
        raise ValueError("GLORYS vertical levels are non-finite")
    if not (np.min(np.abs(depths)) < 2 and np.nanmax(np.abs(depths)) >= 380):
        raise ValueError(f"GLORYS actual vertical range not usable: {depths[:8]}")
    idx = [int(np.argmin(abs(np.abs(depths) - x))) for x in TARGET_DEPTHS_M]
    actual = [float(abs(depths[i])) for i in idx]
    if len(set(idx)) < len(idx):
        raise ValueError(f"Depth probes collapsed into same model level: {actual}")
    if any(abs(a - x) > lim for a, x, lim in zip(actual, TARGET_DEPTHS_M,
                                                 [2, 15, 35, 60])):
        raise ValueError(f"Selected depth diverged from target: {actual}")
    return idx, actual


def source_month_index(ds):
    times = pd.DatetimeIndex(ds.time.values)
    lookup = {(int(x.year), int(x.month)): i for i, x in enumerate(times)}
    missing = [t for t in MONTHS if t not in lookup]
    if missing:
        raise ValueError(f"Source Zarr times missing: {missing}")
    return [lookup[x] for x in MONTHS]


def extract_probe(ds, cells, indexes, depth_idx, actual_depths):
    ys = cells.source_wet_grid_y.to_numpy(dtype=int)
    xs = cells.source_wet_grid_x.to_numpy(dtype=int)
    if np.any(ys < 0) or np.any(xs < 0):
        raise ValueError("Negative original wet-cell index")
    if np.max(ys) >= ds.sizes["latitude"] or np.max(xs) >= ds.sizes["longitude"]:
        raise ValueError("Original wet-cell grid indices out of bounds")
    coords = {
        "time": xr.DataArray(indexes, dims="source_month"),
        "latitude": xr.DataArray(ys, dims="wetcell"),
        "longitude": xr.DataArray(xs, dims="wetcell"),
        "elevation": xr.DataArray(depth_idx, dims="probe_depth"),
    }
    variables = {}
    for v in ("so", "thetao"):
        arr = ds[v].isel(**coords).transpose(
            "source_month", "wetcell", "probe_depth").load().values
        arr = np.asarray(arr, dtype=float)
        if arr.shape != (len(MONTHS), len(cells), len(TARGET_DEPTHS_M)):
            raise ValueError(f"GLORYS source returned unexpected {v} shape: {arr.shape}")
        variables[v] = arr
    valid = (
        np.isfinite(variables["so"])
        & np.isfinite(variables["thetao"])
        & (variables["so"] >= 20.0)
        & (variables["so"] <= 42.0)
        & (variables["thetao"] >= -4.0)
        & (variables["thetao"] <= 25.0)
    )
    rows = []
    for ti, (year, month) in enumerate(MONTHS):
        for ci, c in cells.iterrows():
            for di, target in enumerate(TARGET_DEPTHS_M):
                rows.append({
                    "calendar_month": f"{year:04d}-{month:02d}",
                    "source_wet_grid_y": int(c.source_wet_grid_y),
                    "source_wet_grid_x": int(c.source_wet_grid_x),
                    "probe_depth_name": f"{target}m",
                    "actual_model_level_m": actual_depths[di],
                    "native_so": float(variables["so"][ti, ci, di]),
                    "native_thetao": float(variables["thetao"][ti, ci, di]),
                    "physically_wet_valid": bool(valid[ti, ci, di]),
                })
    p = pd.DataFrame(rows)
    return p, valid


def receipt_from_probe(cohort, cells, regions, obs, actual_levels, archive_sha):
    m = obs.loc[obs.calendar_month.eq(MAIN_PROBE_MONTH)].copy()
    wet = m.pivot(
        index=["source_wet_grid_y", "source_wet_grid_x"],
        columns="probe_depth_name",
        values="physically_wet_valid"
    ).reset_index()
    counts = {x: int(wet[x].sum()) for x in
              [f"{k}m" for k in TARGET_DEPTHS_M]}
    geo = regions.merge(wet, on=["source_wet_grid_y",
                                 "source_wet_grid_x"],
                        how="left", validate="many_to_one")
    per_region = {}
    for region, g in geo.groupby("source_region", sort=True):
        per_region[str(region)] = {
            "source_unique_wetcells": int(len(g)),
            "source_wetcells_valid_50m": int(g["50m"].sum()),
            "source_wetcells_valid_200m": int(g["200m"].sum()),
            "source_wetcells_valid_400m": int(g["400m"].sum()),
        }
    valid_200_regions = int(sum(
        r["source_wetcells_valid_200m"] >= 1 for r in per_region.values()))
    checks = {
        "surface_80_of_82": counts["0m"] >= MIN_DEPTH_VALID["0m"],
        "50m_70_of_82": counts["50m"] >= MIN_DEPTH_VALID["50m"],
        "200m_58_of_82": counts["200m"] >= MIN_DEPTH_VALID["200m"],
        "200m_8_of_13_source_regions": valid_200_regions >= MIN_200M_REGIONS,
        "200m_3_cells_each_target_region": all(
            per_region.get(name, {}).get("source_wetcells_valid_200m", 0) >=
            MIN_200M_PER_TARGET_REGION for name in PRIOR_REGIONS),
    }
    coverage = (obs.groupby(["calendar_month", "probe_depth_name"],
                            as_index=False)
                .physically_wet_valid.sum())
    return {
        "status": ("PASS_FULL_ABC_DEPTH_SUPPORT_PREFLIGHT"
                   if all(checks.values())
                   else "NO_GO_FULL_ABC_EQUAL_SUPPORT"),
        "no_isotope_regression_executed": True,
        "source_is_satellite_reconstructed_d15n_not_direct_diet": True,
        "sample_is_physical_source_depth_coverage_only": True,
        "source_archive_sha256": archive_sha,
        "source_glorys_zarr": ZARR_URL,
        "original_rows": int(len(cohort)),
        "original_sites": int(cohort.site_id.nunique()),
        "original_regions": int(cohort.source_region.nunique()),
        "original_independent_ocean_wetcells": int(len(cells)),
        "actual_levels_m": dict(zip(
            [f"{v}m" for v in TARGET_DEPTHS_M], actual_levels)),
        "probe_months": [f"{y:04d}-{m:02d}" for y, m in MONTHS],
        "main_coverage_probe_month": MAIN_PROBE_MONTH,
        "valid_cells_by_depth_in_main_probe": counts,
        "valid_200m_original_regions_in_main_probe": valid_200_regions,
        "source_regions": per_region,
        "prespecified_checks": checks,
        "month_depth_coverage": coverage.to_dict("records"),
        "failed_gate_is_not_evidence_of_no_biological_mechanism": True,
        "no_change_to_frozen_main_or_original_positive_results": True,
    }


def main(a):
    cohort, cells, regionmap, h = source_cohort(a.original_isotope_zip)
    ds = xr.open_zarr(fsspec.get_mapper(ZARR_URL), consolidated=True)
    depth_idx, depth_real = select_levels(ds)
    ti = source_month_index(ds)
    result, wet = extract_probe(ds, cells, ti, depth_idx, depth_real)
    receipt = receipt_from_probe(cohort, cells, regionmap, result, depth_real, h)
    a.out.mkdir(parents=True, exist_ok=True)
    result.to_csv(a.out / "original_82_wetcells_6months_4depths_GLORYS_source.csv",
                  index=False)
    (a.out / "original_82_wetcells_glorys_depth_source_verdict.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    # A scientifically meaningful insufficient-depth source gate is a SUCCESSFUL
    # observational feasibility test, not a broken data retrieval.
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-isotope-zip", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    main(args)
