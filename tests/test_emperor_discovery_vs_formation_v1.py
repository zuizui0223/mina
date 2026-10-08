"""Tests of actual published record crosswalk and unknown/zero distinction."""
import copy
import json
from pathlib import Path
import importlib.util
import pytest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"external/EMPEROR_FRETWELL_2024_SITE_DETECTION_EVIDENCE_V1.json"
SPEC=importlib.util.spec_from_file_location(
    "emperor_discovery_audit",ROOT/"scripts/audit_emperor_discovery_vs_formation_v1.py"
)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def read_evidence():
    return json.loads(SOURCE.read_text(encoding="utf8"))


def test_four_2024_reported_sites_all_previously_positive_in_archival_imagery():
    result=M.audit(read_evidence())
    assert result["newly_reported_sites"]==4
    assert result["sites_with_verified_positive_image_before_publication"]==4
    assert result["sites_with_at_least_one_positive_image_each_year_2018_to_2022"]==3
    assert result["published_positive_site_years_all_sites"]==16
    assert result["sites_with_verified_repeated_pre_founding_absences"]==0


def test_gipps_visibility_change_does_not_create_first_occurrence():
    evidence=read_evidence()
    site=next(x for x in evidence["four_newly_reported_sites"] if x["id"]=="GIPPS_ICE_RISE")
    assert site["first_reported_positive_year"]==2016
    assert site["disturbance_year"]==2021
    assert site["detectability_change_mentioned_in_source"]
    assert site["confirmed_colony_established_after_disturbance"] is False


def test_umbeashi_not_extant_inventory_not_surveyed_zero():
    result=M.audit(read_evidence())
    record=result["inventory_not_extant_but_subsequently_reappeared_example"]
    assert record["2019_inventory"]=="NOT_EXTANT"
    assert record["published_subsequent_confirmations"]==[2021,2022]
    assert record["known_2019_season_qualified_negative"] is False
    assert record["year_2020_biological_presence"] is None


def test_fails_closed_if_year_before_first_documented_positive():
    evidence=read_evidence()
    evidence["four_newly_reported_sites"][0]["first_reported_positive_year"]=2019
    with pytest.raises(ValueError,match="first positive"):
        M.audit(evidence)


def test_does_not_expose_2026_case_north_as_new_formation():
    data=read_evidence()
    for x in data["recent_new_colonies_2026_excluded_from_2024_four_site_denominator"]:
        assert x["prior_surveyed_zero"]=="NOT_VERIFIED"
    result=M.audit(data)
    assert not result["2026_causal_effect_test_run"]
    assert result["new_2022_plus_observational_data_rows_read"]==0
