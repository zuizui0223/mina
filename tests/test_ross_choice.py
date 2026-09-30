from __future__ import annotations

import numpy as np
import pytest

from mina.ross_choice import (
    COLONIES,
    _choice_design,
    _performance_for_events,
    fit_conditional_logit,
    information_gate,
    permutation_test,
    prepare_choice_arrays,
)


def _softmax(x: np.ndarray) -> np.ndarray:
    y = np.exp(x - np.max(x))
    return y / np.sum(y)


def _synthetic(
    *,
    seed: int,
    beta_perf: float,
    events_per_year: int = 20,
    years: int = 12,
    first_year0: int = 2001,
):
    rng = np.random.default_rng(seed)
    rows = []
    perf_by_year = {}
    event_no = 0

    perf_base = np.asarray([-1.0, 0.0, 1.0])
    colony_baseline = {"CROZ": 0.0, "ROYD": 0.35, "BIRD": -0.25}

    for yi, first_year in enumerate(range(first_year0, first_year0 + years)):
        pyear = first_year - 1
        shifted = np.roll(perf_base, yi % 3)
        perf_by_year[pyear] = {
            colony: float(shifted[idx])
            for idx, colony in enumerate(COLONIES)
        }

        # These vary by year as well as colony so they are not aliases for
        # the frozen alternative effects.
        log_size = {
            colony: float(
                8.0
                + 0.35 * idx
                + 0.18 * np.sin(0.7 * yi + 0.9 * idx)
            )
            for idx, colony in enumerate(COLONIES)
        }
        raw_effort = np.asarray(
            [
                1.2 + 0.25 * np.sin(0.5 * yi),
                1.0 + 0.20 * np.cos(0.6 * yi + 0.3),
                0.8 + 0.22 * np.sin(0.4 * yi + 0.8),
            ],
            dtype=float,
        )
        effort = (raw_effort - np.mean(raw_effort)) / np.std(
            raw_effort, ddof=1
        )
        effort_by_colony = {
            colony: float(effort[idx])
            for idx, colony in enumerate(COLONIES)
        }

        for _ in range(events_per_year):
            event_no += 1
            natal = COLONIES[int(rng.integers(0, 3))]
            options = list(COLONIES)
            utilities = np.asarray(
                [
                    beta_perf * perf_by_year[pyear][c]
                    + 0.55 * (c == natal)
                    + 0.10 * log_size[c]
                    + 0.50 * effort_by_colony[c]
                    + colony_baseline[c]
                    for c in options
                ],
                dtype=float,
            )
            chosen = int(rng.choice(3, p=_softmax(utilities)))
            for oi, colony in enumerate(options):
                rows.append(
                    {
                        "event_id": f"E{event_no:04d}",
                        "first_breeding_season": first_year,
                        "performance_year": pyear,
                        "candidate_colony": colony,
                        "chosen": int(oi == chosen),
                        "performance_state": perf_by_year[pyear][colony],
                        "natal_colony_indicator": int(colony == natal),
                        "log1p_colony_size": log_size[colony],
                        "z_log_resight_days": effort_by_colony[colony],
                    }
                )
    return rows, perf_by_year


def test_positive_performance_preference_is_recovered_with_detection_controls() -> None:
    rows, perf = _synthetic(seed=1, beta_perf=1.4)
    arrays = prepare_choice_arrays(rows, perf)
    fit = fit_conditional_logit(arrays)
    assert fit["converged"]
    assert fit["n_events"] == 240
    assert fit["beta_performance"] > 0.8
    assert fit["beta_natal"] > 0.1
    assert np.isfinite(fit["beta_effort"])
    assert np.isfinite(fit["beta_royd"])
    assert np.isfinite(fit["beta_bird"])


def test_null_performance_preference_is_near_zero_with_detection_controls() -> None:
    rows, perf = _synthetic(seed=9, beta_perf=0.0, events_per_year=40)
    arrays = prepare_choice_arrays(rows, perf)
    fit = fit_conditional_logit(arrays)
    assert fit["converged"]
    assert abs(fit["beta_performance"]) < 0.25


def test_permutation_test_detects_strong_synthetic_effect_v2() -> None:
    rows, perf = _synthetic(seed=21, beta_perf=2.0, events_per_year=18)
    arrays = prepare_choice_arrays(rows, perf)
    result = permutation_test(\n        arrays,\n        source_eligible_first_breeding_events=len(arrays.event_ids) + 25,\n        permutations=999,\n        seed=20261001,\n        batch_size=111,\n    )
    assert result["estimable"]
    assert result["observed"]["beta_performance"] > 1.0
    assert result["one_sided_upper_p"] <= 0.01


def test_one_year_uses_one_common_colony_label_permutation() -> None:
    rows, perf = _synthetic(
        seed=2, beta_perf=0.0, events_per_year=2, years=1
    )
    arrays = prepare_choice_arrays(rows, perf)
    perm = np.asarray([[[7.0, 8.0, 9.0]]])
    mapped = _performance_for_events(arrays, perm)
    for ei in range(len(arrays.event_ids)):
        for oi in range(3):
            if arrays.mask[ei, oi]:
                ci = arrays.colony_index[ei, oi]
                assert mapped[0, ei, oi] == pytest.approx(perm[0, 0, ci])


