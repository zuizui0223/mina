"""Outcome-blind conditional-choice engine for Ross Island first breeding."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np

COLONIES = ("CROZ", "ROYD", "BIRD")
COLONY_INDEX = {name: idx for idx, name in enumerate(COLONIES)}
N_PERMUTATIONS = 100_000
SEED = 20261001


@dataclass(frozen=True)
class ChoiceArrays:
    event_ids: tuple[str, ...]
    first_breeding_seasons: np.ndarray
    performance_years: np.ndarray
    performance_year_index: np.ndarray
    colony_index: np.ndarray
    mask: np.ndarray
    chosen_index: np.ndarray
    static_covariates: np.ndarray
    base_performance: np.ndarray


def _standardize_performance(
    performance_by_year: Mapping[int, Mapping[str, float]],
) -> tuple[tuple[int, ...], np.ndarray]:
    years = tuple(sorted(int(y) for y in performance_by_year))
    values = np.empty((len(years), 3), dtype=float)
    for yi, year in enumerate(years):
        local = performance_by_year[year]
        if set(local) != set(COLONIES):
            raise ValueError(
                f"performance year {year} must contain exactly {COLONIES}, "
                f"observed {sorted(local)}"
            )
        row = np.asarray([float(local[c]) for c in COLONIES], dtype=float)
        if not np.all(np.isfinite(row)):
            raise ValueError(f"non-finite performance in year {year}")
        values[yi] = row
    return years, values


def prepare_choice_arrays(
    rows: Iterable[Mapping[str, object]],
    performance_by_year: Mapping[int, Mapping[str, float]],
) -> ChoiceArrays:
    local_rows = [dict(r) for r in rows]
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in local_rows:
        groups[str(row["event_id"])].append(row)
    if not groups:
        raise ValueError("no choice events")

    perf_years, base_perf = _standardize_performance(performance_by_year)
    year_lookup = {year: idx for idx, year in enumerate(perf_years)}

    event_ids = tuple(sorted(groups))
    n = len(event_ids)
    colony_index = np.full((n, 3), -1, dtype=int)
    mask = np.zeros((n, 3), dtype=bool)
    chosen_index = np.empty(n, dtype=int)
    static = np.zeros((n, 3, 2), dtype=float)
    first_season = np.empty(n, dtype=int)
    performance_year = np.empty(n, dtype=int)
    perf_year_index = np.empty(n, dtype=int)

    for ei, event_id in enumerate(event_ids):
        options = groups[event_id]
        if not 2 <= len(options) <= 3:
            raise ValueError(
                f"event {event_id} has {len(options)} candidates; expected 2-3"
            )
        option_colonies = [str(r["candidate_colony"]) for r in options]
        if len(set(option_colonies)) != len(option_colonies):
            raise ValueError(f"duplicate candidate colony in event {event_id}")
        if any(c not in COLONY_INDEX for c in option_colonies):
            raise ValueError(f"unknown Ross colony in event {event_id}")
        chosen = [idx for idx, r in enumerate(options) if int(r["chosen"]) == 1]
        if len(chosen) != 1:
            raise ValueError(
                f"event {event_id} must have exactly one chosen option"
            )

        seasons = {int(r["first_breeding_season"]) for r in options}
        pyears = {int(r["performance_year"]) for r in options}
        if len(seasons) != 1 or len(pyears) != 1:
            raise ValueError(f"inconsistent year fields in event {event_id}")
        season = next(iter(seasons))
        pyear = next(iter(pyears))
        if pyear != season - 1:
            raise ValueError(
                f"event {event_id} performance_year != first_breeding_season-1"
            )
        if pyear not in year_lookup:
            raise ValueError(f"missing complete performance year {pyear}")

        first_season[ei] = season
        performance_year[ei] = pyear
        perf_year_index[ei] = year_lookup[pyear]

        # Canonical option order is Ross colony order, not input row order.
        sorted_options = sorted(
            options, key=lambda r: COLONY_INDEX[str(r["candidate_colony"])]
        )
        chosen_colony = str(options[chosen[0]]["candidate_colony"])
        chosen_pos = None
        for oi, row in enumerate(sorted_options):
            colony = str(row["candidate_colony"])
            ci = COLONY_INDEX[colony]
            colony_index[ei, oi] = ci
            mask[ei, oi] = True
            static[ei, oi, 0] = float(row["natal_colony_indicator"])
            static[ei, oi, 1] = float(row["log1p_colony_size"])
            if int(row["chosen"]) == 1:
                chosen_pos = oi

            stated = float(row["performance_state"])
            expected = float(base_perf[year_lookup[pyear], ci])
            if not np.isclose(stated, expected, rtol=0.0, atol=1e-12):
                raise ValueError(
                    f"row performance disagrees with year table for "
                    f"{event_id}/{colony}/{pyear}"
                )
        if chosen_pos is None or chosen_colony not in option_colonies:
            raise ValueError(f"cannot resolve chosen option for {event_id}")
        chosen_index[ei] = chosen_pos

    if not np.all(np.isfinite(static[mask])):
        raise ValueError("non-finite static choice covariate")

    return ChoiceArrays(
        event_ids=event_ids,
        first_breeding_seasons=first_season,
        performance_years=performance_year,
        performance_year_index=perf_year_index,
        colony_index=colony_index,
        mask=mask,
        chosen_index=chosen_index,
        static_covariates=static,
        base_performance=base_perf,
    )


def _performance_for_events(
    arrays: ChoiceArrays,
    performance_matrix: np.ndarray,
) -> np.ndarray:
    """Map [batch, year, colony] performance to [batch, event, option]."""
    if performance_matrix.ndim != 3 or performance_matrix.shape[2] != 3:
        raise ValueError("performance_matrix must be [batch, year, 3]")
    by_event = performance_matrix[:, arrays.performance_year_index, :]
    safe_colony = np.where(arrays.mask, arrays.colony_index, 0)
    return np.take_along_axis(
        by_event,
        safe_colony[None, :, :],
        axis=2,
    )


def _choice_design(
    arrays: ChoiceArrays,
    performance_matrix: np.ndarray,
) -> np.ndarray:
    perf = _performance_for_events(arrays, performance_matrix)
    b = performance_matrix.shape[0]
    static = np.broadcast_to(
        arrays.static_covariates[None, :, :, :],
        (b,) + arrays.static_covariates.shape,
    )
    return np.concatenate([perf[..., None], static], axis=3)


def fit_conditional_logit_batch(
    design: np.ndarray,
    mask: np.ndarray,
    chosen_index: np.ndarray,
    *,
    max_iterations: int = 50,
    coefficient_tolerance: float = 1e-10,
    gradient_tolerance: float = 1e-9,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit conditional logits for a batch of design matrices."""
    if design.ndim != 4:
        raise ValueError("design must be [batch,event,option,covariate]")
    b, e, k, p = design.shape
    if mask.shape != (e, k):
        raise ValueError("mask shape mismatch")
    if chosen_index.shape != (e,):
        raise ValueError("chosen_index shape mismatch")

    beta = np.zeros((b, p), dtype=float)
    converged = np.zeros(b, dtype=bool)
    batch_idx = np.arange(b)[:, None]
    event_idx = np.arange(e)[None, :]
    chosen = np.broadcast_to(chosen_index[None, :], (b, e))
    chosen_x = design[batch_idx, event_idx, chosen, :]

    for _ in range(max_iterations):
        eta = np.einsum("bekp,bp->bek", design, beta, optimize=True)
        eta = np.where(mask[None, :, :], eta, -np.inf)
        max_eta = np.max(eta, axis=2, keepdims=True)
        exp_eta = np.where(
            mask[None, :, :], np.exp(eta - max_eta), 0.0
        )
        denom = np.sum(exp_eta, axis=2, keepdims=True)
        prob = exp_eta / denom

        mean_x = np.einsum("bek,bekp->bep", prob, design, optimize=True)
        grad = np.sum(chosen_x - mean_x, axis=1)

        exx = np.einsum(
            "bek,bekp,bekq->bepq",
            prob,
            design,
            design,
            optimize=True,
        )
        cov = exx - np.einsum(
            "bep,beq->bepq", mean_x, mean_x, optimize=True
        )
        info = np.sum(cov, axis=1)

        step = np.einsum(
            "bij,bj->bi",
            np.linalg.pinv(info, rcond=1e-12),
            grad,
            optimize=True,
        )
        beta_new = beta + step
        conv_step = np.max(np.abs(step), axis=1) <= coefficient_tolerance
        conv_grad = np.max(np.abs(grad), axis=1) <= gradient_tolerance
        converged_now = conv_step | conv_grad
        beta = beta_new
        converged |= converged_now
        if np.all(converged):
            break

    return beta, converged


