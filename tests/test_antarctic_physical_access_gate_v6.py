"""Protect causal interpretations of Antarctic physical-access comparisons.

All inputs are published case summaries/metadata, not newly opened penguin
tracking or meteorological outcomes.
"""
import json
from pathlib import Path

D = json.loads(
    (Path(__file__).resolve().parents[1] / "results"
     / "ANTARCTIC_PHYSICAL_ACCESS_GATE_SUPPORT_V6.json").read_text(encoding="utf8")
)


def test_existing_stable_ice_relations_are_classified_as_prior_art():
    a = D["prior_art"]["atka_2013"]
    assert a["observed_penguins_relocated_to_ice_shelf_approx"] == 2000
    assert a["fast_ice_stable"]
    assert a["snow_ramp_and_wind_causation_verified_separately"] is False
    tracks = D["prior_art"]["three_emperor_colonies"]
    assert tracks["atka_on_ice_shelf_years"] == 7
    assert tracks["atka_total_years"] == 8
    assert tracks["atka_fast_ice_early_breakup_in_study_years"] is False


def test_data_alignment_not_claimed_complete():
    d = D["data_sources"]
    assert d["satellite_colony_tracks"]["first_party_shapefile_rows_loaded"] is False
    assert d["neumayer_wind"]["complete_matching_weather_2017_2024_confirmed"] is False
    assert d["ramp_access_state"]["date_specific_physical_ramp_passability_q_observed_independently_for_2017_2024"] is False
    assert d["ramp_access_state"]["movement_not_permitted_as_proxy_for_accessibility"]


def test_physical_landmass_boundary_is_not_assumed_from_sea_ice_group_paths():
    x = D["candidate_tests"]
    assert x["H_ocean_only"].startswith("ALREADY_REFUTED_AS_UNIVERSAL")
    assert x["H_snow_ramp_threshold"].startswith("HOLD")
    assert x["H_local_capacity_retention_affects_natal_first_breeding"] == "NOT_IDENTIFIABLE_FROM_SEA_ICE_COLONY_GROUP_TRACKS"
    assert x["H_neighbor_island_rescue"] == "NOT_IDENTIFIABLE_FROM_SEA_ICE_COLONY_GROUP_TRACKS"


def test_no_new_analysis_or_frozen_manuscript_contamination():
    e = D["execution"]
    assert e["new_colony_position_rows_read"] == 0
    assert e["new_wind_time_series_rows_read"] == 0
    assert e["new_causal_coefficients"] == 0
    assert e["new_inferential_p_values"] == 0
    assert e["new_positive_discovery_claim"] is False
    assert e["PR189_scientific_freeze_unchanged"]
    assert e["PR142_resight_lock_unchanged"]
