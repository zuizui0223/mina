#!/usr/bin/env python3
"""Reproduce the frozen Ross Island V2 decline/recovery analysis.

Input is a derived CSV containing only the six Ross Island census rows and
the years frozen in contracts/ROSS_ISLAND_DECLINE_RECOVERY_SPATIAL_ASYMMETRY_V2.md.
The original workbook source is DOI 10.7931/kf06-x745.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

DECLINE = list(range(1985, 2000))
RECOVERY = [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2009, 2010, 2011, 2012]
SIX = [
    "Cape Royds",
    "Cape Bird South",
    "Cape Bird Middle",
    "Cape Bird North",
    "Cape Crozier West",
    "Cape Crozier East",
]

def effective_number(values):
    total = float(sum(values))
    shares = [v / total for v in values]
    return 1.0 / sum(p * p for p in shares)

def aggregate3(row):
    return {
        "Royds": row["Cape Royds"],
        "Bird": row["Cape Bird South"] + row["Cape Bird Middle"] + row["Cape Bird North"],
        "Crozier": row["Cape Crozier West"] + row["Cape Crozier East"],
    }

def slope(x, y):
    return float(np.polyfit(np.asarray(x, float), np.asarray(y, float), 1)[0])

def read_counts(path):
    out = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            year = int(row["year"])
            out[year] = {k: int(row[k]) for k in SIX}
    return out

def summarize(counts, years):
    annual = {}
    for year in years:
        six = counts[year]
        three = aggregate3(six)
        n = sum(six.values())
        annual[year] = {
            "N": n,
            "E3": effective_number(three.values()),
            "E6": effective_number(six.values()),
            "three": three,
        }

    start, end = years[0], years[-1]
    a0, a1 = annual[start]["three"], annual[end]["three"]
    n0, n1 = annual[start]["N"], annual[end]["N"]
    p0 = {k: a0[k] / n0 for k in a0}
    expected = {k: n1 * p0[k] for k in a0}
    residual = {k: a1[k] - expected[k] for k in a0}
    changes = {k: a1[k] - a0[k] for k in a0}

    logn = [math.log(annual[y]["N"]) for y in years]
    loge3 = [math.log(annual[y]["E3"]) for y in years]
    loge6 = [math.log(annual[y]["E6"]) for y in years]

    return {
        "years": years,
        "n_years": len(years),
        "slope_logN_per_year": slope(years, logn),
        "slope_logE3_per_year": slope(years, loge3),
        "slope_logE6_per_year": slope(years, loge6),
        "kappa3_secondary": slope(logn, loge3),
        "kappa6_secondary": slope(logn, loge6),
        "start": {
            "year": start,
            "N": n0,
            "E3": annual[start]["E3"],
            "E6": annual[start]["E6"],
            "colonies": a0,
        },
        "end": {
            "year": end,
            "N": n1,
            "E3": annual[end]["E3"],
            "E6": annual[end]["E6"],
            "colonies": a1,
        },
        "endpoint_change": {
            "N": n1 - n0,
            "E3": annual[end]["E3"] - annual[start]["E3"],
            "E6": annual[end]["E6"] - annual[start]["E6"],
            "N_fraction": n1 / n0 - 1.0,
            "E3_fraction": annual[end]["E3"] / annual[start]["E3"] - 1.0,
            "E6_fraction": annual[end]["E6"] / annual[start]["E6"] - 1.0,
        },
        "colony_absolute_changes": changes,
        "colony_proportional_residuals": residual,
        "gross_endpoint_gain": sum(max(v, 0) for v in changes.values()),
        "gross_endpoint_loss": sum(max(-v, 0) for v in changes.values()),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("external/ross_island_v2_frozen_counts.csv"))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    counts = read_counts(args.input)
    decline = summarize(counts, DECLINE)
    recovery = summarize(counts, RECOVERY)
    result = {
        "schema_version": 1,
        "contract": "contracts/ROSS_ISLAND_DECLINE_RECOVERY_SPATIAL_ASYMMETRY_V2.md",
        "source_doi": "10.7931/kf06-x745",
        "decline": decline,
        "recovery": recovery,
        "decision": {
            "decline_abundance_gate_pass": decline["slope_logN_per_year"] < 0,
            "recovery_abundance_gate_pass": recovery["slope_logN_per_year"] > 0,
            "P1_decline_E3_direction_pass": (
                decline["slope_logE3_per_year"] < 0 and decline["endpoint_change"]["E3"] < 0
            ),
            "P2_recovery_E3_deconcentration_pass": (
                recovery["slope_logE3_per_year"] > 0 and recovery["endpoint_change"]["E3"] > 0
            ),
            "recovery_all_three_colonies_increased": all(
                v > 0 for v in recovery["colony_absolute_changes"].values()
            ),
        },
    }
    result["decision"]["strong_v2_support"] = all([
        result["decision"]["decline_abundance_gate_pass"],
        result["decision"]["recovery_abundance_gate_pass"],
        result["decision"]["P1_decline_E3_direction_pass"],
        result["decision"]["P2_recovery_E3_deconcentration_pass"],
    ])

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

if __name__ == "__main__":
    main()
