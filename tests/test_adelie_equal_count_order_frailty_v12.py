"""Exact history order contrasts remain noncausal even after fixed-count matching."""
import importlib.util
from pathlib import Path
import pytest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/audit_adelie_equal_count_order_frailty_v12.py"
spec=importlib.util.spec_from_file_location("order_frailty_v12",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_histories_equal_count_and_identical_last_outcome():
    assert m.HISTORY_A==(1,0,1)
    assert m.HISTORY_B==(0,1,1)
    assert len(m.HISTORY_A)==len(m.HISTORY_B)==3
    assert sum(m.HISTORY_A)==sum(m.HISTORY_B)==2
    assert m.HISTORY_A[-1]==m.HISTORY_B[-1]==1

def test_iid_quality_cannot_generate_order_effect_when_counts_equal():
    r=m.analyze()["quality_iid"]
    assert r["posterior_high_type_given_101"]==pytest.approx(.8)
    assert r["posterior_high_type_given_011"]==pytest.approx(.8)
    assert r["next_success_given_101"]==pytest.approx(.68)
    assert r["next_success_given_011"]==pytest.approx(.68)
    assert r["apparent_order_difference"]==pytest.approx(0,abs=1e-12)
    assert r["real_outcome_to_outcome_causal_memory"]==0

def test_common_logit_year_effects_still_not_history_order():
    r=m.analyze()["quality_additive_year"]
    assert r["posterior_high_type_given_101"]==pytest.approx(r["posterior_high_type_given_011"])
    assert r["next_success_given_101"]==pytest.approx(r["next_success_given_011"])
    assert abs(r["apparent_order_difference"])<1e-12

def test_year_by_quality_interaction_creates_false_order_signal_without_memory():
    r=m.analyze()["quality_interacting_year"]
    assert r["posterior_high_type_given_101"]==pytest.approx(11/14)
    assert r["posterior_high_type_given_011"]==pytest.approx(3/14)
    assert r["next_success_given_101"]==pytest.approx(9/14)
    assert r["next_success_given_011"]==pytest.approx(5/14)
    assert r["apparent_order_difference"]==pytest.approx(2/7)
    assert r["real_outcome_to_outcome_causal_memory"]==0

def test_failed_survey_or_nonbreeder_not_silently_encoded_as_success_failure():
    with pytest.raises(ValueError):
        m.binary_prob((1,None,1),[.8,.8,.8])
    with pytest.raises(ValueError):
        m.binary_prob((1,0),[.8])
    with pytest.raises(ValueError):
        m.next_probability((1,0,1),[.8]*3,[.2]*4)

def test_synthetic_experiment_has_no_individual_penguin_or_new_biological_results():
    r=m.analyze()
    assert r["individual_penguin_source_data_rows_read"]==0
    assert r["new_Crozier_cohort_outcomes_fitted"]==0
    assert r["no_confirmation_of_true_biological_memory_or_learning"]
    assert r["quality_by_year_interaction_induces_order_dependence_without_any_carryover"]
    assert r["observed_breeding_success_conditional_on_an_attempt_not_survival_or_participation"]
    assert r["Ecology_PR189_unmodified"]
