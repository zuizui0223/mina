#!/usr/bin/env python3
"""V54 official BAS coast map proximity: descriptive nests and 3-island transfer.

POST-V52 exploratory, NOT a V51 successful shore-to-nest access fit. Original
BAS coastline contains only ~85.64% of Hewison mapped nests. Every genuine
original XY nevertheless has a mathematical (unsigned) distance to the
independently sourced official 2020 shoreline, regardless land status. We
evaluate only incremental source class location information, never physical
walking, actual vacant nesting habitat, mammalian predator or flight traits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from shapely import contains_xy,points,distance

import analyze_paper2_three_island_penguin_coast_access_v51 as v51
import audit_paper2_bas_subantarctic_exact_coast_v52 as v52
import audit_paper2_original_coast_disagreement_v53 as v53

SHA=v53.COAST_ZIP_SHA
SOURCE_SHAPE_INDEX={"Saunders":458,"Bellingshausen":451,"Thule":450}
SOURCE_KM2={"Saunders":37.93281019131191,
            "Bellingshausen":1.558257101129231,
            "Thule":16.739957193777226}
SOURCE_SAMPLE_COUNTS=v53.EXPECTED

def qsummary(x):
    n=np.asarray(x,dtype=float)
    n=n[np.isfinite(n)]
    if len(n)==0:return {"n":0,"q05":None,"median":None,"q95":None}
    return {
       "n":int(len(n)),
       "q05":float(np.quantile(n,.05)),
       "median":float(np.median(n)),
       "q95":float(np.quantile(n,.95)),
    }


def original_exact_coastal_geography(orig):
    names=set(v51.PARENT.values())
    if set(orig)!=set(v51.ORIGINAL_LOCALITIES):
        raise ValueError("ORIGINAL_FOUR_LOCALITY_KEYS_NOT_IDENTICAL")
    medians={}
    for island in names:
        concat=np.vstack([v["xy"] for site,v in orig.items()
                          if v51.PARENT[site]==island])
        medians[island]=tuple(np.median(concat,axis=0))
    raw=v52.original_download()
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("V54_ORIGINAL_OFFICIAL_BAS_COAST_ZIP_SHA_CHANGED")
    polygon,proof=v52.original_native_land_geometry(raw,medians)
    if len(polygon)!=3:
        raise ValueError("V54_ORIGINAL_REAL_PHYSICAL_ISLAND_IDENTITY_MISSING")
    observed=proof["provisionally_strict_source_coast_shapes"]
    for island in sorted(names):
        if (observed[island]["original_shape_index"]!=SOURCE_SHAPE_INDEX[island]
           or abs(observed[island]["original_island_projected_area_km2"]-SOURCE_KM2[island])>.005):
            raise ValueError("V54_ORIGINAL_VERIFIED_2020_SOURCE_ISLAND_ID_OR_AREA_CHANGED")
    return polygon,proof


def island_coast_map_only(source,coast):
    """Mathematical map proximity; never modifies original nest coordinates."""
    measures={}
    atlas={}
    for site in v51.ORIGINAL_LOCALITIES:
        data=source[site]
        xy=data["xy"]
        polygon=coast[v51.PARENT[site]]
        inside=contains_xy(polygon,xy[:,0],xy[:,1])
        count,originside=SOURCE_SAMPLE_COUNTS[site]
        if len(xy)!=count or int(inside.sum())!=originside:
            raise ValueError("V54_ORIGINAL_V52_NESTS_AND_POLYGON_MEMBERSHIP_DRIFT:"+site)
        map_dist=np.asarray(distance(points(xy[:,0],xy[:,1]),
                                     polygon.boundary),dtype=float)
        if (len(map_dist)!=len(xy)
            or not np.isfinite(map_dist).all()
            or np.any(map_dist<0)):
            raise ValueError("V54_ORIGINAL_MAP_COAST_DISTANCE_NOT_FINITE:"+site)
        # Original source DEM completeness: identical independent V27 stage.
        valid=np.isfinite(data["elev"]) & np.isfinite(data["slope"])
        if valid.mean()<v51.MIN_VALID_TERRAIN:
            raise ValueError("V54_SOURCE_NEST_DEM_COVERAGE_LESS_THAN_95_PERCENT")
        measures[site]={"D_coast":map_dist,"keep":valid}
        by_original_taxon={}
        for code,species in enumerate(v51.SPECIES):
            member=(data["label"]==code)&valid
            if not np.any(member):continue
            by_original_taxon[species]={
                "source_geolocated_nests_n":int(np.sum(member)),
                "original_gis_coast_inside_fraction":float(np.mean(inside[member])),
                "source_original_map_distance_to_published_coast_metres":qsummary(map_dist[member]),
                "source_original_inside_2020_land_coast_distance":qsummary(map_dist[member&inside]),
                "source_original_outside_2020_land_coast_distance":qsummary(map_dist[member&~inside]),
            }
        atlas[site]={
            "source_original_locality":site,
            "source_2020_official_physical_island":v51.PARENT[site],
            "original_unique_nest_points_n":len(xy),
            "original_land_coast_contains_source_nests_n":int(np.sum(inside)),
            "original_land_coast_excludes_source_nests_n":int(np.sum(~inside)),
            "original_land_coast_contains_fraction":float(np.mean(inside)),
            "original_source_nest_DEM_completeness_fraction":float(np.mean(valid)),
            "actual_unsigned_map_distance_defined_for_all_source_points":True,
            "original_species_descriptors":by_original_taxon,
        }
    return measures,atlas


def run(source_file:Path):
    data,source_qa=v51.read_original_npz(source_file)
    coast,coast_qa=original_exact_coastal_geography(data)
    measures,atlas=island_coast_map_only(data,coast)
    result=v51.source_heldout_predictive_qa(data,measures)
    return {
       "status":"V54_SOURCE_POSTRESULT_MAP_COAST_PROXIMITY_AND_TRANSFER_COMPLETED",
       "original_coast_2020_BAS_DOI":v52.DOI,
       "original_coast_ZIP_sha256":SHA,
       "original_2019_20_penguin_npz_SHA256":v51.SOURCE_NPZ_SHA,
       "original_truly_three_2020_coast_islands":coast_qa,
       "source_original_species_coast_distance_per_locality":atlas,
       "source_island_heldout_elevation_slope_vs_additional_map_coast_distance":result,
       "V51_failed_original_geography_gate_NOT_RESOLVED":True,
       "source_unsigned_coastal_map_distance_includes_original_offshore_points":True,
       "source_land_sign_original_geometry_kept_separate":True,
       "source_coastal_distance_not_real_land_route_or_bird_landing_path":True,
       "source_nest_locations_not_independent_sample_of_available_empty_land":True,
       "all_original_birds_in_source_flightless":True,
       "ecological_flight_trait_comparison_or_mammalian_predator_effect_fitted":False,
       "exploratory_post_results_not_independent_discovery_validation":True
    }


def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--v26-npz",required=True,type=Path)
    pa.add_argument("--out",required=True,type=Path)
    a=pa.parse_args()
    report={
       "status":"V54_ORIGINAL_SOURCE_SHORE_PROXIMITY_MODEL_HOLD",
       "date":"2026-10-28",
       "frozen_contract":"contracts/PAPER2_V54_ORIGINAL_COAST_MAP_PROXIMITY_EXPLORATORY.md",
       "source_original_coast_SHA256":SHA,
       "no_mammal_or_flying_seabird_effect":True,
    }
    try:
        report.update(run(a.v26_npz))
    except Exception as e:
        report["status"]="V54_ORIGINAL_SOURCE_SHORE_PROXIMITY_MODEL_HOLD"
        report["error"]=type(e).__name__+": "+str(e)[:900]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    qa=report.get("source_island_heldout_elevation_slope_vs_additional_map_coast_distance",{})
    print(json.dumps({
      "status":report["status"],
      "mean_gain_B1_minus_B2":qa.get("island_equal_mean_B1_minus_B2_gain"),
      "islands_gain_positive_n":qa.get("original_3_island_groups_with_positive_access_gain"),
      "frozen_increment_pass":qa.get("fixed_coast_increment_at_least_two_islands_and_gain_ge_0p005_pass"),
      "heldout":qa.get("heldout_island_Brier"),
      "source_nesting_coastal_map_descriptors":report.get("source_original_species_coast_distance_per_locality"),
      "error":report.get("error")
    },ensure_ascii=False))
    if report["status"]=="V54_ORIGINAL_SOURCE_SHORE_PROXIMITY_MODEL_HOLD":
        raise SystemExit(2)


if __name__=="__main__":
    main()
