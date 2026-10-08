"""Frozen published image annotations, not independent habitat/cause evidence."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/"scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0,str(SCRIPTS))
SPEC=importlib.util.spec_from_file_location(
    "annotated_emperor_fastice", SCRIPTS/"audit_larue_2024_annotation_ice_bird_state_v1.py"
)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
D=json.loads((ROOT/"results/EMPEROR_LARUE_AUTHOR_NO_IMAGE_ICE_BIRD_ANNOTATIONS_V1.json").read_text(encoding="utf8"))


def test_source20_and_three_explicit_ice_states():
    assert D["original_2009_2018_usable_and_unusable_image_records"] == 599
    assert D["raw_bpresent_categories"] == {"yes":502,"no":20,"NA":77}
    assert D["literal_no_rows"] == 20
    assert D["literal_no_annotation_categories"] == {
        M.ICE_ABSENT:4,M.ICE_PRESENT:3,M.ICE_UNRESOLVED:13
    }
    assert len(D["literal_no_observations"]) == 20
    assert D["literal_no_rows_eligible_basic_original_date_area_filters"] == 15
    assert all(not x["independent_fast_ice_absence_or_presence_verified"]
               for x in D["literal_no_observations"])


@pytest.mark.parametrize("note,expected",[
    ("no fast ice",M.ICE_ABSENT),
    ("Ice has broken out already October where colony was",M.ICE_ABSENT),
    ("fast ice available no birds",M.ICE_PRESENT),
    ("fast ice available",M.ICE_PRESENT),
    ("ice shelf looks like it's breaking up?",M.ICE_UNRESOLVED),
    ("No penguins were evident",M.ICE_UNRESOLVED),
    ("Cannot see birds",M.ICE_UNRESOLVED),
])
def test_ice_state_classification_literal_annotation_only(note,expected):
    assert M.state_from_no({"bpresent":"no","comments":note}) == expected


def test_comment_not_published_ice_measure():
    with pytest.raises(ValueError,match="Only literal No"):
        M.state_from_no({"bpresent":"yes","comments":"fast ice available"})
    with pytest.raises(ValueError,match="contradictory"):
        M.state_from_no({"bpresent":"no","comments":"no fast ice; fast ice available"})


def test_ledda_same_site_ice_present_but_birds_unseen_and_ice_gone():
    assert D["Ledda_explicit_no_fast_ice_years"] == [2009,2012,2016]
    assert D["Ledda_explicit_fast_ice_present_and_no_birds_years"] == [2011,2014,2015]
    assert D["Ledda_fast_ice_present_no_birds_in_original_basic_fit_years"] == [2011,2014]
    assert D["Ledda_years_raw_bpresent_yes"] == [2010,2013,2017]
    assert len(D["Ledda_2009_to_2018_annual_sequence"]) == 10
    assert D["Ledda_immediate_no_fast_ice_to_raw_yes_both_original_date_area_eligible"] == 2
    assert D["Ledda_immediate_available_ice_no_birds_to_raw_yes_both_original_date_area_eligible"] == 0
    assert D["Ledda_next_observed_year_raw_yes_after_prior_explicit_no_fast_ice"]["episodes"] == 3
    assert D["Ledda_next_observed_year_raw_yes_after_prior_explicit_ice_present_no_birds"]["episodes"] == 0


def test_late_2015_and_early_2016_not_original_fitted_negative():
    v={int(x["year"]):x for x in D["Ledda_2009_to_2018_annual_sequence"]}
    assert v[2011]["passes_basic_original_fit_filter"]
    assert v[2014]["passes_basic_original_fit_filter"]
    assert not v[2015]["passes_basic_original_fit_filter"]
    assert not v[2016]["passes_basic_original_fit_filter"]
    assert not v[2017]["passes_basic_original_fit_filter"]


def test_no_code_or_yes_area_does_not_prove_bird_presence():
    assert D["literal_no_rows_nonzero_penguin_area"] == [
        {"site_id":"SANA","date":"2012-09-24","area_m2":93}
    ]
    assert {x["site_id"] for x in D["literal_yes_rows_zero_penguin_area"]} == {
        "AMUN","FOLD","LAZA"
    }
    assert D["new_causal_effect_estimated"] is False


def test_author_date_area_eligibility_only():
    a={"img_month":"10","area_m2":"0","remove":""}
    assert M.fits_basic_original_window(a)
    a["img_month"]="11"
    assert not M.fits_basic_original_window(a)
    a["area_m2"]="10"
    assert M.fits_basic_original_window(a)
    a["remove"]="exclude"
    assert not M.fits_basic_original_window(a)