def fit_conditional_logit(
    arrays: ChoiceArrays,
) -> dict[str, object]:
    perf = arrays.base_performance[None, :, :]
    design = _choice_design(arrays, perf)
    beta, converged = fit_conditional_logit_batch(
        design, arrays.mask, arrays.chosen_index
    )
    return {
        "beta_performance": float(beta[0, 0]),
        "beta_natal": float(beta[0, 1]),
        "beta_log_size": float(beta[0, 2]),
        "converged": bool(converged[0]),
        "n_events": len(arrays.event_ids),
        "n_option_rows": int(np.sum(arrays.mask)),
    }


def information_gate(arrays: ChoiceArrays) -> dict[str, object]:
    destinations = set()
    for ei in range(len(arrays.event_ids)):
        oi = int(arrays.chosen_index[ei])
        destinations.add(COLONIES[int(arrays.colony_index[ei, oi])])
    n_events = len(arrays.event_ids)
    years = set(int(x) for x in arrays.first_breeding_seasons)
    return {
        "eligible_first_breeding_events": n_events,
        "events_with_at_least_two_observed_candidate_colonies": n_events,
        "unique_first_breeding_years": len(years),
        "destination_colonies": sorted(destinations),
        "pass": bool(
            n_events >= 100
            and n_events >= 50
            and len(years) >= 8
            and len(destinations) >= 2
        ),
    }


