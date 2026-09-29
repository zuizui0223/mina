import numpy as np

from mina.small_group_reproductive_success import (
    build_groups,
    combine_test,
    conditional_size_effect,
    simulate_multinomial_contributions,
)


def _rows():
    rows = []
    for island, season in (("CHR", 2000), ("COR", 2000), ("CHR", 2001), ("COR", 2001)):
        pairs = [10.0, 20.0, 40.0, 80.0]
        # Per-pair success rises with group size.
        rates = [0.4, 0.6, 0.9, 1.2]
        for idx, (p, r) in enumerate(zip(pairs, rates)):
            rows.append(
                {
                    "island": island,
                    "season": season,
                    "colony_code": str(idx),
                    "pairs": p,
                    "chicks": float(round(p * r)),
                    "chicks_per_pair": r,
                }
            )
    return rows


def test_positive_size_performance_signal():
    groups = build_groups(_rows())
    assert len(groups) == 4
    assert all(float(g["score"]) > 0 for g in groups)
    effect = conditional_size_effect(groups)
    assert effect["beta_per_within_group_sd_log1p_pairs"] > 0
    assert effect["multiplicative_per_pair_success_per_1sd_larger_group"] > 1


def test_null_simulation_is_centered_and_observed_is_positive():
    groups = build_groups(_rows())
    contributions = simulate_multinomial_contributions(
        groups, n_draws=1999, seed=7
    )
    result = combine_test(groups, contributions)
    assert result["observed_z"] > 0
    assert abs(result["null_mean_z"]) < 0.15
    assert result["one_sided_upper_p"] < 0.05


def test_minimum_pair_filter_rebuilds_groups():
    rows = _rows()
    rows[0]["pairs"] = 1.0
    rows[0]["chicks"] = 0.0
    groups = build_groups(rows, min_pairs=2.0)
    # One CHR:2000 group falls below four colonies and is excluded.
    assert len(groups) == 3
