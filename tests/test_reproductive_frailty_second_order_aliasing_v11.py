"""Analytical stable quality mixture, not observed penguin outcome."""
import importlib.util
from pathlib import Path
import pytest

SRC=Path(__file__).resolve().parents[1]/"scripts/prove_reproductive_frailty_second_order_aliasing_v11.py"
spec=importlib.util.spec_from_file_location("no_memory_frailty",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_exact_second_lag_signal_with_no_true_state_memory():
    z=m.evaluate()
    a=z["state_sequences"]["previous_success_current_success"]["next_success_probability"]
    b=z["state_sequences"]["previous_failure_current_success"]["next_success_probability"]
    assert a==pytest.approx(13/17)
    assert b==pytest.approx(0.5)
    assert a-b==pytest.approx(9/34)
    assert z["individual_specific_state_memory_parameter"]==0
    assert z["predictive_information_does_not_imply_causal_history"]
    assert not z["new_biological_causal_effect_estimated"]

def test_second_lag_is_also_present_conditioned_on_current_failure():
    z=m.evaluate()
    assert z["apparent_old_success_bonus_given_current_failure"]==pytest.approx(9/34)

def test_source_free_math_does_not_pretend_to_observe_antarctic_penguins():
    z=m.evaluate()
    assert z["actual_penguin_individual_records_read"]==0
    assert not z["observed_wbwa_test_explained_by_this_simulation"]
    assert not z["different_and_independent_island_replication_present"]
    assert z["Ecology_PR189_unchanged"]

def test_invalid_probabilities_and_unobserved_state_are_not_interpretable():
    with pytest.raises(ValueError):
        m.posterior_high([1,0],p_low=0.9,p_high=0.8)
    with pytest.raises(ValueError):
        m.posterior_high([1,None])
    with pytest.raises(ValueError):
        m.posterior_high([])
