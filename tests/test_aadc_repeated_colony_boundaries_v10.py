"""No-network tests for frozen V9 AADC repeated GIS source cohort and polygon estimands."""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest
from pyproj import CRS
import shapefile
from shapely.geometry import box

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from derive_aadc_repeated_colony_boundaries_v10 import (
    identify_source_geometry, read_original_geometry, compare_pairs
)


def test_select_13_actual_source_repeat_ids_without_opening_any_geometry():
    path=Path(__file__).resolve().parents[1]/"results"/"ANTARCTIC_SOURCE_BOUNDARY_MANIFEST_V9.json"
    metadata=json.loads(path.read_text(encoding="utf-8"))
    selected,receipt=identify_source_geometry(metadata)
    assert len(selected)==28
    assert len({r["site_id"] for r in selected})==13
    assert receipt["original_colony_polygon_features_read_before_site_selection"]==0
    assert {r["source_group"] for r in selected}=={"HBW","HBE"}
    assert all("2mbuff" in r["original_shape_path"].lower() for r in selected)
    assert receipt["original_site_years_from_paths_only"]["74585"]==[2012,2013,2015,2016]
    assert len({(r["site_id"],r["season_start_year"]) for r in selected})==28


def test_original_polygon_reader_and_prj_sidecars(tmp_path):
    base=tmp_path/"colony"
    with shapefile.Writer(str(base),shapeType=shapefile.POLYGON) as writer:
        writer.field("SITE_ID","C")
        writer.poly([[[0,0],[10,0],[10,10],[0,10],[0,0]]])
        writer.record("X")
    originals={ext:base.with_suffix(ext).read_bytes() for ext in (".shp",".shx",".dbf")}
    originals[".prj"]=CRS.from_epsg(3031).to_wkt().encode()
    geom,meta=read_original_geometry(originals)
    assert geom.area==pytest.approx(100)
    assert meta["original_source_polygon_record_n"]==1
    assert meta["original_union_polygon_components_n"]==1
    assert len(meta["original_polygon_union_wkb_SHA256"])==64
    assert "SITE_ID" in meta["original_DBf_fields"]


def test_polygon_overlap_is_mapped_area_not_individual_bird_colonisation():
    rows=[
        ({"site_id":"11","source_group":"HBW","season_start_year":2013},
         box(0,0,10,10)),
        ({"site_id":"11","source_group":"HBW","season_start_year":2015},
         box(5,0,15,10)),
        ({"site_id":"22","source_group":"HBE","season_start_year":2012},
         box(0,0,10,10)),
        ({"site_id":"22","source_group":"HBE","season_start_year":2015},
         box(0,0,10,10)),
    ]
    result=compare_pairs(rows)
    assert len(result)==2
    r=next(x for x in result if x["original_site_id"]=="11")
    assert r["mapped_overlap_jaccard"]==pytest.approx(1/3)
    assert r["earlier_mapped_area_retained_in_later"]==pytest.approx(.5)
    assert r["later_mapped_area_outside_earlier"]==pytest.approx(.5)
    assert r["later_divided_by_earlier_mapped_area"]==pytest.approx(1)
    assert r["gap_between_observed_seasons_years"]==2
    assert r["mapped_breeding_gain_is_individual_colonisation"] is False
    other=next(x for x in result if x["original_site_id"]=="22")
    assert other["source_same_polygon_geometric_equals"] is True


def test_shrinking_nested_polygons_distinguish_jaccard_from_relative_retention():
    original=box(0,0,20,20)
    later=box(0,0,10,10)
    rows=[
      ({"site_id":"4","source_group":"HBE","season_start_year":2012},original),
      ({"site_id":"4","source_group":"HBE","season_start_year":2013},later)
    ]
    result=compare_pairs(rows)
    assert len(result)==1
    assert result[0]["later_divided_by_earlier_mapped_area"]==pytest.approx(.25)
    assert result[0]["earlier_mapped_area_retained_in_later"]==pytest.approx(.25)
    assert result[0]["later_mapped_area_outside_earlier"]==pytest.approx(0)
    assert result[0]["mapped_overlap_jaccard"]==pytest.approx(.25)
