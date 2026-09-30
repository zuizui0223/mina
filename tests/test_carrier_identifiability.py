from __future__ import annotations

import numpy as np

from mina.carrier_identifiability import (
    carrier_design_rank,
    constrained_transition_rank,
    transition_rank,
    twin_generators,
)


def test_carrier_columns_are_rank_one() -> None:
    result = carrier_design_rank(np.asarray([-1.0, -0.5, 0.5, 1.0]))
    assert result["rank"] == 1
    assert result["nullity"] == 2


def test_unconstrained_transition_has_two_k_dimensional_null_directions() -> None:
    for k in (2, 3, 5, 10):
        result = transition_rank(k)
        assert result["rank"] == k
        assert result["nullity"] == 2 * k


def test_movement_conservation_does_not_identify_carrier() -> None:
    for k in (2, 3, 5, 10):
        without_recruitment = constrained_transition_rank(
            k, include_recruitment=False
        )
        with_recruitment = constrained_transition_rank(
            k, include_recruitment=True
        )
        assert without_recruitment["rank"] == k
        assert without_recruitment["nullity"] == k - 1
        assert with_recruitment["rank"] == k
        assert with_recruitment["nullity"] == 2 * k - 1


def test_twin_generators_are_exactly_observationally_equivalent() -> None:
    result = twin_generators(np.asarray([-1.4, -0.5, 0.2, 0.6, 1.1]))
    assert result["movement_conserves_island_total"]
    assert result["all_attendance_nonnegative"]
    assert result["all_recruitment_nonnegative"]
    assert result["attendance_vs_movement_max_abs_observed_difference"] < 1e-12
    assert result["attendance_vs_recruitment_max_abs_observed_difference"] < 1e-12
