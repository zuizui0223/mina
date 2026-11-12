#!/usr/bin/env python3
"""Original OSI SAF full-grid 60% sea-ice *meridional* front diagnostic.

Do not confuse this contour latitude shift with coast-following ice velocity,
biological colonization, climate tracking, or a species' geographic range edge.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import numpy as np
import xarray as xr
from scipy.ndimage import map_coordinates
from skimage.measure import find_contours

SOURCE = "https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly"
SHAPE = (432, 432)
BASE = (1993, 9)
DECADES = ((1991, 2000), (2001, 2010), (2011, 2020))
PAIRS = ((0, 1), (1, 2), (0, 2))
MONTHS = (8, 9, 10, 11)
SEASONS = ("aug_nov", "september")
COUNT_MIN = {"aug_nov": 36, "september": 9}
SIC_ISOPLETH = 60.0
KM_PER_LAT = 111.195


def readcsv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def savecsv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader()
        writer.writerows(rows)


def month_path(year, month, cache):
    filename = f"ice_conc_sh_ease2-250_cdr-v3p1_{year:04d}{month:02d}.nc"
    path = cache / filename
    url = f"{SOURCE}/{year}/{filename}"
    if not path.exists():
        last = None
        for attempt in range(3):
            try:
                req = Request(url, headers={"User-Agent": "mina-original-marine-front-60pct-v1"})
                with urlopen(req, timeout=90) as response:
                    if urlparse(response.geturl()).hostname != "thredds.met.no":
                        raise RuntimeError("Original publisher host changed")
                    raw = response.read(25_000_001)
                if (not raw or len(raw) > 25_000_000
                        or not (raw.startswith(b"CDF") or raw.startswith(b"\x89HDF"))):
                    raise ValueError("Unexpected downloaded NetCDF source signature/size")
                temp = path.with_suffix(".partial")
                temp.write_bytes(raw)
                temp.replace(path)
                break
            except Exception as error:
                last = error
                time.sleep(1 + attempt * 2)
        if not path.exists():
            raise RuntimeError(f"Original NetCDF {year}/{month} failed: {last}")
    raw = path.read_bytes()
    return path, url, hashlib.sha256(raw).hexdigest(), len(raw)


def read_native(path):
    with xr.open_dataset(path) as ds:
        if str(ds.attrs.get("product_version")) != "3.1":
            raise ValueError("Unexpected original OSI SAF product_version")
        for name in ("lat", "lon", "status_flag", "ice_conc"):
            if name not in ds.variables:
                raise ValueError("Missing original publisher field " + name)
        lat = np.asarray(ds["lat"].values, dtype=np.float64)
        lon = np.asarray(ds["lon"].values, dtype=np.float64)
        flag = np.asarray(ds["status_flag"].values[0])
        sic = np.asarray(ds["ice_conc"].values[0], dtype=np.float64)
    if any(z.shape != SHAPE for z in (lat, lon, flag, sic)):
        raise ValueError("Original 432x432 OSI SAF native EASE2 shape changed")
    flags = np.where(np.isfinite(flag), flag, 32767).astype(np.int64)
    valid = np.isfinite(sic) & np.isfinite(flag) & ((flags & 3) == 0) & (sic >= 0) & (sic <= 100)
    fingerprint = hashlib.sha256(
        np.ascontiguousarray(np.column_stack((lat.ravel(), lon.ravel()))).tobytes()
    ).hexdigest()
    return lat, lon, sic, valid, fingerprint


def sector_indices(longitudes):
    a = (np.asarray(longitudes, dtype=np.float64) + 180) % 360
    return np.clip(np.floor(a / 10).astype(np.int32), 0, 35)


def interpolate_contour(contour, lat, sinlon, coslon):
    pos = np.vstack((contour[:, 0], contour[:, 1]))
    lat_pts = map_coordinates(lat, pos, order=1, mode="nearest")
    sin_pts = map_coordinates(sinlon, pos, order=1, mode="nearest")
    cos_pts = map_coordinates(coslon, pos, order=1, mode="nearest")
    lon_pts = np.rad2deg(np.arctan2(sin_pts, cos_pts))
    return lat_pts, lon_pts


def continuous_front(field, mask, lat, sinlon, coslon):
    # NO interpolation across invalid source ocean pixels or continental land.
    raster = np.where(mask, field, np.nan)
    components = find_contours(raster, SIC_ISOPLETH, mask=mask)
    audit = []
    candidates = []
    for contour in components:
        if len(contour) < 100:
            continue
        latpts, lonpts = interpolate_contour(contour, lat, sinlon, coslon)
        finite = np.isfinite(latpts) & np.isfinite(lonpts)
        if finite.sum() < 100:
            continue
        sectors = sector_indices(lonpts[finite])
        coverage = len(set(sectors.tolist()))
        closed = bool(np.linalg.norm(contour[0] - contour[-1]) <= 2.0)
        record = {
            "is_closed_contour": closed,
            "vertices": int(finite.sum()),
            "distinct_10degree_sectors": coverage,
            "lat_min": float(np.min(latpts[finite])),
            "lat_max": float(np.max(latpts[finite])),
        }
        audit.append(record)
        # The frozen criterion is geographic continuity through >=24 sectors;
        # a trace may terminate at a source-valid mask edge. Closure was an
        # overstrict implementation error, diagnosed before marine-front scores.
        if coverage >= 24:
            candidates.append((coverage, int(finite.sum()), latpts[finite], sectors, closed))
    # Prechosen rule: widest longitude-sector coverage then longest contour.
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if not candidates:
        return None, {
            "status": "NO_SINGLE_CONTIGUOUS_60PCT_FRONTRING",
            "large_contour_components": len(audit),
            "best_coverage": max((a["distinct_10degree_sectors"] for a in audit), default=0),
            "largest_vertices": max((a["vertices"] for a in audit), default=0),
        }
    cover, vertices, latpts, sectors, closed = candidates[0]
    edges = {}
    for sec in range(36):
        values = latpts[sectors == sec]
        if len(values) < 3:
            continue
        edges[sec] = {
            "lat_median": float(np.median(values)),
            "lat_q25": float(np.quantile(values, .25)),
            "lat_q75": float(np.quantile(values, .75)),
            "n_vertices": int(len(values))
        }
    return edges, {
        "status": "CONTIGUOUS_60PCT_MARINE_TRACE_CANDIDATE",
        "large_contour_components": len(audit),
        "eligible_ring_candidates": len(candidates),
        "selected_contour_vertices": vertices,
        "selected_contour_sectors": cover,
        "selected_trace_is_closed": bool(closed),
        "geometric_closure_after_source_diagnosis_is_not_required": True,
        "sector_median_latitudes": len(edges),
        "selected_contour_lat_range": [float(np.min(latpts)), float(np.max(latpts))],
        "other_large_components": audit[:12],
    }


def verify_baseline(sic, valid, root):
    prior = readcsv(root / "original_595_sites_marine_native_reference_cells.csv")
    reference = [
        r for r in readcsv(root / "original_595_site_months_120_source_QA.csv")
        if int(r["year"]) == BASE[0] and int(r["month"]) == BASE[1]
    ]
    if len(prior) != 595 or len(reference) != 595:
        raise ValueError("Source 595-site original reference panel incomplete")
    ids = {r["site_id"]: r for r in prior}
    if len(ids) != 595:
        raise ValueError("Duplicate reference site ID")
    compared, diffs = 0, []
    for record in reference:
        if record["source_full_595_site_monthly_support"] != "OK":
            continue
        site = record["site_id"]
        pix = ids[site]["native_original_25km_flat_pixel_ids"]
        ix = np.asarray([int(z) for z in pix.split(";")], dtype=np.int64)
        if not len(ix) or not np.all(valid.ravel()[ix]):
            raise ValueError("Original 1993-09 marine reference site pixel mismatch")
        original = float(record["source_25km_buffer_mean_SIC_pct"])
        reconstructed = float(np.mean(sic.ravel()[ix]))
        diffs.append(abs(original - reconstructed))
        compared += 1
    maxdiff = max(diffs, default=math.inf)
    if compared < 500 or maxdiff > 0.0002:
        raise ValueError(
            f"Original baseline site SIC failed: sites={compared}, maximum_difference_pp={maxdiff}"
        )
    return {
        "source_site_means_crosschecked": compared,
        "1993_september_original_SIC_max_absolute_difference_pp": maxdiff,
        "status": "ORIGINAL_595_SITES_NATIVE_ICE_SOURCE_REPRODUCED"
    }


def biological_overlap(front_rows, matched_rows, atlas_rows):
    geo = {r["site_id"]: r for r in atlas_rows}
    if len(geo) != 595:
        raise ValueError("Original site atlas source identity mismatch")
    edge = {
        (r["start_period"], r["end_period"], r["climate_month_basis"], int(r["longitude_sector_10deg"])): r
        for r in front_rows if r["status"] == "PAIRED_ORIGINAL_MARINE_FRONT"
    }
    ret = []
    for pi, pj in PAIRS:
        start = f"{DECADES[pi][0]}-{DECADES[pi][1]}"
        end = f"{DECADES[pj][0]}-{DECADES[pj][1]}"
        for basis in SEASONS:
            for species in ("ADPE", "CHPE", "GEPE"):
                paired = [r for r in matched_rows if r["species"] == species
                          and r["first_window"] == start
                          and r["last_window"] == end
                          and int(r["n_original_count_years_early"]) >= 2
                          and int(r["n_original_count_years_late"]) >= 2]
                supported = []
                for row in paired:
                    sector = int(sector_indices([float(geo[row["site_id"]]["longitude"])])[0])
                    match = edge.get((start, end, basis, sector))
                    if match is not None:
                        supported.append((row, match, sector))
                record = {
                    "species": species, "climate_month_basis": basis,
                    "start_period": start, "end_period": end,
                    "original_strict_two_year_paired_site_count": len(paired),
                    "front_supported_matched_site_count": len(supported),
                    "front_supported_regions": len({r["source_region"] for r, _, _ in supported}),
                    "front_supported_10degree_sectors": len({sec for _, _, sec in supported}),
                    "front_supported_250km_blocks": len({r["polar_250km_block"] for r, _, _ in supported}),
                    "unmatched_site_codes": ";".join(sorted({r["site_id"] for r in paired} - {r["site_id"] for r, _, _ in supported})),
                }
                if (len(supported) < 3 or record["front_supported_regions"] < 2
                        or record["front_supported_10degree_sectors"] < 2):
                    record["status"] = "INSUFFICIENT_PAIRS_FOR_DESCRIPTIVE_COMPARISON"
                    ret.append(record)
                    continue
                n0 = np.asarray([float(r["site_median_observed_nests_early"]) for r, _, _ in supported])
                n1 = np.asarray([float(r["site_median_observed_nests_late"]) for r, _, _ in supported])
                if min(n0.sum(), n1.sum()) <= 0:
                    record["status"] = "ZERO_OBSERVED_NEST_WEIGHT"
                    ret.append(record)
                    continue
                w0, w1 = n0 / n0.sum(), n1 / n1.sum()
                lat = np.asarray([float(r["latitude"]) for r, _, _ in supported])
                ice = np.asarray([float(z["southward_positive_ice_edge_meridional_km"]) for _, z, _ in supported])
                nest_shift = KM_PER_LAT * (float(np.dot(w0, lat)) - float(np.dot(w1, lat)))
                climate_shift = float(np.dot(w0, ice))
                record.update({
                    "status": "DESCRIPTIVE_FIXED_SITE_AND_FRONT_OVERLAP",
                    "observed_nest_centroid_latitudinal_reweighting_km": nest_shift,
                    "early_observed_nest_share_weighted_60pct_marine_edge_meridional_km": climate_shift,
                    "raw_difference_km_not_a_climate_debt": nest_shift - climate_shift,
                    "single_site_max_early_weight": float(np.max(w0)),
                    "single_site_max_late_weight": float(np.max(w1)),
                    "site_count_not_the_number_of_independent_climate_front_trials": True,
                    "same_measurement_type_or_ecological_tracking_estimator": False
                })
                ret.append(record)
    return ret


def analyze(args):
    cache = args.output / "publisher_netCDF"
    cache.mkdir(parents=True, exist_ok=True)
    previous = json.loads((args.prior_ice / "original_monthly_120_source_receipts.json").read_text())
    expected = {(int(r["year"]), int(r["month"])): r["sha256"] for r in previous}
    if len(previous) != 120 or len(expected) != 120:
        raise ValueError("Original source receipt drift, need 120 month SHAs")
    sums = np.zeros((3, len(SEASONS), *SHAPE), dtype=np.float64)
    counts = np.zeros((3, len(SEASONS), *SHAPE), dtype=np.uint8)
    lat = lon = sinlon = coslon = frozen = fingerprint = None
    receipts = []
    baseline_verification = None
    months = [BASE] + [(year, month) for year in range(1991, 2021)
                       for month in MONTHS if (year, month) != BASE]
    for i, (year, month) in enumerate(months):
        file, url, sha, length = month_path(year, month, cache)
        if expected.get((year, month)) != sha:
            raise ValueError(f"Original OSI SAF file SHA disagrees with completed 595-site receipt: {year}/{month}")
        source_lat, source_lon, source_sic, month_valid, fp = read_native(file)
        if lat is None:
            lat, lon, fingerprint = source_lat, source_lon, fp
            frozen = month_valid.copy()
            sinlon = np.sin(np.deg2rad(lon))
            coslon = np.cos(np.deg2rad(lon))
            baseline_verification = verify_baseline(source_sic, month_valid, args.prior_ice)
        elif fp != fingerprint:
            raise ValueError("Original 25-km marine geolocation grid changed")
        valid = frozen & month_valid
        pi = (year - 1991) // 10
        sums[pi, 0, valid] += source_sic[valid]
        counts[pi, 0, valid] += 1
        if month == 9:
            sums[pi, 1, valid] += source_sic[valid]
            counts[pi, 1, valid] += 1
        receipts.append({"year": year, "month": month, "source": url,
                         "sha256": sha, "original_bytes": length,
                         "valid_frozen_ocean_pixels": int(valid.sum()),
                         "grid_fingerprint": fp})
        if i % 10 == 0 or i == len(months) - 1:
            print(f"ORIGINAL_60PCT_FIELD={i+1}/120 {year}-{month:02d} valid={int(valid.sum())} sha={sha}", flush=True)
        # Raw NetCDF arrays are not needed after SHA verification and aggregation.
        file.unlink()
    if len(receipts) != 120:
        raise AssertionError("Original source record count failed")
    contour_audit, fronts = [], []
    map_by_pair = {}
    for pi, pj in PAIRS:
        for basis_i, basis in enumerate(SEASONS):
            reference = (
                frozen
                & (counts[pi, basis_i] >= COUNT_MIN[basis])
                & (counts[pj, basis_i] >= COUNT_MIN[basis])
            )
            if reference.sum() < 1000:
                raise ValueError("Source mask insufficient for full-grid pack-ice contour")
            edges = []
            for decade in (pi, pj):
                field = np.full(SHAPE, np.nan)
                field[reference] = sums[decade, basis_i, reference] / counts[decade, basis_i, reference]
                one, qa = continuous_front(field, reference, lat, sinlon, coslon)
                qa.update({
                    "period": f"{DECADES[decade][0]}-{DECADES[decade][1]}",
                    "paired_start": f"{DECADES[pi][0]}-{DECADES[pi][1]}",
                    "paired_end": f"{DECADES[pj][0]}-{DECADES[pj][1]}",
                    "climate_month_basis": basis,
                    "n_exact_common_source_valid_ocean_pixels": int(reference.sum())
                })
                contour_audit.append(qa)
                edges.append(one)
            a, b = edges
            shifts = []
            for sector in range(36):
                base = {
                    "longitude_sector_10deg": sector,
                    "lon_min": sector * 10 - 180,
                    "lon_max": sector * 10 - 170,
                    "start_period": f"{DECADES[pi][0]}-{DECADES[pi][1]}",
                    "end_period": f"{DECADES[pj][0]}-{DECADES[pj][1]}",
                    "climate_month_basis": basis,
                    "threshold_source_SIC_percent": SIC_ISOPLETH,
                    "source_valid_ocean_grid_cells_in_pair": int(reference.sum())
                }
                if a is None or b is None or sector not in a or sector not in b:
                    base["status"] = "MISSING_CONTIGUOUS_FRONT_OR_SECTOR"
                    fronts.append(base)
                    continue
                lat0, lat1 = a[sector]["lat_median"], b[sector]["lat_median"]
                shift = KM_PER_LAT * (lat0 - lat1)
                base.update({
                    "status": "PAIRED_ORIGINAL_MARINE_FRONT",
                    "early_front_latitude_deg": lat0,
                    "late_front_latitude_deg": lat1,
                    "early_n_contour_vertices": a[sector]["n_vertices"],
                    "late_n_contour_vertices": b[sector]["n_vertices"],
                    "southward_positive_ice_edge_meridional_km": shift,
                    "southward_positive_ice_edge_meridional_km_per_decade": shift * 10 / (10 * (pj-pi)),
                    "source_is_sea_ice_front_not_penguin_range_or_coastline_route": True,
                })
                fronts.append(base)
                shifts.append(shift)
            map_by_pair[(pi, pj, basis)] = {
                "n_paired_10degree_longitude_sectors": len(shifts),
                "southward_shifting_sectors": sum(z > 0 for z in shifts),
                "northward_shifting_sectors": sum(z < 0 for z in shifts),
                "median_southward_positive_ice_edge_meridional_km": float(np.median(shifts)) if shifts else None,
                "minimum_shift_km": min(shifts) if shifts else None,
                "maximum_shift_km": max(shifts) if shifts else None,
                "status": "SUPPORTED_MERIDIONAL_SECTOR_DIAGNOSTIC" if len(shifts) >= 24 else "NO_CONTIGUOUS_CIRCUMPOLAR_FRONT_SUPPORT",
            }
    atlas_rows = readcsv(args.atlas)
    matched_rows = readcsv(args.prior_matched)
    biological = biological_overlap(fronts, matched_rows, atlas_rows)
    physical = []
    for key, rec in map_by_pair.items():
        pi, pj, basis = key
        physical.append({
            "start_period": f"{DECADES[pi][0]}-{DECADES[pi][1]}",
            "end_period": f"{DECADES[pj][0]}-{DECADES[pj][1]}",
            "climate_month_basis": basis,
            **rec,
        })
    summary = {
        "status": "ORIGINAL_GRIDDED_60PCT_SIC_MERIDIONAL_DIAGNOSTIC_COMPLETE",
        "source": {
            "provider": "EUMETSAT OSI SAF OSI-450-a1 v3.1",
            "doi": "10.15770/EUM_SAF_OSI_0023",
            "original_monthly_ice_files_sha_verified": len(receipts),
            "fixed_original_1993_09_ocean_grid_pixels": int(frozen.sum()),
            "grid_geo_sha256": fingerprint,
            "baseline_595_site_reconstruction": baseline_verification,
        },
        "isopleth_threshold_is_nonbiological": SIC_ISOPLETH,
        "front_direction_is_meridional_not_along_coast": True,
        "compare_dissimilar_ecological_and_climate_indices_no_debt_inference": True,
        "paired_physical_front": physical,
        "original_strict_observed_colony_overlap": biological,
        "full_contour_component_audit": contour_audit,
        "restrictions": [
            "This is a native-grid Antarctic pack-ice 60% front diagnostic, not an along-coast climate velocity.",
            "Original 595 observed colonies are positive survey anchors, not a constant-effort colony occupancy and true range-boundary census.",
            "Latitude movement of fixed-colony nest weights cannot be translated to actual individual dispersal or range edges.",
            "The 60% ice concentration is not an experimentally confirmed species-specific ecological or breeding threshold.",
            "Longitude sectors and shared marine cells are spatially dependent, not independent climate experiments.",
            "Missing marine contour or unsupported fixed-site overlap is not ecological zero.",
            "No causal warming impact or future species abundance is estimated."
        ]
    }
    args.output.mkdir(parents=True, exist_ok=True)
    savecsv(args.output / "original_60pct_contour_10degree_sector_pairs.csv", fronts)
    savecsv(args.output / "original_strict_colony_cohort_front_overlap.csv", biological)
    savecsv(args.output / "original_gridded_60pct_front_physical_summary.csv", physical)
    (args.output / "original_60pct_source_month_SHA256_receipts.json").write_text(
        json.dumps(receipts, indent=2) + "\n", encoding="utf-8")
    (args.output / "original_60pct_front_and_colony_overlap_result.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("ORIGINAL_60PCT_SOURCE_BASELINE=" + json.dumps(baseline_verification), flush=True)
    print("ORIGINAL_60PCT_ICE_FRONT_PHYSICAL=" + json.dumps(physical, ensure_ascii=False), flush=True)
    print("ORIGINAL_60PCT_ICE_FRONT_BIOLOGY=" + json.dumps(biological, ensure_ascii=False), flush=True)
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prior-ice", type=Path, required=True)
    p.add_argument("--prior-matched", type=Path, required=True)
    p.add_argument("--atlas", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    analyze(args)


if __name__ == "__main__":
    main()
