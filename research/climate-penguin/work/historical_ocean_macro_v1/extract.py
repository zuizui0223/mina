"""Source-pinned GLORYS12 (202311) 1993–2020 coastal ocean at macro colony sites within 25 km.
No weather or biological prediction. Preserve original 2011–2020 wet pixels and verify values.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fsspec
import numpy as np
import pandas as pd
import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "historical_ocean_macro_v1"
SOURCE = ROOT / "outputs"
EXPECTED_GIT_BLOBS = {
    "grid": ("climate_penguin/ocean_grid_support.csv", "5d0f90cab39e192645b3ff3406a40349a0ff22d0"),
    "paired": ("warming_species_breeding_v1/matched_species_breeding_change.csv", "f17b4a21e9e5a045a40f5a4af9019e3bbc011758"),
    "original": ("climate_penguin/ocean_monthly_2011_2021.csv", "cafa0e6f934ad5e3ae67ca0c6cd52d1e29156dd6"),
    "manifest": ("climate_penguin/ocean_monthly_manifest.json", "7d62ce17e77ae356ea62116d2446b0a8521c7ded"),
}
def pinned(name: str) -> Path:
    rel, expected = EXPECTED_GIT_BLOBS[name]
    path = SOURCE / rel
    data = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if actual != expected:
        raise ValueError(f"Git source SHA drift {name} {actual} != {expected}")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    grid = pd.read_csv(pinned("grid"))
    pairs = pd.read_csv(pinned("paired"))
    old = pd.read_csv(pinned("original"))
    metadata = json.loads(pinned("manifest").read_text(encoding="utf-8"))
    sites = sorted(pairs.loc[pairs.gate == 1, "site_id"].unique())
    if len(sites) != 8:
        raise ValueError("Paired 8-site source subset changed")
    original_macro = grid.loc[grid.cohort == "macro_40"].copy()
    if len(original_macro) != 40 or original_macro.site_id.nunique() != 40:
        raise ValueError("Original 40-site macro geography changed")
    focus = original_macro.loc[original_macro.grid_within_25km].sort_values("site_id").reset_index(drop=True)
    if len(focus) != 34 or not focus.grid_within_25km.all():
        raise ValueError("Source-defined 25-km wet marine-grid gate has changed")
    if not set(sites).issubset(set(focus.site_id)):
        raise ValueError("Lost original 8 species-comparison biological sites")
    n_site = len(focus)
    n_grid = focus[["grid_y", "grid_x"]].drop_duplicates().shape[0]
    store = metadata["store"]
    print(f"OPEN FIXED SOURCE {store}", flush=True)
    ds = xr.open_zarr(fsspec.get_mapper(store), consolidated=True)
    lat_idx = focus.grid_y.astype(int).to_numpy()
    lon_idx = focus.grid_x.astype(int).to_numpy()
    if not np.allclose(ds.latitude.values[lat_idx], focus.grid_lat.to_numpy(), atol=2e-4):
        raise ValueError("Native latitude grid has changed since previous source extraction")
    if not np.allclose(ds.longitude.values[lon_idx], focus.grid_lon.to_numpy(), atol=2e-4):
        raise ValueError("Native longitude grid has changed since previous source extraction")
    depth_idx = int(np.argmin(np.abs(ds.elevation.values)))
    if not np.isclose(float(ds.elevation.values[depth_idx]), metadata["top_level_coordinate_m"], atol=1e-5):
        raise ValueError("Selected sea-surface model depth is not the frozen value")
    times = pd.DatetimeIndex(ds.time.values)
    chosen = np.flatnonzero(
        (times.year >= 1993) & (times.year <= 2020) & np.isin(times.month, [8, 9, 10, 11])
    )
    if len(chosen) != (2020 - 1993 + 1) * 4:
        raise ValueError(f"Historical archive lacks expected 112 months: {len(chosen)}")
    lat_sel = xr.DataArray(lat_idx, dims="site")
    lon_sel = xr.DataArray(lon_idx, dims="site")
    time_sel = xr.DataArray(chosen, dims="target_month")
    arrays: dict[str, np.ndarray] = {}
    for var in ("so", "thetao"):  # do not trigger unnecessary reads of mixed layer depth
        data = ds[var].isel(
            elevation=depth_idx, time=time_sel, latitude=lat_sel, longitude=lon_sel
        ).load()
        if data.dims != ("target_month", "site"):
            data = data.transpose("target_month", "site")
        values = np.asarray(data.values, dtype=float)
        if values.shape != (112, n_site):
            raise ValueError(f"Wrong shape for {var}: {values.shape}")
        arrays[var] = values
        print(f"LOADED {var}: {values.shape}, valid={np.isfinite(values).sum()}", flush=True)
    records = []
    for ti, idx in enumerate(chosen):
        for i, site in focus.iterrows():
            records.append({
                "site_id": site.site_id, "location_id": site.location_id,
                "year": int(times[idx].year), "month": int(times[idx].month),
                "grid_y": int(site.grid_y), "grid_x": int(site.grid_x),
                "grid_distance_km": float(site.grid_distance_km),
                "surface_salinity": arrays["so"][ti, i],
                "surface_potential_temperature_c": arrays["thetao"][ti, i],
            })
    hist = pd.DataFrame(records)
    if len(hist) != n_site * 112 or hist.duplicated(["site_id", "year", "month"]).any():
        raise ValueError("Monthly site/time key duplication")
    q = hist.loc[hist.year.between(2011, 2020)].merge(
        old[["location_id", "year", "month", "surface_salinity", "surface_potential_temperature_c"]],
        on=["location_id", "year", "month"], validate="one_to_one", suffixes=("_new", "_frozen")
    )
    if len(q) != n_site * 4 * 10:
        raise ValueError(f"Frozen old-source overlap: expected {n_site * 40} values, got {len(q)}")
    diffs = {}
    for var in ("surface_salinity", "surface_potential_temperature_c"):
        left = q[f"{var}_new"].to_numpy(float)
        right = q[f"{var}_frozen"].to_numpy(float)
        if not np.array_equal(np.isfinite(left), np.isfinite(right)):
            raise ValueError(f"Source finite/missing mask changed: {var}")
        diff = float(np.max(np.abs(left[np.isfinite(left)] - right[np.isfinite(right)])))
        diffs[var] = diff
        if diff > 1e-5:
            raise ValueError(f"Source historical overlap changed: {var} max error {diff}")
    hist.to_csv(OUT / "original_glorys_34sites_1993_2020_monthly.csv", index=False)
    receipt = {
        "status": "historical_ocean_source_retrieved_and_old_2011_2020_values_verified",
        "source_store": store, "source_version": metadata["version"], "source_original_git_blobs": {
            name: sha for name, (_, sha) in EXPECTED_GIT_BLOBS.items()
        },
        "surface_depth_m": float(ds.elevation.values[depth_idx]),
        "months": 112, "sites": 8, "monthly_site_rows": len(hist),
        "unique_ocean_native_cells": n_grid,
        "start_year": 1993, "end_year": 2020, "frozen_overlap_rows": len(q),
        "max_abs_reanalysis_difference": diffs,
        "grid_max_distance_km": float(focus.grid_distance_km.max()),
        "derived_csv_sha256": hashlib.sha256((OUT / "original_glorys_8sites_1993_2020_monthly.csv").read_bytes()).hexdigest(),
        "interpretation": "This is a Copernicus model reanalysis (assimilation includes SIC and SST), not an independent satellite salinity observation.",
    }
    (OUT / "source_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("SOURCE AUDIT " + json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
