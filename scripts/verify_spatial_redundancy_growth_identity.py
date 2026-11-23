#!/usr/bin/env python3
"""Verify the exact finite-interval spatial-redundancy identity."""

from __future__ import annotations
import math

def decompose(start, end):
    if len(start) != len(end) or not start:
        raise ValueError("start/end must be non-empty and equal length")
    if any(x <= 0 for x in start) or any(x <= 0 for x in end):
        raise ValueError("identity implementation expects positive abundances")

    n0 = float(sum(start))
    n1 = float(sum(end))
    p0 = [x / n0 for x in start]
    p1 = [x / n1 for x in end]
    growth = [b / a for a, b in zip(start, end)]

    h0 = sum(p * p for p in p0)
    h1 = sum(p * p for p in p1)
    e0 = 1.0 / h0
    e1 = 1.0 / h1

    g_bar = sum(p * g for p, g in zip(p0, growth))
    weights = [p * p / h0 for p in p0]
    g_d = math.sqrt(sum(w * g * g for w, g in zip(weights, growth)))
    predicted_e_ratio = (g_bar / g_d) ** 2

    return {
        "E0": e0,
        "E1": e1,
        "observed_E_ratio": e1 / e0,
        "predicted_E_ratio": predicted_e_ratio,
        "G_bar": g_bar,
        "G_D": g_d,
    }

def verify(name, start, end):
    x = decompose(start, end)
    if not math.isclose(x["observed_E_ratio"], x["predicted_E_ratio"], rel_tol=1e-12, abs_tol=1e-12):
        raise AssertionError((name, x))
    direction = "down" if x["E1"] < x["E0"] else "up" if x["E1"] > x["E0"] else "flat"
    print(
        f"{name}: E {x['E0']:.6f} -> {x['E1']:.6f} ({direction}); "
        f"G_bar={x['G_bar']:.6f}, G_D={x['G_D']:.6f}"
    )

def main():
    verify("Ross decline 1985-1999", [3214, 53534, 167666], [3620, 47350, 156441])
    verify("Ross recovery 2001-2012", [1367, 26317, 67114], [3083, 75696, 272340])
    verify("Beaufort recovery 2004-2010", [47725, 460], [63760, 957])

if __name__ == "__main__":
    main()
