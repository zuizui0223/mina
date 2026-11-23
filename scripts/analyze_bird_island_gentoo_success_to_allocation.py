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
SEED = 20261006
B = 9999

def parse_year(s):
    if not s:
        return None
    return datetime.strptime(s, "%d/%m/%Y").year

def read_csv(path):
    lines = [
        line for line in Path(path).read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
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

def matrix(data, field, years, units=UNITS):
    return np.array([[data[(y,u)][field] for u in units] for y in years], dtype=float)

def twoway_demean(x):
    return x - x.mean(axis=1, keepdims=True) - x.mean(axis=0, keepdims=True) + x.mean()

def beta_fe(x, y):
    xd = twoway_demean(x)
    yd = twoway_demean(y)
    return float(np.sum(xd*yd)/np.sum(xd*xd)), xd, yd

def permutation_from_demeaned(xd, yd, seed=SEED, B=B, alternative="positive"):
    obs = float(np.sum(xd*yd)/np.sum(xd*xd))
    den = float(np.sum(xd*xd))
    rng = np.random.default_rng(seed)
    vals = np.empty(B)
    for b in range(B):
        p = rng.permutation(xd.shape[0])
        vals[b] = np.sum(xd[p,:]*yd)/den
    if alternative == "positive":
        extreme = int(np.sum(vals >= obs))
    elif alternative == "negative":
        extreme = int(np.sum(vals <= obs))
    else:
        raise ValueError(alternative)
    return {
        "beta": obs,
        "extreme": extreme,
        "p": float((1 + extreme)/(B+1)),
        "q05": float(np.quantile(vals,0.05)),
        "median": float(np.quantile(vals,0.5)),
        "q95": float(np.quantile(vals,0.95)),
    }

def partial_out(a, z):
    av = a.ravel()
    zv = z.ravel()
    coef = float(np.dot(zv,av)/np.dot(zv,zv))
    return (av - coef*zv).reshape(a.shape), coef

def perm_partial(xd, yd, z, seed=SEED, B=B):
    yr, ycoef = partial_out(yd, z)
    xr, xcoef = partial_out(xd, z)
    obs = float(np.sum(xr*yr)/np.sum(xr*xr))

    zv=z.ravel()
    zz=float(np.dot(zv,zv))
    yrv=yr.ravel()
    rng=np.random.default_rng(seed)
    vals=np.empty(B)
    for b in range(B):
        p=rng.permutation(xd.shape[0])
        xp=xd[p,:].ravel()
        coef=float(np.dot(zv,xp)/zz)
        xpr=xp-coef*zv
        vals[b]=float(np.dot(xpr,yrv)/np.dot(xpr,xpr))
    extreme=int(np.sum(vals>=obs))
    return {
        "beta":obs,
        "p":float((1+extreme)/(B+1)),
        "extreme":extreme,
        "q05":float(np.quantile(vals,0.05)),
        "median":float(np.quantile(vals,0.5)),
        "q95":float(np.quantile(vals,0.95)),
        "x_covariate_coefficient":xcoef,
        "y_covariate_coefficient":ycoef,
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
    nests_prev=matrix(d,"nests",[y-1 for y in ELIGIBLE])

    S=chicks/nests
    p0=nests/nests.sum(axis=1,keepdims=True)
    p1=nests_next/nests_next.sum(axis=1,keepdims=True)
    pm1=nests_prev/nests_prev.sum(axis=1,keepdims=True)
    Y=np.log(p1/p0)
    Yprev=np.log(p0/pm1)

    beta, Sd, Yd=beta_fe(S,Y)
    primary=permutation_from_demeaned(Sd,Yd)

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
    bad_years=sorted({x["year"] for x in bad_rows})

    # Post-effect diagnostic A: success index against current log share.
    logp=twoway_demean(np.log(p0))
    success_on_share=float(np.dot(logp.ravel(),Sd.ravel())/np.dot(logp.ravel(),logp.ravel()))
    corr_success_share=float(np.corrcoef(Sd.ravel(),logp.ravel())[0,1])
    neg_perm=permutation_from_demeaned(Sd,logp,alternative="negative")

    # Post-effect diagnostic B: backward share change.
    _, Yprevd=beta_fe(Yprev,Yprev)[1:]  # only need two-way demeaned Yprev
    backward=permutation_from_demeaned(Sd,Yprevd,alternative="negative")
    backward["residual_correlation"]=float(np.corrcoef(Sd.ravel(),Yprevd.ravel())[0,1])

    # Post-effect diagnostic C: primary plus current log share control.
    current_share_control=perm_partial(Sd,Yd,logp)

    # Post-effect diagnostic D: ratio-free log chick count, controlling log current nests.
    logchicks=twoway_demean(np.log1p(chicks))
    lognests=twoway_demean(np.log(nests))
    ratio_free=perm_partial(logchicks,Yd,lognests)

    # Post-effect diagnostic E: Johnson + Square Pond timing colonies only.
    timing_idx=[UNITS.index("Johnson"),UNITS.index("Square Pond")]
    _, Stiming, Ytiming=beta_fe(S[:,timing_idx],Y[:,timing_idx])
    timing=permutation_from_demeaned(Stiming,Ytiming)

    # Post-effect diagnostic F: remove every year containing any S>2.
    good=[i for i,y in enumerate(ELIGIBLE) if y not in bad_years]
    _, Sgood, Ygood=beta_fe(S[good,:],Y[good,:])
    no_gt2=permutation_from_demeaned(Sgood,Ygood)

    result={
        "primary":primary,
        "n_years":len(ELIGIBLE),
        "n_rows":len(ELIGIBLE)*len(UNITS),
        "sd_success_two_way":sdS,
        "effect_per_1sd_log_share":beta*sdS,
        "share_multiplier_per_1sd":math.exp(beta*sdS),
        "fully_standardized_beta":beta*sdS/sdY,
        "leave_one_unit_out_beta":loo,
        "rows_success_gt_2":bad_rows,
        "post_effect_diagnostics":{
            "success_vs_current_log_share":{
                "coefficient":success_on_share,
                "residual_correlation":corr_success_share,
                "negative_permutation":neg_perm
            },
            "success_vs_previous_share_change":backward,
            "primary_plus_current_log_share_control":current_share_control,
            "ratio_free_log1p_chicks_controlling_log_nests":ratio_free,
            "timing_colonies_only":timing,
            "exclude_years_with_any_success_gt_2":{
                "n_years":len(good),
                "years_removed":bad_years,
                **no_gt2
            }
        }
    }

    text=json.dumps(result,indent=2)+"\n"
    if args.out:
        args.out.write_text(text,encoding="utf-8")
    else:
        print(text,end="")

if __name__=="__main__":
    main()
