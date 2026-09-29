import math

import numpy as np

from mina.colony_extinction_hazard import (
    build_transitions,
    exchangeable_test,
    size_conditioned_neutral_test,
)


def _series(island, code, values, start=2000):
    return [
        {
            "study_name": f"S{year}",
            "year": year,
            "island": island,
            "colony_code": code,
            "count": float(value),
        }
        for year, value in zip(
            range(start, start + len(values)), values
        )
    ]


def test_durable_zero_is_event_but_temporary_zero_is_not():
    rows = (
        _series("CHR", "A", [5, 4, 0, 0, 0])
        + _series("CHR", "B", [10, 10, 9, 8, 7])
        + _series("CHR", "C", [8, 7, 0, 3, 2])
    )
    transitions = build_transitions(rows)
    lookup = {
        (row["colony_code"], row["end_year"]): row["event"]
        for row in transitions
    }
    assert lookup[("A", 2002)] == 1
    assert lookup[("C", 2002)] == 0


def test_unresolved_terminal_zero_is_right_censored():
    rows = (
        _series("CHR", "A", [5, 4, 0])
        + _series("CHR", "B", [10, 9, 8])
    )
    transitions = build_transitions(rows)
    assert ("A", 2002) not in {
        (row["colony_code"], row["end_year"])
        for row in transitions
    }


def test_exchangeable_signal_can_fail_size_conditioned_neutral_gate():
    standardized = []
    prior = np.asarray([1.0, 100.0, 200.0, 300.0])
    log_prior = np.log1p(prior)
    z = (log_prior - np.mean(log_prior)) / np.std(
        log_prior, ddof=1
    )
    for year in (2001, 2002, 2003):
        current = [0.0, 5.0, 5.0, 5.0]
        for index, (p, c, zz) in enumerate(
            zip(prior, current, z)
        ):
            standardized.append(
                {
                    "island": "CHR",
                    "colony_code": str(index),
                    "end_year": year,
                    "prior_count": float(p),
                    "current_count": c,
                    "event": 1 if index == 0 else 0,
                    "z_log1p_prior": float(zz),
                }
            )

    exchangeable = exchangeable_test(
        standardized,
        n_permutations=4999,
        seed=7,
    )
    neutral = size_conditioned_neutral_test(
        standardized,
        family="poisson",
        n_draws=4999,
        seed=7,
    )

    assert exchangeable["observed_contrast"] < 0
    assert exchangeable["one_sided_lower_p"] <= 0.05
    assert exchangeable["supported"] is True
    assert neutral["one_sided_lower_p"] > 0.05
    assert neutral["mechanism_gate_pass"] is False
    assert math.isfinite(neutral["null_mean"])
