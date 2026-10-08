"""Published-only source/effect audit: prevent combining breeding-adult relocations
with prebreeder visits as if they shared an annual settlement denominator.
No new individual data records are opened by these tests.
"""
import json
from pathlib import Path

R = json.loads(
    (
        Path(__file__).resolve().parents[1]
        / "results" / "ROSS_BEAUFORT_STAGE_AND_ACCESS_PRIOR_ART_V5.json"
    ).read_text(encoding="utf8")
)


def test_documented_prior_breeders_cross_island_sightings():
    adult = R["previous_breeding_adults"]
    assert sum(row[1] for row in adult["data"]) == 2681
    assert sum(row[2] for row in adult["data"]) == 5
    assert adult["n_prior_ross_breeders"] == 2681
    assert adult["documented_later_seen_beaufort"] == 5
    assert [row[2] for row in adult["data"]] == [3, 1, 1]
    assert adult["first_time_beaufort_breeders"] is False


def test_table3_resight_does_not_prove_north_shore_reproduction():
    adult = R["previous_breeding_adults"]
    assert adult["beaufort_north_versus_south_resolved"] is False
    assert adult["destination_breeding_status"] == (
        "not_identifiable_from_table3_resighting"
    )
    assert adult["original_breeding_status"] == "bred_at_origin_ross_at_least_once"


def test_different_age_cohorts_are_not_bilateral_dispersal_probabilities():
    young = R["prospective_comparison_young"]
    b2r = R["counterpart_beaufort_to_ross"]
    assert young["bird_banded_young_seen"] == [348, 160]
    assert young["visitors_at_crozier"] == [2, 7]
    assert young["destination_first_breeding_verified"] is False
    assert b2r["directly_comparable_to_2010_prior_breeder_5_out_of_2681"] is False
    assert b2r["first_breeding_destinations"] is False
    assert R["inference_gates"]["adult_move_observations_and_juvenile_visits_share_population_denominator"] == "NO"


def test_access_geometry_is_explicit_competing_mechanism_not_novelty():
    assert "iceberg" in R["prospective_comparison_young"]["established_mechanism"]
    assert "iceberg_obstruction_2001_to_mid_2000s_alters_access_and_prospecting" in (
        R["nuisance_and_rival_mechanisms"]
    )
    assert R["inference_gates"]["source_nesting_options_vs_access_effect_sep"] == "UNIDENTIFIED"
    assert R["new_unopened_individual_data_rows_accessed"] == 0
    assert R["new_claim_of_successful_source_option_causation"] is False
    assert R["literature_reanalysis_is_prospective"] is False
