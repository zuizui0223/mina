#!/usr/bin/env python3
"""Reproduce the post-result Ross Island shock/rebound and branch-dependence audits."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

SIX = [
    "Cape Royds",
    "Cape Bird South",
    "Cape Bird Middle",
    "Cape Bird North",
    "Cape Crozier West",
    "Cape Crozier East",
]
DECLINE = list(range(1985, 2000))
RECOVERY = [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2009, 2010, 2011, 2012]

def read_counts(path: Path):
    out = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            year = int(row["year"])
            out[year] = {k: int(row[k]) for k in SIX}
    return out

def aggregate3(six):
    return {
        "Royds": six["Cape Royds"],
        "Bird": six["Cape Bird South"] + six["Cape Bird Middle"] + six["Cape Bird North"],
        "Crozier": six["Cape Crozier West"] + six["Cape Crozier East"],
    }

def effective_number(values):
    total = float(sum(values))
    return 1.0 / sum((v / total) ** 2 for v in values)

def state(counts, year):
    six = counts[year]
    three = aggregate3(six)
    n = sum(six.values())
    return {
        "year": year,
        "N": n,
        "E3": effective_number(three.values()),
        "E6": effective_number(six.values()),
        "three": three,
        "six": six,
        "shares3": {k: v / n for k, v in three.items()},
    }

def transition(a, b):
    out = {
        "start": a["year"],
        "end": b["year"],
        "N_fraction": b["N"] / a["N"] - 1.0,
        "E3_fraction": b["E3"] / a["E3"] - 1.0,
        "E6_fraction": b["E6"] / a["E6"] - 1.0,
        "three_factors": {k: b["three"][k] / a["three"][k] for k in a["three"]},
        "six_factors": {k: b["six"][k] / a["six"][k] for k in a["six"]},
        "three_changes": {k: b["three"][k] - a["three"][k] for k in a["three"]},
        "six_changes": {k: b["six"][k] - a["six"][k] for k in a["six"]},
    }
    out["all_three_increased"] = all(v > 1 for v in out["three_factors"].values())
    out["all_three_declined"] = all(v < 1 for v in out["three_factors"].values())
    out["all_six_increased"] = all(v > 1 for v in out["six_factors"].values())
    out["all_six_declined"] = all(v < 1 for v in out["six_factors"].values())
    return out

def matched_branch_pairs(states):
    decline_n = [states[y]["N"] for y in DECLINE]
    lo, hi = min(decline_n), max(decline_n)
    eligible = [y for y in RECOVERY if lo <= states[y]["N"] <= hi]
    pairs = []
    for ry in eligible:
        nearest = min(
            DECLINE,
            key=lambda dy: abs(math.log(states[ry]["N"]) - math.log(states[dy]["N"])),
        )
        d, r = states[nearest], states[ry]
        pairs.append({
            "decline_year": nearest,
            "recovery_year": ry,
            "decline_N": d["N"],
            "recovery_N": r["N"],
            "N_fraction_difference": r["N"] / d["N"] - 1.0,
            "decline_E3": d["E3"],
            "recovery_E3": r["E3"],
            "E3_fraction_difference": r["E3"] / d["E3"] - 1.0,
            "decline_E6": d["E6"],
            "recovery_E6": r["E6"],
            "E6_fraction_difference": r["E6"] / d["E6"] - 1.0,
        })
    return {"decline_N_support": [lo, hi], "eligible_recovery_years": eligible, "pairs": pairs}

def build(counts):
    states = {y: state(counts, y) for y in sorted(counts)}
    return {
        "schema_version": 1,
        "source": "external/ross_island_v2_frozen_counts.csv",
        "states": {str(y): states[y] for y in [1999, 2001, 2002, 2012]},
        "transitions": {
            "1999_2001_shock": transition(states[1999], states[2001]),
            "2001_2002_rebound": transition(states[2001], states[2002]),
            "2002_2012_later": transition(states[2002], states[2012]),
            "1999_2012_pre_shock_to_late": transition(states[1999], states[2012]),
        },
        "matched_branch": matched_branch_pairs(states),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("external/ross_island_v2_frozen_counts.csv"))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    result = build(read_counts(args.input))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

if __name__ == "__main__":
    main()
