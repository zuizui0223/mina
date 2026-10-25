"""Test independent AADC geographic source-edition QA without biological data."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_aadc_geography_editions_v1 import (
    parse_geo, evaluate_geography, _percentile
)


def test_original_site_comparison_is_not_colonisation_or_extinction():
    old_rows = [
        {"Geog_Site_ID":"ABC","Geog_Site_Latitude":-70.0,"Geog_Site_Longitude":10.0},
        {"Geog_Site_ID":"DEF","Geog_Site_Latitude":-70.0,"Geog_Site_Longitude":10.1},
        {"Geog_Site_ID":"GHI","Geog_Site_Latitude":-71.0,"Geog_Site_Longitude":11.0},
    ]
    new_rows = [
        {"geog_site_id":"ABC","geog_site_latitude":-70.0,"geog_site_longitude":10.0,
         "geog_site_feature":"island"},
        {"geog_site_id":"DEF","geog_site_latitude":-70.0,"geog_site_longitude":10.2,
         "geog_site_feature":"continent"},
        {"geog_site_id":"XYZ","geog_site_latitude":-70.0,"geog_site_longitude":10.0,
         "geog_site_feature":"island"},
    ]
    old, qold = parse_geo(old_rows, old=True)
    new, qnew = parse_geo(new_rows, old=False)
    result = evaluate_geography(old,new)
    assert qold["geographic_site_ids"] == 3
    assert qnew["geographic_site_ids"] == 3
    assert result["common_original_geographic_site_ids"] == 2
    assert result["only_in_2025_original_site_ids"] == 1
    assert result["only_in_2021_original_site_ids"] == 1
    assert result["same_identifier_exactly_identical_latlon"] == 1
    assert result["same_site_id_original_coordinate_shift_bins"]["SHIFT_GT2000M"] == 1
    assert result["source_2025_coordinate_groups_shared_by_multiple_original_site_ids"] == 1
    assert result["source_2025_site_ids_with_nonunique_exact_coordinate_pairs"] == 2
    assert result["new_original_site_id_is_recolonization"] is False
    assert result["penguin_or_other_animal_counts_opened"] == 0


def test_missing_coords_are_missing_not_zero():
    rows=[
        {"geog_site_id":"ONE","geog_site_latitude":None,"geog_site_longitude":150},
        {"geog_site_id":"TWO","geog_site_latitude":-52,"geog_site_longitude":300},
        {"geog_site_id":"THREE","geog_site_latitude":-75.5,"geog_site_longitude":25},
    ]
    m,q = parse_geo(rows,old=False)
    assert q["missing_lat_lon"] == 1
    assert q["invalid_lat_lon"] == 1
    assert q["sites_with_valid_coordinates"] == 1
    assert m["TWO"]["lat"] is None
    assert m["THREE"]["lat"] == -75.5


def test_source_site_identity_duplicate_is_not_silently_merged():
    rows=[
        {"geog_site_id":"C1","geog_site_latitude":-70,"geog_site_longitude":10},
        {"geog_site_id":"c1","geog_site_latitude":-70,"geog_site_longitude":10}
    ]
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        parse_geo(rows,old=False)


def test_percentile_no_fake_zero():
    assert _percentile([],0.5) is None
    assert _percentile([0,100],0.5) == 50
    assert _percentile([0,100],0.9) == pytest.approx(90)
