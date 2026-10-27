"""V45 post-result theoretical and synthetic two-epoch measurement diagnostics."""
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import diagnose_jncc_v44_two_epoch_sampling_v45 as v


def test_exact_two_epoch_unbiased_simpson_for_boundary_panels():
    assert v.unbiased_simpson([2, 0, 0]) == 1.0
    assert v.unbiased_simpson([1, 1, 0]) == 0.0
    assert v.both_epoch_unbiased_delta([2, 0, 0], [1, 1, 0]) == -1.0
    with pytest.raises(ValueError,match="N>=2"):
        v.unbiased_simpson([1,0,0])


def test_same_latent_composition_but_two_independent_snapshots_has_negative_legacy_bias():
    p=np.asarray([.5,.3,.2],dtype=float)
    N0=9;N1=80
    rng=np.random.default_rng(20261027)
    old=rng.multinomial(N0,p,size=60000)
    later=rng.multinomial(N1,p,size=60000)
    C0=((old/N0)**2).sum(axis=1)
    C1=((later/N1)**2).sum(axis=1)
    actual_old=(C1-(C0+(1-C0)/N1)).mean()
    theoretical=v.expected_legacy_E_two_snapshot([1]*N0,[1]*N1,p)
    unbiased_early=(old*(old-1)).sum(axis=1)/(N0*(N0-1))
    unbiased_late=(later*(later-1)).sum(axis=1)/(N1*(N1-1))
    assert theoretical < -.03
    assert abs(actual_old-theoretical)<.004
    assert abs((unbiased_late-unbiased_early).mean())<.004


def test_direct_original_legacy_formula_and_unbiased_formula_separate():
    a=[10,7,3];b=[3,3,2]
    raw=v.old_legacy_E(a,b)
    corrected=v.both_epoch_unbiased_delta(a,b)
    assert np.isfinite(raw)
    assert np.isfinite(corrected)
    assert v.old_legacy_E(a,a) < 0  # subtracts late finite count expectation
    assert v.both_epoch_unbiased_delta(a,a)==0


def test_3999_pooled_null_preserves_two_census_n_and_is_reproducible():
    key=("Accessible","Scotland","sample","AON")
    cache={key:{"old":[5,2,1],"late":[2,1,1],"N0":8,"N1":4}}
    p1=v.diagnostic_sim(cache,[key],np.random.default_rng(v.SEED))
    p2=v.diagnostic_sim(cache,[key],np.random.default_rng(v.SEED))
    assert len(p1[key]["E_both"])==3999
    assert np.array_equal(p1[key]["E_both"],p2[key]["E_both"])
    assert np.array_equal(p1[key]["E_legacy"],p2[key]["E_legacy"])


def test_fixed_postresult_support_filter_reports_small_sample_without_inference():
    keys=[
        ("Herring Gull","Scotland","A","AON"),
        ("Black-legged Kittiwake","Scotland","A","AON")
    ]
    net=[{"source_master":("Scotland","A"),"high":[keys[0]],"low":[keys[1]]}]
    score={
        keys[0]:{"E_both":-.1,"N0":10,"N1":5,"k":4,"C0":.3,"species":"Herring Gull","guild":"ACCESSIBLE"},
        keys[1]:{"E_both":+.1,"N0":200,"N1":120,"k":4,"C0":.3,"species":"Black-legged Kittiwake","guild":"CLIFF_PROTECTED"},
    }
    reports=v.numeric_support_diagnostics(net,score)
    assert all(q["eligible_original_Master_networks"]==0 for q in reports.values())
    assert all(q["original_source_gate_10_networks_still_met"] is False for q in reports.values())
    assert v.ORIGINAL_V44_T==-0.10001721634243599
