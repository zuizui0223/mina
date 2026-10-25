#!/usr/bin/env python3
"""Outcome-blind Antarctic exposed-rock × mapped-land archipelago atlas.

Builds independent candidate breeding-habitat network features; NO animal
counts, P/A observations or penguin coordinates are downloaded or inspected.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

from shapely.strtree import STRtree

import link_apbp_to_add_island_rock_v3 as bas
import validate_apbp_highres_coast_v4 as coast

LAND_SHA256 = "66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4"
RADIUS_M = 2000.0
MAX_BOX_CANDIDATES = 50000


def _closer(old: float | None, value: float) -> float:
    return value if old is None or value < old else old


def build_archipelago(
    land_features: list,
    rock_features: list,
    radius_m: float = RADIUS_M,
) -> tuple[list[dict], dict]:
    """Use native EPSG:3031 geometries. Input features: (source_FID, geom, attrs).

    A source rock polygon is mapped only when exactly one original land
    feature covers the *whole polygon*. Polygon IDs are NOT named islands.
    Distances are nearest polygon-edge gaps, right-censored at radius_m.
    """
    if not 0 < radius_m <= 20000:
        raise ValueError("GEOMETRY_STOP invalid fixed local-search radius")
    if not land_features or not rock_features:
        raise ValueError("GEOMETRY_STOP no valid original land/rock polygons")

    land_geoms = [r[1] for r in land_features]
    land_index = STRtree(land_geoms)
    rows = []
    eligible = []

    for rock_fid, geom, _attrs in rock_features:
        if geom.is_empty or not geom.is_valid or geom.area <= 0:
            raise ValueError("GEOMETRY_STOP source rock features not valid")
        covered = [
            int(i) for i in land_index.query(geom)
            if land_geoms[int(i)].covers(geom)
        ]
        if len(covered) == 1:
            pos = covered[0]
            land_id = land_features[pos][0]
            status = "EXACT_WHOLE_ROCK_ONE_LAND"
            distance_to_land_edge = float(geom.distance(land_geoms[pos].boundary))
            eligible.append((len(rows), geom))
        else:
            land_id = None
            distance_to_land_edge = None
            status = (
                "HOLD_MULTIPLE_FULLY_COVERING_LANDS" if len(covered) > 1
                else "HOLD_ROCK_NOT_WHOLE_WITHIN_ONE_LAND"
            )
        rows.append({
            "rock_source_feature_id": rock_fid,
            "land_source_feature_id": land_id,
            "assignment_status": status,
            "rock_projected_area_epsg3031_km2": float(geom.area / 1000000.0),
            "distance_rock_edge_to_land_edge_m": distance_to_land_edge,
            "nearest_same_land_rock_gap_m": None,
            "nearest_different_land_rock_gap_m": None,
            "same_gap_censored_at_radius": True,
            "different_gap_censored_at_radius": True,
            "different_land_gap_closer_than_same": None,
        })

    same_pairs = 0
    different_pairs = 0
    if eligible:
        eligible_geoms = [e[1] for e in eligible]
        tree = STRtree(eligible_geoms)
        for i, (ri, gi) in enumerate(eligible):
            candidates = tree.query(gi.buffer(radius_m))
            if len(candidates) > MAX_BOX_CANDIDATES:
                raise ValueError("GEOMETRY_STOP unexpectedly dense patch neighborhood")
            for j0 in candidates:
                j = int(j0)
                if j <= i:
                    continue
                rj, gj = eligible[j]
                distance = float(gi.distance(gj))
                if distance > radius_m:
                    continue
                if rows[ri]["land_source_feature_id"] == rows[rj]["land_source_feature_id"]:
                    key = "nearest_same_land_rock_gap_m"
                    same_pairs += 1
                else:
                    key = "nearest_different_land_rock_gap_m"
                    different_pairs += 1
                rows[ri][key] = _closer(rows[ri][key], distance)
                rows[rj][key] = _closer(rows[rj][key], distance)

    both = inverted = 0
    for r in rows:
        same = r["nearest_same_land_rock_gap_m"]
        diff = r["nearest_different_land_rock_gap_m"]
        r["same_gap_censored_at_radius"] = same is None
        r["different_gap_censored_at_radius"] = diff is None
        if same is not None and diff is not None:
            both += 1
            r["different_land_gap_closer_than_same"] = bool(diff < same)
            inverted += int(diff < same)

    summary = {
        "status": "FUNCTIONAL_ARCHIPELAGO_OUTCOME_BLIND_GEOGRAPHY_V1",
        "radius_m": radius_m,
        "mapped_land_polygon_n": len(land_features),
        "mapped_rock_polygon_n": len(rock_features),
        "source_rock_assignment_status_n": dict(
            sorted(Counter(r["assignment_status"] for r in rows).items())
        ),
        "unambiguous_rock_polygon_n": len(eligible),
        "within_same_land_rock_patch_pairs_within_radius": same_pairs,
        "between_different_land_rock_patch_pairs_within_radius": different_pairs,
        "rocks_with_both_neighborhood_categories": both,
        "rocks_with_different_land_neighbor_closer": inverted,
        "disagreement_fraction_conditional_on_both": (
            inverted / both if both else None
        ),
        "all_original_animal_counts_or_occupancy_opened": 0,
        "mapped_land_polygon_is_named_physical_island": False,
        "different_land_polygon_implies_open_ocean_barrier": False,
        "observed_rock_gap_estimates_ice_crossing_cost": False,
        "mapped_rock_equals_available_nesting_capacity": False,
    }
    return rows, summary


def download_original_geography() -> tuple[bytes, bytes]:
    """Use already-audited publisher fetch functions, no biological endpoint."""
    previous = bas.MAX_BYTES
    try:
        bas.MAX_BYTES = coast.HIGH_ZIP_LIMIT
        land_zip = bas.fetch_bas(coast.HIGH_URL)
    finally:
        bas.MAX_BYTES = previous
    land_sha = hashlib.sha256(land_zip).hexdigest()
    if land_sha != LAND_SHA256:
        raise ValueError("SOURCE_STOP original 2026 land source SHA changed")
    rock_zip = bas.fetch_bas(bas.ROCK_ZIP)
    return land_zip, rock_zip


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--features", type=Path, required=True)
    args = parser.parse_args()

    land_blob, rock_blob = download_original_geography()
    with tempfile.TemporaryDirectory(prefix="functional-archipelago-") as td:
        root = Path(td)
        land, land_meta = coast.original_highres_shapes(
            land_blob, root / "land", {}
        )
        rock_file = bas.unpack_shapefile(rock_blob, root / "rock")
        rock, rock_meta = bas.mapped_features(rock_file, require_surface=False)
        rows, summary = build_archipelago(land, rock)

    summary["provenance"] = {
        "land_source_doi": coast.HIGH_DOI,
        "land_original_zip_sha256": hashlib.sha256(land_blob).hexdigest(),
        "rock_source_doi": bas.ROCK_DOI,
        "rock_original_zip_sha256": hashlib.sha256(rock_blob).hexdigest(),
        "land_source_geometry": land_meta,
        "rock_source_geometry": rock_meta,
        "geometry_crs": "EPSG:3031",
        "area_note": "EPSG:3031 planar area, not equal-area or ground-truth nesting habitat",
        "two_source_edition_mismatch": "land v7.12 / rock v7.11",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.features.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    fieldnames = list(rows[0])
    with args.features.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
