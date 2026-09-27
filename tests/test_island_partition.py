import csv
import math

import numpy as np

from mina.island_partition import (
    ISLANDS,
    _permute_labels_within_strata,
    _size_strata,
    analyze,
)


def _write_compensating_fixture(path, add_incomplete=False):
    states = {
        (island, colony): 200.0 + 20.0 * colony
        for island in ISLANDS
        for colony in range(4)
    }
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "study_name",
                "time",
                "island_name",
                "colony_code",
                "num_breeding_pairs",
            ]
        )
        writer.writerow(["", "UTC", "", "", "1"])
        for year in range(1991, 2018):
            if year > 1991:
                common = 0.05 * math.sin(year)
                for island_index, island in enumerate(ISLANDS):
                    island_shock = common + 0.02 * math.cos(
                        0.4 * year + island_index
                    )
                    compensation = 0.14 * math.sin(
                        0.7 * year + 0.4 * island_index
                    )
                    for colony in range(4):
                        local = compensation if colony % 2 == 0 else -compensation
                        states[(island, colony)] = max(
                            1.0,
                            states[(island, colony)]
                            * math.exp(island_shock + local),
                        )
            for island in ISLANDS:
                for colony in range(4):
                    writer.writerow(
                        [
                            f"PAL{year}",
                            f"{year}-11-15T00:00:00Z",
                            island,
                            str(colony + 1),
                            round(states[(island, colony)]),
                        ]
                    )
            if add_incomplete:
                writer.writerow(
                    [
                        f"PAL{year}",
                        f"{year}-11-15T00:00:00Z",
                        "CHR",
                        "99",
                        10,
                    ]
                ) if year < 2000 else None


def test_island_partition_detects_synthetic_hierarchy(tmp_path):
    census = tmp_path / "census.csv"
    _write_compensating_fixture(census)
    result = analyze(census, n_permutations=500, seed=2)

    assert result["validity_pass"] is True
    assert result["decision"]["island_partition_detected"] is True
    assert result["decision"]["within_island_spatial_insurance_supported"] is True
    assert result["observed"]["hierarchy_gap_phi"] > 0
    assert result["null"]["hierarchy_gap_phi"]["upper_p"] <= 0.05

    for island in ISLANDS:
        v = result["observed"]["wang_loreau_by_group"][island]
        assert np.isclose(v["gamma_cv2"], v["alpha_cv2"] * v["phi"])
        assert np.isclose(v["beta"], 1.0 / v["phi"])


def test_complete_case_rule_is_explicit(tmp_path):
    census = tmp_path / "census.csv"
    _write_compensating_fixture(census, add_incomplete=True)
    result = analyze(census, n_permutations=99, seed=3)

    assert "99" in result["excluded_incomplete"]["CHR"]
    assert result["eligible_group_sizes"]["CHR"] == 4
    assert result["total_unique_codes"]["CHR"] == 5
    assert result["retention_fraction"]["CHR"] == 0.8


def test_stratified_permutation_preserves_group_composition():
    labels = np.asarray(
        ["CHR", "COR", "HUM", "LIT", "TOR"] * 4,
        dtype=object,
    )
    size = np.arange(labels.size, dtype=float)
    strata = _size_strata(size)
    rng = np.random.default_rng(7)
    permuted = _permute_labels_within_strata(labels, strata, rng)

    assert sorted(permuted.tolist()) == sorted(labels.tolist())
    for stratum in sorted(set(strata.tolist())):
        idx = np.flatnonzero(strata == stratum)
        assert sorted(permuted[idx].tolist()) == sorted(labels[idx].tolist())
