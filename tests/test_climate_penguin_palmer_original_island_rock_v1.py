"""Only geometry and source status logic: no real habitat effects."""
import importlib.util
from pathlib import Path
from shapely.geometry import Point,box

TARGET=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/audit_palmer_original_island_rock_v1.py"

def load():
    sp=importlib.util.spec_from_file_location("palmer_island_rock",TARGET)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def test_strict_original_land_point_not_snapped_to_nearest():
    m=load()
    poly=[(17,box(0,0,10,10)),(23,box(11,0,21,10))]
    exact=m.classify(Point(5,5),poly)
    assert exact["category"]=="EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON"
    assert exact["original_land_fid"]==17
    assert m.classify(Point(10.5,5),poly)["category"]=="NEAR_ONLY_HOLD_NOT_EXACT"
    assert m.classify(Point(600,600),poly)["category"]=="HOLD_SITE_POINT_UNMATCHED"
    overlap=m.classify(Point(5,5),[(17,box(0,0,10,10)),(24,box(4,4,12,12))])
    assert overlap["category"]=="HOLD_MULTIPLE_ORIGINAL_MAPPED_LAND_POLYGONS"
    assert overlap["original_land_fid"] is None

def test_original_source_is_pinned_and_not_phenological():
    m=load()
    assert m.COAST_SHA=="66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4"
    assert m.ROCK_SHA=="4d93119052d3c6bf51d20dab218447686e2273e7489e1b63351b69e4bc3d7d8b"
    assert "high_res_polygon_v7_12" in m.COAST_URL
    assert m.NEAR_DIAGNOSTIC_M==250.0
