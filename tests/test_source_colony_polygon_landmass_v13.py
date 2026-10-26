"""Geometry-only landmass classification from original source polygon bounds."""
from __future__ import annotations
import json,sys
from pathlib import Path
from shapely.geometry import box

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_source_colony_polygon_landmass_v13 import land_feature_assignment


def synthetic():
    rows=[]
    for n in range(13):
        site=str(70000+n)
        for year in (2013,2015) if n!=0 else (2012,2013,2015,2016):
            a=[10,10,30,30] if n<6 else [110,10,130,30]
            rows.append({
               "site_id":site,
               "source_group":"HBE" if n<6 else "HBW",
               "season_start_year":str(year),
               "original_source_polygon_record_n":"1",
               "source_polygon_bounds_epsg3031_m":json.dumps(a),
            })
    # Make exactly 28 authentic-repeat-style inputs (12*2 + 4).
    assert len(rows)==28
    return rows


def test_physical_landmass_not_original_site_id_count():
    land=[
        (10,box(0,0,100,100),{}),
        (20,box(100,0,200,100),{})
    ]
    rows,result=land_feature_assignment(synthetic(),land)
    assert result["original_source_repeat_unique_site_IDs"]==13
    assert result["original_source_repeat_site_seasons"]==28
    assert result["distinct_strictly_verified_source_land_features_with_repeated_sites"]==2
    assert result["unique_site_IDs_all_seasons_strict_same_parent_land"]==13
    assert all(r["original_full_bbox_match_status"]=="EXACT_ONE_LAND_FULL_BOUNDING_RECTANGLE" for r in rows)
    assert result["new_penguin_observations_or_colony_geometry_loaded"] is False


def test_one_year_crossing_land_boundary_stops_physical_identity():
    rows=synthetic()
    change=next(r for r in rows if r["site_id"]=="70001")
    change["source_polygon_bounds_epsg3031_m"]=json.dumps([95,10,115,30])
    land=[
        (10,box(0,0,100,100),{}),
        (20,box(100,0,200,100),{})
    ]
    _,result=land_feature_assignment(rows,land)
    assert result["unique_site_IDs_source_continuity_unresolved"]==1
    assert result["unique_site_IDs_all_seasons_strict_same_parent_land"]==12
    assert result["site_original_parent_land_fid_qa"]["70001"]["mapped_land_source_FID"] is None
    assert result["source_polygon_buffer_or_spatial_tolerance_tuned"] is False
