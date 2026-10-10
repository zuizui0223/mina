"""Synthetic tagged-entry example. No original AADC wildlife tags accessed."""
import importlib.util
from pathlib import Path
import pytest

SRC=Path(__file__).resolve().parents[1]/"scripts/simulate_bechervaise_tag_to_egg_denominator_v21.py"
spec=importlib.util.spec_from_file_location("tag_egg_synthetic",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_gate_passes_are_not_unique_entrants_and_nest_tags_not_eggs():
    z=m.source_free_event_gate(m.demo_events())
    assert z["n_raw_gate_in_rows"]==5
    assert z["n_unique_tag_seasons_with_gate_in"]==4
    assert z["n_same_tag_direct_egg_AFTER_first_observed_gate_in"]==1
    assert z["n_same_tag_direct_egg_before_or_at_first_gate_in"]==1
    assert z["n_tag_at_nest_but_NO_DIRECT_EGG"]==1
    assert z["n_unobserved_nest_status_given_tag_gate"]==1
    assert z["lower_bound_fraction_with_observed_post_gate_egg"]==0.25
    assert z["upper_bound_fraction_with_unobserved_or_observed_post_gate_egg"]==1
    assert z["past_reproductive_history_of_mock_tags_known"] is False
    assert z["true_first_breeding_transition_identified"] is False

def test_do_not_silently_accept_original_individual_tag_ids():
    samples=m.demo_events()
    samples[0]["mock_tag"]="04534673833"
    with pytest.raises(ValueError,match="SYNTHETIC"):
        m.source_free_event_gate(samples)

def test_zero_gate_entering_people_has_no_defined_denominator():
    with pytest.raises(ValueError,match="No synthetic tagged cohort"):
        m.source_free_event_gate([{"mock_tag":"SYNTH_X","season":"2008/09",
             "time":"2008-11-04T12:00:00","kind":"tag_at_nest"}])

def test_unknown_code_or_year_bad_timestamp_not_invented():
    e=m.demo_events()
    e[0]["kind"]="unknown_encoded_15"
    with pytest.raises(ValueError,match="unknown code"):
        m.source_free_event_gate(e)
    e=m.demo_events()
    e[0]["time"]="November 9"
    with pytest.raises(ValueError,match="full ISO"):
        m.source_free_event_gate(e)

def test_duplicate_gate_rows_cannot_count_as_individual_fresh_arrival():
    events=m.demo_events()
    events.append(dict(events[0]))
    with pytest.raises(ValueError,match="duplicate"):
        m.source_free_event_gate(events)

def test_one_nest_scan_negative_never_proves_no_breeding():
    z=m.source_free_event_gate(m.demo_events())
    assert z["nest_reader_negative_not_verified_no_egg"]
    assert z["same_tag_nest_scan_not_equal_verified_egg"]
    assert z["first_logged_gate_pass_not_first_island_arrival"]
    assert z["no_real_original_Bechervaise_source_bird_rows_loaded"]
    assert z["no_new_causal_result"]

def test_2019_prior_art_and_publisher_access_contract_preserved():
    import json
    c=json.loads((Path(__file__).resolve().parents[1]/
       "contracts/BECHERVAISE_2019_TAG_NEST_PRIOR_ART_AND_ACCESS_V21.json").read_text())
    assert c["key_prior_art"]["individual_identity_link_proven_by_authors"]
    assert c["key_prior_art"]["past_study_also_knew_failed_breeders_with_direct_eggs"]=="yes in subset observed via direct daily nest censuses"
    assert not c["source_download_truth"]["original_gate_crossing_URL_confirmed"]
    assert c["source_animal_rows_read"]==0
    assert c["Pr189_unchanged"] and c["Pr142_unchanged"] and c["Pr195_unchanged"]
