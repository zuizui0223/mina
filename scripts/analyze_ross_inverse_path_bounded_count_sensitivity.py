#!/usr/bin/env python3
"""Bounded-perturbation sensitivity for exact Ross inverse-path reversal.

Uses only numpy, which is a declared project dependency.
"""

from __future__ import annotations

import numpy as np

NAMES = [
    "Cape Royds",
    "Cape Bird South",
    "Cape Bird Middle",
    "Cape Bird North",
    "Cape Crozier West",
    "Cape Crozier East",
]

A = np.array([3620, 11664, 3333, 32353, 139386, 17055], dtype=float)
B = np.array([1367, 7149, 1834, 17334, 59170, 7944], dtype=float)
C = np.array([2239, 7636, 2357, 30685, 147224, 13855], dtype=float)


def component_delta(k: float) -> np.ndarray:
    """Minimum symmetric relative tolerance by component at fixed scale k."""
    pred = k * A + (1.0 - k) * B
    if np.any(pred <= 0):
        return np.full_like(pred, np.inf)
    return np.abs(C - pred) / (C + pred)


def max_delta(k: float) -> float:
    return float(np.max(component_delta(k)))


def minimize_scale(lo: float = 0.0, hi: float = 2.0) -> tuple[float, float]:
    """Minimize max_delta without scipy.

    First bracket the global minimum on a dense grid, then refine the best
    grid cell with a golden-section search.  This is deterministic and more
    than sufficient for the reported sensitivity precision.
    """
    grid = np.linspace(lo, hi, 20001)
    vals = np.array([max_delta(float(k)) for k in grid])
    idx = int(np.argmin(vals))

    left = float(grid[max(0, idx - 1)])
    right = float(grid[min(len(grid) - 1, idx + 1)])

    phi = (1.0 + 5.0**0.5) / 2.0
    invphi = 1.0 / phi

    c = right - (right - left) * invphi
    d = left + (right - left) * invphi
    fc = max_delta(c)
    fd = max_delta(d)

    for _ in range(100):
        if right - left < 1e-13:
            break
        if fc <= fd:
            right, d, fd = d, c, fc
            c = right - (right - left) * invphi
            fc = max_delta(c)
        else:
            left, c, fc = c, d, fd
            d = left + (right - left) * invphi
            fd = max_delta(d)

    k = 0.5 * (left + right)
    return k, max_delta(k)


def main() -> None:
    k_obs = (C.sum() - B.sum()) / (A.sum() - B.sum())
    d_obs = component_delta(k_obs)

    k_free, delta_free = minimize_scale()
    d_free = component_delta(k_free)

    print(f"k_obs={k_obs:.12f}")
    print(f"fixed_k_delta_min={d_obs.max():.12f}")
    for name, delta in zip(NAMES, d_obs):
        print(f"fixed {name}: {delta:.12f}")

    print(f"free_k={k_free:.12f}")
    print(f"free_k_delta_min={delta_free:.12f}")
    for name, delta in zip(NAMES, d_free):
        print(f"free {name}: {delta:.12f}")


if __name__ == "__main__":
    main()
