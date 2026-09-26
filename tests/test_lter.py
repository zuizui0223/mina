import csv
import math

from mina.lter import (
    ISLANDS,
    additive_decomposition,
    analyze,
)


def _write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "study_name",
            "time",
            "island_name",
            "colony_code",
            "num_breeding_pairs",
        ])
        writer.writerow(["", "UTC", "", "", "1"])
        writer.writerows(rows)


def test_five_island_synchrony_pipeline(tmp_path):
    path = tmp_path / "census.csv"
    rows = []
    for year in range(2000, 2008):
        shared = 1.0 - 0.05 * (year - 2000)
        for i, island in enumerate(ISLANDS):
            total = (1000 + i * 100) * shared * (1 + 0.01 * i * (year - 2000))
            rows.append([
                f"PAL{str(year)[2:]}{str(year + 1)[2:]}",
                f"{year}-11-15T00:00:00Z",
                island,
                "1.0",
                round(total * 0.6),
            ])
            rows.append([
                f"PAL{str(year)[2:]}{str(year + 1)[2:]}",
                f"{year}-11-15T00:00:00Z",
                island,
                "2.0",
                round(total * 0.4),
            ])
    _write(path, rows)
    result = analyze(path)
    assert result["synchronized_panel"]["n_years"] == 8
    assert result["source_row_count"] == 8 * 5 * 2
    assert len(result["growth_synchrony"]["pairwise_correlations"]) == 10
    assert result["common_component"]["pc1_variance_fraction"] > 0.9
    assert result["additive_decomposition"]["additive_r2"] > 0.9


def test_additive_decomposition_fractions_are_finite():
    years = [2000, 2001, 2002, 2003]
    values = {
        island: __import__("numpy").asarray(
            [1000 - 50 * j + 20 * i for j in range(4)],
            dtype=float,
        )
        for i, island in enumerate(ISLANDS)
    }
    out = additive_decomposition(years, values)
    for value in out.values():
        assert math.isfinite(value)
