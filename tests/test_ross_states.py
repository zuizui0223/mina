from __future__ import annotations

import pytest

from mina.ross_states import (
    annualize_resights,
    banded_breeder_performance,
    build_choice_rows,
    canonical_detection_observations,
    cohort_start_year_from_season,
    first_breeding_choice_events,
    source_eligible_first_breeding_events,
    match_band_inventory,
    season_start_year_from_date,
)


def _inventory(low=100, high=199, colony="ROYD", season="0001"):
    return [{"Low": low, "High": high, "Colony": colony, "Season": season}]


def _obs(band, date, colony, eggs=0, chicks=0):
    return {
        "Band": band,
        "Date": date,
        "Colony": colony,
        "Eggs": eggs,
        "Chicks": chicks,
    }


def test_frozen_oct_mar_season_alignment() -> None:
    assert season_start_year_from_date("10/31/2000") == 2000
    assert season_start_year_from_date("11/20/2000") == 2000
    assert season_start_year_from_date("12/31/2000") == 2000
    assert season_start_year_from_date("01/05/2001") == 2000
    assert season_start_year_from_date("03/15/2001") == 2000
    with pytest.raises(ValueError, match="Oct-Mar"):
        season_start_year_from_date("04/01/2001")


def test_banding_season_and_unique_interval_match() -> None:
    assert cohort_start_year_from_season("9495") == 1994
    assert cohort_start_year_from_season("0001") == 2000
    with pytest.raises(ValueError, match="non-consecutive"):
        cohort_start_year_from_season("9496")

    match = match_band_inventory(150, _inventory())
    assert match is not None
    assert match["natal_colony"] == "ROYD"
    assert match["cohort_start_year"] == 2000

    overlap = _inventory() + [
        {"Low": 140, "High": 160, "Colony": "BIRD", "Season": "0001"}
    ]
    with pytest.raises(ValueError, match="matches 2"):
        match_band_inventory(150, overlap)


def test_pb_to_first_br_to_nb_and_prospecting_candidates() -> None:
    observations = [
        _obs(150, "11/20/2002", "ROYD", 0, 0),
        _obs(150, "12/05/2002", "BIRD", 0, 0),
        _obs(150, "11/15/2003", "BIRD", 1, 0),
        _obs(150, "12/20/2003", "BIRD", 0, 1),
        _obs(150, "11/18/2004", "ROYD", 0, 0),
    ]
    annual = annualize_resights(observations, _inventory())
    lookup = {row["season"]: row for row in annual}
    assert lookup[2002]["state"] == "PB"
    assert lookup[2002]["visited_ross_colonies"] == ["ROYD", "BIRD"]
    assert lookup[2003]["state"] == "BR"
    assert lookup[2003]["breeding_colony"] == "BIRD"
    assert lookup[2003]["breeder_chick_presence"] == 1
    assert lookup[2004]["state"] == "NB"

    events = first_breeding_choice_events(annual)
    assert len(events) == 1
    assert events[0]["candidate_colonies"] == ["ROYD", "BIRD"]
    assert events[0]["chosen_colony"] == "BIRD"
    assert events[0]["natal_colony"] == "ROYD"
    assert events[0]["age_at_first_breeding"] == 3


def test_prior_beaufort_breeding_prevents_later_ross_first_breeding_event() -> None:
    observations = [
        _obs(150, "11/20/2002", "BEAU", 1, 0),
        _obs(150, "11/20/2003", "ROYD", 0, 0),
        _obs(150, "12/01/2003", "BIRD", 0, 0),
        _obs(150, "11/20/2004", "BIRD", 1, 1),
    ]
    annual = annualize_resights(observations, _inventory())
    lookup = {row["season"]: row for row in annual}
    assert lookup[2002]["state"] == "BR"
    assert lookup[2002]["breeding_colony"] == "BEAU"
    assert lookup[2003]["state"] == "NB"
    assert lookup[2004]["state"] == "BR"
    assert first_breeding_choice_events(annual) == []


def test_ambiguous_two_breeding_colonies_fails_closed() -> None:
    observations = [
        _obs(150, "11/20/2002", "CROZ", 1, 0),
        _obs(150, "12/05/2002", "ROYD", 0, 1),
    ]
    annual = annualize_resights(observations, _inventory())
    assert annual[0]["state"] == "AMBIG_BR"
    assert annual[0]["breeding_colony"] is None
    assert first_breeding_choice_events(annual) == []


def test_unknown_chick_checks_do_not_become_failure() -> None:
    observations = [
        _obs(150, "11/20/2003", "ROYD", 1, 9),
        _obs(150, "12/01/2003", "ROYD", 1, 9),
    ]
    annual = annualize_resights(observations, _inventory())
    assert annual[0]["state"] == "BR"
    assert annual[0]["breeder_chick_presence"] is None


