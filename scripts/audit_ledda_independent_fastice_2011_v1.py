#!/usr/bin/env python3
"""Independent, fixed-site physical fast-ice audit. No penguin causal fitting.

Source: Fraser and Massom (2020), AADC fast-ice v2.2, doi:10.26179/5d267d1ceb60c.
Fixed target: Ledda Bay (Fretwell et al. 2021) -74.272, -131.243.
Original LaRue satellite observation: 2011-09-23, 'fast ice available', bp=no.
The 15-day composite may contain imagery acquired AFTER that source observation.
"""
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np

SOURCE_DOI = "10.26179/5d267d1ceb60c"
TARGET_DATE = date(2011, 9, 23)
LAT, LON = -74.272, -131.243
RADII_KM = (1, 3, 5)
ICE_CODES = {4, 5, 6}
CATEGORY = {"0": "PACK_OCEAN_OR_FILL_AMBIGUOUS", "1": "CONTINENT",
            "2": "ISLAND", "3": "ICE_SHELF", "4": "FAST_ICE_INTERIOR",
            "5": "FAST_ICE_MANUAL_EDGE", "6": "FAST_ICE_AUTO_EDGE"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_axis(values, axis):
    v = np.asarray(values, dtype=np.float64)
    if v.ndim != 1 or len(v) < 4 or not np.isfinite(v).all():
        raise ValueError(f"{axis}: expected finite 1D coordinate axis")
    diffs = np.diff(v)
    if not (np.all(diffs > 0) or np.all(diffs < 0)):
        raise ValueError(f"{axis}: non-monotonic projected grid")
    spacing = float(np.median(np.abs(diffs)))
    if not 700 <= spacing <= 1300:
        raise ValueError(f"{axis}: not a roughly 1 km grid: {spacing}")
    return spacing


def select_window(axis, projected, radius_m=5500):
    values = np.asarray(axis)
    ids = np.where(np.abs(values - projected) <= radius_m)[0]
    if len(ids) < 5:
        raise ValueError("Projected site lies off grid or window has too few pixels")
    return slice(int(ids.min()), int(ids.max()) + 1)


def summarize_pixels(codes, distance_m, radius_km):
    a = np.asarray(codes)
    d = np.asarray(distance_m)
    if a.shape != d.shape:
        raise ValueError("Spatial coordinate / pixel orientation mismatch")
    if not np.isfinite(a).all() or not np.all(np.equal(a, a.astype(int))):
        raise ValueError("Non-integer or NaN pixel code")
    values = set(int(x) for x in np.unique(a))
    if not values.issubset(set(range(7))):
        raise ValueError(f"Undocumented fast-ice classes: {values - set(range(7))}")
    local = a[d <= radius_km * 1000]
    if not len(local):
        raise ValueError("No grid pixels fall inside radius")
    counts = {str(k): int(np.count_nonzero(local == k)) for k in range(7)}
    return {
        "radius_km": radius_km,
        "pixel_total": len(local),
        "class_counts": counts,
        "fast_ice_4_5_6_pixels": sum(counts[str(k)] for k in ICE_CODES),
        "fast_ice_4_5_6_fraction_all_pixels": float(sum(counts[str(k)] for k in ICE_CODES) / len(local)),
        "ocean_or_pack_or_fill_0_is_not_verified_open_water": True,
    }


def bracket_dates(days, target):
    if days != sorted(days) or len(set(days)) != len(days):
        raise ValueError("Map timestamps must be unique chronological dates")
    before = [d.isoformat() for d in days if d <= target]
    after = [d.isoformat() for d in days if d > target]
    return {"latest_label_on_or_before_image": before[-1] if before else None,
            "first_label_after_image": after[0] if after else None,
            "time_bounds_known": False,
            "time_label_not_proof_of_strict_pre_observation_ice_exposure": True}


def decode_map(var, t_index, yi, xi):
    dims = list(var.dimensions)
    if len(dims) != 3 or set(dims) != {"x", "y", "time"}:
        raise ValueError(f"Unexpected data dimensions: {dims}")
    indexing = {"x": xi, "y": yi, "time": t_index}
    raw = np.asarray(var[tuple(indexing[d] for d in dims)])
    rest = [d for d in dims if d != "time"]
    return raw if rest == ["y", "x"] else raw.T


def build_result(nc_path):
    import netCDF4
    from pyproj import CRS, Transformer

    fp = Path(nc_path)
    if not fp.is_file() or fp.stat().st_size == 0:
        raise ValueError("Missing or empty original annual NetCDF")
    ps70 = CRS.from_proj4("+proj=stere +lat_0=-90 +lat_ts=-70 +lon_0=0 +datum=WGS84 +units=m +no_defs")
    project = Transformer.from_crs("EPSG:4326", ps70, always_xy=True)
    xp, yp = project.transform(LON, LAT)

    with netCDF4.Dataset(fp, "r") as nc:
        for required in ("x", "y", "time", "Fast_Ice_Time_series"):
            if required not in nc.variables:
                raise ValueError(f"Source NetCDF missing required {required}")
        x, y = np.asarray(nc.variables["x"][:]), np.asarray(nc.variables["y"][:])
        dx, dy = validate_axis(x, "x"), validate_axis(y, "y")
        if min(abs(x - xp)) > 2500 or min(abs(y - yp)) > 2500:
            raise ValueError("Fixed Ledda coordinate is not represented by projected grid")
        xi, yi = select_window(x, xp), select_window(y, yp)
        xx, yy = np.meshgrid(x[xi], y[yi])
        dist = np.hypot(xx - xp, yy - yp)

        tv = nc.variables["time"]
        if not hasattr(tv, "units"):
            raise ValueError("Missing time reference units")
        raw_times = tv[:]
        times = netCDF4.num2date(raw_times, units=tv.units,
                                 calendar=getattr(tv, "calendar", "standard"),
                                 only_use_cftime_datetimes=False)
        days = [date(int(t.year), int(t.month), int(t.day)) for t in times]
        if not days or not (min(days) <= TARGET_DATE <= max(days)):
            raise ValueError("2011 image date absent from annual 15-day series")
        bracketing = bracket_dates(days, TARGET_DATE)
        var = nc.variables["Fast_Ice_Time_series"]
        var.set_auto_maskandscale(False)
        entries = []
        for i, day in enumerate(days):
            grid = decode_map(var, i, yi, xi)
            entry = {"map_time_label": day.isoformat()}
            for radius in RADII_KM:
                entry[f"radius_{radius}km"] = summarize_pixels(grid, dist, radius)
            entries.append(entry)

    return {
        "source": "Fraser and Massom 2020 AADC v2.2 " + SOURCE_DOI,
        "source_file": fp.name,
        "source_size_bytes": fp.stat().st_size,
        "source_sha256": sha256_file(fp),
        "reference": "Fretwell et al. 2021 published rounded Ledda centroid",
        "site": "LEDD",
        "latitude": LAT,
        "longitude": LON,
        "image_date": TARGET_DATE.isoformat(),
        "image_author_label": "fast ice available / bird nondetection",
        "grid_transform": "WGS84 to PS70, x/y are NSIDC polar stereographic 70S coordinates",
        "projected_site_x_m": float(xp),
        "projected_site_y_m": float(yp),
        "grid_step_m": {"x": dx, "y": dy},
        "radii_km_frozen_before_raster_result": list(RADII_KM),
        "maps": entries,
        "map_count": len(entries),
        "map_bracketing": bracketing,
        "status": "INDEPENDENT_PHYSICAL_MAP_CONTEXT_ONLY_NOT_NEST_HABITABILITY",
        "season_long_breeding_ice_confirmed": False,
        "exact_nesting_footprint_confirmed": False,
        "same_date_pure_pre_exposure_confirmed": False,
        "penguin_recruitment_or_causal_social_effect_identified": False,
        "pr189_modified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="unmodified v2.2 FastIce_70_2011.nc")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    report = build_result(args.input)
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("LEDD_INDEPENDENT_FASTICE_PILOT_MAPS", report["map_count"])
    print("BRACKET", report["map_bracketing"])
    print("SOURCE_SHA256", report["source_sha256"])
    print("NO_BIOLOGICAL_CAUSAL_RESULT")


if __name__ == "__main__":
    main()
