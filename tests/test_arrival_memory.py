from __future__ import annotations

import datetime as dt

import pytest

from mina.arrival_memory import (
    _prepare_model,
    arrival_metrics,
)


def _row(season: int, colony: str, date: str, adults: float):
    return {
        "season": season,
        "date": dt.date.fromisoformat(date),
        "island": "HUM",
        "colony": colony,
        "adults": adults,
    }


def test_arrival_t50_uses_monotone_envelope_and_interpolation() -> None:
    rows = [
        _row(2000, "1.0", "2000-10-01", 10),
        _row(2000, "1.0", "2000-10-05", 20),
        _row(2000, "1.0", "2000-10-09", 15),
        _row(2000, "1.0", "2000-10-13", 60),
        _row(2000, "1.0", "2000-10-17", 100),
        _row(2000, "2.0", "2000-10-01", 5),
        _row(2000, "2.0", "2000-10-05", 10),
        _row(2000, "2.0", "2000-10-09", 30),
        _row(2000, "2.0", "2000-10-13", 60),
        _row(2000, "2.0", "2000-10-17", 100),
    ]
    metrics = arrival_metrics(rows)
    lookup = {r["colony"]: r for r in metrics}
    # Colony 1: Q moves from .2 on Oct 5 to .6 on Oct 13 because the
    # Oct 9 decline is suppressed by the monotone envelope.
    assert lookup["1.0"]["t50"] == pytest.approx(11.0)
    assert sum(float(r["relative_t50"]) for r in metrics) == pytest.approx(0.0)


def test_arrival_duplicate_disagreement_fails_closed() -> None:
    rows = [
        _row(2000, "1.0", "2000-10-01", 10),
        _row(2000, "1.0", "2000-10-01", 11),
        _row(2000, "1.0", "2000-10-05", 20),
        _row(2000, "1.0", "2000-10-09", 30),
        _row(2000, "1.0", "2000-10-13", 40),
        _row(2000, "1.0", "2000-10-17", 50),
    ]
    with pytest.raises(ValueError, match="discordant duplicate"):
        arrival_metrics(rows)


def test_colony_fixed_effect_model_recovers_negative_state_timing_signal() -> None:
    panel = []
    for colony, shift in (("1", 4.0), ("2", -3.0), ("3", 1.5)):
        for season, state in enumerate((-1.0, 0.0, 1.0), start=2000):
            panel.append(
                {
                    "colony": colony,
                    "season": season,
                    "state": state,
                    "zsize": 0.0,
                    "relative_t50": shift - 1.25 * state,
                }
            )
    model = _prepare_model(panel, "relative_t50")
    assert model["observed"] == pytest.approx(-1.25)


def test_frozen_source_repair_excludes_pal9293_before_duplicate_check() -> None:
    rows = [
        _row(1992, "2.1", "1992-10-13", 3),
        _row(1992, "2.1", "1992-10-13", 6),
        _row(1992, "2.1", "1992-10-15", 24),
        _row(1992, "2.1", "1992-10-18", 85),
        _row(1992, "2.1", "1992-10-22", 103),
        _row(1992, "2.1", "1992-10-24", 211),
    ]
    assert arrival_metrics(rows) == []