def test_banded_breeder_performance_uses_one_binary_value_per_bird() -> None:
    rows = []
    band = 100
    for colony, presences in {
        "CROZ": [1, 1],
        "ROYD": [1, 0],
        "BIRD": [0, 0],
    }.items():
        for presence in presences:
            band += 1
            rows.append(
                {
                    "band": band,
                    "season": 2005,
                    "state": "BR",
                    "breeding_colony": colony,
                    "breeder_chick_presence": presence,
                }
            )
    performance, audit = banded_breeder_performance(
        rows, minimum_eligible_breeders=2
    )
    assert audit["n_eligible_performance_years"] == 1
    assert performance[2005]["CROZ"] == pytest.approx(1.0)
    assert performance[2005]["ROYD"] == pytest.approx(0.0)
    assert performance[2005]["BIRD"] == pytest.approx(-1.0)


def test_choice_rows_attach_prior_performance_natal_and_size() -> None:
    events = [
        {
            "event_id": "150:2006",
            "band": 150,
            "first_breeding_season": 2006,
            "performance_year": 2005,
            "chosen_colony": "BIRD",
            "candidate_colonies": ["ROYD", "BIRD"],
            "natal_colony": "ROYD",
            "cohort_start_year": 2000,
            "age_at_first_breeding": 6,
        }
    ]
    perf = {
        2005: {"CROZ": 1.0, "ROYD": -1.0, "BIRD": 0.0}
    }
    sizes = {
        2005: {"CROZ": 200000.0, "ROYD": 3000.0, "BIRD": 50000.0}
    }
    effort = {
        "150:2006": {"CROZ": -1.0, "ROYD": 0.0, "BIRD": 1.0}
    }
    rows, audit = build_choice_rows(events, perf, sizes, effort)
    assert audit["retained_events"] == 1
    assert len(rows) == 2
    by_colony = {r["candidate_colony"]: r for r in rows}
    assert by_colony["BIRD"]["chosen"] == 1
    assert by_colony["ROYD"]["natal_colony_indicator"] == 1
    assert by_colony["BIRD"]["natal_colony_indicator"] == 0
    assert by_colony["ROYD"]["performance_state"] == -1.0


def test_missing_candidate_control_excludes_whole_event() -> None:
    events = [
        {
            "event_id": "150:2006",
            "first_breeding_season": 2006,
            "performance_year": 2005,
            "chosen_colony": "BIRD",
            "candidate_colonies": ["ROYD", "BIRD"],
            "natal_colony": "ROYD",
            "cohort_start_year": 2000,
            "age_at_first_breeding": 6,
        }
    ]
    perf = {
        2005: {"CROZ": 1.0, "ROYD": -1.0, "BIRD": 0.0}
    }
    effort = {
        "150:2006": {"CROZ": -1.0, "ROYD": 0.0, "BIRD": 1.0}
    }
    rows, audit = build_choice_rows(
        events,
        perf,
        {2005: {"ROYD": 3000.0}},
        effort,
    )
    assert rows == []
    assert audit["retained_events"] == 0
    assert audit["excluded_events"]["150:2006"] == "missing_candidate_colony_size"


def test_canonical_detection_rows_preserve_individual_date_colony_observer() -> None:
    rows = canonical_detection_observations(
        [
            {
                "Band": 150,
                "Date": "11/20/2005",
                "Colony": "ROYD",
                "Eggs": 0,
                "Chicks": 0,
                "Initials": "ABC",
            }
        ]
    )
    assert rows[0]["individual_id"] == "150"
    assert rows[0]["date"].year == 2005
    assert rows[0]["colony"] == "ROYD"
    assert rows[0]["observer"] == "ABC"


def test_source_gate_can_retain_single_candidate_before_choice_gate() -> None:
    events = [
        {
            "event_id": "150:2006",
            "individual_id": "150",
            "first_breeding_season": 2006,
            "performance_year": 2005,
            "chosen_colony": "ROYD",
            "candidate_colonies": ["ROYD"],
            "natal_colony": "ROYD",
            "cohort_start_year": 2000,
            "age_at_first_breeding": 6,
        }
    ]
    perf = {
        2005: {"CROZ": 1.0, "ROYD": -1.0, "BIRD": 0.0}
    }
    sizes = {
        2005: {"CROZ": 200000.0, "ROYD": 3000.0, "BIRD": 50000.0}
    }
    effort = {
        "150:2006": {"CROZ": -1.0, "ROYD": 0.0, "BIRD": 1.0}
    }
    source, audit = source_eligible_first_breeding_events(
        events, perf, sizes, effort
    )
    assert audit["retained_source_events"] == 1
    assert len(source) == 1

    choice_rows, choice_audit = build_choice_rows(
        source, perf, sizes, effort
    )
    assert choice_rows == []
    assert choice_audit["excluded_events"]["150:2006"] == (
        "candidate_count_not_2_to_3"
    )
