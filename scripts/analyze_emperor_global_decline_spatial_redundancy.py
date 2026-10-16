#!/usr/bin/env python3
"""Reproduce the prospective global emperor-penguin endpoint decomposition.

Pinned public source:
  davidiles/EMPE_Global
  commit 13f71112da43c1fd082273677757b41c550457ed
  analysis/output/model_results/3_Colony_Level/colony_summary.csv
"""
from __future__ import annotations

import csv
import io
import json
import math
import urllib.request

URL = (
    "https://raw.githubusercontent.com/davidiles/EMPE_Global/"
    "13f71112da43c1fd082273677757b41c550457ed/"
    "analysis/output/model_results/3_Colony_Level/colony_summary.csv"
)

def load_pairs():
    with urllib.request.urlopen(URL) as response:
        text = response.read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    y0 = {r["site_id"]: r for r in rows if int(r["year"]) == 2009}
    y1 = {r["site_id"]: r for r in rows if int(r["year"]) == 2018}
    ids = sorted(set(y0) & set(y1), key=lambda k: int(y0[k]["site_number"]))
    return [(y0[k], y1[k]) for k in ids]

def effective_number(values):
    total = sum(values)
    return total * total / sum(x * x for x in values)

def main():
    pairs = load_pairs()
    n0 = [float(a["N_median"]) for a, _ in pairs]
    n1 = [float(b["N_median"]) for _, b in pairs]

    N0, N1 = sum(n0), sum(n1)
    E0, E1 = effective_number(n0), effective_number(n1)

    g_bar = N1 / N0
    g_d_star = math.sqrt(
        sum(x * x for x in n1) /
        sum(x * x for x in n0)
    )

    observed = E1 / E0
    predicted = (g_bar / g_d_star) ** 2
    assert math.isclose(observed, predicted, rel_tol=1e-12, abs_tol=1e-12)

    changes = [b - a for a, b in zip(n0, n1)]

    result = {
        "n_colonies": len(pairs),
        "N2009": N0,
        "N2018": N1,
        "E2009": E0,
        "E2018": E1,
        "N_ratio": N1 / N0,
        "E_ratio": E1 / E0,
        "G_bar": g_bar,
        "G_D_star": g_d_star,
        "identity_ratio": predicted,
        "n_up": sum(x > 0 for x in changes),
        "n_down": sum(x < 0 for x in changes),
        "zero_baseline_sites": [
            a["site_name"] for a, _ in pairs if float(a["N_median"]) == 0
        ],
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
