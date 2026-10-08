#!/usr/bin/env python3
"""Prospective Ross subcolony configuration -> next-year growth test.

Depends only on the project-declared numpy runtime plus the Python standard
library. Reproduces:
  results/ROSS_SUBCOLONY_CONFIGURATION_NEXT_YEAR_GROWTH_V1.json
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

CROZ_ORDER = [
    "203","304","405","506","607","708","809","910",
    "1011","1112","1213","1314","1415","1516","1617","1718"
]
ROYDS_ORDER = ["1415","1516","1617","1718"]
B_PERM = 9999
SEED = 20261006


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def as_float(value: str | None) -> float | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.upper() == "NA":
        return None
    try:
        x = float(s)
    except ValueError:
        return None
    return x if math.isfinite(x) else None


def build_eligible(
    rows: list[dict[str, str]],
    colony: str,
    seasons: list[str],
) -> list[dict[str, float | str]]:
    index = {
        (str(r["season"]), str(r["subcol"])): r
        for r in rows
    }
    by_season: dict[str, set[str]] = {}
    for r in rows:
        by_season.setdefault(str(r["season"]), set()).add(str(r["subcol"]))

    out: list[dict[str, float | str]] = []
    for s0, s1 in zip(seasons[:-1], seasons[1:]):
        for sub in sorted(by_season.get(s0, set()) & by_season.get(s1, set())):
            a = index[(s0, sub)]
            b = index[(s1, sub)]
            B = as_float(a.get("active_ct"))
            B1 = as_float(b.get("active_ct"))
            pa = as_float(a.get("pa_ratio"))
            area = as_float(a.get("area"))
            if None in (B, B1, pa, area):
                continue
            assert B is not None and B1 is not None and pa is not None and area is not None
            if not (B > 0 and B1 > 0 and pa > 0 and area > 0):
                continue
            out.append({
                "colony": colony,
                "year": s0,
                "subcol": sub,
                "B": B,
                "B1": B1,
                "pa": pa,
                "area": area,
            })
    return out


def add_geometry_z(panel: list[dict]) -> dict[str, list[dict[str, float | str]]]:
    geometry: dict[str, dict[str, tuple[float, float]]] = {}
    for r in panel:
        col, sub = str(r["colony"]), str(r["subcol"])
        geometry.setdefault(col, {})
        pair = (float(r["pa"]), float(r["area"]))
        if sub in geometry[col] and geometry[col][sub] != pair:
            raise ValueError(f"non-static geometry for {col}:{sub}")
        geometry[col][sub] = pair

    geom_lists: dict[str, list[dict[str, float | str]]] = {}
    zmap: dict[tuple[str, str], tuple[float, float]] = {}
    for col, items in geometry.items():
        subs = sorted(items)
        log_pa = np.asarray([math.log(items[s][0]) for s in subs], dtype=float)
        log_area = np.asarray([math.log(items[s][1]) for s in subs], dtype=float)
        P = (log_pa - log_pa.mean()) / log_pa.std(ddof=1)
        A = (log_area - log_area.mean()) / log_area.std(ddof=1)
        geom_lists[col] = []
        for sub, p, a in zip(subs, P, A):
            zmap[(col, sub)] = (float(p), float(a))
            geom_lists[col].append({"subcol": sub, "P": float(p), "A": float(a)})

    for r in panel:
        r["P"], r["A"] = zmap[(str(r["colony"]), str(r["subcol"]))]

    return geom_lists


def group_codes(panel: list[dict]) -> tuple[np.ndarray, list[np.ndarray]]:
    labels = np.asarray([f'{r["colony"]}|{r["year"]}' for r in panel], dtype=object)
    _, codes = np.unique(labels, return_inverse=True)
    members = [np.where(codes == i)[0] for i in range(codes.max() + 1)]
    return codes, members


def demean(v: np.ndarray, members: list[np.ndarray]) -> np.ndarray:
    out = v.astype(float).copy()
    for idx in members:
        out[idx] -= out[idx].mean()
    return out


def fit_panel(panel: list[dict]) -> np.ndarray:
    _, members = group_codes(panel)
    y = demean(
        np.asarray([math.log(float(r["B1"]) / float(r["B"])) for r in panel]),
        members,
    )
    b = demean(np.asarray([math.log(float(r["B"])) for r in panel]), members)
    p = demean(np.asarray([float(r["P"]) for r in panel]), members)
    a = demean(np.asarray([float(r["A"]) for r in panel]), members)
    X = np.column_stack([b, p, a])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crozier", type=Path, required=True)
    ap.add_argument("--royds", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    panel = (
        build_eligible(read_rows(args.crozier), "croz", CROZ_ORDER)
        + build_eligible(read_rows(args.royds), "royds", ROYDS_ORDER)
    )
    geom_lists = add_geometry_z(panel)

    gamma, beta_p, beta_a = map(float, fit_panel(panel))

    row_col = np.asarray([str(r["colony"]) for r in panel], dtype=object)
    row_sub = np.asarray([str(r["subcol"]) for r in panel], dtype=object)
    row_idx: dict[str, dict[str, int]] = {
        col: {str(x["subcol"]): i for i, x in enumerate(items)}
        for col, items in geom_lists.items()
    }

    rng = np.random.default_rng(SEED)
    perm = np.empty(B_PERM, dtype=float)
    for k in range(B_PERM):
        x = [dict(r) for r in panel]
        for col in ("croz", "royds"):
            items = geom_lists[col]
            order = rng.permutation(len(items))
            P = np.asarray([float(z["P"]) for z in items])[order]
            A = np.asarray([float(z["A"]) for z in items])[order]
            for j, r in enumerate(x):
                if r["colony"] != col:
                    continue
                i = row_idx[col][str(row_sub[j])]
                r["P"], r["A"] = float(P[i]), float(A[i])
        perm[k] = float(fit_panel(x)[1])

    extreme = int(np.sum(perm <= beta_p))
    p = (1 + extreme) / (B_PERM + 1)

    loo = []
    for col, items in geom_lists.items():
        for item in items:
            sub = str(item["subcol"])
            x = [
                r for r in panel
                if not (r["colony"] == col and r["subcol"] == sub)
            ]
            loo.append(float(fit_panel(x)[1]))

    colony_specific = {}
    for col in ("croz", "royds"):
        x = [r for r in panel if r["colony"] == col]
        b = fit_panel(x)
        colony_specific[col] = {
            "n_rows": len(x),
            "n_subcolonies": len({str(r["subcol"]) for r in x}),
            "n_transitions": len({str(r["year"]) for r in x}),
            "gamma_log_current_abundance": float(b[0]),
            "beta_P": float(b[1]),
            "beta_A": float(b[2]),
        }

    result = {
        "n_rows": len(panel),
        "n_subcolonies": sum(len(v) for v in geom_lists.values()),
        "gamma_log_current_abundance": gamma,
        "beta_P": beta_p,
        "beta_A": beta_a,
        "growth_multiplier_per_plus1SD_P": math.exp(beta_p),
        "permutation": {
            "B": B_PERM,
            "seed": SEED,
            "rng": "numpy default_rng PCG64",
            "extreme_count": extreme,
            "p": p,
            "q05": float(np.quantile(perm, 0.05)),
            "median": float(np.quantile(perm, 0.50)),
            "q95": float(np.quantile(perm, 0.95)),
        },
        "loo": {
            "n": len(loo),
            "n_negative": int(sum(v < 0 for v in loo)),
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
