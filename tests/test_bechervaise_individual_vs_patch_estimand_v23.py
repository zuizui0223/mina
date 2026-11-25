"""No tagged penguin data: only metadata-level source-field eligibility tests."""
import importlib.util,json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("bechv23",ROOT/"scripts/audit_bechervaise_individual_vs_patch_estimand_v23.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def contract():
    return json.loads((ROOT/"contracts/BECHERVAISE_INDIVIDUAL_VS_PATCH_GEOMETRY_V23.json").read_text())

def test_current_source_no_raw_join_and_no_patch_position():
    z=m.inspect(contract())
    a=z["candidate_estimand_gates"]
    assert a["E1_FUTURE_ON_NEST_SCAN"]["status"]=="HOLD_MISSING_OR_UNVERIFIED_SOURCE_FIELDS"
    assert a["E2_FUTURE_FIRST_OWN_EGG"]["status"]=="HOLD_MISSING_OR_UNVERIFIED_SOURCE_FIELDS"
    assert a["E3_FIDELITY_TO_SPECIFIC_PREVIOUSLY_VISITED_NEST_PATCH"]["status"].startswith("SOURCE_DESIGN_")
    assert a["E4_CAUSAL_INTERISLAND_COLONIST_SUPPLY_EFFECT"]["status"].startswith("SOURCE_DESIGN_")
    assert z["source_gate_shared_by_several_subcolonies"]
    assert z["source_nest_scan_is_not_independently_verified_own_egg"]
    assert z["published_2019_same_season_breeder_status_link_prior_art"]
    assert z["published_2022_first_nesting_age_already_in_source"]
    assert z["source_bird_ID_observations_read"]==0
    assert not z["current_causal_mechanism_discovered"]
    assert z["PR189_unchanged"] and z["PR142_unchanged"] and z["PR195_unchanged"]

def test_even_full_gate_nest_tag_record_wont_establish_own_egg_or_prospecting_patch():
    additions={
        "gate_file_bytes":True,
        "nest_resight_file_bytes":True,
        "same_tag_encoding_verified":True,
        "reader_operating_effort_and_tag_at_risk_denominator":True,
        "direct_t_plus_1_same_tag_nest_observation":True,
    }
    z=m.inspect(contract(),additions)
    a=z["candidate_estimand_gates"]
    assert a["E1_FUTURE_ON_NEST_SCAN"]["status"]=="SOURCE_FIELDS_POTENTIALLY_ELIGIBLE_NOT_CAUSAL_VALIDATION"
    assert a["E2_FUTURE_FIRST_OWN_EGG"]["status"]=="HOLD_MISSING_OR_UNVERIFIED_SOURCE_FIELDS"
    assert "direct_own_first_egg_per_tag" in a["E2_FUTURE_FIRST_OWN_EGG"]["currently_missing_fields"]
    assert a["E3_FIDELITY_TO_SPECIFIC_PREVIOUSLY_VISITED_NEST_PATCH"]["status"].startswith("SOURCE_DESIGN_")
    assert a["E4_CAUSAL_INTERISLAND_COLONIST_SUPPLY_EFFECT"]["status"].startswith("SOURCE_DESIGN_")

def test_egg_and_natal_are_an_additional_requirements_beyond_on_nest():
    d={k:True for k in ("gate_file_bytes","nest_resight_file_bytes",
        "same_tag_encoding_verified","reader_operating_effort_and_tag_at_risk_denominator",
        "direct_t_plus_1_same_tag_nest_observation","direct_own_first_egg_per_tag",
        "known_lifetime_prior_breeding_history")}
    z=m.inspect(contract(),d)
    assert z["candidate_estimand_gates"]["E2_FUTURE_FIRST_OWN_EGG"]["status"]=="SOURCE_FIELDS_POTENTIALLY_ELIGIBLE_NOT_CAUSAL_VALIDATION"
    assert z["candidate_estimand_gates"]["E3_FIDELITY_TO_SPECIFIC_PREVIOUSLY_VISITED_NEST_PATCH"]["status"].startswith("SOURCE_DESIGN_")
    assert not z["current_causal_mechanism_discovered"]

def test_cannot_add_nonexistent_species_or_schema_field_by_fiat():
    with pytest.raises(ValueError,match="invented"):
        m.inspect(contract(),{"I_GUESSED_FIRST_EGG":True})
    with pytest.raises(ValueError,match="nonboolean"):
        m.inspect(contract(),{"gate_file_bytes":"TRUE"})
