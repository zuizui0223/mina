"""Synthetic tests only; real source outcomes tested by pinned public CI."""
import importlib.util
from pathlib import Path
import pytest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/audit_cape_crozier_solo_nest_spatial_outcome_join_v1.py"
spec=importlib.util.spec_from_file_location("solo_source",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def source_fixture():
    outcomes=[
        {"nestid":"solo1","breeder":"1","cr_confirm":"1"},
        {"nestid":"solo2","breeder":"0","cr_confirm":"NA"},
        {"nestid":"solo3","breeder":"1","cr_confirm":"0"},
        {"nestid":"KEY","breeder":"","cr_confirm":""},
    ]
    loc=[
        {"nestid":f"solo{i}","latitude":"-77.5",
         "longitude":str(169+i*.001)} for i in (1,2,3)
    ]
    follow=[
        {"nestid":"1","date":"12/3/2022","status":"INC","egg_n":"2","chick_n":""},
        {"nestid":"2","date":"12/2/2022","status":"MT","egg_n":"","chick_n":""},
        {"nestid":"2","date":"12/14/2023","status":"INC","egg_n":"2","chick_n":""},
        {"nestid":"3","date":"1/15/2023","status":"G","egg_n":"","chick_n":"1"},
        {"nestid":"3","date":"","status":"","egg_n":"","chick_n":""},
    ]
    return outcomes,loc,follow


def test_ids_exact_and_2023_dec_temporal_mismatch_protected():
    outcome,loc,follow=source_fixture()
    z=m.audit(outcome,loc,follow,require_original_counts=False)
    assert z["exact_outcome_location_nestid_matches"]==3
    assert z["outcome_table_footer_rows_excluded"]==1
    assert z["followup_source_rows"]==5
    assert z["source_date_after_public_release_rows"]==1
    assert z["raw_active_ids_only_outside_window"]==["2"]
    assert z["raw_detected_active_nest_counts"]=={"all_rows":3,"season_window":2}
    assert z["raw_detected_occupied_nest_counts"]=={"all_rows":3,"season_window":2}
    assert z["author_followup_occupancy_not_a_marked_individual"]


def test_no_missing_gps_no_implicit_outcome_nest_drop():
    outcome,loc,follow=source_fixture()
    loc[2]["longitude"]="NA"
    with pytest.raises(ValueError):
        m.audit(outcome,loc,follow,require_original_counts=False)
    outcome,loc,follow=source_fixture()
    outcome[2]["nestid"]="solo4"
    with pytest.raises(ValueError):
        m.audit(outcome,loc,follow,require_original_counts=False)


def test_future_timestamp_is_not_a_confirmed_2023_bird_event():
    outcome,loc,follow=source_fixture()
    z=m.audit(outcome,loc,follow,require_original_counts=False)
    assert z["out_of_season_2023_rows_may_be_date_typos_not_proven_separate_season"]
    assert not z["new_causal_hypothesis_or_p_values_fitted"]
    assert not z["independent_exogenous_ice_or_access_shift_at_nest"]
    assert z["frozen_ecology_pr189_unchanged"]


def test_canonical_keys_strict_and_no_repeated_key_duplicate():
    assert m.canonical_key("solo23")=="23"
    assert m.canonical_key(" 23 ")=="23"
    assert m.canonical_key("KEY") is None
    outcome,loc,follow=source_fixture()
    outcome.append(dict(outcome[0]))
    with pytest.raises(ValueError):
        m.audit(outcome,loc,follow,require_original_counts=False)
