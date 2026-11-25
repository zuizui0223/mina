#!/usr/bin/env python3
"""Original AADC 2021/2025 geographic site identity and positional drift audit.

The original *geography* tables only: no occupancy workbook is downloaded,
no P/A/NR outcomes opened, no source coordinate construed as nesting GPS.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import quote

from pyproj import Geod
import requests

from audit_aadc_original_workbook_headers_v11 import (
    DATASETS, HOST, MIME_LIMIT, public_dataset_manifests, trusted_response_get
)
from join_aadc_original_site_occupancy_v13 import (
    SOURCE_SPECS, REQUIRED_HEADERS, sheet_source, source_id, source_text,
)

GEO_SOURCE_KEYS = ("potential_geography_2021", "potential_geography_2025")
SOURCE_2021_COUNT = 4884
SOURCE_2025_COUNT = 7785
DRIFT_BINS_M = (0.0, 250.0, 2000.0)
WGS84 = Geod(ellps="WGS84")


def parse_geo(rows, old: bool):
    """Read source-defined site ID and geometry fields without animal records."""
    prefix = "Geog_Site_" if old else "geog_site_"
    id_col = prefix + ("ID" if old else "id")
    lat_col = prefix + ("Latitude" if old else "latitude")
    lon_col = prefix + ("Longitude" if old else "longitude")
    sites = {}
    missing_xy = 0
    invalid_xy = 0
    for r in rows:
        site = source_id(r.get(id_col))
        if not site or site in sites:
            raise ValueError("SOURCE_STOP missing or duplicate geographic site ID")
        raw_lat = source_text(r.get(lat_col))
        raw_lon = source_text(r.get(lon_col))
        lat = lon = None
        if not raw_lat or not raw_lon:
            missing_xy += 1
        else:
            try:
                lat = float(raw_lat)
                lon = float(raw_lon)
            except (ValueError, TypeError):
                lat = lon = None
            if lat is None or not (-90 <= lat <= -60 and -180 <= lon <= 180):
                invalid_xy += 1
                lat = lon = None
        sites[site] = {
            "lat": lat, "lon": lon,
            "feature": source_text(r.get("geog_site_feature")) if not old else None,
            "area": source_text(r.get("geog_site_area")) if not old else None,
        }
    return sites, {"geographic_site_ids": len(sites),
                   "missing_lat_lon": missing_xy,
                   "invalid_lat_lon": invalid_xy,
                   "sites_with_valid_coordinates": sum(
                       s["lat"] is not None for s in sites.values())}


def _percentile(values, fraction: float):
    if not values:
        return None
    s = sorted(values)
    pos = (len(s) - 1) * fraction
    low, high = math.floor(pos), math.ceil(pos)
    return s[low] + (s[high] - s[low]) * (pos - low)


def evaluate_geography(old, new):
    common = sorted(set(old) & set(new))
    unseen = sorted(set(new) - set(old))
    disappeared = sorted(set(old) - set(new))
    source_feature = Counter(s["feature"] or "MISSING" for s in new.values())
    valid_old = {k for k in old if old[k]["lat"] is not None}
    valid_new = {k for k in new if new[k]["lat"] is not None}
    displacements = []
    exact_coord_count = 0
    drift_categories = Counter()
    for site in common:
        if site not in valid_old or site not in valid_new:
            continue
        a = old[site]
        b = new[site]
        if a["lat"] == b["lat"] and a["lon"] == b["lon"]:
            exact_coord_count += 1
            d = 0.0
        else:
            _az1, _az2, d = WGS84.inv(a["lon"], a["lat"], b["lon"], b["lat"])
            if not math.isfinite(d) or d < 0:
                raise ValueError("GEOMETRY_STOP invalid source location shift")
        displacements.append(d)
        if d == 0:
            group = "EXACT_UNCHANGED"
        elif d <= DRIFT_BINS_M[1]:
            group = "SHIFT_GT0_LE250M"
        elif d <= DRIFT_BINS_M[2]:
            group = "SHIFT_GT250_LE2000M"
        else:
            group = "SHIFT_GT2000M"
        drift_categories[group] += 1

    # Exact position duplicates are a warning about site coordinate grain,
    # not evidence that two independent site IDs refer to the same bird colony.
    groups = defaultdict(set)
    for site in valid_new:
        s = new[site]
        groups[(s["lat"], s["lon"])].add(site)
    duplicate_coordinate_groups = [s for s in groups.values() if len(s) > 1]
    return {
        "status": "AADC_GEOGRAPHY_ONLY_TWO_SOURCE_EDITION_AUDIT",
        "original_site_n_2021": len(old),
        "original_site_n_2025": len(new),
        "common_original_geographic_site_ids": len(common),
        "only_in_2025_original_site_ids": len(unseen),
        "only_in_2021_original_site_ids": len(disappeared),
        "2025_original_geog_site_feature_classes": dict(sorted(source_feature.items())),
        "common_sites_with_valid_coordinates_both_editions": len(displacements),
        "same_identifier_exactly_identical_latlon": exact_coord_count,
        "same_site_id_original_coordinate_shift_bins": dict(sorted(drift_categories.items())),
        "source_position_displacement_median_m": _percentile(displacements, 0.5),
        "source_position_displacement_p90_m": _percentile(displacements, 0.9),
        "source_position_displacement_max_m": max(displacements) if displacements else None,
        "source_2025_distinct_exact_coordinate_pairs": len(groups),
        "source_2025_coordinate_groups_shared_by_multiple_original_site_ids": len(duplicate_coordinate_groups),
        "source_2025_site_ids_with_nonunique_exact_coordinate_pairs": sum(
            len(s) for s in duplicate_coordinate_groups
        ),
        "new_original_site_id_is_recolonization": False,
        "old_absent_site_id_is_biological_extinction": False,
        "source_coordinate_precision_is_independent_field_gps": False,
        "penguin_or_other_animal_counts_opened": 0,
        "animal_presence_absence_or_NRs_opened": 0,
        "ecological_effects_fitted": 0,
    }


def source_geography_only():
    # Only the 2021 and 2025 geographic files; no species/occurrence workbooks.
    with requests.Session() as session:
        manifests, index_receipt = public_dataset_manifests(session)
        geography = {}
        receipts = {}
        for key in GEO_SOURCE_KEYS:
            eds, filename, expected_sha, sheet, expected_rows = SOURCE_SPECS[key]
            manifest = manifests[eds]["original_object_manifest"]["file_descriptors"]
            if filename not in manifest:
                raise ValueError("SOURCE_STOP official geographical source missing")
            url = (
                f"https://{HOST}/eds/api/dataset/{quote(manifests[eds]['uuid'])}"
                f"/object/download?prefix={quote(filename,safe='')}"
            )
            raw, receipt = trusted_response_get(session, url, MIME_LIMIT)
            if receipt["source_sha256"] != expected_sha:
                raise ValueError("SOURCE_STOP AADC original geographic XLS/XLSX SHA drift")
            headers, rows = sheet_source(raw, sheet)
            if not REQUIRED_HEADERS[key].issubset(set(headers)):
                raise ValueError("SCHEMA_STOP original source geography headers changed")
            if len(rows) != expected_rows:
                raise ValueError("SOURCE_STOP source geographic sites row count changed")
            geography[key] = rows
            receipts[key] = {
                "source_doi": DATASETS[eds]["doi"],
                "source_geographic_file_name": filename,
                "source_geographic_sheet": sheet,
                "original_SHA256": hashlib.sha256(raw).hexdigest(),
                "geographic_rows": len(rows),
                "source_file_bytes": len(raw),
            }
        return geography, receipts, index_receipt["source_sha256"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    data, receipts, manifest_sha = source_geography_only()
    old, old_qa = parse_geo(data["potential_geography_2021"], old=True)
    new, new_qa = parse_geo(data["potential_geography_2025"], old=False)
    if len(old) != SOURCE_2021_COUNT or len(new) != SOURCE_2025_COUNT:
        raise ValueError("SOURCE_STOP geographic source count drift")
    report = evaluate_geography(old, new)
    report["original_coordinate_qa"] = {"2021": old_qa, "2025": new_qa}
    report["original_geographic_source_receipts"] = receipts
    report["AADC_original_public_dataset_manifest_sha256"] = manifest_sha
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
