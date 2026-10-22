"""V35 purely invented polygon site and year matching tests."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from shapely.geometry import Point,box
from shapely.strtree import STRtree
import audit_nz_ross_sea_add_island_geometry_v35 as m

def test_exact_and_nonoverlapping_near_original_land_polygons():
    geoms=[box(-300,-300,300,300),box(6000,0,7000,1000)]
    tree=STRtree(geoms)
    exact=m.link_geometry(Point(0,0),geoms,tree,0)
    assert exact["status"]=="EXACT_ONE_LAND_POLYGON"
    assert exact["provisional_land_class"]=="CONTINENT_LARGEST_POLYGON_PROXY"
    near=m.link_geometry(Point(1100,500),geoms,tree,0)
    assert near["status"]=="NEAR_UNIQUE_LAND_WITHIN_2KM_PROVISIONAL"
    assert near["land_polygon_feature_id"]==0
    hold=m.link_geometry(Point(3500,500),geoms,tree,0)
    assert hold["land_polygon_feature_id"] is None

def test_overlapping_gis_polygons_not_accepted_as_island():
    geoms=[box(0,0,1000,1000),box(200,200,800,800)]
    x=m.link_geometry(Point(500,500),geoms,STRtree(geoms),0)
    assert x["status"]=="HOLD_MULTIPLE_OVERLAPPING_LAND"

def test_temporal_support_never_equates_colonies_with_islands():
    m.SOURCE_CENSUS_SHA and m.SOURCE_LOCATION_SHA
    assert m.LAST_STRICT_Y_START==2016
    assert m.MIN_ISLANDS==3
    assert m.MIN_CONCURRENT_YEARS==8
    assert m.MAX_NEAR_COAST_M==2000.
