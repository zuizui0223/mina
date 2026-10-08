#!/usr/bin/env python3
"""Reproduce Ross aggregate-versus-spatial restoration decomposition.

Input:
  external/ross_island_v2_frozen_counts.csv

Anchors:
  1999 = last complete pre-shock six-component census
  2001 = documented common iceberg-disturbance trough
  2002 = immediate rebound
  2012 = late recovery state
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

SIX = [
    "Cape Royds",
    "Cape Bird South",
    "Cape Bird Middle",
    "Cape Bird North",
    "Cape Crozier West",
    "Cape Crozier East",
]

def read_counts(path: Path):
    rows = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            y = int(row["year"])
            rows[y] = {k: int(row[k]) for k in SIX}
    return rows

def effective_number(values):
    n = float(sum(values))
    p = [x / n for x in values]
    return 1.0 / sum(x*x for x in p)

def aggregate3(row):
    return {
        "Royds": row["Cape Royds"],
        "Bird": row["Cape Bird South"] + row["Cape Bird Middle"] + row["Cape Bird North"],
        "Crozier": row["Cape Crozier West"] + row["Cape Crozier East"],
    }

def shares(d):
    n = float(sum(d.values()))
    return {k: v/n for k,v in d.items()}

def total_variation(p, q):
    return 0.5 * sum(abs(p[k] - q[k]) for k in p)

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("external/ross_island_v2_frozen_counts.csv"))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    x = read_counts(args.input)
    pre, shock, rebound, late = (x[y] for y in (1999, 2001, 2002, 2012))

    n_pre = sum(pre.values())
    n_shock = sum(shock.values())
    n_rebound = sum(rebound.values())
    n_late = sum(late.values())

    loss = {k: pre[k] - shock[k] for k in SIX}
    gain = {k: rebound[k] - shock[k] for k in SIX}
    restored_fraction = {k: gain[k] / loss[k] for k in SIX}

    pre3, shock3, rebound3, late3 = map(aggregate3, (pre, shock, rebound, late))
    loss3 = {k: pre3[k] - shock3[k] for k in pre3}
    gain3 = {k: rebound3[k] - shock3[k] for k in pre3}
    restored3 = {k: gain3[k] / loss3[k] for k in pre3}

    expected3 = {k: n_rebound * pre3[k] / n_pre for k in pre3}
    residual3 = {k: rebound3[k] - expected3[k] for k in pre3}
    expected6 = {k: n_rebound * pre[k] / n_pre for k in SIX}
    residual6 = {k: rebound[k] - expected6[k] for k in SIX}

    p_pre3, p_reb3 = shares(pre3), shares(rebound3)
    p_pre6, p_reb6 = shares(pre), shares(rebound)

    result = {
        "schema_version": 1,
        "source": "external/ross_island_v2_frozen_counts.csv",
        "anchors": [1999, 2001, 2002, 2012],
        "aggregate": {
            "pre_shock_N_1999": n_pre,
            "shock_N_2001": n_shock,
            "rebound_N_2002": n_rebound,
            "late_N_2012": n_late,
            "shock_loss_1999_2001": n_pre - n_shock,
            "rebound_gain_2001_2002": n_rebound - n_shock,
            "fraction_aggregate_loss_restored_by_2002": (n_rebound - n_shock)/(n_pre - n_shock),
            "N_2002_over_N_1999": n_rebound/n_pre,
        },
        "three_colony": {
            "loss_1999_2001": loss3,
            "gain_2001_2002": gain3,
            "fraction_loss_restored": restored3,
            "composition_preserving_expected_2002": expected3,
            "observed_minus_expected_2002": residual3,
            "E_1999": effective_number(pre3.values()),
            "E_2001": effective_number(shock3.values()),
            "E_2002": effective_number(rebound3.values()),
            "E_2012": effective_number(late3.values()),
            "E_2002_over_E_1999": effective_number(rebound3.values())/effective_number(pre3.values()),
            "TV_1999_2002": total_variation(p_pre3, p_reb3),
        },
        "six_component": {
            "loss_1999_2001": loss,
            "gain_2001_2002": gain,
            "fraction_loss_restored": restored_fraction,
            "composition_preserving_expected_2002": expected6,
            "observed_minus_expected_2002": residual6,
            "E_1999": effective_number(pre.values()),
            "E_2001": effective_number(shock.values()),
            "E_2002": effective_number(rebound.values()),
            "E_2012": effective_number(late.values()),
            "E_2002_over_E_1999": effective_number(rebound.values())/effective_number(pre.values()),
            "TV_1999_2002": total_variation(p_pre6, p_reb6),
        },
        "decision": {
            "aggregate_nearly_restored_by_2002": n_rebound/n_pre >= 0.95,
            "all_three_colonies_exactly_restored": all(abs(restored3[k]-1) < 1e-12 for k in restored3),
            "spatial_composition_restored": total_variation(p_pre3, p_reb3) < 1e-12,
            "crozier_overshot_pre_shock": rebound3["Crozier"] > pre3["Crozier"],
            "royds_below_pre_shock": rebound3["Royds"] < pre3["Royds"],
            "bird_below_pre_shock": rebound3["Bird"] < pre3["Bird"],
        },
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

if __name__ == "__main__":
    main()
