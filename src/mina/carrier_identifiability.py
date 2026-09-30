"""Structural identifiability checks for the carrier of Palmer demographic memory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def transition_rank(k: int, *, include_recruitment: bool = True) -> dict[str, int]:
    if k < 2:
        raise ValueError("k must be >= 2")
    eye = np.eye(k, dtype=float)
    blocks = [eye, eye]
    if include_recruitment:
        blocks.append(eye)
    jac = np.column_stack(blocks)
    rank = int(np.linalg.matrix_rank(jac))
    return {
        "k": k,
        "n_latent_parameters": int(jac.shape[1]),
        "n_observations": int(jac.shape[0]),
        "rank": rank,
        "nullity": int(jac.shape[1] - rank),
    }


def movement_conserving_basis(k: int) -> np.ndarray:
    """Basis for vectors m with sum(m)=0."""
    if k < 2:
        raise ValueError("k must be >= 2")
    q = np.zeros((k, k - 1), dtype=float)
    for j in range(k - 1):
        q[j, j] = 1.0
        q[-1, j] = -1.0
    return q


def constrained_transition_rank(
    k: int, *, include_recruitment: bool = True
) -> dict[str, int]:
    eye = np.eye(k, dtype=float)
    movement = movement_conserving_basis(k)
    blocks = [eye, movement]
    if include_recruitment:
        blocks.append(eye)
    jac = np.column_stack(blocks)
    rank = int(np.linalg.matrix_rank(jac))
    return {
        "k": k,
        "n_latent_parameters": int(jac.shape[1]),
        "n_observations": int(jac.shape[0]),
        "rank": rank,
        "nullity": int(jac.shape[1] - rank),
    }


def carrier_design_rank(s: np.ndarray) -> dict[str, object]:
    values = np.asarray(s, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("s must be a one-dimensional vector of length >= 2")
    x = np.column_stack([values, values, values])
    singular = np.linalg.svd(x, compute_uv=False)
    rank = int(np.linalg.matrix_rank(x))
    return {
        "n_rows": int(values.size),
        "n_carrier_coefficients": 3,
        "rank": rank,
        "nullity": int(3 - rank),
        "singular_values": [float(v) for v in singular],
    }


def twin_generators(s: np.ndarray, theta: float = 2.0) -> dict[str, object]:
    """Construct observationally identical latent carrier histories."""
    state = np.asarray(s, dtype=float)
    if state.ndim != 1 or state.size < 2:
        raise ValueError("s must be one dimensional")
    centered = state - float(np.mean(state))
    scale = float(np.max(np.abs(theta * centered)))
    base = np.full(state.size, scale + 10.0, dtype=float)
    recruitment_offset = np.full(state.size, scale + 1.0, dtype=float)

    attendance_a = base + theta * centered
    movement_a = np.zeros_like(state)
    recruitment_a = recruitment_offset
    observed_a = attendance_a + movement_a + recruitment_a

    attendance_m = base
    movement_m = theta * centered
    recruitment_m = recruitment_offset
    observed_m = attendance_m + movement_m + recruitment_m

    attendance_j = base
    movement_j = np.zeros_like(state)
    recruitment_j = recruitment_offset + theta * centered
    observed_j = attendance_j + movement_j + recruitment_j

    return {
        "movement_conserves_island_total": bool(
            abs(float(np.sum(movement_m))) < 1e-12
        ),
        "all_attendance_nonnegative": bool(
            np.min(attendance_a) >= 0 and np.min(attendance_m) >= 0
        ),
        "all_recruitment_nonnegative": bool(
            np.min(recruitment_a) >= 0 and np.min(recruitment_j) >= 0
        ),
        "attendance_vs_movement_max_abs_observed_difference": float(
            np.max(np.abs(observed_a - observed_m))
        ),
        "attendance_vs_recruitment_max_abs_observed_difference": float(
            np.max(np.abs(observed_a - observed_j))
        ),
        "observed": [float(v) for v in observed_a],
        "state_centered": [float(v) for v in centered],
    }


def analyze(max_k: int = 20) -> dict[str, object]:
    if max_k < 2:
        raise ValueError("max_k must be >= 2")
    state = np.asarray([-1.4, -0.5, 0.2, 0.6, 1.1], dtype=float)
    design = carrier_design_rank(state)
    twin = twin_generators(state)
    unconstrained = [transition_rank(k) for k in range(2, max_k + 1)]
    movement_only = [
        constrained_transition_rank(k, include_recruitment=False)
        for k in range(2, max_k + 1)
    ]
    with_recruitment = [
        constrained_transition_rank(k, include_recruitment=True)
        for k in range(2, max_k + 1)
    ]

    carrier_identifiable = bool(
        design["nullity"] == 0
        and all(x["nullity"] == 0 for x in unconstrained)
        and all(x["nullity"] == 0 for x in movement_only)
        and all(x["nullity"] == 0 for x in with_recruitment)
        and twin["attendance_vs_movement_max_abs_observed_difference"] > 1e-12
        and twin["attendance_vs_recruitment_max_abs_observed_difference"] > 1e-12
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-carrier-identifiability-v1",
        "contract_id": "mina-palmer-carrier-identifiability-v1",
        "carrier_coefficient_design": design,
        "transition_rank_unconstrained": unconstrained,
        "transition_rank_movement_conserving_without_recruitment": movement_only,
        "transition_rank_movement_conserving_with_recruitment": with_recruitment,
        "twin_generators": twin,
        "decision": {
            "carrier_identifiable_from_colony_counts": carrier_identifiable,
            "attendance_vs_movement_separable": False,
            "attendance_vs_recruitment_separable": False,
        },
        "interpretation": (
            "Breeder counts identify the total state-dependent contribution to future "
            "breeder abundance, but not whether that contribution is carried by local "
            "adult attendance/breeding propensity, net mature-bird movement, or first "
            "recruitment. Movement conservation within an island does not remove the "
            "rank deficiency, and exact latent twin histories can generate identical "
            "observed breeder counts."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-k", type=int, default=20)
    args = parser.parse_args()
    result = analyze(args.max_k)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
