"""Synthetic original-site × independent rock geometry crosswalk tests."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

from shapely.geometry import box
from build_functional_archipelago_v1 import build_archipelago
from join_aadc_geography_to_scar_network_v1 import crosswalk_source_sites


def feature(fid,geometry):
    return fid,geometry,{}


def test_exact_site_point_crosswalk_not_nest_gps():
    land = [
        feature(10,box(-500,-500,500,500)),
        feature(20,box(1000,-500,2000,500)),
    ]
    rocks = [
        feature(101,box(-100,-100,100,100)),
        feature(202,box(1200,-100,1300,100)),
    ]
    rock_rows,_summary = build_archipelago(land,rocks)
    sites = {
        "POLE":{"lat":-90.0,"lon":0.0,"feature":"island"},
        "NEAR":{"lat":-89.998,"lon":0.0,"feature":"continent"},
        "MISSING":{"lat":None,"lon":None,"feature":"island"},
    }
    rows,result = crosswalk_source_sites(sites,land,rocks,rock_rows)
    by={r["original_geographic_site_id"]:r for r in rows}
    assert result["original_2025_geographic_site_count"]==3
    assert result["strict_exact_point_in_rock_and_exact_whole_rock_parent_land_sites"]==1
    assert by["POLE"]["mapped_rock_spatial_category"]=="POINT_IN_ONE_MAPPED_ROCK"
    assert by["POLE"]["site_point_inside_whole_rock_with_same_parent_land"] is True
    assert by["NEAR"]["mapped_rock_spatial_category"]=="POINT_OUTSIDE_ROCK_NEAREST_LE250M"
    assert by["NEAR"]["site_point_inside_whole_rock_with_same_parent_land"] is False
    assert by["MISSING"]["mapped_rock_spatial_category"]=="HOLD_SOURCE_COORDINATE_MISSING"
    assert by["MISSING"]["nearest_rock_gap_m"] is None
    assert result["source_presence_absence_or_NRs_opened"]==0
    assert result["source_coordinate_inside_rock_proves_site_available_for_penguin_nesting"] is False


def test_outside_rock_and_multiple_covering_lands_are_holds():
    land=[
        feature(1,box(-100,-100,100,100)),
        feature(2,box(-50,-50,200,200)),
    ]
    rocks=[feature(11,box(-10,-10,10,10))]
    rock_rows,_=build_archipelago(land,rocks)
    sites={"ONE":{"lat":-90,"lon":0,"feature":"island"}}
    rows,result=crosswalk_source_sites(sites,land,rocks,rock_rows)
    assert result["strict_exact_point_in_rock_and_exact_whole_rock_parent_land_sites"]==0
    assert rows[0]["point_land_category"]=="HOLD_MULTIPLE_MAPPED_LAND_FEATURES"
    assert rows[0]["site_point_inside_whole_rock_with_same_parent_land"] is False
