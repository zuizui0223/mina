"""Synthetic source-free tests for V46 two-epoch leader and baseline size null."""
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_leader_turnover_two_epoch_v46 as m


def test_source_endpoint_counts_unchanged_from_original_V38():
    assert m.SOURCE_DECLINING == 959
    assert m.SOURCE_SIZE_INFORMATIVE == 955
    assert m.SOURCE_EPOS == 597
    assert m.SOURCE_EPOS_SIZE_NEG == 321
    assert m.SOURCE_LEAD_BOTH_UNIQUE == 846
    assert m.SOURCE_LEAD_SWITCH == 412
    assert m.SOURCE_EPOS_AND_SWITCH == 284
    assert m.R == 1999


def test_fixed_latent_site_shares_could_change_observed_leader():
    rng=np.random.default_rng(m.SEED)
    sim=m._null_from_pooled_multinomial([9,8,1],[5,4,2],rng)
    assert len(sim["switched"]) == m.R
    assert np.all(~sim["switched"] | sim["eligible_unique"])
    assert sim["switched"].sum() > 0
    assert np.all(
        ~sim["joint_E_legacy_positive_and_switched"] | sim["switched"]
    )
    assert np.all(
        ~sim["joint_E_both_positive_and_switched"] | sim["switched"]
    )


def test_fixed_composition_two_census_independent_sim_produces_negative_old_size_score():
    rng=np.random.default_rng(1008)
    score=m._null_from_pooled_multinomial([22,11,7],[10,7,3],rng)
    valid=score["score_S_valid"]
    assert valid.sum()>1950
    assert np.isfinite(score["score_S"][valid]).all()
    assert score["score_S"][valid].mean() < 0


def test_tied_synthetic_leaders_do_not_become_false_site_replacements():
    rng=np.random.default_rng(33)
    sim=m._null_from_pooled_multinomial([2,1,0],[1,0,1],rng)
    assert (~sim["eligible_unique"]).sum()>0
    assert (~sim["score_S_valid"]).sum()>0
    assert not np.any(sim["switched"] & ~sim["eligible_unique"])


def test_both_epoch_simulation_is_deterministic_and_rejects_sample_size_tuning():
    x=m._null_from_pooled_multinomial([5,2,1],[2,1,1],np.random.default_rng(m.SEED))
    y=m._null_from_pooled_multinomial([5,2,1],[2,1,1],np.random.default_rng(m.SEED))
    for k in x:
        assert np.array_equal(x[k],y[k],equal_nan=True)
    with pytest.raises(ValueError,match="FROZEN_MC"):
        m._null_from_pooled_multinomial([5,2,1],[2,1,1],np.random.default_rng(m.SEED),replicates=99)


def test_conditional_distribution_summary_uses_valid_replicates_only():
    a=np.linspace(0,1,m.R)
    observed=.5
    r=m._stats(a,observed)
    assert r["null_replicates_valid"] == m.R
    assert .49 <= r["conditional_model_tail_fraction_not_field_error_calibrated_p_value"] <= .51
    assert r["null_replicates_valid"] == m.R
