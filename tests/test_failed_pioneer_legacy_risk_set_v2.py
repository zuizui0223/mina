"""Synthetic-only controls for counterfactual risk set and source taxonomy."""
import importlib.util
from pathlib import Path
import pytest

PATH=Path(__file__).resolve().parents[1]/"scripts/audit_failed_pioneer_legacy_risk_set_v2.py"
spec=importlib.util.spec_from_file_location("failed_pioneer_risk",PATH)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def synthetic():
    sites=[
        {"nestid":"solo1","latitude":"-77.45","longitude":"169.22"},
        {"nestid":"solo2","latitude":"-77.46","longitude":"169.24"},
        {"nestid":"solo3","latitude":"-77.44","longitude":"169.23"},
    ]
    outcomes=[
        {"nestid":"solo1","breeder":"1","cr_confirm":"1"},
        {"nestid":"solo2","breeder":"1","cr_confirm":"0"},
        {"nestid":"solo3","breeder":"0","cr_confirm":"NA"},
        {"nestid":"KEY","breeder":"","cr_confirm":""},
    ]
    return sites,outcomes


def test_no_control_group_can_be_synthesized_from_all_preselected_site_roster():
    sites,outcomes=synthetic()
    r=m.coverage(sites,outcomes,strict=False)
    assert r["source_original_nest_site_count"]==3
    assert r["source_nest_location_outcome_identical_ids"]==3
    assert r["source_breeder_codes"]=={"1":2,"0":1}
    assert r["independently_sampled_physically_available_never_used_patches"]==0
    assert r["nonbreeder_zero_is_not_failed_egg_laying_attempt"]
    assert r["absence_of_crèche_confirmation_not_verified_failure"]
    assert not r["H1_failed_pioneer_vs_H3_static_habitat_identifiable"]
    assert not r["causal_effect_or_new_novel_mechanism_fitted"]


def test_missing_gps_site_invalidated_not_silently_filled():
    sites,outcomes=synthetic()
    sites.pop()
    with pytest.raises(ValueError,match="join"):
        m.coverage(sites,outcomes,strict=False)


def test_repeated_breeders_or_invalid_source_codes_fail():
    sites,outcomes=synthetic()
    outcomes[2]["breeder"]="unknown"
    with pytest.raises(ValueError):
        m.coverage(sites,outcomes,strict=False)
    sites,outcomes=synthetic()
    outcomes[2]["cr_confirm"]="2"
    with pytest.raises(ValueError):
        m.coverage(sites,outcomes,strict=False)


def test_a_nonconfirmed_creche_nest_cannot_be_called_biological_failed():
    sites,outcomes=synthetic()
    v=m.coverage(sites,outcomes,strict=False)
    assert v["source_crèche_direct_observation_codes_in_breeders"]=={
        "confirmed_positive":1,"not_confirmed":1}
    assert v["matched_failed_vs_never_used_risk_set_constructible"] is False
    assert v["no_2022_or_later_penguin_outcome_rows_opened"]
    assert v["frozen_Ecology_PR189_changed"] is False
