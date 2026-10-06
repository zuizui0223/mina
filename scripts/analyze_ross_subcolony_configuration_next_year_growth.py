#!/usr/bin/env python3
"""Prospective Ross subcolony configuration -> next-year growth test."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

CROZ_ORDER = [
    "203","304","405","506","607","708","809","910",
    "1011","1112","1213","1314","1415","1516","1617","1718"
]
ROYDS_ORDER = ["1415","1516","1617","1718"]
B_PERM = 9999
SEED = 20261006


def build_eligible(df: pd.DataFrame, colony: str, seasons: list[str]) -> pd.DataFrame:
    df = df.copy()
    df["season"] = df["season"].astype(str)
    df["subcol"] = df["subcol"].astype(str)
    rows = {(r.season, r.subcol): r for r in df.itertuples(index=False)}
    out = []
    for s0, s1 in zip(seasons[:-1], seasons[1:]):
        subs = sorted(
            set(df.loc[df.season == s0, "subcol"])
            & set(df.loc[df.season == s1, "subcol"])
        )
        for sub in subs:
            a, b = rows[(s0, sub)], rows[(s1, sub)]
            vals = [a.active_ct, b.active_ct, a.pa_ratio, a.area]
            if any(pd.isna(x) for x in vals):
                continue
            if not (a.active_ct > 0 and b.active_ct > 0 and a.area > 0 and a.pa_ratio > 0):
                continue
            out.append({
                "colony": colony,
                "year": s0,
                "subcol": sub,
                "B": float(a.active_ct),
                "B1": float(b.active_ct),
                "pa": float(a.pa_ratio),
                "area": float(a.area),
            })
    return pd.DataFrame(out)


def demean(v: np.ndarray, group: np.ndarray) -> np.ndarray:
    out = v.astype(float).copy()
    for g in np.unique(group):
        m = group == g
        out[m] -= out[m].mean()
    return out


def fit_panel(panel: pd.DataFrame) -> np.ndarray:
    group = (panel["colony"] + "|" + panel["year"]).to_numpy()
    y = demean(np.log(panel["B1"].to_numpy() / panel["B"].to_numpy()), group)
    b = demean(np.log(panel["B"].to_numpy()), group)
    p = demean(panel["P"].to_numpy(), group)
    a = demean(panel["A"].to_numpy(), group)
    X = np.column_stack([b, p, a])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crozier", type=Path, required=True)
    ap.add_argument("--royds", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    c = build_eligible(pd.read_csv(args.crozier), "croz", CROZ_ORDER)
    r = build_eligible(pd.read_csv(args.royds), "royds", ROYDS_ORDER)
    panel = pd.concat([c, r], ignore_index=True)

    geom = panel[["colony","subcol","pa","area"]].drop_duplicates()
    geom["log_pa"] = np.log(geom["pa"])
    geom["log_area"] = np.log(geom["area"])
    geom["P"] = geom.groupby("colony")["log_pa"].transform(
        lambda x: (x - x.mean()) / x.std(ddof=1)
    )
    geom["A"] = geom.groupby("colony")["log_area"].transform(
        lambda x: (x - x.mean()) / x.std(ddof=1)
    )
    panel = panel.merge(geom[["colony","subcol","P","A"]], on=["colony","subcol"])

    beta = fit_panel(panel)
    gamma, beta_p, beta_a = map(float, beta)

    rng = np.random.default_rng(SEED)
    perm = np.empty(B_PERM)
    for k in range(B_PERM):
        pieces = []
        for colony in ("croz", "royds"):
            g = geom[geom["colony"] == colony][["subcol","P","A"]].sort_values("subcol")
            order = rng.permutation(len(g))
            mapping = {
                sub: (float(p), float(a))
                for sub, p, a in zip(g["subcol"], g["P"].to_numpy()[order], g["A"].to_numpy()[order])
            }
            x = panel[panel["colony"] == colony].copy()
            x[["P","A"]] = [mapping[s] for s in x["subcol"]]
            pieces.append(x)
        perm[k] = fit_panel(pd.concat(pieces, ignore_index=True))[1]

    extreme = int(np.sum(perm <= beta_p))
    p = (1 + extreme) / (B_PERM + 1)

    loo = []
    for colony, subcol in geom[["colony","subcol"]].itertuples(index=False):
        x = panel[~((panel["colony"] == colony) & (panel["subcol"] == subcol))]
        loo.append(float(fit_panel(x)[1]))

    colony_specific = {}
    for colony in ("croz","royds"):
        x = panel[panel["colony"] == colony]
        b = fit_panel(x)
        colony_specific[colony] = {
            "n_rows": int(len(x)),
            "n_subcolonies": int(x["subcol"].nunique()),
            "n_transitions": int(x["year"].nunique()),
            "gamma_log_current_abundance": float(b[0]),
            "beta_P": float(b[1]),
            "beta_A": float(b[2]),
        }

    result = {
        "n_rows": int(len(panel)),
        "n_subcolonies": int(geom.shape[0]),
        "gamma_log_current_abundance": gamma,
        "beta_P": beta_p,
        "beta_A": beta_a,
        "growth_multiplier_per_plus1SD_P": math.exp(beta_p),
        "permutation": {
            "B": B_PERM,
            "seed": SEED,
            "extreme_count": extreme,
            "p": p,
            "q05": float(np.quantile(perm,0.05)),
            "median": float(np.quantile(perm,0.50)),
            "q95": float(np.quantile(perm,0.95)),
        },
        "loo": {
            "n": len(loo),
            "n_negative": int(sum(x < 0 for x in loo)),
            "min": min(loo),
            "median": float(np.median(loo)),
            "max": max(loo),
        },
        "colony_specific": colony_specific,
        "decision": {
            "beta_negative": beta_p < 0,
            "p_le_0_05": p <= 0.05,
            "primary_support_pass": beta_p < 0 and p <= 0.05,
        },
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
