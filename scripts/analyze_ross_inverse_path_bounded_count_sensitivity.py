#!/usr/bin/env python3
"""Bounded-perturbation sensitivity for exact Ross inverse-path reversal."""

from __future__ import annotations
import math
import numpy as np
from scipy.optimize import minimize_scalar

NAMES = [
    "Cape Royds",
    "Cape Bird South",
    "Cape Bird Middle",
    "Cape Bird North",
    "Cape Crozier West",
    "Cape Crozier East",
]

A = np.array([3620,11664,3333,32353,139386,17055], dtype=float)
B = np.array([1367,7149,1834,17334,59170,7944], dtype=float)
C = np.array([2239,7636,2357,30685,147224,13855], dtype=float)

def component_delta(k: float) -> np.ndarray:
    pred = k*A + (1-k)*B
    if np.any(pred <= 0):
        return np.full_like(pred, np.inf)
    return np.abs(C-pred)/(C+pred)

def max_delta(k: float) -> float:
    return float(np.max(component_delta(k)))

def main():
    k_obs=(C.sum()-B.sum())/(A.sum()-B.sum())
    d_obs=component_delta(k_obs)

    opt=minimize_scalar(max_delta,bounds=(0.0,2.0),method="bounded")
    d_free=component_delta(float(opt.x))

    print(f"k_obs={k_obs:.12f}")
    print(f"fixed_k_delta_min={d_obs.max():.12f}")
    for name,d in zip(NAMES,d_obs):
        print(f"fixed {name}: {d:.12f}")

    print(f"free_k={opt.x:.12f}")
    print(f"free_k_delta_min={opt.fun:.12f}")
    for name,d in zip(NAMES,d_free):
        print(f"free {name}: {d:.12f}")

if __name__ == "__main__":
    main()
