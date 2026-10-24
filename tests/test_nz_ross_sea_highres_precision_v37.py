"""V37 original GEOGRAPHY-only synthetic observations. No penguin counts."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from shapely.geometry import Point,box
from shapely.strtree import STRtree
import audit_nz_ross_sea_highres_precision_v37 as m

class FakeTransformer:
    def transform(self,lon,lat):
        return lon,lat

def test_minute_resolution_rectangle_stability_is_not_just_center_in_land():
    fake=FakeTransformer()
    land=[box(-.1,-.1,.1,.1),box(8.,8.,10.,10.)]
    point=Point(0,0)
    rec=m.classify_geo_point(point,0,0,fake,land,STRtree(land),1)
    assert rec["source_reported_georef_center_exact_island"] is True
    assert rec["round_or_truncate_conservative_one_arcminute_rectangle_on_one_land_feature"]
    close=Point(.096,0)
    rec=m.classify_geo_point(close,0,.096,fake,land,STRtree(land),1)
    assert rec["source_reported_georef_center_exact_island"] is True
    assert not rec["rounded_half_arcminute_rectangle_on_one_land_feature"]

def test_nearby_offshore_source_point_never_becomes_positional_robust_island():
    fake=FakeTransformer()
    geoms=[box(0.,0.,1.,1.),box(10000.,10000.,11000.,11000.)]
    v=m.classify_geo_point(Point(1.2,.5),.5,1.2,fake,geoms,STRtree(geoms),1)
    assert v["status"]=="NEAR_UNIQUE_LAND_WITHIN_2KM_PROVISIONAL"
    assert v["source_reported_georef_center_exact_island"] is False
    assert v["round_or_truncate_conservative_one_arcminute_rectangle_on_one_land_feature"] is False

def test_unknown_coast_and_two_polygons_are_not_robust_sources():
    tr=FakeTransformer()
    geoms=[box(-.1,-.1,.1,.1),box(-.05,-.05,.05,.05)]
    r=m.classify_geo_point(Point(0,0),0,0,tr,geoms,STRtree(geoms),0)
    assert r["status"]=="HOLD_MULTIPLE_ORIGINAL_HIGHRES_LAND_POLYGONS"
    assert r["polygon_id"] is None

def test_13year_original_roster_and_island_gate_are_immutable():
    assert m.FROZEN_13==tuple(list(range(1983,1993))+[2001,2004,2005])
    assert len(m.FROZEN_UNITS)==4
    assert m.MIN_ISLAND_YEARS==5 and m.MIN_COINCIDENT_YEARS==8
    assert m.MAX_NEAR_M==2000.
    assert m.HIGHSRC_DOI.startswith("10.5285/")
