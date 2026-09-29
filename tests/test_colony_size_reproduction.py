import math

from mina.colony_size_reproduction import (
    build_island_season_sets,
    conditional_multinomial_score_test,
    fit_beta,
    score_at_one,
)


def _rows(island, season, pairs, chicks):
    return [
        {
            "study_name": f"S{season}",
            "time": f"{season + 1}-01-15T00:00:00Z",
            "season": season,
            "island": island,
            "colony_code": str(i + 1),
            "pairs": float(p),
            "chicks": float(c),
            "census_time": "chick",
        }
        for i, (p, c) in enumerate(zip(pairs, chicks))
    ]


def test_proportional_chick_output_has_beta_one():
    rows = _rows("CHR", 2000, [2, 4, 8, 16], [4, 8, 16, 32])
    sets = build_island_season_sets(rows)
    fit = fit_beta(sets)
    assert fit["converged"]
    assert math.isclose(fit["beta_hat"], 1.0, rel_tol=0, abs_tol=1e-10)
    assert math.isclose(score_at_one(sets), 0.0, rel_tol=0, abs_tol=1e-10)


def test_superlinear_chick_output_recovers_beta_two():
    rows = (
        _rows("CHR", 2000, [2, 4, 8, 16], [4, 16, 64, 256])
        + _rows("COR", 2000, [3, 6, 12, 24], [9, 36, 144, 576])
    )
    sets = build_island_season_sets(rows)
    fit = fit_beta(sets)
    assert fit["converged"]
    assert math.isclose(fit["beta_hat"], 2.0, rel_tol=0, abs_tol=1e-9)
    assert score_at_one(sets) > 0


def test_primary_null_is_one_sided_for_superlinear_pattern():
    rows = []
    for season in range(2000, 2004):
        rows += _rows("CHR", season, [2, 4, 8, 16], [4, 16, 64, 256])
    sets = build_island_season_sets(rows)
    result = conditional_multinomial_score_test(
        sets, n_draws=1999, seed=1234
    )
    assert result["observed_score"] > 0
    assert result["one_sided_upper_p"] <= 0.01


def test_sets_require_three_colonies_and_positive_chicks():
    rows = (
        _rows("CHR", 2000, [2, 4], [2, 4])
        + _rows("COR", 2000, [2, 4, 8], [0, 0, 0])
        + _rows("HUM", 2000, [2, 4, 8], [2, 4, 8])
    )
    sets = build_island_season_sets(rows)
    assert len(sets) == 1
    assert sets[0]["island"] == "HUM"