def test_permutation_changes_only_performance_dimension() -> None:
    rows, perf = _synthetic(
        seed=3, beta_perf=0.0, events_per_year=2, years=1
    )
    arrays = prepare_choice_arrays(rows, perf)
    original = _choice_design(
        arrays, arrays.base_performance[None, :, :]
    )
    permuted_perf = arrays.base_performance[:, [2, 0, 1]][None, :, :]
    permuted = _choice_design(arrays, permuted_perf)
    assert np.array_equal(original[..., 1:], permuted[..., 1:])
    assert not np.array_equal(original[..., 0], permuted[..., 0])


def test_colony_effects_are_derived_deterministically() -> None:
    rows, perf = _synthetic(
        seed=31, beta_perf=0.0, events_per_year=1, years=1
    )
    arrays = prepare_choice_arrays(rows, perf)
    event_rows = rows[:3]
    assert {r["candidate_colony"] for r in event_rows} == set(COLONIES)

    # Static columns: natal, size, effort, is_ROYD, is_BIRD.
    for oi in range(3):
        if not arrays.mask[0, oi]:
            continue
        colony = COLONIES[int(arrays.colony_index[0, oi])]
        assert arrays.static_covariates[0, oi, 3] == float(colony == "ROYD")
        assert arrays.static_covariates[0, oi, 4] == float(colony == "BIRD")


def test_information_gate_uses_frozen_thresholds() -> None:
    rows, perf = _synthetic(
        seed=4, beta_perf=1.0, events_per_year=10, years=10
    )
    arrays = prepare_choice_arrays(rows, perf)
    gate = information_gate(\n        arrays, source_eligible_first_breeding_events=120\n    )\n    assert gate["eligible_first_breeding_events"] == 120\n    assert gate["events_with_at_least_two_observed_candidate_colonies"] == 100\n    assert gate["unique_first_breeding_years"] == 10\n    assert gate["pass"]


def test_rejects_multiple_chosen_options() -> None:
    rows, perf = _synthetic(
        seed=5, beta_perf=0.0, events_per_year=1, years=1
    )
    first = rows[0]["event_id"]
    for row in rows:
        if row["event_id"] == first:
            row["chosen"] = 1
    with pytest.raises(ValueError, match="exactly one chosen"):
        prepare_choice_arrays(rows, perf)


def test_rejects_single_option_event() -> None:
    rows, perf = _synthetic(
        seed=6, beta_perf=0.0, events_per_year=1, years=1
    )
    event = rows[0]["event_id"]
    kept = [r for r in rows if r["event_id"] != event]
    kept.append(next(r for r in rows if r["event_id"] == event))
    with pytest.raises(ValueError, match="expected 2-3"):
        prepare_choice_arrays(kept, perf)


def test_row_performance_must_match_frozen_year_table() -> None:
    rows, perf = _synthetic(
        seed=7, beta_perf=0.0, events_per_year=1, years=1
    )
    rows[0]["performance_state"] += 0.25
    with pytest.raises(ValueError, match="performance disagrees"):
        prepare_choice_arrays(rows, perf)


def test_missing_effort_is_fail_closed() -> None:
    rows, perf = _synthetic(
        seed=8, beta_perf=0.0, events_per_year=1, years=1
    )
    rows[0]["z_log_resight_days"] = np.nan
    with pytest.raises(ValueError, match="non-finite static choice covariate"):
        prepare_choice_arrays(rows, perf)


def test_bird_candidate_is_rejected_from_2014_onward() -> None:
    rows, perf = _synthetic(
        seed=10,
        beta_perf=0.0,
        events_per_year=1,
        years=1,
        first_year0=2014,
    )
    with pytest.raises(ValueError, match="includes BIRD"):
        prepare_choice_arrays(rows, perf)


def test_two_stage_information_gate_keeps_100_and_50_distinct() -> None:
    rows, perf = _synthetic(
        seed=41, beta_perf=0.0, events_per_year=6, years=10
    )
    arrays = prepare_choice_arrays(rows, perf)
    assert len(arrays.event_ids) == 60

    gate = information_gate(
        arrays, source_eligible_first_breeding_events=100
    )
    assert gate["pass"]

    source_fail = information_gate(
        arrays, source_eligible_first_breeding_events=99
    )
    assert not source_fail["pass"]

    rows49, perf49 = _synthetic(
        seed=42, beta_perf=0.0, events_per_year=7, years=7
    )
    arrays49 = prepare_choice_arrays(rows49, perf49)
    assert len(arrays49.event_ids) == 49
    choice_fail = information_gate(
        arrays49, source_eligible_first_breeding_events=120
    )
    assert not choice_fail["pass"]


def test_source_gate_count_cannot_be_smaller_than_choice_count() -> None:
    rows, perf = _synthetic(
        seed=43, beta_perf=0.0, events_per_year=6, years=10
    )
    arrays = prepare_choice_arrays(rows, perf)
    with pytest.raises(ValueError, match="cannot be smaller"):
        information_gate(
            arrays, source_eligible_first_breeding_events=50
        )
