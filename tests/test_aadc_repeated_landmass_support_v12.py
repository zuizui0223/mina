"""Geographic independent landmass support QC for original 13 repeated colony sites."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pytest
from pyproj import Transformer
from shapely.geometry import box

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from derive_aadc_repeated_colony_boundaries_v10 import identify_source_geometry
from audit_aadc_repeated_landmass_support_v12 import (
    crosswalk_repeated_site_references, validate_polygon_bbox
)


def selected():
    path=Path(__file__).resolve().parents[1]/"results"/"ANTARCTIC_SOURCE_BOUNDARY_MANIFEST_V9.json"
    r=json.loads(path.read_text(encoding="utf-8"))
    sample,_=identify_source_geometry(r)
    return sample


def test_original_survey_groups_not_number_of_physical_islands():
    items=selected()
    ids=sorted({x["site_id"] for x in items})
    assert len(ids)==13
    source_geography={}
    groups=[]
    proj=Transformer.from_crs(4326,3031,always_xy=True)
    A=(-75.,45.)
    B=(-75.,55.)
    xy=[proj.transform(A[1],A[0]),proj.transform(B[1],B[0])]
    site_pairs=[]
    for i,site in enumerate(ids):
        category="island" if i<6 else "continent"
        lat,lon=A if i<6 else B
        source_geography[site]={"lat":lat,"lon":lon,"feature":category}
    for t in items:
        lat,lon=A if t["site_id"] in ids[:6] else B
        x,y=proj.transform(lon,lat)
        site_pairs.append({**t,"source_polygon_bounds_epsg3031_m":
                          json.dumps([x-1,y-1,x+1,y+1])})
    land=[
        (5,box(xy[0][0]-10000,xy[0][1]-10000,xy[0][0]+10000,xy[0][1]+10000),{}),
        (7,box(xy[1][0]-10000,xy[1][1]-10000,xy[1][0]+10000,xy[1][1]+10000),{})
    ]
    rec,qa=crosswalk_repeated_site_references(items,site_pairs,source_geography,land)
    assert len(rec)==13
    assert qa["original_sites"]==13
    assert qa["original_site_year_source_records"]==28
    assert qa["distinct_original_SCAR_parent_land_feature_ids_with_repeated_colonies"]==2
    assert all(x["min_original_sitepoint_distance_to_colony_bbox_m"]==0 for x in rec)
    assert qa["original_source_publisher_group_equals_independent_island"] is False
    assert qa["original_observed_population_count_or_P_A_opened"]==0


def test_invalid_original_bbox_does_not_infer_missing_site():
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        validate_polygon_bbox({"source_polygon_bounds_epsg3031_m":"[9,8,1,2]"})
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        validate_polygon_bbox({"source_polygon_bounds_epsg3031_m":"NOT_A_MAP"})
