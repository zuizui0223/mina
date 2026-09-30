from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from mina.ross_detection import (
    build_date_observer_proxy,
    build_resight_day_proxy,
    season_start_year,
)


def test_austral_season_mapping_is_frozen() -> None:
    assert season_start_year(date(2010, 10, 1)) == 2010
    assert season_start_year(date(2010, 12, 31)) == 2010
    assert season_start_year(date(2011, 1, 1)) == 2010
    assert season_start_year(date(2011, 3, 31)) == 2010
    assert season_start_year(date(2011, 4, 1)) is None
    assert season_start_year(date(2011, 9, 30)) is None


def _obs(
    individual: str,
    colony: str,
    day: int,
    *,
    observer: str = "AA",
    month: int = 11,
    year: int = 2010,
):
    return {
        "individual_id": individual,
        "colony": colony,
        "date": date(year, month, day),
        "observer": observer,
    }


def test_resight_day_proxy_excludes_focal_individual_dates() -> None:
    observations = [
        _obs("A", "CROZ", 1),
        _obs("FOCAL", "CROZ", 2),
        _obs("B", "CROZ", 3),
        _obs("C", "ROYD", 1),
        _obs("D", "ROYD", 2),
        _obs("E", "BIRD", 1),
        _obs("E", "BIRD", 2),
        _obs("E", "BIRD", 3),
        _obs("E", "BIRD", 4),
    ]
    events = [
        {
            "event_id": "E1",
            "individual_id": "FOCAL",
            "first_breeding_season": 2010,
            "candidate_colonies": ["CROZ", "ROYD"],
        }
    ]
    proxy, dropped = build_resight_day_proxy(observations, events)
    assert dropped == {}
    assert set(proxy["E1"]) == {"CROZ", "ROYD", "BIRD"}
    # CROZ has two non-focal dates, ROYD two, BIRD four.
    assert proxy["E1"]["CROZ"] == pytest.approx(proxy["E1"]["ROYD"])
    assert proxy["E1"]["BIRD"] > proxy["E1"]["CROZ"]
    values = np.asarray(list(proxy["E1"].values()))
    assert np.mean(values) == pytest.approx(0.0, abs=1e-12)
    assert np.std(values, ddof=1) == pytest.approx(1.0, abs=1e-12)


def test_proxy_requires_nonfocal_dates_at_all_three_colonies() -> None:
    observations = [
        _obs("A", "CROZ", 1),
        _obs("A", "ROYD", 1),
        _obs("FOCAL", "BIRD", 1),
        _obs("FOCAL", "BIRD", 2),
    ]
    events = [
        {
            "event_id": "E1",
            "individual_id": "FOCAL",
            "first_breeding_season": 2010,
            "candidate_colonies": ["CROZ", "ROYD"],
        }
    ]
    proxy, dropped = build_resight_day_proxy(observations, events)
    assert proxy == {}
    assert (
        dropped["E1"]
        == "missing_nonfocal_resight_date_in_one_or_more_colonies"
    )


def test_bird_candidate_post_2013_is_fail_closed() -> None:
    observations = [
        _obs("A", "CROZ", 1, year=2014),
        _obs("A", "ROYD", 1, year=2014),
        _obs("A", "BIRD", 1, year=2014),
    ]
    events = [
        {
            "event_id": "E1",
            "individual_id": "FOCAL",
            "first_breeding_season": 2014,
            "candidate_colonies": ["CROZ", "BIRD"],
        }
    ]
    proxy, dropped = build_resight_day_proxy(observations, events)
    assert proxy == {}
    assert dropped["E1"] == "bird_candidate_post_2013"


def test_equal_resight_days_map_to_zero_effort_contrast() -> None:
    observations = []
    for colony in ("CROZ", "ROYD", "BIRD"):
        observations.extend(
            [_obs("A", colony, 1), _obs("B", colony, 3)]
        )
    events = [
        {
            "event_id": "E1",
            "individual_id": "FOCAL",
            "first_breeding_season": 2010,
            "candidate_colonies": ["CROZ", "ROYD", "BIRD"],
        }
    ]
    proxy, dropped = build_resight_day_proxy(observations, events)
    assert dropped == {}
    assert proxy["E1"] == {"CROZ": 0.0, "ROYD": 0.0, "BIRD": 0.0}


def test_january_observations_contribute_to_starting_year_season() -> None:
    observations = []
    for colony in ("CROZ", "ROYD", "BIRD"):
        observations.append(
            _obs("A", colony, 15, month=1, year=2011)
        )
    events = [
        {
            "event_id": "E1",
            "individual_id": "FOCAL",
            "first_breeding_season": 2010,
            "candidate_colonies": ["CROZ", "ROYD"],
        }
    ]
    proxy, dropped = build_resight_day_proxy(observations, events)
    assert dropped == {}
    assert "E1" in proxy


def test_date_observer_proxy_counts_distinct_pairs_and_ignores_empty_observer() -> None:
    observations = [
        _obs("A", "CROZ", 1, observer="AA"),
        _obs("B", "CROZ", 1, observer="BB"),
        _obs("C", "ROYD", 1, observer="AA"),
        _obs("D", "BIRD", 1, observer="AA"),
        _obs("E", "BIRD", 2, observer="AA"),
        _obs("F", "BIRD", 3, observer=""),
    ]
    events = [
        {
            "event_id": "E1",
            "individual_id": "FOCAL",
            "first_breeding_season": 2010,
            "candidate_colonies": ["CROZ", "ROYD"],
        }
    ]
    proxy, dropped = build_date_observer_proxy(observations, events)
    assert dropped == {}
    assert proxy["E1"]["CROZ"] > proxy["E1"]["ROYD"]
    assert proxy["E1"]["BIRD"] == pytest.approx(proxy["E1"]["CROZ"])


def test_unknown_candidate_colony_is_rejected() -> None:
    events = [
        {
            "event_id": "E1",
            "individual_id": "FOCAL",
            "first_breeding_season": 2010,
            "candidate_colonies": ["CROZ", "NOPE"],
        }
    ]
    with pytest.raises(ValueError, match="unknown candidate colony"):
        build_resight_day_proxy([], events)
