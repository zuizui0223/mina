import numpy as np

from mina.hierarchy_component_audit import (
    _normalized_excess,
    _pairwise_summary,
)


def test_normalized_excess_beta_removes_unit_count_scale():
    assert _normalized_excess(1.2,3)==0.1
    assert _normalized_excess(1.4,5)==0.1


def test_pairwise_summary_identical_series_is_one():
    x=np.asarray([1.0,2.0,3.0,4.0])
    out=_pairwise_summary({"a":x,"b":x.copy(),"c":x.copy()})
    assert out["n_pairs"]==3
    assert abs(out["mean_pairwise_correlation"]-1.0)<1e-12