def permutation_test(
    arrays: ChoiceArrays,
    *,
    permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
    batch_size: int = 500,
) -> dict[str, object]:
    gate = information_gate(arrays)
    if not gate["pass"]:
        return {
            "estimable": False,
            "information_gate": gate,
            "observed_model_fit": False,
            "permutations_run": 0,
        }

    observed = fit_conditional_logit(arrays)
    if not observed["converged"]:
        raise RuntimeError("observed conditional logit did not converge")

    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=float)
    offset = 0
    y = arrays.base_performance.shape[0]

    while offset < permutations:
        batch = min(batch_size, permutations - offset)
        order = np.argsort(rng.random((batch, y, 3)), axis=2)
        base = np.broadcast_to(
            arrays.base_performance[None, :, :],
            (batch, y, 3),
        )
        permuted = np.take_along_axis(base, order, axis=2)
        design = _choice_design(arrays, permuted)
        beta, converged = fit_conditional_logit_batch(
            design, arrays.mask, arrays.chosen_index
        )
        if not np.all(converged):
            raise RuntimeError("one or more permutation fits did not converge")
        null[offset : offset + batch] = beta[:, 0]
        offset += batch

    target = float(observed["beta_performance"])
    p_value = float(
        (1 + int(np.sum(null >= target))) / (permutations + 1)
    )
    return {
        "estimable": True,
        "information_gate": gate,
        "observed": observed,
        "permutations": permutations,
        "seed": seed,
        "null_mean": float(np.mean(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q975": float(np.quantile(null, 0.975)),
        "one_sided_upper_p": p_value,
        "supported": bool(target > 0 and p_value <= 0.05),
    }
