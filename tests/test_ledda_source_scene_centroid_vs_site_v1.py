"""Synthetic tests of image center versus genuine nesting footprint separation."""
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1]/"scripts/audit_ledda_source_scene_centroid_vs_site_v1.py"
spec=importlib.util.spec_from_file_location("ledda_scene",PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def synthetic_rows():
    return [{
        "site_id":"LEDD","img_year":str(y),"img_month":"10","img_day":"13",
        "bpresent":"no" if y==2014 else "yes",
        "img_lat":"-74.228","img_long":"-130.784",
        "catalog_id":"synthetic2024"
    } for y in range(2009,2019)]

def test_2014_source_scene_center_cannot_be_reinterpreted_as_nest():
    d=m.audit(synthetic_rows())
    assert d["source_years"]==list(range(2009,2019))
    assert d["focus_2014"]["author_img_date"]=="2014-10-13"
    assert d["focus_2014"]["distance_scene_center_to_reference_km"]["LaRue_static_colony"]==0
    assert 14<d["focus_2014"]["distance_scene_center_to_reference_km"]["Fretwell_2021_colony"]<16
    assert d["image_scene_center_is_not_penguin_center"]
    assert not d["2014_scene_extent_verified"]
    assert not d["2014_Zhang_polygon_verified"]
    assert not d["new_breeding_event_or_migration_claim"]

def test_missing_img_coordinates_are_unknown_not_zeros():
    rows=synthetic_rows()
    rows[5]["img_lat"]="NA"
    out=m.audit(rows)["focus_2014"]
    assert out["image_scene_centroid_lat"] is None
    assert out["distance_scene_center_to_reference_km"]["LaRue_static_colony"] is None

def test_unapproved_year_or_mutated_2014_bird_code_stops():
    rows=synthetic_rows()
    rows[5]["bpresent"]="yes"
    with pytest.raises(ValueError):
        m.audit(rows)
    rows=synthetic_rows()
    rows[0]["img_year"]="2008"
    with pytest.raises(ValueError):
        m.audit(rows)
