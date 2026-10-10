"""Synthetic stage-aware RFID source-denominator tests; no wildlife records."""
from pathlib import Path
import importlib.util
import pytest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/audit_bechervaise_season_phase_selected_entrants_v22.py"
spec=importlib.util.spec_from_file_location("early_risk22",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_first_pre_egg_vs_after_hatch_gate_cohorts_are_different_risk_sets():
    a=m.audit(*m.demo())
    assert a["n_synthetic_tag_seasons_with_gate_in"]==5
    assert a["n_synthetic_gate_in_events"]==6
    assert a["phase_tag_season_counts"]=={
        "PRE_COLONY_FIRST_EGG":2,
        "AFTER_FIRST_COLONY_EGG_PRE_FIRST_HATCH":1,
        "POST_FIRST_COLONY_HATCH":2
    }
    assert a["pre_first_colony_egg_candidates"]==2
    assert a["pre_first_colony_egg_same_tag_direct_own_egg_AFTER_pass"]==1
    assert a["pre_first_colony_egg_direct_egg_not_confirmed"]==1
    assert a["prelay_observed_documented_egg_fraction"]==pytest.approx(.5)
    assert a["prelay_max_documented_egg_fraction_if_ALL_unknown_eggs_revealed"]==1
    assert a["all_phase_naive_documented_postgate_egg_fraction"]==pytest.approx(.4)
    assert a["all_phase_fraction_NOT_a_true_breeding_propensity"]

def test_documented_egg_prior_to_first_seen_gate_not_reclassified_as_post_gate():
    a=m.audit(*m.demo())
    d=next(z for z in a["individual_mock_event_roles"] if z["tag"]=="SYNTH_D")
    assert d["directly_confirmed_own_egg_prior_or_same_time"]
    assert not d["directly_confirmed_own_egg_after_first_pass"]

def test_late_rare_egg_is_not_impossible_and_not_early_cohort():
    a=m.audit(*m.demo())
    e=next(z for z in a["individual_mock_event_roles"] if z["tag"]=="SYNTH_E")
    assert e["phase_of_FIRST_OBSERVED_gate_crossing"]=="POST_FIRST_COLONY_HATCH"
    assert e["directly_confirmed_own_egg_after_first_pass"]
    assert a["after_hatch_possible_late_egg_not_mathematically_impossible"]
    assert a["equal_season_first_colony_egg_not_individual_latest_laying_date"]

def test_unknown_nest_scan_never_computed_as_proven_nonbreeder():
    z=m.audit(*m.demo())
    b=next(x for x in z["individual_mock_event_roles"] if x["tag"]=="SYNTH_B")
    assert b["egg_status_missing_after_first_pass"]
    assert b["tag_observed_at_nest_without_direct_egg"]
    assert z["no_unobserved_eggs_turned_into_false_negatives"]

def test_broken_dates_bad_source_tags_and_missing_anchor_cannot_be_used():
    events,bound=m.demo()
    events[0]["tag"]="ACTUAL_WILDLIFE_TAG_987"
    with pytest.raises(ValueError,match="Actual wildlife"):
        m.audit(events,bound)
    events,bound=m.demo()
    events[0]["time"]="late october 2008"
    with pytest.raises(ValueError,match="full source time"):
        m.audit(events,bound)
    events,bound=m.demo()
    bound["2008/09"]["first_colony_egg_observed"]="2008-12-27T00:00:00"
    with pytest.raises(ValueError,match="predate"):
        m.audit(events,bound)

def test_contract_retains_prior_art_causality_source_stop():
    import json
    root=Path(__file__).resolve().parents[1]
    x=json.loads((root/"contracts/BECHERVAISE_ARRIVAL_PHASE_VS_FIRST_EGG_RISKSET_V22.json").read_text())
    assert x["source_bird_records_read"]==0
    assert x["PR189_science_frozen"]
    assert x["PR142_source_locked"]
    assert x["PR195_unchanged"]
    z=m.audit(*m.demo())
    assert not z["true_same_tag_first_breeding_transition_identified"]
    assert z["source_publisher_and_methods_bechervaise_original_data_rows_read"]==0
    assert z["frozen_Ecology_PR189_unchanged"]
