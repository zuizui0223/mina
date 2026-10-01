from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from mina.repro_redistribution import (
    _positive_event,
    load_repro,
    repro_states,
    redistribution_panel,
    prepare_model,
)


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    fields = [
        "studyName", "Island", "Colony", "Site Number", "Nest Number",
        "Egg 1 Lay Date", "Egg 2 Lay Date", "Egg 1 Loss Date", "Egg 2 Loss Date",
        "Chick 1 Hatch Date", "Chick 2 Hatch Date",
        "Chick 1 Loss Date", "Chick 2 Loss Date",
        "Chick 1 Creche Date", "Chick 2 Creche Date", "Notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _row(colony: str, site: int, nest: int, c1: object, c2: object) -> dict[str, object]:
    return {
        "studyName": "PAL0001",
        "Island": "HUM",
        "Colony": colony,
        "Site Number": site,
        "Nest Number": nest,
        "Egg 1 Lay Date": "",
        "Egg 2 Lay Date": "",
        "Egg 1 Loss Date": "",
        "Egg 2 Loss Date": "",
        "Chick 1 Hatch Date": "",
        "Chick 2 Hatch Date": "",
        "Chick 1 Loss Date": "",
        "Chick 2 Loss Date": "",
        "Chick 1 Creche Date": c1,
        "Chick 2 Creche Date": c2,
        "Notes": "",
    }


def test_creche_semantic_repair_counts_only_positive_values() -> None:
    assert _positive_event("107") == 1
    assert _positive_event("1") == 1
    assert _positive_event("0") == 0
    assert _positive_event("") == 0
    assert _positive_event("NULL") == 0


def test_duplicate_nest_keys_fail_closed_by_exclusion(tmp_path: Path) -> None:
    path = tmp_path / "repro.csv"
    duplicate = _row("1.0", 1, 1, 100, 100)
    unique = _row("1.0", 1, 2, 100, 0)
    _write(path, [duplicate, duplicate, unique])
    rows, audit = load_repro(path)
    assert len(rows) == 1
    assert rows[0]["nest"] == "2"
    assert audit["duplicate_nest_keys"] == 1
    assert audit["rows_excluded_by_duplicate_rule"] == 2


def test_repro_state_is_standardized_within_island_season() -> None:
    rows = []
    for colony, successes in {
        "1.0": [2, 2, 2, 2, 2],
        "2.0": [1, 1, 1, 1, 1],
        "3.0": [0, 0, 0, 0, 0],
    }.items():
        for nest, value in enumerate(successes, start=1):
            rows.append({
                "season": 2000,
                "island": "HUM",
                "colony": colony,
                "site": "1",
                "nest": str(nest),
                "creched_chicks": value,
            })
    states, audit = repro_states(rows)
    z = np.asarray([float(r["state"]) for r in states])
    assert len(states) == 3
    assert audit["eligible_island_seasons"] == 1
    assert np.mean(z) == pytest.approx(0.0, abs=1e-12)
    assert np.std(z, ddof=1) == pytest.approx(1.0, abs=1e-12)


def test_lag1_panel_uses_next_year_growth_and_current_size() -> None:
    states = [
        {"island": "HUM", "colony": "1.0", "season": 2000, "state": 1.0, "n_nests": 5, "success": 2.0},
        {"island": "HUM", "colony": "2.0", "season": 2000, "state": 0.0, "n_nests": 5, "success": 1.0},
        {"island": "HUM", "colony": "3.0", "season": 2000, "state": -1.0, "n_nests": 5, "success": 0.0},
    ]
    adults = []
    for colony, pair in {
        "1.0": (10.0, 15.0),
        "2.0": (20.0, 18.0),
        "3.0": (30.0, 25.0),
    }.items():
        adults.extend([
            {"island": "HUM", "colony": colony, "year": 2000, "adult_pairs": pair[0]},
            {"island": "HUM", "colony": colony, "year": 2001, "adult_pairs": pair[1]},
        ])
    panel, audit = redistribution_panel(adults, states, lag=1)
    assert len(panel) == 3
    assert audit["predictor_island_seasons"] == 1
    row = next(r for r in panel if r["colony"] == "1.0")
    assert row["start_year"] == 2000
    assert row["prior_size"] == 10.0
    assert np.isfinite(row["relative_growth"])


def test_permutation_source_group_can_exceed_complete_case_panel() -> None:
    # Panel has 50 rows to satisfy the frozen information gate, but one
    # predictor group contains an additional eligible colony missing from the
    # adult outcome. The permutation source must retain that colony.
    states = []
    panel = []
    for season in range(2000, 2010):
        for idx, colony in enumerate(("1.0", "2.0", "3.0", "4.0", "5.0", "6.0")):
            states.append({
                "island": "HUM",
                "colony": colony,
                "season": season,
                "state": float(idx - 2.5 + 0.07 * (season - 2000) * (idx - 1.5)),
                "n_nests": 5,
                "success": float(idx),
            })
            if colony == "6.0":
                continue
            panel.append({
                "island": "HUM",
                "colony": colony,
                "season": season,
                "state": float(idx - 2.5 + 0.07 * (season - 2000) * (idx - 1.5)),
                "n_nests": 5,
                "success": float(idx),
                "predictor_group": f"HUM:{season}",
                "start_year": season,
                "prior_size": float(10 + idx),
                "growth": 0.01 * idx,
                "relative_growth": 0.01 * (idx - 2),
                "z_prior_size": float(idx - 2),
            })
    model = prepare_model(panel, states)
    colonies, values = model["all_groups"][("HUM", 2000)]
    assert len(colonies) == 6
    assert values.shape == (6,)
    rows, positions = model["group_rows"][("HUM", 2000)]
    assert len(rows) == 5
    assert len(positions) == 5
