#!/usr/bin/env python3
"""Bird Island Gentoo frozen success-to-allocation test and post-effect diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np

UNITS = [
    "Johnson",
    "Square Pond",
    "Upper Natural Arch",
    "Lower Natural Arch",
    "Upper Mountain Cwm",
    "Lower Mountain Cwm",
]
ELIGIBLE = [
    1984, 1986, 1987, 1988, 1989,
    1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999,
    2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
    2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
    2020, 2021, 2022, 2023,
]

def parse_year(s):
    if not s:
        return None
    return datetime.strptime(s, "%d/%m/%Y").year

def read_csv(path):
    lines = [line for line in Path(path).read_text(encoding="utf-8").splitlines() if not line.startswith("#")]
    rows = list(csv.DictReader(lines))
    out = {}
    for r in rows:
        if r.get("Colony") not in UNITS or not r.get("Date_nests_counted"):
            continue
        y = parse_year(r["Date_nests_counted"])
        out[(y, r["Colony"])] = {
            "nests": None if not r.get("Number_of_nests") else float(r["Number_of_nests"]),
            "chicks": None if not r.get("Number_of_chicks") else float(r["Number_of_chicks"]),
        }
    return out

def matrix(data, field, years):
    return np.array([[data[(y,u)][field] for u in UNITS] for y in years], dtype=float)

def twoway_demean(x):
    return x - x.mean(axis=1, keepdims=True) - x.mean(axis=0, keepdims=True) + x.mean()

def beta_fe(x, y):
    xd = twoway_demean(x)
    yd = twoway_demean(y)
    return float(np.sum(xd*yd)/np.sum(xd*xd)), xd, yd

def permutation(xd, yd, seed=20261006, B=9999):
    obs = float(np.sum(xd*yd)/np.sum(xd*xd))
    den = float(np.sum(xd*xd))
    rng = np.random.default_rng(seed)
    vals = np.empty(B)
    for b in range(B):
        p = rng.permutation(xd.shape[0])
        vals[b] = np.sum(xd[p,:]*yd)/den
    return {
        "beta": obs,
        "extreme": int(np.sum(vals >= obs)),
        "p": float((1 + np.sum(vals >= obs))/(B+1)),
        "q05": float(np.quantile(vals,0.05)),
        "median": float(np.quantile(vals,0.5)),
        "q95": float(np.quantile(vals,0.95)),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", type=Path)
    args=ap.parse_args()

    d=read_csv(args.input)
    nests=matrix(d,"nests",ELIGIBLE)
    chicks=matrix(d,"chicks",ELIGIBLE)
    nests_next=matrix(d,"nests",[y+1 for y in ELIGIBLE])

    S=chicks/nests
    p0=nests/nests.sum(axis=1,keepdims=True)
    p1=nests_next/nests_next.sum(axis=1,keepdims=True)
    Y=np.log(p1/p0)

    beta, Sd, Yd=beta_fe(S,Y)
    primary=permutation(Sd,Yd)

    loo={}
    for j,u in enumerate(UNITS):
        keep=[k for k in range(len(UNITS)) if k != j]
        loo[u]=beta_fe(S[:,keep],Y[:,keep])[0]

    sdS=float(Sd.ravel().std(ddof=1))
    sdY=float(Yd.ravel().std(ddof=1))

    bad=np.argwhere(S>2)
    bad_rows=[
        {
            "year": ELIGIBLE[i],
            "unit": UNITS[j],
            "nests": float(nests[i,j]),
            "chicks": float(chicks[i,j]),
            "ratio": float(S[i,j]),
        }
        for i,j in bad
    ]

    result={
        "primary": primary,
        "n_years": len(ELIGIBLE),
        "n_rows": len(ELIGIBLE)*len(UNITS),
        "sd_success_two_way": sdS,
        "effect_per_1sd_log_share": beta*sdS,
        "share_multiplier_per_1sd": math.exp(beta*sdS),
        "fully_standardized_beta": beta*sdS/sdY,
        "leave_one_unit_out_beta": loo,
        "rows_success_gt_2": bad_rows,
    }

    text=json.dumps(result,indent=2)+"\n"
    if args.out:
        args.out.write_text(text,encoding="utf-8")
    else:
        print(text,end="")

if __name__=="__main__":
    main()
