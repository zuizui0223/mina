"""Regression tests for season-aligned Beaufort founder bounds.

Numbers are deterministic arithmetic, NOT biological immigration estimates.
"""
import importlib.util
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "beaufort_ceiling", ROOT / "scripts" / "audit_beaufort_founder_ceiling.py"
)
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)


def test_season_anchor_and_factual_historic_pairs():
    d = A.audit()
    assert d["observed_north_shore_records"]["1994/95"]["season_start"] == 1994
    assert d["observed_north_shore_records"]["2005/06"]["season_start"] == 2005
    assert d["age3_model"]["observed_2005_06"] == 525
    n = A.closed_pairs_upper(until_year=2006)
    assert n[1994] == 2
    assert n[1995] == 9.5
    assert n[1996] == 9.5
    assert n[1997] == 11  # three Jan-1995 chicks first breed in 1997/98
    assert n[2004] == 194
    assert n[2005] == 285.5
    assert n[2006] == 418


def test_reproduces_conditional_falsification_without_claiming_migration():
    d = A.audit()
    assert d["age3_model"]["shortfall_2005_06_pair_equivalents"] == 239.5
    assert d["age3_model"]["counterfactual_2004_05_shortfall_if_site_matched"] == 266
    assert d["decisions"]["closed_given_complete_1994_95_roster_and_age3"] == "CONTRADICTED"
    assert d["decisions"]["actual_external_immigration_necessary"] == "NOT_IDENTIFIED"
    assert d["decisions"]["minimum_immigrants_inferred"] is False


def test_initial_chicks_and_age_sensitivity():
    d = A.audit()
    assert d["sensitivity"]["four_initial_chicks_instead_of_three_2005_06"] == 292
    assert d["sensitivity"]["first_breed_age4_2005_06"] == 140.5
    assert d["age3_model"]["pairs_2006_07_extra_season"] < 525


def test_unseen_founders_destroy_unconditional_migration_claim():
    d = A.audit()
    early = d["sensitivity"]["earliest_1995_unseen_pair_equivalents_needed_for_525"]
    assert abs(early - (525 - 285.5) / 28) < 1e-12
    assert d["sensitivity"]["ceil_unseen_whole_adults_required_under_perfect_case"] == 18
    n = A.closed_pairs_upper(
        until_year=2005, unseen_breeding_pair_equivalents_1995=early
    )
    assert abs(n[2005] - 525) < 1e-8
    assert d["sensitivity"]["unseen_founders_are_possible_not_estimated"]


def test_age2_shortcut_requires_majority_under_perfect_conditions():
    d = A.audit()
    q = d["sensitivity"]["counterfactual_min_age2_recruit_share_to_reach_525_in_2005"]
    assert .52 < q < .53
    n = A.closed_pairs_upper(until_year=2005, age2_fraction=q)
    assert abs(n[2005] - 525) < 1e-8


def test_age2_recruits_each_birth_cohort_once():
    two = A.closed_pairs_upper(until_year=2005, first_breeding_age=2)
    split = A.closed_pairs_upper(until_year=2005, age2_fraction=1)
    assert two == split
    assert split[2005] == 928


@pytest.mark.parametrize("bad", [
    {"first_breeding_age": 1}, {"max_chicks_per_pair": -1},
    {"initial_pairs_1994": -1}, {"age2_fraction": 1.1},
    {"age2_fraction": float("nan")}, {"until_year": 1993},
    {"unseen_breeding_pair_equivalents_1995": -1},
    {"first_breeding_age": 4, "age2_fraction": .1}
])
def test_invalid_demography_rejected(bad):
    with pytest.raises(ValueError):
        A.closed_pairs_upper(**bad)
