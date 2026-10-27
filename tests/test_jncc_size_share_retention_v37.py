"""V37 H1a conditional breeding-site share retention on SYNTHETIC data only."""
from __future__ import annotations
import math
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import model_jncc_size_share_retention_v37 as h


def test_larger_baseline_child_increasing_relative_share_positive_score():
    q=h.baseline_size_score([16,8,2],[36,4,1])
    assert q is not None
    assert q["score"] > 0
    assert q["declining"] is False
    assert math.isclose(sum(q["pstar"]),1.0,abs_tol=1e-12)
    assert abs(float(q["pstar"] @ q["size_standardized"])) < 1e-12


def test_larger_baseline_child_losing_relative_share_negative_score():
    q=h.baseline_size_score([16,8,2],[1,16,9])
    assert q is not None
    assert q["score"] < 0


def test_smoothing_keeps_zero_baseline_component_in_support():
    q=h.baseline_size_score([0,10,2],[4,3,1])
    assert q is not None
    assert all(p>0 for p in q["pstar"])
    assert q["declining"]


def test_equal_early_component_sizes_cannot_identify_size_effect():
    assert h.baseline_size_score([3,3,3],[9,1,1]) is None
    # The actual V30 numeric gate forbids N0 < 2; no invented zeros.
    with pytest.raises(ValueError,match="INVALID_TOTAL"):
        h.baseline_size_score([0,0,0],[5,2,2])


def test_arithmetic_null_calibrates_conditional_score_zero():
    q=h.baseline_size_score([30,8,1],[12,10,2])
    sim=h.exact_null_scores(q,np.random.default_rng(20261027))
    assert len(sim)==1999
    assert abs(float(np.mean(sim)))<0.08
    with pytest.raises(ValueError,match="NULL_REPLICATES_NOT_FROZEN"):
        h.exact_null_scores(q,np.random.default_rng(1),1998)


def test_source_model_requires_unmodified_smoothing_and_both_totals():
    with pytest.raises(ValueError,match="SMOOTHING_NOT_FROZEN"):
        h.baseline_size_score([10,3,2],[8,5,1],alpha=0.1)
    with pytest.raises(ValueError,match="INVALID_TOTAL"):
        h.baseline_size_score([10,3,2],[0,0,0])
    with pytest.raises(ValueError,match="SOURCE_COMPONENT_COUNT_INVALID"):
        h.baseline_size_score([10,3],[8,2])


def make_source_panels(nspecies=8,per_species=15):
    out=[]
    units=("AON","AOT","IND")
    for j in range(nspecies):
        for i in range(per_species):
            # 8 species × 15 networks = 120 invented panels/40 masters/unit etc.
            parent=(f"Invented species {j}",f"Source country {i%3}",
                    f"Invented unique master {j}:{i}",units[i%3])
            original=[30,15,5]
            later=[13,5,1] if (i%2)==0 else [8,9,2]
            out.append((parent,original,later))
    return out


def test_synthetic_source_support_report_and_species_weighting():
    result=h.conditional_h1a_analysis(make_source_panels())
    assert result["status"]=="JNCC_V37_FIXED_NULL_BASELINE_SIZE_SHARE_SCORE_COMPUTED"
    assert result["source_support"]["informative_size_panels_declining"]==120
    primary=result["primary_declining_parent_result"]
    assert primary["species_sample_count"]==8
    assert len(primary["species_data"])==8
    assert primary["species_positive_mean_count"]<=8
    assert len(primary["equal_species_score_leave_one_species_out"])==8
    assert 0.0005<=primary["conditional_multinomial_null_upper_tail"]<=1


def test_declining_size_uninformative_panels_stop_without_rescue():
    # 120 synthetic parents pass cardinality but never have varying early site sizes.
    records=[(key,[6,6,6],[2,3,3]) for key,_,_ in make_source_panels()]
    outcome=h.conditional_h1a_analysis(records)
    assert outcome["status"]=="STOP_V37_H1A_INFORMATIVE_SOURCE_GATE"
    assert outcome["source_support"]["informative_size_panels_declining"]==0
