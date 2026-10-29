"""No-animal original Landsat auto-rock source geometry tests."""
from __future__ import annotations

import csv
import io
import hashlib
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile

import pytest
from pyproj import CRS
import shapefile
from shapely.geometry import Point,Polygon,mapping

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_auto_landsat_rock_geography_v6 import (
    CATS, classify_shapes, categorise,source_extract_shapefile,
    summarize,load_old_source_crosswalk,OLD_CROSSWALK_SHA,
)


class SyntheticShape:
    shapeType=shapefile.POLYGON
    def __init__(self,polygon):
        self.bbox=polygon.bounds
        self.__geo_interface__=mapping(polygon)


def test_nearest_rock_containment_and_censored_distance():
    points=[Point(0,0),Point(110,0),Point(1000,0),Point(10000,0)]
    shapes=[SyntheticShape(Polygon([(-10,-10),(10,-10),(10,10),(-10,10)])),
            SyntheticShape(Polygon([(90,-10),(100,-10),(100,10),(90,10)]))]
    rows,qa=classify_shapes(shapes,["a","b","c","d"],points)
    assert [r["independent_landsat_2020_mapped_rock_category"] for r in rows]==[
        "IN_ONE_ROCK","OUTSIDE_ROCK_NEAR_250M",
        "OUTSIDE_ROCK_250_TO_2000M","OUTSIDE_ROCK_MORE_THAN_2000M"]
    assert rows[0]["covering_landsat_rock_source_feature_count"]==1
    assert rows[1]["nearest_landsat_rock_gap_m_within_2km"]==pytest.approx(10)
    assert rows[2]["nearest_landsat_rock_gap_m_within_2km"]==pytest.approx(900)
    assert rows[3]["nearest_landsat_rock_gap_m_within_2km"] is None
    assert qa["source_shapefile_record_shapes"]==2


def test_overlapping_original_rock_polygons_and_invalid_source_hold():
    points=[Point(0,0),Point(3400,0)]
    good1=SyntheticShape(Polygon([(-20,-20),(20,-20),(20,20),(-20,20)]))
    good2=SyntheticShape(Polygon([(-15,-15),(15,-15),(15,15),(-15,15)]))
    invalid=SyntheticShape(Polygon([(3300,-20),(3420,20),(3300,20),(3420,-20)]))
    # Self-intersecting polygon is not silently interpreted as absence.
    rows,qa=classify_shapes([good1,good2,invalid],["a","b"],points)
    assert rows[0]["independent_landsat_2020_mapped_rock_category"]=="IN_MULTIPLE_ROCKS"
    assert rows[1]["independent_landsat_2020_mapped_rock_category"]=="HOLD_INVALID_NEAR_SITE"
    assert qa["SOURCE_INVALID_GEOMETRY_WITHIN_2KM_SITE_WINDOW"]==1


def test_cross_map_agreement_is_about_locations_not_penguin_response():
    new=[
        {"original_geographic_site_id":"a","independent_landsat_2020_mapped_rock_category":"IN_ONE_ROCK"},
        {"original_geographic_site_id":"b","independent_landsat_2020_mapped_rock_category":"IN_ONE_ROCK"},
        {"original_geographic_site_id":"c","independent_landsat_2020_mapped_rock_category":"OUTSIDE_ROCK_MORE_THAN_2000M"},
    ]
    sites={k:{"feature":"island" if k!="c" else "continent"} for k in ("a","b","c")}
    old={"a":"POINT_IN_ONE_MAPPED_ROCK",
         "b":"POINT_OUTSIDE_ROCK_NEAREST_LE250M",
         "c":"POINT_IN_ONE_MAPPED_ROCK"}
    r=summarize(new,sites,{"a","c"},old)
    assert r["new_independent_landsat_exact_point_in_rock_sites"]==2
    assert r["old_original_2025_manual_rock_exact_point_in_rock_sites"]==2
    assert r["new_exact_site_centres_missed_by_old_manual_rock"]==1
    assert r["old_exact_sites_missed_by_new_auto_rock"]==1
    assert r["animal_P_A_NRs_or_penguin_abundance_opened"]==0


def test_original_shapefile_CRS_and_zip_slip_safety(tmp_path):
    source_dir=tmp_path/"src"
    source_dir.mkdir()
    base=source_dir/"rock"
    with shapefile.Writer(str(base),shapeType=shapefile.POLYGON) as writer:
        writer.field("source","C")
        writer.poly([[[-10,-10],[10,-10],[10,10],[-10,10],[-10,-10]]])
        writer.record("Landsat")
    base.with_suffix(".prj").write_text(CRS.from_epsg(3031).to_wkt(),encoding="utf-8")
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w") as z:
        for ext in (".shp",".dbf",".shx",".prj"):
            p=base.with_suffix(ext)
            z.write(p,arcname=p.name)
    shp,receipt=source_extract_shapefile(buf.getvalue(),tmp_path/"ok")
    assert shp.exists()
    assert receipt["original_source_CRS"]=="EPSG:3031"
    with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as z:
        original=z.read("rock.shp")
    malicious=io.BytesIO()
    with zipfile.ZipFile(malicious,"w") as z:
        z.writestr("../bad.shp",original)
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        source_extract_shapefile(malicious.getvalue(),tmp_path/"bad")


def test_invalid_distance_is_no_source_zero():
    assert categorise(float("inf"),0,False)=="OUTSIDE_ROCK_MORE_THAN_2000M"
    assert categorise(float("inf"),0,True)=="HOLD_INVALID_NEAR_SITE"
