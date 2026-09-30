from __future__ import annotations

import numpy as np
import pytest

from mina.repro_performance_replication import (
    _event_observed,
    colony_performance,
)


def test_event_observed_excludes_archive_sentinels() -> None:
    assert _event_observed("44")
    assert _event_observed("998")
    assert not _event_observed("")
    assert not _event_observed("NULL")
    assert not _event_observed("0")
    assert not _event_observed("999")


def test_colony_performance_standardizes_within_island_season() -> None:
    nests = []
    for colony, success_count in (("1.0", 4), ("2.0", 2), ("3.0", 0)):
        for nest in range(5):
            nests.append(
                {
                    "season": 2000,
                    "island": "HUM",
                    "colony": colony,
                    "site": "1",
                    "nest": str(nest + 1),
                    "success": int(nest < success_count),
                }
            )
    rows, audit = colony_performance(nests, minimum_nests=5)
    assert len(rows) == 3
    state = np.asarray([float(r["state"]) for r in rows])
    assert np.mean(state) == pytest.approx(0.0, abs=1e-12)
    assert np.std(state, ddof=1) == pytest.approx(1.0, abs=1e-12)
    assert audit["performance_island_seasons"] == 1


def test_colony_performance_drops_island_season_with_lt3_colonies() -> None:
    nests = []
    for colony in ("1.0", "2.0"):
        for nest in range(5):
            nests.append(
                {
                    "season": 2000,
                    "island": "HUM",
                    "colony": colony,
                    "site": "1",
                    "nest": str(nest + 1),
                    "success": nest % 2,
                }
            )
    rows, audit = colony_performance(nests, minimum_nests=5)
    assert rows == []
    assert audit["dropped_island_seasons_with_lt3_colonies"] == [
        {"island": "HUM", "season": 2000}
    ]


def test_minimum_nests_is_per_colony_season() -> None:
    nests = []
    for colony, n in (("1.0", 4), ("2.0", 5), ("3.0", 5), ("4.0", 5)):
        for nest in range(n):
            nests.append(
                {
                    "season": 2000,
                    "island": "HUM",
                    "colony": colony,
                    "site": "1",
                    "nest": str(nest + 1),
                    "success": nest % 2,
                }
            )
    rows, _ = colony_performance(nests, minimum_nests=5)
    assert {r["colony"] for r in rows} == {"2.0", "3.0", "4.0"}
