"""V38 new descriptive metrics on invented JNCC-like counts; NO actual outcomes."""
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import analyze_jncc_hierarchy_turnover_v38 as d


def test_new_leader_can_raise_concentration_while_original_largest_loses():
    # 30 old leading > 15 old second. The second captures all later counted units.
    m=d.decomposition([30,15,5],[0,20,0])
    assert m["E_positive"] is True
    assert m["S_negative"] is True
    assert m["S_informative"] is True
    assert m["leader_switch"] is True
    assert m["initial_leader_share_change"] < 0


def test_unique_leader_tie_is_missing_not_forced_switch():
    assert d.leader([2,2,1]) is None
    assert d.leader([2,3,1]) == 1
    m=d.decomposition([10,10,4],[5,3,1])
    assert m["both_leaders_unique"] is False
    assert m["leader_switch"] is None


def test_simulated_null_uses_exact_later_total_and_same_events():
    m=d.decomposition([30,15,5],[0,20,0])
    z=d.simulate_events(m,np.random.default_rng(20261028))
    assert len(z["Epos"])==1999
    assert len(z["A"])==1999
    assert len(z["B"])==1999
    assert z["B_denominator"].shape==(1999,)
    with pytest.raises(ValueError,match="FROZEN_V38_REPLICATES"):
        d.simulate_events(m,np.random.default_rng(1),2000)


def test_equal_original_sites_no_H1_score_and_no_forced_site_winner():
    m=d.decomposition([5,5,5],[0,12,0])
    assert m["S_informative"] is False
    assert m["S"] is None
    assert m["early_leader_unique"] is False
    z=d.simulate_events(m,np.random.default_rng(20261028))
    assert z["A"] is None
    assert len(z["Epos"])==1999


def test_no_trajectory_which_increased_total_is_permitted_in_declining_primary():
    with pytest.raises(ValueError,match="V38_PRIMARY_COHORT_MUST_BE_DECLINING"):
        d.decomposition([30,8,2],[50,10,10])


def test_known_fixed_true_share_counterexample_shows_measurement_regression():
    x=d.simulation_counterexample()
    assert x["simulated_independent_censuses_no_change_in_underlying_site_shares"]
    assert x["simulated_negative_size_score_average"] < 0
    assert x["this_is_not_a_fitted_model_of_real_JNCC_counting_error"]


def test_post_result_metric_species_equal_rate_is_fixed_and_not_cherrypicked():
    scores={"A":3,"B":0}
    den={"A":5,"B":5}
    nums={"A":np.full(1999,2,dtype=float),"B":np.full(1999,1,dtype=float)}
    dens={"A":np.full(1999,5,dtype=float),"B":np.full(1999,5,dtype=float)}
    res=d._summary_event(scores,den,nums,dens)
    assert res["observed_all_valid_panels_count"]==3
    assert res["observed_all_valid_panels_denominator"]==10
    assert res["observed_species_equal_fraction"]==.3
    assert np.isclose(res["null_species_equal_mean"],.3)
