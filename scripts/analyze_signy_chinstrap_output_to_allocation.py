#!/usr/bin/env python3
"""Prospective Signy Chinstrap late-output -> next-season allocation test.

Frozen by:
  contracts/SIGNY_CHINSTRAP_OUTPUT_TO_ALLOCATION_V1.md
  contracts/SIGNY_CHINSTRAP_OUTPUT_TO_ALLOCATION_SUPPORT_AMENDMENT_V1.md
  results/SIGNY_CHINSTRAP_OUTPUT_TO_ALLOCATION_SUPPORT_V1.json

The primary result is terminal if beta <= 0 or permutation p > 0.05.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import urllib.request
from pathlib import Path

import numpy as np

SOURCE_REF = "09fd3f36b76ad98f4b6a736a37d8e5606c0003da"
SOURCE_URL = (
    "https://raw.githubusercontent.com/azira104/PolarRegion/"
    + SOURCE_REF
    + "/static/data/pr_animal/pr_animal_chinstrappenguin.csv"
)
CORE = ["C15", "C18", "C46", "C47", "C79", "C80", "C81"]
YEARS = [
    "1998-1999", "1999-2000", "2000-2001", "2001-2002", "2002-2003",
    "2003-2004", "2004-2005", "2005-2006", "2006-2007", "2007-2008",
    "2008-2009", "2011-2012", "2012-2013", "2013-2014", "2014-2015",
]
B_PERM = 9999
SEED = 20261006


class Mulberry32:
    """32-bit RNG matching the frozen JS audit implementation."""

    def __init__(self, seed: int):
        self.seed = seed & 0xFFFFFFFF

    def random(self) -> float:
        self.seed = (self.seed + 0x6D2B79F5) & 0xFFFFFFFF
        t = self.seed
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        t &= 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

    def permutation(self, n: int) -> list[int]:
        a = list(range(n))
        for i in range(n - 1, 0, -1):
            j = int(self.random() * (i + 1))
            a[i], a[j] = a[j], a[i]
        return a


def load_rows(path: str | None) -> list[dict[str, str]]:
    if path:
        text = Path(path).read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(SOURCE_URL) as response:
            text = response.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def next_season(s: str) -> str:
    y = int(s[:4])
    return f"{y+1}-{y+2}"


def previous_season(s: str) -> str:
    y = int(s[:4])
    return f"{y-1}-{y}"


def design(rows, extras):
    colonies = list(dict.fromkeys(r["colony"] for r in rows))
    years = list(dict.fromkeys(r["year"] for r in rows))
    X = []
    for r in rows:
        x = [1.0]
        x.extend(float(r["colony"] == c) for c in colonies[1:])
        x.extend(float(r["year"] == y) for y in years[1:])
        x.extend(float(f(r)) for f in extras)
        X.append(x)
    return np.asarray(X, dtype=float)


def fit(X: np.ndarray, y: np.ndarray):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    residual = y - X @ beta
    return beta, residual


def residualize(X: np.ndarray, v: np.ndarray) -> np.ndarray:
    return fit(X, v)[1]


def build_panel(raw):
    by = {(r["SEASON"], r["COLONY"]): r for r in raw}
    panel = []
    for year in YEARS:
        nxt = next_season(year)
        N0 = sum(float(by[(year, c)]["TOTAL_NUMBER_OF_PAIRS"]) for c in CORE)
        N1 = sum(float(by[(nxt, c)]["TOTAL_NUMBER_OF_PAIRS"]) for c in CORE)
        for colony in CORE:
            r0 = by[(year, colony)]
            r1 = by[(nxt, colony)]
            B0 = float(r0["TOTAL_NUMBER_OF_PAIRS"])
            B1 = float(r1["TOTAL_NUMBER_OF_PAIRS"])
            C0 = float(r0["TOTAL_NUMBER_OF_FLEDGLINGS"])
            panel.append({
                "year": year,
                "colony": colony,
                "B": B0,
                "B1": B1,
                "logB": math.log(B0),
                "log1pC": math.log1p(C0),
                "L": math.log(B0 / N0),
                "Y": math.log(B1 / N1),
            })
    return panel, by


def run_primary(panel):
    X1 = design(panel, [lambda r: r["logB"]])
    b1, q = fit(X1, np.asarray([r["log1pC"] for r in panel]))
    gamma = float(b1[-1])
    for r, qi in zip(panel, q):
        r["Q"] = float(qi)

    X2 = design(panel, [lambda r: r["L"], lambda r: r["Q"]])
    b2, _ = fit(X2, np.asarray([r["Y"] for r in panel]))
    rho, beta = map(float, b2[-2:])

    Xc = design(panel, [lambda r: r["L"]])
    yres = residualize(Xc, np.asarray([r["Y"] for r in panel]))
    qres = residualize(Xc, np.asarray([r["Q"] for r in panel]))
    standardized = beta * np.std(qres, ddof=1) / np.std(yres, ddof=1)
    return gamma, rho, beta, float(standardized)


def permutation_test(panel, observed_beta):
    Xc = design(panel, [lambda r: r["L"]])
    yres = residualize(Xc, np.asarray([r["Y"] for r in panel]))

    q_by_year = np.asarray([
        [next(r["Q"] for r in panel if r["year"] == y and r["colony"] == c) for c in CORE]
        for y in YEARS
    ], dtype=float)

    rng = Mulberry32(SEED)
    perm_betas = np.empty(B_PERM, dtype=float)
    exceed = 0

    for b in range(B_PERM):
        order = rng.permutation(len(YEARS))
        qp = q_by_year[order, :].reshape(-1)
        qres = residualize(Xc, qp)
        beta = float(np.dot(qres, yres) / np.dot(qres, qres))
        perm_betas[b] = beta
        exceed += beta >= observed_beta

    return {
        "exceedances_ge_observed": int(exceed),
        "p": (1 + exceed) / (B_PERM + 1),
        "q05": float(np.quantile(perm_betas, 0.05)),
        "median": float(np.quantile(perm_betas, 0.50)),
        "q95": float(np.quantile(perm_betas, 0.95)),
    }


def loo(panel):
    out = {}
    for omit in CORE:
        sub = [dict(r) for r in panel if r["colony"] != omit]
        out[omit] = run_primary(sub)[2]
    return out


def backward(panel, by):
    rows = []
    for r in panel:
        prev = previous_season(r["year"])
        try:
            prev_counts = [float(by[(prev, c)]["TOTAL_NUMBER_OF_PAIRS"]) for c in CORE]
            cur_counts = [float(by[(r["year"], c)]["TOTAL_NUMBER_OF_PAIRS"]) for c in CORE]
        except (KeyError, ValueError):
            continue
        if any(x <= 0 for x in prev_counts + cur_counts):
            continue
        Nprev, Ncur = sum(prev_counts), sum(cur_counts)
        rp = by[(prev, r["colony"])]
        rc = by[(r["year"], r["colony"])]
        q = dict(r)
        q["Yback"] = math.log(
            (float(rc["TOTAL_NUMBER_OF_PAIRS"]) / Ncur)
            / (float(rp["TOTAL_NUMBER_OF_PAIRS"]) / Nprev)
        )
        rows.append(q)
    if not rows:
        return None
    X = design(rows, [lambda r: r["L"], lambda r: r["Q"]])
    b, _ = fit(X, np.asarray([r["Yback"] for r in rows]))
    return {
        "n_rows": len(rows),
        "n_start_seasons": len(set(r["year"] for r in rows)),
        "rho_current_log_share": float(b[-2]),
        "beta_Q": float(b[-1]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    raw = load_rows(args.input)
    panel, by = build_panel(raw)
    gamma, rho, beta, standardized = run_primary(panel)
    perm = permutation_test(panel, beta)

    result = {
        "gamma_log_current_pairs": gamma,
        "beta_Q": beta,
        "rho_current_log_share": rho,
        "standardized_beta_Q": standardized,
        "permutation": perm,
        "loo_beta": loo(panel),
        "backward_control": backward(panel, by),
        "decision": {
            "beta_positive": beta > 0,
            "p_le_0_05": perm["p"] <= 0.05,
            "primary_support_pass": beta > 0 and perm["p"] <= 0.05,
        },
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
