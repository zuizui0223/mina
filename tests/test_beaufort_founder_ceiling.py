"""Prospective-safe arithmetic tests: no open individual records."""
import importlib.util
import pathlib
import pytest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "beaufort_ceiling",ROOT/"scripts"/"audit_beaufort_founder_ceiling.py"
)
A=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)

def test_optimistic_founder_ceiling_age3():
    d=A.audit()
    assert d["generous_start_1995_breeding_pair_equivalents"]==9.5
    assert d["max_closed_pairs_2004_age3"]==180.5
    assert d["max_closed_pairs_2005_age3"]==266
    assert d["max_closed_pairs_2006_age3"]==389.5
    assert d["closed_founder_ceiling_below_2005_06_even_if_assigned_to_2006"] is True
    assert d["gap_pairs_relative_to_age3_ceiling_if_2006"]==135.5

def test_age2_counterfactual_can_exceed_observation():
    d=A.audit()
    assert d["all_first_breed_age2_sensitivity_upper_2006"]==1368
    q=d["counterfactual_min_age2_share_to_reach_525_by_2006"]
    assert 0.24<q<0.25
    n=A.closed_pairs_upper(until_year=2006,age2_recruit_fraction=q)[2006]
    assert abs(n-525)<1e-6

def test_maturity_delay_never_raises_bound():
    seq3=A.closed_pairs_upper(until_year=2006,min_breeding_age=3)
    seq4=A.closed_pairs_upper(until_year=2006,min_breeding_age=4)
    for year in range(1995,2007):
        assert seq4[year]<=seq3[year]

def test_missing_founder_or_source_not_treated_as_proven_immigration():
    d=A.audit()
    assert "unobserved founding adults" in "|".join(d["alternative_explanations"])
    assert d["decision"]["external_origin_proven"] is False
    assert d["decision"]["within_versus_between_island_origins_identified"] is False
    assert d["decision"]["source_rescue_consequence_identified"] is False

@pytest.mark.parametrize("bad",[
    {"min_breeding_age":1},{"max_chicks_per_pair":-1},
    {"initial_pairs":-1},{"age2_recruit_fraction":1.1},
    {"until_year":1994}
])
def test_reject_invalid_demography(bad):
    with pytest.raises(ValueError):
        A.closed_pairs_upper(**bad)
