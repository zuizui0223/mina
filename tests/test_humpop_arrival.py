from __future__ import annotations

from datetime import date

import pytest

from mina.humpop_arrival import arrival_endpoints, matched_panel


def test_first_upward_crossing_is_linearly_interpolated() -> None:
    rows = [
        {"season": 2000, "date": date(2000, 10, 1), "colony": "A", "adults": 10.0},
        {"season": 2000, "date": date(2000, 10, 5), "colony": "A", "adults": 30.0},
        {"season": 2000, "date": date(2000, 10, 9), "colony": "A", "adults": 50.0},
    ]
    endpoint = arrival_endpoints(rows, threshold=0.5)[0]
    # Max = 50, threshold count = 25. Crossing from 10 to 30 is
    # 15/20 = 0.75 of the four-day interval: Oct 4 => day 3 from Oct 1.
    assert endpoint["arrival_day"] == pytest.approx(3.0)


def test_non_crossing_curve_is_not_estimable() -> None:
    rows = [
        {"season": 2000, "date": date(2000, 10, 1), "colony": "A", "adults": 30.0},
        {"season": 2000, "date": date(2000, 10, 5), "colony": "A", "adults": 40.0},
        {"season": 2000, "date": date(2000, 10, 9), "colony": "A", "adults": 50.0},
    ]
    assert arrival_endpoints(rows, threshold=0.5) == []


def test_match_uses_exact_colony_code_and_previous_season() -> None:
    adults = [
        {"island": "HUM", "colony": "1.0", "year": 2000, "adult_pairs": 10.0},
        {"island": "HUM", "colony": "2.0", "year": 2000, "adult_pairs": 20.0},
        {"island": "HUM", "colony": "3.0", "year": 2000, "adult_pairs": 30.0},
        {"island": "HUM", "colony": "1", "year": 2000, "adult_pairs": 99.0},
    ]
    performance = [
        {"island": "HUM", "colony": "1.0", "season": 2000, "state": 1.0},
        {"island": "HUM", "colony": "2.0", "season": 2000, "state": 0.0},
        {"island": "HUM", "colony": "3.0", "season": 2000, "state": -1.0},
        {"island": "HUM", "colony": "1", "season": 2000, "state": 9.0},
    ]
    endpoints = [
        {"arrival_season": 2001, "colony": "1.0", "arrival_day": 10.0, "threshold": 0.5, "n_observations": 5, "season_max_adults": 10.0, "first_date": "2001-10-01", "last_date": "2001-10-10"},
        {"arrival_season": 2001, "colony": "2.0", "arrival_day": 11.0, "threshold": 0.5, "n_observations": 5, "season_max_adults": 20.0, "first_date": "2001-10-01", "last_date": "2001-10-10"},
        {"arrival_season": 2001, "colony": "3.0", "arrival_day": 12.0, "threshold": 0.5, "n_observations": 5, "season_max_adults": 30.0, "first_date": "2001-10-01", "last_date": "2001-10-10"},
    ]
    panel, diagnostic = matched_panel(adults, performance, endpoints)
    assert len(panel) == 3
    assert {row["predictor_season"] for row in panel} == {2000}
    lookup = {row["colony"]: row for row in panel}
    assert lookup["1.0"]["state"] == 1.0
    assert "1" not in {row["colony"] for row in panel}
    assert set(diagnostic["exact_code_overlap"]) == {"1.0", "2.0", "3.0"}


def test_minimum_observation_sensitivity_filters_short_curves() -> None:
    rows = [
        {"season": 2000, "date": date(2000, 10, 1), "colony": "A", "adults": 0.0},
        {"season": 2000, "date": date(2000, 10, 5), "colony": "A", "adults": 10.0},
        {"season": 2000, "date": date(2000, 10, 9), "colony": "A", "adults": 20.0},
    ]
    assert len(arrival_endpoints(rows, threshold=0.5)) == 1
    assert arrival_endpoints(rows, threshold=0.5, minimum_observations=4) == []
