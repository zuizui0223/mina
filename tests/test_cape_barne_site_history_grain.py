"""Prevent treating 3/6 major colony support as whole-Ross micro-site occupancy."""
import json
from pathlib import Path

RESULT = json.loads((
    Path(__file__).resolve().parents[1]
    / "results/CAPE_BARNE_SITE_TURNOVER_GRAIN_AUDIT_V7.json"
).read_text(encoding="utf8"))


def test_known_positive_1988_and_observed_absence_2001_are_distinct():
    obs=RESULT["published_observations"]
    assert obs[0]["explicit_breeding_nests"] == 5
    assert obs[0]["date"] == "1988-12-01"
    assert obs[2]["survey_visit_no_breeding_pairs_seen"] is True
    assert obs[2]["complete_annual_zero_roster"] is False


def test_royds_count_matrix_does_not_include_cape_barne():
    geo=RESULT["spatial_identity"]
    assert geo["physical_landmass"] == "Ross Island"
    assert geo["separate_physical_island"] is False
    assert geo["in_frozen_royds_bird_crozier_census_roster"] is False
    assert geo["in_frozen_six_aerial_components"] is False
    roster=RESULT["frozen_roster_support"]
    assert roster["major_colony_unit_years"] == 78
    assert roster["major_colony_zero_years"] == 0
    assert roster["six_component_unit_years"] == 156
    assert roster["six_component_zero_years"] == 0


def test_no_unlicensed_interisland_rescue_or_complete_detection_claim():
    d=RESULT["conclusion"]
    assert d["exact_date_of_zero_to_positive_before_1988_known"] is False
    assert d["all_year_1988_to_2001_occupancy_path_identified"] is False
    assert d["five_nests_are_known_immigrants"] is False
    assert d["cross_island_rescue_claim_licensed"] is False
    assert d["site_reoccupation_mechanism_identified"] is False
    assert d["newly_opened_individual_records"] == 0
