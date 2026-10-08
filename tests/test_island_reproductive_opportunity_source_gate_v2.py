"""Contract integrity: never turn disjoint Antarctic data into spatial-fitness claims."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"contracts/ISLAND_REPRODUCTIVE_OPPORTUNITY_VS_SUCCESS_SOURCE_GATE_V2.json"


def test_all_source_gates_are_explicit_hold():
    d=json.loads(DOC.read_text())
    assert d["decision"]=="HOLD_NEST_HABITAT_FITNESS_JOIN_AND_IDENTIFICATION"
    assert len(d["candidate_independent_data_join"])==6
    for z in d["candidate_independent_data_join"]:
        assert z["eligibility"].startswith("HOLD_"),z["source_id"]
        assert z.get("source_id")
    assert d["actual_new_biological_outcome_rows_read"]==0
    assert d["causal_model_fitted"] is False
    assert d["new_positive_island_ecology_mechanism_established"] is False


def test_no_wrong_grain_join_or_misleading_fitness():
    d=json.loads(DOC.read_text())
    sources={x["source_id"]:x for x in d["candidate_independent_data_join"]}
    assert sources["AAD_Bechervaise_2000_nest_points"]["reproductive_outcome_at_same_nest_id"]=="NOT_DEMONSTRATED"
    assert sources["AAD_Bechervaise_1990_2005_success"]["join_to_AAD_Bechervaise_2000_nest_points"]=="NOT_SUPPORTED"
    assert sources["NOAA_Hinke_nest_camera_1977_2017"]["per_nest_coordinates"]=="NOT_ADVERTISED_BY_PUBLISHED_REPRO_ENTITY"
    assert sources["AADC_Windmill_2011_2021_behaviour"]["eligibility"]=="HOLD_ACCESS_AND_ALREADY_TESTED_MECHANISM"
    assert sources["BAS_Signy_1978_2020"]["eligibility"]=="HOLD_SOURCE_ACCESS_AND_DEMOGRAPHIC_ORIGIN"
    assert any("whole-island chick totals" in x for x in d["forbidden_shortcuts"])


def test_core_scientific_submission_and_pre_registered_data_untouched():
    d=json.loads(DOC.read_text())
    assert "PR189" in d["branch_scope"]
    assert d["minimum_new_data_before_fitting"]
    assert all(k in d["stage_specific_independent_endpoint_requirements"]
        for k in ("pre_choice_habitat","settlement","reproductive_fitness","recruitment_debt","identity"))
