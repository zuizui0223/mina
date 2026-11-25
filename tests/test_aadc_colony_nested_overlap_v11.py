"""Synthetic arithmetic tests for post-V10 area-conditional source-polygon overlap."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyze_aadc_colony_nested_overlap_v11 import (
    derive_area_conditional_overlap,report_summary
)


def row(site,region,a,b,intersection,j):
    return {
       "original_site_id":site,
       "original_source_group":region,
       "earlier_season_start_year":"2013",
       "later_season_start_year":"2015",
       "earlier_mapped_colony_area_m2":str(a),
       "later_mapped_colony_area_m2":str(b),
       "mapped_polygon_intersection_area_m2":str(intersection),
       "mapped_overlap_jaccard":str(j)
    }


def test_nested_shrinkage_has_no_spatial_mismatch_beyond_area():
    records=derive_area_conditional_overlap([row("a","HBW",100,40,40,.4)])
    x=records[0]
    assert x["smaller_year_footprint_fully_contained_fraction"]==pytest.approx(1)
    assert x["residual_mapped_spatial_mismatch_beyond_area_ratio"]==pytest.approx(0)
    assert x["maximum_possible_jaccard_conditional_on_area"]==pytest.approx(.4)
    assert x["jaccard_fraction_of_area_constrained_maximum"]==pytest.approx(1)
    assert x["field_site_fidelity_demonstrated"] is False


def test_relocation_same_area_high_mismatch_measured_separately():
    x=derive_area_conditional_overlap([row("b","HBE",100,100,50,1/3)])[0]
    assert x["observed_mapped_area_ratio"]==pytest.approx(1)
    assert x["mapped_jaccard"]==pytest.approx(1/3)
    assert x["smaller_year_footprint_fully_contained_fraction"]==pytest.approx(.5)
    assert x["residual_mapped_spatial_mismatch_beyond_area_ratio"]==pytest.approx(.5)


def test_one_site_repeated_years_not_three_independent_islands():
    records=[
       row("a","HBW",100,50,50,.5),
       row("a","HBW",50,60,40,40/(50+60-40)),
       row("a","HBW",60,40,20,20/(60+40-20)),
       row("b","HBE",100,100,100,1),
    ]
    out=derive_area_conditional_overlap(records)
    receipt,sites=report_summary(out)
    assert receipt["original_site_IDs"]==2
    assert receipt["original_site_year_observation_pairs"]==4
    assert receipt["by_unique_original_site_ID_equal_weight"]["n"]==2
    assert receipt["actual_nest_survival_or_social_site_fidelity_measured"] is False


def test_bad_original_polygon_jaccard_cannot_be_tuned():
    with pytest.raises(ValueError,match="GEOMETRY_STOP"):
        derive_area_conditional_overlap([row("x","HBE",100,10,10,.9)])
