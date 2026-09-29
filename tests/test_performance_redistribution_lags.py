from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from mina.performance_redistribution_lags import (
    _study_season,
    load_chick_rows,
    performance_rows,
)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_study_season_uses_pal_identifier() -> None:
    assert _study_season("PAL9192") == 1991
    assert _study_season("PAL9798") == 1997
    assert _study_season("PAL0001") == 2000
    with pytest.raises(ValueError):
        _study_season("PAL9799")


def test_chick_loader_ignores_inconsistent_calendar_date(tmp_path: Path) -> None:
    path = tmp_path / "chicks.csv"
    _write_csv(
        path,
        [
            "study_name",
            "time",
            "island_name",
            "colony_code",
            "num_breeding_pairs",
            "num_chicks",
            "census_time",
        ],
        [
            {
                "study_name": "PAL9798",
                "time": "1997-01-29T00:00:00Z",
                "island_name": "LIT",
                "colony_code": "8.0",
                "num_breeding_pairs": 70,
                "num_chicks": 80,
                "census_time": 1400,
            }
        ],
    )
    rows = load_chick_rows(path)
    assert rows[0]["season"] == 1997


def test_chick_loader_fails_closed_on_study_season_duplicate(tmp_path: Path) -> None:
    path = tmp_path / "chicks.csv"
    row = {
        "study_name": "PAL9798",
        "time": "1998-01-20T00:00:00Z",
        "island_name": "LIT",
        "colony_code": "8.0",
        "num_breeding_pairs": 70,
        "num_chicks": 80,
        "census_time": 1400,
    }
    _write_csv(
        path,
        [
            "study_name",
            "time",
            "island_name",
            "colony_code",
            "num_breeding_pairs",
            "num_chicks",
            "census_time",
        ],
        [row, row],
    )
    with pytest.raises(ValueError, match="duplicate usable chick row"):
        load_chick_rows(path)


def test_performance_state_is_within_island_season_standardized() -> None:
    adults = [
        {"island": "TOR", "colony": "1.0", "year": 2000, "adult_pairs": 10.0},
        {"island": "TOR", "colony": "2.0", "year": 2000, "adult_pairs": 20.0},
        {"island": "TOR", "colony": "3.0", "year": 2000, "adult_pairs": 30.0},
    ]
    chicks = [
        {
            "island": "TOR",
            "colony": "1.0",
            "season": 2000,
            "chicks": 8.0,
            "chick_denominator": 11.0,
        },
        {
            "island": "TOR",
            "colony": "2.0",
            "season": 2000,
            "chicks": 18.0,
            "chick_denominator": 22.0,
        },
        {
            "island": "TOR",
            "colony": "3.0",
            "season": 2000,
            "chicks": 40.0,
            "chick_denominator": 33.0,
        },
    ]
    rows = performance_rows(adults, chicks)
    state = np.asarray([float(row["state"]) for row in rows])
    assert len(rows) == 3
    assert np.mean(state) == pytest.approx(0.0, abs=1e-12)
    assert np.std(state, ddof=1) == pytest.approx(1.0, abs=1e-12)
