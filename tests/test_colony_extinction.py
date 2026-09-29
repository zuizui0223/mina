import csv
from pathlib import Path

import numpy as np

from mina.colony_extinction_hazard import (
    _event_risk_sets,
    build_transitions,
    load_rows,
    standardize_risk_sets,
)
from mina.colony_extinction_zero_boundary import subset_dist


def write_panel(path: Path):
    rows = []
    series = {
        "1": [10, 5, 0, 0, 0],
        "2": [40, 35, 30, 25, 20],
        "3": [8, 4, 0, 3, 2],
    }
    for i, year in enumerate(range(2000, 2005)):
        for code, values in series.items():
            rows.append(
                {
                    "study_name": f"S{year}",
                    "time": f"{year}-11-01T00:00:00Z",
                    "island_name": "CHR",
                    "colony_code": code,
                    "num_breeding_pairs": values[i],
                }
            )
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


def event_sets(path: Path):
    rows = load_rows(path)
    transitions = build_transitions(rows)
    standardized = standardize_risk_sets(transitions)
    return _event_risk_sets(standardized)


def test_durable_zero_excludes_reappearance(tmp_path):
    path = tmp_path / "x.csv"
    write_panel(path)
    rows = load_rows(path)
    transitions = build_transitions(rows)
    events = [row for row in transitions if row["event"]]
    assert len(events) == 1
    assert events[0]["colony_code"] == "1"
    assert events[0]["end_year"] == 2002


def test_event_is_smaller_in_matched_risk_set(tmp_path):
    path = tmp_path / "x.csv"
    write_panel(path)
    risk_sets = event_sets(path)
    assert len(risk_sets) == 1
    assert risk_sets[0]["observed_contrast"] < 0


def test_zero_null_prefers_small_colonies(tmp_path):
    path = tmp_path / "x.csv"
    write_panel(path)
    risk = event_sets(path)[0]
    values, weights, _ = subset_dist(risk, 0.0)
    assert np.isclose(weights.sum(), 1.0)
    assert values[np.argmax(weights)] < 0
