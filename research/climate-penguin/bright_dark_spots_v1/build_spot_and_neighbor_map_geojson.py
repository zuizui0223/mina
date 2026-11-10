#!/usr/bin/env python3
"""Build GIS-compatible WGS84 source-evidence GeoJSON without false absences.

Points are all 100 original site×species long source series, including sites
incomparable among original species-region peers. Lines are all 147 exact
co-census-year local pair contrasts. All geometries are actual original
source colony coordinates, not inferred transitions or migration paths.
"""
from __future__ import annotations
import argparse
import json
import math
from collections import Counter
from pathlib import Path

from discover_bright_dark_colonies import readcsv

N_POINTS=100
N_PAIRS=147
EXPECTED_SOURCE_GROUPS=6


def boolean(v):
    if isinstance(v,bool):return v
    if str(v).lower() not in ("true","false","0","1",""):
        raise ValueError("Nonboolean source field: "+str(v))
    return str(v).lower() in ("true","1")


def numeric(v):
    if v is None or str(v).strip()=="":
        return None
    num=float(v)
    if not math.isfinite(num):
        raise ValueError("Nonfinite source mapped metric")
    return num


def coords(meta):
    lat=numeric(meta["latitude"])
    lon=numeric(meta["longitude"])
    if lat is None or lon is None or not -90<=lat<=-55 or not -180<=lon<=180:
        raise ValueError("Invalid original Antarctic site longitude/latitude")
    return [lon,lat]


def source_point_status(item,validated):
    if item["source_peer_eligibility"]!="SAME_SPECIES_REGION_PAIRED_REFERENCE_AVAILABLE":
        return "NOT_COMPARABLE_REGION_SPECIES"
    if boolean(validated.get("outside_spatial_block_replicated_lead","False")):
        sign=item["relative_direction"]
        return "EXTERNAL_BLOCK_SUPPORTED_"+sign.upper()
    if boolean(validated.get("same_year_sign_qualified_candidate","False")):
        return "COMMON_YEAR_SUPPORTED_"+item["relative_direction"].upper()
    if str(item.get("robust_source_candidate_status","")).startswith("SOURCE_ROBUST_"):
        return "INITIAL_STRICT_ONLY_"+item["relative_direction"].upper()
    return "EXPLORATORY_"+item["relative_direction"].upper()


