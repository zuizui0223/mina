import csv
from pathlib import Path

import numpy as np

from mina.concentration_chick_success import (
    circular_shift_test,
    joined_panel,
)


def synthetic_rows():
    patterns = {
        "COR": [1.0, 1.5, 2.2, 3.1, 2.7, 2.0, 1.4, 1.8],
        "HUM": [3.2, 2.8, 2.0, 1.3, 1.7, 2.4, 3.0, 2.6],
        "LIT": [1.8, 2.9, 1.4, 2.5, 3.1, 1.6, 2.7, 2.0],
    }
    abundance = {
        "COR": [120, 118, 111, 109, 104, 98, 94, 90],
        "HUM": [95, 92, 90, 85, 82, 79, 76, 73],
        "LIT": [80, 76, 71, 65, 60, 55, 50, 44],
    }
    rows = []
    years = list(range(2000, 2008))
    for island in ("COR", "HUM", "LIT"):
        logn = np.log(np.asarray(patterns[island], dtype=float))
        z = (logn - logn.mean()) / logn.std(ddof=1)
        for i, year in enumerate(years):
            # Add a shared year effect; the frozen model should remove it.
            year_effect = 0.03 * (i - 3.5)
            success = 1.0 + 0.28 * z[i] + year_effect
            rows.append(
                {
                    "island": island,
                    "year": year,
                    "adult_total": float(abundance[island][i]),
                    "effective_colony_number": float(patterns[island][i]),
                    "active_positive_colonies": 3,
                    "chick_total": success * abundance[island][i],
                    "breeding_success": float(success),
                }
            )
    return rows


def test_partial_neff_coefficient_recovers_positive_signal():
    result = circular_shift_test(
        synthetic_rows(),
        n_permutations=1999,
        seed=17,
    )
    assert result["n_rows"] == 24
    assert result["n_islands"] == 3
    assert result["beta_neff"] > 0.15
    assert 0.0 < result["two_sided_p"] <= 1.0
    assert np.isfinite(result["null_sd"])


def test_joined_panel_uses_adult_island_total_as_denominator(tmp_path: Path):
    adult = tmp_path / "adult.csv"
    chick = tmp_path / "chick.csv"

    adult_rows = [
        {
            "study_name": "S2000",
            "time": "2000-11-01T00:00:00Z",
            "island_name": "COR",
            "colony_code": "1",
            "num_breeding_pairs": 30,
        },
        {
            "study_name": "S2000",
            "time": "2000-11-01T00:00:00Z",
            "island_name": "COR",
            "colony_code": "2",
            "num_breeding_pairs": 70,
        },
    ]
    with adult.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=adult_rows[0].keys())
        writer.writeheader()
        writer.writerows(adult_rows)

    chick_rows = [
        {
            "study_name": "C2001",
            "time": "2001-01-15T00:00:00Z",
            "island_name": "COR",
            "colony_code": "1",
            "num_breeding_pairs": 1,
            "num_chicks": 40,
            "census_time": "Chicks",
        },
        {
            "study_name": "C2001",
            "time": "2001-01-15T00:00:00Z",
            "island_name": "COR",
            "colony_code": "2",
            "num_breeding_pairs": 1,
            "num_chicks": 80,
            "census_time": "Chicks",
        },
    ]
    with chick.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=chick_rows[0].keys())
        writer.writeheader()
        writer.writerows(chick_rows)

    panel = joined_panel(adult, chick, ("COR",))
    assert len(panel) == 1
    assert panel[0]["adult_total"] == 100.0
    assert panel[0]["chick_total"] == 120.0
    assert panel[0]["breeding_success"] == 1.2
    assert np.isclose(panel[0]["effective_colony_number"], 1.0 / (0.3**2 + 0.7**2))
