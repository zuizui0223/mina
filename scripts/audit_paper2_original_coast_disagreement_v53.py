#!/usr/bin/env python3
"""V53 original BAS sub-Antarctic land polygon outside-point distance SOURCE QA.

No ecological effect. Three exact original polygons vs original V26 actual
2019–20 nest points that did not lie inside 2020 coast. Identifies severity
of source-cartography / survey-georeference disagreement; no point snapping.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from shapely import contains_xy,distance,points

import audit_paper2_bas_subantarctic_exact_coast_v52 as v52
import analyze_paper2_three_island_penguin_coast_access_v51 as v51

COAST_ZIP_SHA="27b4cd2085b9c845abf7928c336cf82f0d37492bbe2c21522ac4c670750f6cff"
GRID_M=30
EXPECTED={
    "Ashen_Hills":(75255,72903),
    "Bellingshausen":(14005,13370),
    "Beach_Point":(7089,7089),
    "Hewison_Point":(22424,19203),
}


def source_disagreement(original_xy, original_polygon):
    """Source-only original point/shore geometry. Species labels not accepted."""
    xy=np.asarray(original_xy,dtype=float)
    if xy.ndim!=2 or xy.shape[1]!=2 or not np.isfinite(xy).all():
        raise ValueError("ORIGINAL_NEST_XY_NOT_VALID_FOR_SOURCE_GEOGRAPHY")
    if original_polygon.is_empty or not original_polygon.is_valid:
        raise ValueError("ORIGINAL_UNMODIFIED_LAND_GEOMETRY_INVALID")
    inside=contains_xy(original_polygon,xy[:,0],xy[:,1])
    outside=xy[~inside]
    result={
        "original_unique_original_source_points_n":int(len(xy)),
        "strict_original_source_on_land_n":int(np.sum(inside)),
        "strict_original_source_outside_land_n":int(len(outside)),
        "strict_original_source_land_fraction":float(np.mean(inside)),
        "original_off_land_nest_centres_are_not_automatically_actual_sea_nests":True,
        "no_original_points_snapped_or_reprojected_to_land":True,
    }
    if not len(outside):
        result["original_outside_distance_to_own_island_coast_m"]={
            "source_outside_point_n":0,"median_m":None,
            "p05_m":None,"p95_m":None,"max_m":None,
            "le5m":0,"le10m":0,"le30m":0,"le100m":0,"gt100m":0,"gt500m":0,
            "distinct_30m_grid_cells_outside_original_land":0,
        }
        return result
    dist=np.asarray(distance(points(outside[:,0],outside[:,1]),
                             original_polygon.boundary),dtype=float)
    if not np.isfinite(dist).all() or np.min(dist)<0:
        raise ValueError("ORIGINAL_NATIVE_COAST_BOUNDARY_DISTANCE_INVALID")
    pixel=np.floor(outside/GRID_M).astype(np.int64)
    result["original_outside_distance_to_own_island_coast_m"]={
        "source_outside_point_n":int(len(dist)),
        "p05_m":float(np.quantile(dist,.05)),
        "median_m":float(np.median(dist)),
        "p95_m":float(np.quantile(dist,.95)),
        "max_m":float(np.max(dist)),
        "le5m":int(np.sum(dist<=5)),
        "le10m":int(np.sum(dist<=10)),
        "le30m":int(np.sum(dist<=30)),
        "le100m":int(np.sum(dist<=100)),
        "gt100m":int(np.sum(dist>100)),
        "gt500m":int(np.sum(dist>500)),
        "distinct_30m_grid_cells_outside_original_land":len(np.unique(pixel,axis=0)),
    }
    return result


def original_source_all(site_data, original_polygons, original_source_qa):
    if len(original_polygons)!=3:
        raise ValueError("V53_SOURCE_THREE_UNIQUE_ORIGINAL_POLYGONS_REQUIRED")
    if set(site_data)!=set(v51.ORIGINAL_LOCALITIES):
        raise ValueError("V53_SOURCE_ORIGINAL_LOCALITY_KEYS_DRIFT")
    if set(original_polygons)!=set(v51.PARENT.values()):
        raise ValueError("V53_SOURCE_ORIGINAL_THREE_ISLAND_NAMES_DRIFT")
    summaries={}
    for site in v51.ORIGINAL_LOCALITIES:
        report=source_disagreement(site_data[site]["xy"],original_polygons[v51.PARENT[site]])
        expected_n,expected_inside=EXPECTED[site]
        if (report["original_unique_original_source_points_n"]!=expected_n or
            report["strict_original_source_on_land_n"]!=expected_inside):
            raise ValueError("V53_PREVIOUS_ORIGINAL_V52_MATCH_COUNTS_DRIFT:"+site)
        report["original_named_locality"]=site
        report["same_original_physical_island_as"]=v51.PARENT[site]
        summaries[site]=report
    h=summaries["Hewison_Point"]["original_outside_distance_to_own_island_coast_m"]
    out={
      "original_public_coast_publisher":"BAS/SCAR South Sandwich coastline, DOI 10.5285/c1d83502-8799-4e3c-bdca-21db6a4405d4",
      "original_public_coast_ZIP_SHA256":COAST_ZIP_SHA,
      "source_site_original_dataset":"BAS/Hart 2019-20 122139 located penguin nests",
      "source_v26_original_NPZ_SHA256":v51.SOURCE_NPZ_SHA,
      "original_publisher_coast_native_EPSG":original_source_qa["original_source_native_crs_EPSG"],
      "original_GSHHG_v51_biological_effect_fitted":False,
      "original_BAS_coast_3_original_physical_island_IDs":
          original_source_qa["provisionally_strict_source_coast_shapes"],
      "original_nest_outside_land_disagreement_by_source_locality":summaries,
      "original_Hewison_outside_fraction_within30m_of_source_coast":
          h["le30m"]/h["source_outside_point_n"],
      "original_Hewison_outside_fraction_beyond100m_of_source_coast":
          h["gt100m"]/h["source_outside_point_n"],
      "source_v52_95percent_all_sites_gate_still_failed":True,
      "no_original_penguin_species_labelling_or_bird_ecology_difference_used":True,
      "no_mammal_or_flying_bird_comparison_fitted":True,
      "no_actual_penguin_sea_to_nest_walking_route_observed":True,
    }
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v26-npz",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result={
      "status":"V53_OFFICIAL_BAS_SOURCE_ACCESS_OR_GEO_HOLD",
      "date":"2026-10-28",
      "contract":"contracts/PAPER2_V53_SHORELINE_NEST_COORDINATE_DISAGREEMENT.md",
      "original_geographic_dataset_DOI":v52.DOI,
      "source_public_zip_pinned_sha256":COAST_ZIP_SHA,
      "no_new_biological_outcome_model_fitted":True,
    }
    try:
        data,info=v51.read_original_npz(a.v26_npz)
        medians={}
        for island in set(v51.PARENT.values()):
            combined=np.vstack([v["xy"] for k,v in data.items()
                                if v51.PARENT[k]==island])
            medians[island]=tuple(np.median(combined,axis=0))
        raw=v52.original_download()
        if hashlib.sha256(raw).hexdigest()!=COAST_ZIP_SHA:
            raise ValueError("V53_ORIGINAL_VERIFIED_V52_SOURCE_ZIP_SHA_DRIFT")
        shapes,original_qa=v52.original_native_land_geometry(raw,medians)
        result["original_2020_coast_bird_cohort"]=original_source_all(data,shapes,original_qa)
        result["status"]="V53_SOURCE_SHORELINE_INCONSISTENCY_DISTANCES_MEASURED"
    except Exception as e:
        result["status"]="V53_OFFICIAL_BAS_SOURCE_ACCESS_OR_GEO_HOLD"
        result["source_error"]=type(e).__name__+": "+str(e)[:750]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    brief=result.get("original_2020_coast_bird_cohort",{})
    print(json.dumps({
        "status":result["status"],
        "original_by_site":brief.get("original_nest_outside_land_disagreement_by_source_locality"),
        "original_source_zip_sha":brief.get("original_public_coast_ZIP_SHA256"),
        "error":result.get("source_error"),
    },ensure_ascii=False))
    if result["status"]=="V53_OFFICIAL_BAS_SOURCE_ACCESS_OR_GEO_HOLD":
        raise SystemExit(2)


if __name__=="__main__":
    main()
