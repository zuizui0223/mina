import math

from mina.concentration_chick_output import (
    _fit,
    adult_states,
    build_panel,
)


def test_effective_colony_number_and_concentration():
    rows = [
        {"island": "CHR", "year": 2000, "code": "1", "count": 50.0},
        {"island": "CHR", "year": 2000, "code": "2", "count": 50.0},
    ]
    state = adult_states(rows)[("CHR", 2000)]
    assert math.isclose(
        state["effective_colony_number"],
        2.0,
    )
    assert math.isclose(
        state["concentration"],
        -math.log(2.0),
    )
    assert math.isclose(
        state["largest_colony_share"],
        0.5,
    )


def test_coverage_gate_uses_adult_counts_for_represented_codes():
    adults = [
        {"island": "CHR", "year": 2000, "code": "1", "count": 90.0},
        {"island": "CHR", "year": 2000, "code": "2", "count": 10.0},
    ]
    chicks = [
        {"island": "CHR", "season": 2000, "code": "1", "chicks": 50.0},
    ]
    assert len(
        build_panel(
            adults,
            chicks,
            coverage_threshold=0.90,
            allowed_islands=("CHR",),
        )
    ) == 1
    assert len(
        build_panel(
            adults,
            chicks,
            coverage_threshold=0.95,
            allowed_islands=("CHR",),
        )
    ) == 0


def test_fixed_effect_fit_recovers_concentration_direction():
    panel = []
    islands = ("CHR", "COR", "HUM")
    for island_index, island in enumerate(islands):
        for time_index, season in enumerate(range(2000, 2006)):
            concentration = (
                -1.5
                + 0.15 * time_index
                + 0.07 * island_index
                + 0.04 * ((time_index + island_index) % 3)
            )
            adult_total = (
                100
                + 10 * time_index
                + 7 * island_index
                + 3 * ((time_index * island_index) % 2)
            )
            log_chicks = (
                4.0
                + 1.8 * concentration
                + 0.3 * math.log1p(adult_total)
                + 0.2 * island_index
                + 0.05 * time_index
            )
            panel.append(
                {
                    "island": island,
                    "season": season,
                    "adult_total_pairs": float(adult_total),
                    "concentration": float(concentration),
                    "largest_colony_share": 0.5,
                    "total_chicks": math.exp(log_chicks) - 1.0,
                }
            )

    fit = _fit(panel, "concentration")
    assert math.isclose(
        fit["coefficient"],
        1.8,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )
