#!/usr/bin/env python3
"""Verify path-aware spatial-redundancy examples for PR189."""

from __future__ import annotations
import math

def summary(values):
    total = float(sum(values))
    p = [v / total for v in values]
    return {
        "N": total,
        "shares": p,
        "E": 1.0 / sum(x*x for x in p),
        "dominant": max(range(len(values)), key=lambda i: values[i]),
    }

def tv(a, b):
    pa, pb = summary(a)["shares"], summary(b)["shares"]
    return 0.5 * sum(abs(x-y) for x, y in zip(pa, pb))

def exact_ratio(start, end):
    s0, s1 = summary(start), summary(end)
    g = [b/a for a,b in zip(start,end)]
    h0 = sum(p*p for p in s0["shares"])
    w0 = [p*p/h0 for p in s0["shares"]]
    gbar = sum(p*x for p,x in zip(s0["shares"],g))
    gd = math.sqrt(sum(w*x*x for w,x in zip(w0,g)))
    pred = (gbar/gd)**2
    obs = s1["E"]/s0["E"]
    assert math.isclose(pred, obs, rel_tol=1e-12, abs_tol=1e-12)
    return gbar, gd, obs

def main():
    ross0=[1367,26317,67114]
    ross1=[3083,75696,272340]
    heard={
        1963:[13,5],
        1965:[36,9],
        1969:[49,37],
        1980:[82,400],
        1988:[215,3100],
    }
    beau0=[47725,460]
    beau1=[63760,957]

    for name,a,b in [
        ("Ross 2001-2012",ross0,ross1),
        ("Heard 1963-1988",heard[1963],heard[1988]),
        ("Beaufort 2004-2010",beau0,beau1),
    ]:
        x0,x1=summary(a),summary(b)
        gbar,gd,er=exact_ratio(a,b)
        print(
            f"{name}: N {x0['N']:.0f}->{x1['N']:.0f}; "
            f"E {x0['E']:.6f}->{x1['E']:.6f}; "
            f"TV={tv(a,b):.6f}; dominant {x0['dominant']}->{x1['dominant']}; "
            f"Gbar={gbar:.6f}; GD={gd:.6f}; Eratio={er:.6f}"
        )

    print("Heard trajectory")
    for year,vals in heard.items():
        x=summary(vals)
        print(year, int(x["N"]), f"{x['E']:.6f}", x["dominant"])

if __name__ == "__main__":
    main()
