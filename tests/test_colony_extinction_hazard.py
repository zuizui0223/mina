from mina.colony_extinction_hazard import (
    matched_hazard,
    proportional_thinning_null,
    transition_rows_from_rows,
)


def _row(island, code, year, count):
    return {
        "study_name": f"S{year}",
        "year": year,
        "island": island,
        "colony_code": code,
        "breeding_pairs": float(count),
    }


def test_durable_extinction_requires_no_reappearance():
    rows = []
    for year, a, b, c in [
        (2000, 50, 10, 30),
        (2001, 40, 0, 25),
        (2002, 0, 5, 20),
        (2003, 0, 4, 18),
    ]:
        rows += [
            _row("COR", "A", year, a),
            _row("COR", "B", year, b),
            _row("COR", "C", year, c),
        ]
    out = transition_rows_from_rows(rows)
    lookup = {(r["colony_code"], r["start_year"]): r for r in out}
    assert lookup[("A", 2001)]["durable_extinction"] is True
    assert lookup[("B", 2000)]["durable_extinction"] is False
    assert ("B", 2001) not in lookup


def test_matched_hazard_orders_small_groups_toward_extinction():
    rows = []
    for year, small, large in [
        (2000, 2, 100),
        (2001, 3, 90),
        (2002, 4, 80),
        (2003, 5, 70),
        (2004, 60, 6),
    ]:
        rows.append(
            {
                "island": "COR",
                "colony_code": f"small{year}",
                "start_year": year,
                "current_pairs": float(small),
                "current_share": small / (small + large),
                "durable_extinction": True,
            }
        )
        rows.append(
            {
                "island": "COR",
                "colony_code": f"large{year}",
                "start_year": year,
                "current_pairs": float(large),
                "current_share": large / (small + large),
                "durable_extinction": False,
            }
        )
    result = matched_hazard(rows, ("COR",), n_permutations=999, seed=7)
    assert result["n_informative_strata"] == 5
    assert result["conditional_logit"]["beta_per_sd_log1p_pairs"] < 0
    assert result["conditional_logit"]["odds_ratio_per_sd"] < 1
    assert (
        result["descriptive_risk_set_comparison"]["durable_extinction_events"][
            "median_pairs"
        ]
        < result["descriptive_risk_set_comparison"]["same_stratum_survivors"][
            "median_pairs"
        ]
    )


def test_proportional_thinning_null_detects_excess_zeros():
    rows = []
    for code in ("A", "B", "C"):
        rows.append(_row("COR", code, 2000, 10))
    rows += [
        _row("COR", "A", 2001, 30),
        _row("COR", "B", 2001, 0),
        _row("COR", "C", 2001, 0),
    ]
    result = proportional_thinning_null(
        rows,
        ("COR",),
        n_simulations=1999,
        seed=9,
    )
    assert result["observed_next_year_zero_transitions"] == 2
    assert result["null"]["mean_zero_transitions"] < 1
    assert result["excess_zero_supported"] is True
