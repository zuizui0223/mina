from __future__ import annotations

import numpy as np
import pytest

from mina.performance_memory import (
    _colony_fixed_effects,
    _prepare_permutation_model,
    bridge_panel,
    memory_panel,
)


def test_memory_panel_matches_same_colony_at_future_lag() -> None:
    performance = [
        {"island": "TOR", "colony": "1", "season": 2000, "state": 1.0},
        {"island": "TOR", "colony": "2", "season": 2000, "state": -1.0},
        {"island": "TOR", "colony": "1", "season": 2001, "state": 0.5},
        {"island": "TOR", "colony": "2", "season": 2001, "state": -0.5},
    ]
    panel = memory_panel(performance, 1)
    assert len(panel) == 2
    lookup = {row["colony"]: row for row in panel}
    assert lookup["1"]["past"] == 1.0
    assert lookup["1"]["future"] == 0.5
    assert lookup["2"]["past"] == -1.0
    assert lookup["2"]["future"] == -0.5


def test_fixed_effect_residualization_recovers_positive_within_colony_signal() -> None:
    panel = []
    performance = []
    for colony, shift in (("1", 5.0), ("2", -4.0), ("3", 2.0)):
        for season, x in enumerate((-1.0, 0.0, 1.0), start=2000):
            panel.append(
                {
                    "island": "TOR",
                    "colony": colony,
                    "season": season,
                    "past": x,
                    "future": shift + 0.75 * x,
                }
            )
            performance.append(
                {"island": "TOR", "colony": colony, "season": season, "state": x}
            )
    model = _prepare_permutation_model(
        panel,
        performance,
        x_field="past",
        y_field="future",
        controls=_colony_fixed_effects(panel),
    )
    assert model["observed"] == pytest.approx(0.75)


def test_permutation_null_uses_full_eligible_predictor_group() -> None:
    performance = [
        {"island": "TOR", "colony": "1", "season": 2000, "state": 1.0},
        {"island": "TOR", "colony": "2", "season": 2000, "state": 0.0},
        {"island": "TOR", "colony": "3", "season": 2000, "state": -1.0},
        {"island": "TOR", "colony": "1", "season": 2001, "state": 0.4},
        {"island": "TOR", "colony": "2", "season": 2001, "state": -0.4},
    ]
    panel = memory_panel(performance, 1)
    assert len(panel) == 2
    model = _prepare_permutation_model(
        panel,
        performance,
        x_field="past",
        y_field="future",
        controls=_colony_fixed_effects(panel),
    )
    colonies, values = model["performance_groups"][("TOR", 2000)]
    assert colonies == ["1", "2", "3"]
    assert values.shape == (3,)
    row_indices, source_positions = model["group_rows"][("TOR", 2000)]
    assert row_indices.shape == (2,)
    assert source_positions.shape == (2,)


def test_bridge_panel_uses_tplus1_performance_and_lag2_growth() -> None:
    adults = []
    for colony, counts in {
        "1": [10, 12, 15],
        "2": [20, 18, 16],
        "3": [30, 31, 32],
    }.items():
        for year, count in zip((2000, 2001, 2002), counts):
            adults.append(
                {
                    "island": "TOR",
                    "colony": colony,
                    "year": year,
                    "adult_pairs": float(count),
                }
            )
    performance = [
        {"island": "TOR", "colony": "1", "season": 2000, "state": 1.0},
        {"island": "TOR", "colony": "2", "season": 2000, "state": -1.0},
        {"island": "TOR", "colony": "3", "season": 2000, "state": 0.0},
        {"island": "TOR", "colony": "1", "season": 2001, "state": 0.4},
        {"island": "TOR", "colony": "2", "season": 2001, "state": -0.4},
        {"island": "TOR", "colony": "3", "season": 2001, "state": 0.0},
    ]
    panel = bridge_panel(adults, performance)
    assert len(panel) == 3
    row = next(r for r in panel if r["colony"] == "1")
    assert row["season"] == 2000
    assert row["start_year"] == 2001
    assert row["past"] == 1.0
    assert row["current"] == 0.4
    assert np.isfinite(row["outcome"])
