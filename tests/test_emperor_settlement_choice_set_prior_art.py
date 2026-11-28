"""Pure published-prior-art consistency guard for PR #195.

Does not open Dryad/BAS biological outcome rows or fit an ecological effect.
"""
import json
import math
from pathlib import Path

R = json.loads(
    (Path(__file__).resolve().parents[1]
     / "results" / "EMPEROR_SETTLEMENT_CHOICE_SET_PRIOR_ART_AUDIT_V2.json").read_text(encoding="utf-8")
)


def test_published_demographic_genetic_prior_art_excludes_new_knowledge_claim():
    a = R["genetic_demographic_model_prior_art"]
    assert a["DIC"]["semi_informed"] < min(a["DIC"]["random"], a["DIC"]["informed"])
    assert a["mean_successful_dispersal_distance_km_model_inferred"] == 414
    assert a["mean_emigration_rate_model_inferred_per_colony_year"] == .157
    assert a["median_emigration_rate_across_colony_years"] == 0
    assert not a["identifies_social_attraction_to_occupied_vs_vacant"]


def test_pub_example_has_fixed_54_existing_colony_nodes_not_new_sites():
    a = R["genetic_demographic_model_prior_art"]["public_code_example"]
    assert a["ncol_literal"] == 54
    assert a["carrying_capacity_expression"] == "K=2*BE"
    assert a["new_suitable_empty_sites_in_choice_set"] is False
    assert a["carrying_capacity_timevarying"] is False


def test_halley_destination_already_breeding_in_2015():
    a = R["halley_dawson_historical_positive_control"]
    assert a["receiver_had_existing_2015_colony"] is True
    assert a["receiver_2015_pairs"] == 1280
    assert a["receiver_2016_pairs"] == 5315
    assert a["receiver_2017_pairs"] == 11117
    assert a["receiver_2018_pairs"] == 14612
    assert a["receiver_increase_2015_to_2018_pairs"] == 13332
    assert math.isclose(a["receiver_ratio_2018_over_2015"], 14612/1280)
    assert a["local_100km_screen_includes_receiver"]
    assert not a["previous_40km_screen_includes_receiver"]


def test_source_distance_is_not_accepted_as_unique_truth():
    a = R["halley_dawson_historical_positive_control"]
    assert a["reported_distance_2019_km"] == 55
    assert a["reported_distance_2025_km"] == 85
    assert 61 < a["geodesic_from_published_coords_km"] < 63
    assert not a["true_vacant_sites_known_to_be_accessible_nearby"]


def test_no_surrogate_successful_rescue_claim():
    a = R["current_source_support"]
    assert a["baseline_labrousse_pseudoabsence_has_true_surveyed_zeros"] is False
    assert a["known_prior_empty_site_and_pre_switch_2022_accessibility_jointly_verified"] is False
    assert a["positive_new_observation_from_this_audit"] is False
    assert R["new_outcome_rows_opened"] == 0
    assert R["new_biological_effect_test_run"] is False
