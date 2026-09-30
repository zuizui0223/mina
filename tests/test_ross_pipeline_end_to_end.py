from __future__ import annotations

import math

import numpy as np

from mina.ross_choice import permutation_test, prepare_choice_arrays
from mina.ross_detection import build_resight_day_proxy
from mina.ross_states import (
    ROSS_COLONIES,
    annualize_resights,
    banded_breeder_performance,
    build_choice_rows,
    canonical_detection_observations,
    first_breeding_source_events,
    source_eligible_first_breeding_events,
)


def _softmax(x: np.ndarray) -> np.ndarray:
    y = np.exp(x - np.max(x))
    return y / np.sum(y)


def _obs(band: int, date: str, colony: str, eggs: int, chicks: int):
    return {
        "Band": band,
        "Date": date,
        "Colony": colony,
        "Eggs": eggs,
        "Chicks": chicks,
    }


def _synthetic_pipeline():
    inventory = [
        {"Low": 10000, "High": 10999, "Colony": "CROZ", "Season": "9495"},
        {"Low": 11000, "High": 11999, "Colony": "ROYD", "Season": "9495"},
        {"Low": 12000, "High": 12999, "Colony": "BIRD", "Season": "9495"},
        {"Low": 40000, "High": 40999, "Colony": "CROZ", "Season": "9899"},
        {"Low": 41000, "High": 41999, "Colony": "ROYD", "Season": "9899"},
        {"Low": 42000, "High": 42999, "Colony": "BIRD", "Season": "9899"},
    ]
    observations = []

    # Planned complete three-colony performance states. Raw breeder success
    # fractions 0.2, 0.5, 0.8 standardize exactly to -1, 0, +1.
    base = np.asarray([-1.0, 0.0, 1.0])
    planned_perf: dict[int, dict[str, float]] = {}

    background_bands = {
        "CROZ": list(range(10000, 10030)),
        "ROYD": list(range(11000, 11030)),
        "BIRD": list(range(12000, 12030)),
    }
    fractions = {-1.0: 6, 0.0: 15, 1.0: 24}

    for yi, year in enumerate(range(2000, 2012)):
        states = np.roll(base, yi % 3)
        planned_perf[year] = {
            colony: float(states[idx])
            for idx, colony in enumerate(ROSS_COLONIES)
        }
        for colony in ROSS_COLONIES:
            success_count = fractions[planned_perf[year][colony]]
            for j, band in enumerate(background_bands[colony]):
                observations.append(
                    _obs(
                        band,
                        f"11/15/{year}",
                        colony,
                        1,
                        1 if j < success_count else 0,
                    )
                )

    sizes: dict[int, dict[str, float]] = {}
    for year in range(2000, 2012):
        sizes[year] = {
            "CROZ": 200000.0 + 1200.0 * (year - 2000),
            "ROYD": 3000.0 + 50.0 * (year - 2000),
            "BIRD": 50000.0 + 400.0 * (year - 2000),
        }

    rng = np.random.default_rng(20261001)
    natal_counters = {"CROZ": 0, "ROYD": 0, "BIRD": 0}
    range_start = {"CROZ": 40000, "ROYD": 41000, "BIRD": 42000}

    # 25 first-breeding events in each of 10 years => 250 choice events.
    for y in range(2002, 2012):
        pyear = y - 1
        perf = planned_perf[pyear]
        for _ in range(25):
            natal = ROSS_COLONIES[int(rng.integers(0, 3))]
            natal_counters[natal] += 1
            band = range_start[natal] + natal_counters[natal]

            # All three colonies were genuinely visited as PB during the frozen
            # two-year lookback, so all three are legitimate observed options.
            for season in (y - 2, y - 1):
                for day, colony in zip((10, 12, 14), ROSS_COLONIES):
                    observations.append(
                        _obs(band, f"11/{day}/{season}", colony, 0, 0)
                    )

            utility = np.asarray(
                [
                    1.8 * perf[colony]
                    + 0.45 * (colony == natal)
                    + 0.08 * math.log1p(sizes[pyear][colony])
                    for colony in ROSS_COLONIES
                ]
            )
            chosen = ROSS_COLONIES[int(rng.choice(3, p=_softmax(utility)))]

            # Eggs establish first breeding; Chicks=9 keeps focal first-breeders
            # out of the prior-year performance index of later focal events.
            observations.append(
                _obs(band, f"11/20/{y}", chosen, 1, 9)
            )

    return observations, inventory, sizes


def test_raw_schema_to_choice_model_end_to_end_synthetic() -> None:
    observations, inventory, sizes = _synthetic_pipeline()
    annual = annualize_resights(observations, inventory)

    performance, perf_audit = banded_breeder_performance(annual)
    assert perf_audit["n_eligible_performance_years"] == 12
    for year in range(2000, 2012):
        assert set(performance[year]) == set(ROSS_COLONIES)

    source_events = first_breeding_source_events(annual)
    focal_source_events = [
        event for event in source_events if int(event["band"]) >= 40000
    ]
    assert len(focal_source_events) == 250
    assert all(
        len(event["candidate_colonies"]) == 3
        for event in focal_source_events
    )

    detection_observations = canonical_detection_observations(observations)
    effort, dropped_effort = build_resight_day_proxy(
        detection_observations, focal_source_events
    )
    assert dropped_effort == {}
    assert len(effort) == 250

    eligible_source, source_audit = source_eligible_first_breeding_events(
        focal_source_events, performance, sizes, effort
    )
    assert source_audit["retained_source_events"] == 250

    rows, row_audit = build_choice_rows(
        eligible_source, performance, sizes, effort
    )
    assert row_audit["retained_events"] == 250
    assert row_audit["retained_option_rows"] == 750
    assert row_audit["excluded_events"] == {}

    arrays = prepare_choice_arrays(rows, performance)
    result = permutation_test(
        arrays,
        source_eligible_first_breeding_events=len(eligible_source),
        permutations=999,
        seed=20261001,
        batch_size=111,
    )
    assert result["estimable"]
    assert result["information_gate"]["pass"]
    assert result["observed"]["n_events"] == 250
    assert result["observed"]["beta_performance"] > 1.0
    assert result["one_sided_upper_p"] <= 0.01