def produce(original,checked,pairs,atlas):
    if len(original)!=N_POINTS or len(checked)!=N_POINTS or len(pairs)!=N_PAIRS:
        raise ValueError("Source-map original observational cohort drift")
    names={(r["site_id"],r["species"]) for r in original}
    lookup={(r["site_id"],r["species"]):r for r in checked}
    source_geo={r["site_id"]:r for r in atlas}
    if len(names)!=100 or len(lookup)!=100 or set(names)!=set(lookup) or len(source_geo)!=595:
        raise ValueError("Source identity drift across original site, species or time audit")
    features=[]
    for item in original:
        orig=source_geo[item["site_id"]]
        if abs(float(orig["latitude"])-float(item["latitude"]))>1e-7 or abs(float(orig["longitude"])-float(item["longitude"]))>1e-7:
            raise ValueError("Original source atlas geographic coordinates drift")
        validated=lookup[item["site_id"],item["species"]]
        status=source_point_status(item,validated)
        properties={
            "source_site_id":item["site_id"],
            "site_name":item["site_name"],
            "species_code":item["species"],
            "original_source_region":item["source_region"],
            "original_250km_block":item["polar_250km_block"],
            "observed_count_n_original_survey_years":int(item["n_actual_original_census_years"]),
            "original_census_year_span":int(item["actual_year_span"]),
            "original_census_year_first":int(item["original_first_census_year"]),
            "original_census_year_last":int(item["original_last_census_year"]),
            "original_first_count_observed":int(item["first_original_observed_nest_count"]),
            "original_last_count_observed":int(item["last_original_observed_nest_count"]),
            "original_OLS_log1p_nest_trend_per_decade":numeric(item["original_OLS_log1p_nest_slope_per_decade"]),
            "regional_leave_site_out_relative_slope_per_decade":numeric(
                item.get("relative_log1p_nest_slope_residual_per_decade")),
            "source_observed_region_peer_status":item["source_peer_eligibility"],
            "source_common_year_reference_peers":int(validated.get("n_actual_year_matched_original_peer_sites") or 0),
            "source_common_year_reference_peers_in_other_250km_block":int(
                validated.get("n_actual_year_matched_outside_block_peer_sites") or 0),
            "source_same_year_strict_sign_supported":boolean(
                validated.get("same_year_sign_qualified_candidate","False")),
            "source_external_blocks_supported":boolean(
                validated.get("outside_spatial_block_replicated_lead","False")),
            "original_any_actual_census_zero":int(item["original_observed_zero_count_years"])>0,
            "candidate_map_status":status,
            "scientific_guard":"SOURCE_OBSERVED_RELATIVE_NEST_COUNTS_NOT_PENGUIN_FITNESS_OR_RANGE_SHIFT",
            "title":item["species"]+" | "+item["site_name"]+" | "+status
        }
        features.append({
            "type":"Feature",
            "id":item["species"]+"_"+item["site_id"],
            "geometry":{"type":"Point","coordinates":coords(orig)},
            "properties":properties
        })
    lines=[]
    seen=set()
    for row in pairs:
        a,b=row["left_site_id"],row["right_site_id"]
        sp=row["species"]
        key=(sp,tuple(sorted((a,b))))
        if key in seen:raise ValueError("Duplicate original same-year pair")
        seen.add(key)
        for site in (a,b):
            if site not in source_geo:raise ValueError("Missing original source pair coordinate")
        props={
            "species_code":sp,
            "source_original_region":row["source_region"],
            "source_original_250km_block":row["polar_250km_fixed_block"],
            "left_site_id":a,"right_site_id":b,
            "left_site_name":row["left_site_name"],
            "right_site_name":row["right_site_name"],
            "n_actual_same_original_census_years":int(row["n_identical_original_observed_nest_seasons"]),
            "separation_between_original_colony_points_km":numeric(row["site_distance_km"]),
            "original_fixed_source_method_matches":boolean(row["source_method_same"]),
            "any_original_long_census_recorded_zero":boolean(row["either_original_long_count_series_contains_real_zero_count"]),
            "absolute_delta_log1p_nest_slope_per_decade":numeric(row["absolute_nest_log1p_OLS_slope_difference_per_decade"]),
            "original_mean_absolute_nearshore_SIC_difference_pp":numeric(row["mean_absolute_source_original_aug_nov_sic_diff_pp"]),
            "same_native_25km_ocean_pixel_Jaccard":numeric(row["native_ocean_pixel_jaccard"]),
            "native_original_25km_ocean_pixel_intersection_count":int(row["n_shared_native_25km_ocean_pixels"]),
            "source_not_observed_migration_or_foraging_route":True,
            "title":sp+" "+a+"–"+b+" (count difference, ice cell overlap)"
        }
        lines.append({
            "type":"Feature","id":sp+"_"+a+"_"+b,
            "geometry":{"type":"LineString","coordinates":[coords(source_geo[a]),coords(source_geo[b])]},
            "properties":props
        })
    if len(features)!=N_POINTS or len(lines)!=N_PAIRS:
        raise AssertionError("Map features not complete")
    return features,lines


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--validated",type=Path,required=True)
    p.add_argument("--pairs",type=Path,required=True)
    p.add_argument("--atlas",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    points,lines=produce(*(
        readcsv(path) for path in (args.original,args.validated,args.pairs,args.atlas)
    ))
    args.out.mkdir(parents=True,exist_ok=True)
    for name,items in (
        ("penguin_original_bright_dark_100_species_site_points.geojson",points),
        ("penguin_original_147_same_year_nearby_colony_pair_contrasts.geojson",lines)
    ):
        (args.out/name).write_text(
            json.dumps({"type":"FeatureCollection","features":items},
                       ensure_ascii=False,separators=(",",":"))+"\n",
            encoding="utf-8")
    status=Counter(item["properties"]["candidate_map_status"] for item in points)
    if (status["EXTERNAL_BLOCK_SUPPORTED_POSITIVE"]!=1
       or status["EXTERNAL_BLOCK_SUPPORTED_NEGATIVE"]!=1):
        raise ValueError("Previously source-supported Ross Island two candidate source map counts drifted")
    r={
        "status":"EXPLORATORY_PENGUIN_SOURCE_GEOJSON_100_POINTS_AND_147_LOCAL_PAIR_LINES",
        "source_original_sites":595,
        "n_source_site_species_points":len(points),
        "n_source_line_pairs_all_original_same_year_census":len(lines),
        "original_source_regions_with_eligible_region_peers":len({
            (q["properties"]["species_code"],q["properties"]["original_source_region"])
            for q in points if q["properties"]["source_observed_region_peer_status"]==
            "SAME_SPECIES_REGION_PAIRED_REFERENCE_AVAILABLE"
        }),
        "points_by_verification_class":dict(sorted(status.items())),
        "source_crzw_royds_are_known_prior_literature_case":True,
        "paired_lines_not_penguin_migration_paths":True,
        "coordinates_WGS84_geographic_lon_lat":True,
        "unmonitored_sites_not_mapped_as_absence":True,
        "map_source_receipts":["42916058266 original 100","42919208344 common-year 100",
                               "42923119624 original native ocean pixel overlap 147"],
        "note":"Both GeoJSON layers are original observed source evidence in EPSG:4326; line segments merely link two observed original colony point coordinates."
    }
    (args.out/"source_map_coverage_and_legend.json").write_text(
        json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PENGUIN_BRIGHT_DARK_GIS="+json.dumps(r,ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
