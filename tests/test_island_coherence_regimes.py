import csv
import math

from mina.island_coherence_regimes import (
    ALL_ISLANDS,
    PHASES,
    analyze,
    phase_panel,
)


def _fixture(path):
    base = {
        (island, colony): 400.0 + 40.0 * colony
        for island in ALL_ISLANDS
        for colony in range(4)
    }
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.writer(handle)
        w.writerow(
            [
                "study_name",
                "time",
                "island_name",
                "colony_code",
                "num_breeding_pairs",
            ]
        )
        w.writerow(["", "UTC", "", "", "1"])
        for year in range(1991, 2018):
            if year > 1991:
                for k, island in enumerate(ALL_ISLANDS):
                    common = 0.18 * math.sin(0.71 * year + 1.31 * k)
                    for colony in range(4):
                        local = 0.015 * math.sin(
                            1.13 * year + 0.37 * colony + 0.11 * k
                        )
                        base[(island, colony)] = max(
                            1.0,
                            base[(island, colony)]
                            * math.exp(common + local),
                        )
            for island in ALL_ISLANDS:
                for colony in range(4):
                    w.writerow(
                        [
                            f"PAL{year}",
                            f"{year}-11-15T00:00:00Z",
                            island,
                            str(colony + 1),
                            round(base[(island, colony)]),
                        ]
                    )

            # Structured ID-regime discontinuities that should not invalidate
            # phase-specific positive-history completeness.
            if year <= 2006:
                w.writerow(
                    [
                        f"PAL{year}",
                        f"{year}-11-15T00:00:00Z",
                        "CHR",
                        "3.1",
                        max(1, 50 + ((year - 1991) % 5)),
                    ]
                )
                w.writerow(
                    [
                        f"PAL{year}",
                        f"{year}-11-15T00:00:00Z",
                        "TOR",
                        "6.0",
                        max(1, 55 + ((year - 1991) % 7)),
                    ]
                )
            else:
                w.writerow(
                    [
                        f"PAL{year}",
                        f"{year}-11-15T00:00:00Z",
                        "CHR",
                        "11.0",
                        0,
                    ]
                )


def test_phase_panel_excludes_all_zero_admin_code(tmp_path):
    p = tmp_path / "census.csv"
    _fixture(p)
    late = phase_panel(p, PHASES["late_2007_2017"], ALL_ISLANDS)
    assert "11.0" in late["reported_but_never_positive_codes"]["CHR"]
    assert late["validity_pass"] is True


def test_regime_validation_detects_repeated_island_coherence(tmp_path):
    p = tmp_path / "census.csv"
    _fixture(p)
    result = analyze(p, n_permutations=500, seed=14)

    for section in (
        "five_island_phase_replication",
        "four_extant_island_sensitivity",
    ):
        for phase in PHASES:
            x = result[section][phase]
            assert x["validity_pass"] is True
            assert x["observed"]["partition_contrast_r"] > 0
            assert x["null"]["two_sided_p"] <= 0.05

    assert result["decision"]["island_coherence_replicated_across_id_regimes"] is True
    assert result["decision"]["not_litchfield_driven"] is True
    assert result["decision"]["strong_confirmation"] is True
