#!/usr/bin/env python3
"""Join original 2025 AADC geographic reference sites to SCAR rock/land polygons.

Independent source geography only. Does not read, download, fit or infer animal
P/A/NR, breeding counts or colonies; original site coordinates are NOT nest GPS.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile

from pyproj import Transformer
from shapely.geometry import Point
from shapely.strtree import STRtree

from audit_aadc_geography_editions_v1 import source_geography_only, parse_geo
from build_functional_archipelago_v1 import build_archipelago, download_original_geography
import link_apbp_to_add_island_rock_v3 as bas
import validate_apbp_highres_coast_v4 as coast

NEAR_SOURCE_DIAGNOSTIC_M = 250.0
FAR_SOURCE_DIAGNOSTIC_M = 2000.0


def crosswalk_source_sites(sites: dict, land: list, rock: list, rock_rows: list):
    land_geoms = [r[1] for r in land]
    rock_geoms = [r[1] for r in rock]
    if len(rock_rows) != len(rock) or any(
        rock_rows[i]["rock_source_feature_id"] != rock[i][0] for i in range(len(rock))
    ):
        raise ValueError("SCHEMA_STOP source-rock geometry order differs from archipelago atlas")
    land_tree = STRtree(land_geoms)
    rock_tree = STRtree(rock_geoms)
    largest_land_id = max(land,key=lambda r:r[1].area)[0]

    rows = []
    converter = Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    for site_id, metadata in sorted(sites.items()):
        if metadata.get("lat") is None or metadata.get("lon") is None:
            rows.append({"original_geographic_site_id":site_id,
                         "source_land_class":metadata.get("feature"),
                         "point_land_category":"HOLD_SOURCE_COORDINATE_MISSING",
                         "point_land_feature_id":None,
                         "mapped_rock_spatial_category":"HOLD_SOURCE_COORDINATE_MISSING",
                         "nearest_rock_gap_m":None,
                         "nearest_rock_source_id":None,
                         "nearest_rock_parent_land_feature_id":None,
                         "site_point_inside_whole_rock_with_same_parent_land":False})
            continue
        x,y = converter.transform(metadata["lon"],metadata["lat"])
        p = Point(x,y)
        land_at_point = [int(i) for i in land_tree.query(p) if land_geoms[int(i)].covers(p)]
        if len(land_at_point)==1:
            point_land_id = land[land_at_point[0]][0]
            land_status = ("CONTINENT_LARGEST_MAPPED_LAND_FEATURE_PROXY" if
                           point_land_id==largest_land_id else "UNIQUE_OTHER_MAPPED_LAND_FEATURE")
        elif len(land_at_point)>1:
            point_land_id=None
            land_status="HOLD_MULTIPLE_MAPPED_LAND_FEATURES"
        else:
            point_land_id=None
            land_status="HOLD_POINT_OUTSIDE_MAPPED_LAND"

        rocks_covering = [
            int(i) for i in rock_tree.query(p) if rock_geoms[int(i)].covers(p)
        ]
        if len(rocks_covering)==1:
            rock_idx=rocks_covering[0]
            gap=0.0
            rock_status="POINT_IN_ONE_MAPPED_ROCK"
        elif len(rocks_covering)>1:
            rock_idx=None
            gap=0.0
            rock_status="HOLD_MULTIPLE_OVERLAPPING_ROCKS_AT_POINT"
        else:
            rock_idx=int(rock_tree.nearest(p))
            gap=float(p.distance(rock_geoms[rock_idx]))
            if gap <= NEAR_SOURCE_DIAGNOSTIC_M:
                rock_status="POINT_OUTSIDE_ROCK_NEAREST_LE250M"
            elif gap <= FAR_SOURCE_DIAGNOSTIC_M:
                rock_status="POINT_OUTSIDE_ROCK_NEAREST_250_TO_2000M"
            else:
                rock_status="POINT_OUTSIDE_ROCK_NEAREST_GT2000M"

        rock_id = rock[rock_idx][0] if rock_idx is not None else None
        rock_parent = (
            rock_rows[rock_idx]["land_source_feature_id"] if rock_idx is not None else None
        )
        site_matches_rock_land = bool(
            len(rocks_covering)==1 and
            rock_rows[rock_idx]["assignment_status"]=="EXACT_WHOLE_ROCK_ONE_LAND" and
            point_land_id is not None and point_land_id==rock_parent
        )
        rows.append({
            "original_geographic_site_id":site_id,
            "source_land_class":metadata.get("feature"),
            "point_land_category":land_status,
            "point_land_feature_id":point_land_id,
            "mapped_rock_spatial_category":rock_status,
            "nearest_rock_gap_m":gap,
            "nearest_rock_source_id":rock_id,
            "nearest_rock_parent_land_feature_id":rock_parent,
            "site_point_inside_whole_rock_with_same_parent_land":site_matches_rock_land,
        })

    categories = Counter(r["mapped_rock_spatial_category"] for r in rows)
    land_cat = Counter(r["point_land_category"] for r in rows)
    ready = sum(r["site_point_inside_whole_rock_with_same_parent_land"] for r in rows)
    return rows, {
        "status":"AADC_GEOGRAPHIC_SITE_SCAR_ROCK_LAND_SOURCE_ONLY_CROSSWALK",
        "original_2025_geographic_site_count":len(sites),
        "point_mapped_land_categories":dict(sorted(land_cat.items())),
        "point_mapped_rock_categories":dict(sorted(categories.items())),
        "strict_exact_point_in_rock_and_exact_whole_rock_parent_land_sites":ready,
        "fraction_strict_exact_source_point_land_rock_matches":ready/len(rows) if rows else None,
        "near_rock_250m_threshold_only_diagnostic_not_site_assignment":True,
        "near_rock_2000m_threshold_only_diagnostic_not_site_assignment":True,
        "original_geographic_site_coordinates_are_verified_nest_GPS":False,
        "original_geographic_site_counts_are_independent_penguin_colonies":False,
        "unmatched_source_site_proves_unsuitable_habitat":False,
        "source_coordinate_inside_rock_proves_site_available_for_penguin_nesting":False,
        "source_presence_absence_or_NRs_opened":0,
        "source_penguin_or_other_animal_counts_opened":0,
        "ecological_effects_fitted":0,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--site-crosswalk",type=Path,required=True)
    args = p.parse_args()
    geo, g_sources, manifest_sha = source_geography_only()
    sites, quality = parse_geo(geo["potential_geography_2025"],old=False)
    if len(sites)!=7785:
        raise ValueError("SOURCE_STOP original site reference count unexpectedly changed")
    land_zip,rock_zip = download_original_geography()
    with tempfile.TemporaryDirectory(prefix="aadc-scar-crosswalk-") as tmp:
        td=Path(tmp)
        land,land_meta = coast.original_highres_shapes(land_zip,td/"land",{})
        rock_file = bas.unpack_shapefile(rock_zip,td/"rock")
        rock,rock_meta = bas.mapped_features(rock_file,require_surface=False)
        rock_rows,rock_summary = build_archipelago(land,rock)
        rows,result = crosswalk_source_sites(sites,land,rock,rock_rows)
    result["original_aadc_geography_receipt"] = g_sources["potential_geography_2025"]
    result["AADC_original_public_manifest_sha256"] = manifest_sha
    result["original_2025_site_coordinate_validity"] = quality
    result["original_SCAR_land_SHA256"] = hashlib.sha256(land_zip).hexdigest()
    result["original_SCAR_rock_SHA256"] = hashlib.sha256(rock_zip).hexdigest()
    result["original_rock_network_2km_check"] = {
        "rock_n":rock_summary["mapped_rock_polygon_n"],
        "unambiguous_parent_land_rock_n":rock_summary["unambiguous_rock_polygon_n"],
        "land_n":rock_summary["mapped_land_polygon_n"]
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.site_crosswalk.parent.mkdir(parents=True,exist_ok=True)
    with args.site_crosswalk.open("w",newline="",encoding="utf-8") as output:
        writer=csv.DictWriter(output,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result["derived_public_AADC_site_SCAR_candidate_crosswalk_SHA256"] = hashlib.sha256(
        args.site_crosswalk.read_bytes()).hexdigest()
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
