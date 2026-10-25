"""Synthetic geometry tests for independent Antarctic functional archipelago.

No penguin census values, occupancy status or source downloads are inspected.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_functional_archipelago_v1 import build_archipelago


def f(identity, geometry):
    return (identity, geometry, {})


def test_cross_land_neighbor_can_be_closer_than_same_land_rock():
    lands = [
        f(5, box(0, 0, 10000, 5000)),
        f(8, box(10200, 0, 12000, 5000)),
    ]
    rocks = [
        f(100, box(9800, 100, 9900, 200)),
        f(101, box(8300, 100, 8400, 200)),
        f(102, box(10300, 100, 10400, 200)),
        f(103, box(9950, 100, 10250, 200)),  # crosses unmatched gap
    ]
    rows, result = build_archipelago(lands, rocks)
    assert result["mapped_land_polygon_n"] == 2
    assert result["mapped_rock_polygon_n"] == 4
    assert result["unambiguous_rock_polygon_n"] == 3
    assert result["within_same_land_rock_patch_pairs_within_radius"] == 1
    assert result["between_different_land_rock_patch_pairs_within_radius"] == 2
    assert result["rocks_with_both_neighborhood_categories"] == 2
    assert result["rocks_with_different_land_neighbor_closer"] == 1
    assert result["disagreement_fraction_conditional_on_both"] == 0.5
    assert rows[0]["nearest_same_land_rock_gap_m"] == pytest.approx(1400)
    assert rows[0]["nearest_different_land_rock_gap_m"] == pytest.approx(400)
    assert rows[0]["different_land_gap_closer_than_same"] is True
    assert rows[1]["nearest_different_land_rock_gap_m"] == pytest.approx(1900)
    assert rows[1]["different_land_gap_closer_than_same"] is False
    assert rows[2]["same_gap_censored_at_radius"] is True
    assert rows[2]["nearest_same_land_rock_gap_m"] is None
    assert rows[3]["assignment_status"] == "HOLD_ROCK_NOT_WHOLE_WITHIN_ONE_LAND"
    assert rows[3]["land_source_feature_id"] is None
    assert rows[3]["nearest_same_land_rock_gap_m"] is None
    assert result["all_original_animal_counts_or_occupancy_opened"] == 0
    assert result["different_land_polygon_implies_open_ocean_barrier"] is False


def test_missing_neighbor_is_censored_not_zero():
    land = [f(0, box(0, 0, 10000, 5000))]
    rock = [f(1, box(100, 100, 200, 200))]
    rows, result = build_archipelago(land, rock)
    assert rows[0]["assignment_status"] == "EXACT_WHOLE_ROCK_ONE_LAND"
    assert rows[0]["nearest_same_land_rock_gap_m"] is None
    assert rows[0]["nearest_different_land_rock_gap_m"] is None
    assert rows[0]["same_gap_censored_at_radius"] is True
    assert rows[0]["different_gap_censored_at_radius"] is True
    assert rows[0]["different_land_gap_closer_than_same"] is None
    assert result["disagreement_fraction_conditional_on_both"] is None


def test_ambiguous_overlapping_lands_never_assigned():
    land = [
        f(1, box(0, 0, 300, 300)),
        f(2, box(100, 0, 400, 300)),
    ]
    rock = [f(7, box(150, 100, 200, 150))]
    rows, _result = build_archipelago(land, rock)
    assert rows[0]["assignment_status"] == "HOLD_MULTIPLE_FULLY_COVERING_LANDS"
    assert rows[0]["land_source_feature_id"] is None


def test_radius_contract_rejects_nonpositive_and_oversized():
    land = [f(1, box(0, 0, 300, 300))]
    rock = [f(1, box(100, 100, 200, 200))]
    for radius in [-1, 0, 20001]:
        with pytest.raises(ValueError, match="GEOMETRY_STOP"):
            build_archipelago(land, rock, radius_m=radius)
