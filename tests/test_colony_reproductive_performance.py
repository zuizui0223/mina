import numpy as np

from mina.colony_reproductive_performance import (
    _simulate_allocations,
    primary_size_productivity,
)


def synthetic_rows():
    rows = []
    for season in range(2000, 2015):
        for code, pairs, chicks in (
            ("A", 2, 0),
            ("B", 5, 4),
            ("C", 10, 14),
            ("D", 20, 32),
        ):
            rows.append(
                {
                    "study_name": f"S{season}",
                    "time": f"{season + 1}-01-15T00:00:00Z",
                    "season_start_year": season,
                    "island": "CHR",
                    "colony_code": code,
                    "pairs": pairs,
                    "chicks": chicks,
                    "chicks_per_pair": chicks / pairs,
                    "census_time": "",
                }
            )
    return rows


def test_multivariate_hypergeometric_respects_two_chick_slots():
    rng = np.random.default_rng(7)
    pairs = np.asarray([1, 3, 5], dtype=int)
    draws = _simulate_allocations(rng, pairs, total_chicks=10, size=500)
    assert draws.shape == (500, 3)
    assert np.all(draws >= 0)
    assert np.all(draws <= 2 * pairs[None, :])
    assert np.all(draws.sum(axis=1) == 10)


def test_primary_detects_strong_positive_size_productivity_pattern():
    result = primary_size_productivity(
        synthetic_rows(),
        n_simulations=1999,
        seed=11,
    )
    assert result["estimable"] is True
    assert result["observed_mean_slope"] > 0
    assert result["one_sided_upper_p"] <= 0.05
    assert result["supported"] is True
