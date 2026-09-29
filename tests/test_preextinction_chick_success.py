from mina.preextinction_chick_success import (
    event_success_test,
    informative_sets,
    size_success_gradient,
)


def _matched_panel():
    rows = []
    for island, season in [("CHR", 2000), ("COR", 2001), ("HUM", 2002)]:
        rows.extend(
            [
                {
                    "island": island,
                    "colony_code": "small",
                    "season": season,
                    "event_next_year": 1,
                    "adult_prior_count": 2.0,
                    "adult_prior_share": 0.02,
                    "chick_dataset_adult_pairs": 2.0,
                    "chicks": 0.0,
                    "chicks_per_pair": 0.0,
                },
                {
                    "island": island,
                    "colony_code": "mid",
                    "season": season,
                    "event_next_year": 0,
                    "adult_prior_count": 20.0,
                    "adult_prior_share": 0.20,
                    "chick_dataset_adult_pairs": 20.0,
                    "chicks": 20.0,
                    "chicks_per_pair": 1.0,
                },
                {
                    "island": island,
                    "colony_code": "large",
                    "season": season,
                    "event_next_year": 0,
                    "adult_prior_count": 60.0,
                    "adult_prior_share": 0.60,
                    "chick_dataset_adult_pairs": 60.0,
                    "chicks": 90.0,
                    "chicks_per_pair": 1.5,
                },
            ]
        )
    return rows


def test_primary_preextinction_contrast_is_negative_for_low_success_events():
    result = event_success_test(
        _matched_panel(),
        permutations=4999,
        seed=7,
    )
    assert result["estimable"] is True
    assert result["observed_contrast"] < 0
    assert result["supported"] is True


def test_size_success_gradient_is_positive_when_larger_groups_do_better():
    result = size_success_gradient(
        _matched_panel(),
        permutations=4999,
        seed=8,
    )
    assert result["estimable"] is True
    assert result["slope"] > 0
    assert result["supported"] is True


def test_log_and_rank_transforms_remain_directionally_negative():
    rows = _matched_panel()
    log_sets = informative_sets(rows, transform="log1p")
    rank_sets = informative_sets(rows, transform="rank")
    assert all(x["observed_contrast"] < 0 for x in log_sets)
    assert all(x["observed_contrast"] < 0 for x in rank_sets)
