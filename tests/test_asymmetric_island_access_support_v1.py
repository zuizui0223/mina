"""A single ecological Paper2 goal; no inferred predator absences or false bird controls.

This tests machine-readable identification requirements against verified original
FIBD/SCAR/Antarctic source receipts, NOT a biological effect or confirmation.
"""
import json
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"contracts/ASYMMETRIC_ISLAND_ACCESS_SOURCE_SUPPORT_V1.json"


def load():
    return json.loads(P.read_text(encoding="utf-8"))


def test_hypotheses_are_one_integrated_question_with_competing_modes():
    d=load()
    assert set(d["hypotheses"])=={"H_M","H_F","H_X"}
    assert not d["ecological_effect_fitted_in_this_manifest"]
    assert "predator" in d["ecological_primary_question"].lower() or "mammal" in d["ecological_primary_question"].lower()


def test_source_root_traces_are_real_and_population_denominators_not_transmuted():
    r={x["id"]:x for x in load()["evidence"]}
    assert r["FALKLAND_GOVERNMENT_FIBD"]["original_island_locations_n"]==534
    assert r["FALKLAND_GOVERNMENT_FIBD"]["original_invasive_mammal_record_rows_n"]==1212
    assert r["FALKLAND_GOVERNMENT_FIBD"]["original_bird_source_rows_including_header_n"]==4959
    assert r["FALKLAND_GOVERNMENT_FIBD"]["exact_matched_invasive_rows_n"]==1211
    assert r["FALKLAND_GOVERNMENT_FIBD"]["can_fit_true_predator_impact_now"] is False
    assert r["ANTARCTIC_BAS_HART_NATIVE_NESTS"]["original_georeferenced_penguin_nests_n"]==122139
    assert r["ANTARCTIC_BAS_HART_NATIVE_NESTS"]["flying_seabird_nest_sources_in_same_original_10_CSVs_n"]==0
    assert not r["ANTARCTIC_BAS_HART_NATIVE_NESTS"]["original_empty_nesting_habitat_mask_verified"]


def test_taxon_and_predator_cell_identification_requires_observation_denominators():
    d=load()
    g=d["gates"]
    assert not g["H_M_field_verified_mammal_presence_and_surveyed_absence_both_available"]
    assert not g["H_M_field_matched_bird_guild_within_island_effort_available"]
    assert not g["H_F_flightless_and_flying_nest_surveyed_same_locality_year_effort_available"]
    assert not g["H_F_independent_candidate_unoccupied_breeding_habitat_mask"]
    assert not g["H_X_crossed_access_predator_and_flight_is_identified"]
    r={x["id"]:x for x in d["evidence"]}
    assert r["ANTARCTIC_AADC_SITES"]["original_shared_eligible_regions_n"]==0
    assert r["UK_JNCC_RSPB_SOURCE_PREDATOR"]["JNCC_within_parent_verified_mixed_island_networks_n"]==3


def test_historical_source_overlap_must_not_be_called_new_replication():
    r={x["id"]:x for x in load()["evidence"]}
    assert r["ANTARCTIC_MAPPPD_V5"]["exact_duplicated_original_NZ_reported_observations_n"]==316
    assert r["ANTARCTIC_MAPPPD_V5"]["can_infer_geographically_independent_island_access_effect_now"] is False
    assert r["UK_JNCC_RSPB_SOURCE_PREDATOR"]["can_infer_mammal_impact_now"] is False
    assert r["ANTARCTIC_BAS_HART_NATIVE_NESTS"]["candidate_islands_n"]==3
