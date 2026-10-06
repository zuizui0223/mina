#!/usr/bin/env python3
"""Compute the Ross six-component inverse-path rebound mismatch."""

from __future__ import annotations
import csv
import json
import math
from pathlib import Path

UNITS = [
    "Cape Royds",
    "Cape Bird South",
    "Cape Bird Middle",
    "Cape Bird North",
    "Cape Crozier West",
    "Cape Crozier East",
]

def read(path: Path):
    out = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[int(row["year"])] = {u:int(row[u]) for u in UNITS}
    return out

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def norm(a):
    return math.sqrt(dot(a,a))

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=Path("external/ross_island_v2_frozen_counts.csv"))
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()

    x=read(args.input)
    loss=[x[1999][u]-x[2001][u] for u in UNITS]
    gain=[x[2002][u]-x[2001][u] for u in UNITS]
    L,G=sum(loss),sum(gain)

    expected=[G*z/L for z in loss]
    residual=[g-e for g,e in zip(gain,expected)]
    mismatch=0.5*sum(abs(z) for z in residual)
    cosine=dot(loss,gain)/(norm(loss)*norm(gain))

    assert math.isclose(sum(residual),0.0,abs_tol=1e-9)
    assert sum(z>0 for z in residual)==1
    assert UNITS[max(range(len(residual)),key=lambda i:residual[i])] == "Cape Crozier West"

    result={
        "total_loss":L,
        "total_gain":G,
        "aggregate_loss_restored_fraction":G/L,
        "cosine_similarity":cosine,
        "expected_inverse_rebound":dict(zip(UNITS,expected)),
        "residual":dict(zip(UNITS,residual)),
        "half_L1_mismatch":mismatch,
        "mismatch_fraction_of_rebound":mismatch/G,
    }
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.write_text(text,encoding="utf-8")
    else:
        print(text,end="")

if __name__=="__main__":
    main()
