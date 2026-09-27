import math

import numpy as np

from mina.neff_momentum import (
    complete_cases,
    enrich_lags,
    shifted_coefficients,
)


def _row(island, year, previous_growth):
    return {
        "island": island,
        "start_year": year,
        "end_year": year + 1,
        "current_total": 100.0 - year,
        "next_total": 99.0 - year,
        "next_growth": -0.01,
        "effective_colony_number": 2.0 + 0.01 * year,
        "previous_growth": previous_growth,
    }


def test_enrich_lags_uses_previous_transition_growth():
    rows = [
        _row("CHR", 2000, None),
        _row("CHR", 2001, 0.10),
        _row("CHR", 2002, 0.20),
        _row("CHR", 2003, 0.30),
    ]
    enriched = enrich_lags(rows)
    assert enriched[1]["lag1_growth"] == 0.10
    assert enriched[2]["lag1_growth"] == 0.20
    assert enriched[2]["lag2_growth"] == 0.10
    assert enriched[3]["lag2_growth"] == 0.20
    local = complete_cases(enriched, ("lag1_growth", "lag2_growth"))
    assert [row["start_year"] for row in local] == [2002, 2003]


def test_shifted_coefficient_identity_matches_direct_standardized_fit():
    rows = []
    for island, offset in (("CHR", 0.0), ("COR", 0.2)):
        for k, year in enumerate(range(2000, 2006)):
            current = 100.0 - 3.0 * k + 10.0 * offset
            eff = 1.5 + 0.3 * k + offset
            lag1 = None if k == 0 else -0.04 + 0.01 * k
            lag2 = None if k < 2 else -0.05 + 0.01 * (k - 1)
            next_growth = (
                -0.08
                + 0.06 * math.log1p(eff)
                + 0.3 * (lag1 or 0.0)
                + 0.1 * offset
            )
            rows.append(
                {
                    "island": island,
                    "start_year": year,
                    "end_year": year + 1,
                    "current_total": current,
                    "next_total": current * math.exp(next_growth),
                    "next_growth": next_growth,
                    "effective_colony_number": eff,
                    "previous_growth": lag1,
                    "lag1_growth": lag1,
                    "lag2_growth": lag2,
                    "_full_index": len(rows),
                }
            )

    local = complete_cases(rows, ("lag1_growth", "lag2_growth"))
    levels = ("CHR", "COR")
    x = np.zeros((len(local), 2), dtype=float)
    lookup = {name: i for i, name in enumerate(levels)}
    for i, row in enumerate(local):
        x[i, lookup[row["island"]]] = 1.0

    continuous = []
    for values in (
        np.asarray([math.log1p(row["current_total"]) for row in local]),
        np.asarray([row["start_year"] for row in local], dtype=float),
        np.asarray(
            [math.log1p(row["effective_colony_number"]) for row in local]
        ),
        np.asarray([row["lag1_growth"] for row in local], dtype=float),
        np.asarray([row["lag2_growth"] for row in local], dtype=float),
    ):
        continuous.append(
            (values - np.mean(values)) / np.std(values, ddof=1)
        )
    x = np.column_stack([x, *continuous])
    y = np.asarray([row["next_growth"] for row in local], dtype=float)
    direct = np.linalg.lstsq(x, y, rcond=None)[0][4]

    topology = np.asarray(
        [
            [math.log1p(row["effective_colony_number"])]
            for row in rows
        ],
        dtype=float,
    )
    shifted = shifted_coefficients(
        rows,
        ("lag1_growth", "lag2_growth"),
        topology,
    )[0]
    assert math.isclose(direct, shifted, rel_tol=0.0, abs_tol=1e-12)
