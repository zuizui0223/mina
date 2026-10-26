"""Synthetic v7 Shapely make_valid and source-provenance audit."""
from __future__ import annotations
import sys
from pathlib import Path
import shapefile
from shapely.geometry import Point,Polygon,mapping

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_scar_landsat_v7_topology_origin import (
    source_origin,polygon_repair,compare_original_record_rocks,summarize
)

class Rec:
    def __init__(self,data):
        self.d=data
    def as_dict(self):
        return self.d

class OriginalShape:
    shapeType=shapefile.POLYGON
    def __init__(self,polygon):
        self.bbox=list(polygon.bounds)
        self.__geo_interface__=mapping(polygon)

class ShapeRecord:
    def __init__(self,polygon,data):
        self.shape=OriginalShape(polygon)
        self.record=Rec(data)


def test_original_gridcode_source_lineage_not_assumed_all_landsat():
    assert source_origin({"GRIDCODE":1,"Source":"Manual"})=="LANDSAT_AUTOMATED_GRIDCODE_1"
    assert source_origin({"GRIDCODE":0,"Source":"Landsat"})=="MANUAL_FALLBACK_GRIDCODE_0"
    assert source_origin({"Source":"Manually derived"})=="MANUAL_SOURCE_TEXT"
    assert source_origin({"Source":"Landsat 8 classification"})=="LANDSAT_SOURCE_TEXT"
    assert source_origin({"Source":"Unknown technique"})=="UNKNOWN_ORIGIN"


def test_make_valid_bowtie_deterministic_no_buffer():
    bow=Polygon([(0,0),(20,20),(0,20),(20,0),(0,0)])
    assert not bow.is_valid
    polygon,status=polygon_repair(bow)
    assert polygon is not None
    assert polygon.is_valid
    assert polygon.area>0
    assert status in ("POLYGON_VALID_AFTER_MAKE_VALID",
                      "GEOMETRYCOLLECTION_POLYGONAL_WITH_REMAINDER")


def test_native_original_and_repaired_source_tiers_not_mixed():
    good=ShapeRecord(Polygon([(-20,-20),(20,-20),(20,20),(-20,20)]),
                     {"GRIDCODE":1})
    invalid=ShapeRecord(Polygon([(3300,-40),(3420,40),(3300,40),(3420,-40)]),
                        {"GRIDCODE":0})
    points=[Point(0,0),Point(3340,25)]
    rows,qa,origins=compare_original_record_rocks(
        [good,invalid],["GOOD","REPAIR"],points)
    assert qa["original_shape_records"]==2
    assert qa["original_invalid_feature_near_candidate"]==1
    assert origins["LANDSAT_AUTOMATED_GRIDCODE_1"]==1
    assert origins["MANUAL_FALLBACK_GRIDCODE_0"]==1
    assert rows[0]["native_valid_original_rock_class"]=="IN_ONE_ROCK"
    assert rows[0]["source_rock_feature_origin_categories_native"]=="LANDSAT_AUTOMATED_GRIDCODE_1"
    assert rows[1]["covering_original_native_valid_rock_features"]==0
    assert rows[1]["source_rock_feature_origin_categories_native"]==""
    assert rows[1]["source_invalid_feature_could_not_be_repaired_near_site"] is False
    assert rows[1]["topology_repaired_source_rock_class"]!="HOLD_INVALID_NEAR_SITE"


def test_source_summary_no_ecology_or_nonindependence_claim():
    rows=[
      {"original_geographic_site_id":"A","native_valid_original_rock_class":"IN_ONE_ROCK",
       "topology_repaired_source_rock_class":"IN_ONE_ROCK",
       "covering_original_native_valid_rock_features":1,
       "covering_source_invalid_but_make_valid_repaired_rock_features":0},
      {"original_geographic_site_id":"B","native_valid_original_rock_class":"OUTSIDE_ROCK_MORE_THAN_2000M",
       "topology_repaired_source_rock_class":"IN_ONE_ROCK",
       "covering_original_native_valid_rock_features":0,
       "covering_source_invalid_but_make_valid_repaired_rock_features":1}
    ]
    try:
        summarize(rows,{"A":{"feature":"island"},"B":{"feature":"island"}},
                  {"A":"POINT_IN_ONE_MAPPED_ROCK",
                   "B":"POINT_OUTSIDE_ROCK_NEAREST_LE250M"},{},{})
    except ValueError as e:
        assert "SOURCE_STOP" in str(e)
    else:
        raise AssertionError("source summary requires frozen original 7785-site cohort")
