from __future__ import annotations

import csv
from pathlib import Path

from mina.colony_extinction import (
    build_risk_rows,
    durable_extinctions,
    event_bearing_risk_sets,
    permutation_test,
)


def _series():
    return {
        ("CHR", "a"): {1991: 2.0, 1992: 0.0, 1993: 0.0, 1994: 0.0},
        ("CHR", "b"): {1991: 20.0, 1992: 18.0, 1993: 16.0, 1994: 15.0},
        ("CHR", "c"): {1991: 40.0, 1992: 35.0, 1993: 30.0, 1994: 28.0},
        ("COR", "a"): {1991: 3.0, 1992: 0.0, 1993: 0.0, 1994: 0.0},
        ("COR", "b"): {1991: 30.0, 1992: 28.0, 1993: 25.0, 1994: 24.0},
        ("COR", "c"): {1991: 60.0, 1992: 58.0, 1993: 54.0, 1994: 50.0},
    }


def test_durable_extinction_requires_followup_and_no_reappearance():
    series = _series()
    series[("HUM", "x")] = {1991: 5.0, 1992: 0.0, 1993: 4.0, 1994: 0.0}
    events = durable_extinctions(series, min_later_censuses=2)
    assert events[("CHR", "a")] == 1992
    assert events[("COR", "a")] == 1992
    assert ("HUM", "x") not in events


def test_small_groups_give_negative_matched_contrast():
    series = _series()
    events = durable_extinctions(series, min_later_censuses=2)
    rows = build_risk_rows(series, events, islands=("CHR", "COR"))
    risk_sets = event_bearing_risk_sets(rows)
    assert len(risk_sets) == 2
    assert all(group["contrast"] < 0 for group in risk_sets)
    test = permutation_test(risk_sets, n_permutations=999, seed=7)
    assert test["observed_contrast"] < 0


def test_risk_set_requires_adjacent_observation():
    series = {
        ("CHR", "a"): {1991: 2.0, 1993: 0.0, 1994: 0.0, 1995: 0.0},
        ("CHR", "b"): {1991: 20.0, 1993: 18.0, 1994: 17.0, 1995: 16.0},
    }
    events = durable_extinctions(series, min_later_censuses=2)
    rows = build_risk_rows(series, events, islands=("CHR",))
    assert not any(row["end_year"] == 1993 for row in rows)
