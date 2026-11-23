#!/usr/bin/env python3
"""Verify Ross iceberg shock/rebound decomposition from frozen six-component counts."""

from __future__ import annotations
import csv
from pathlib import Path

SIX = [
    "Cape Royds",
    "Cape Bird South",
    "Cape Bird Middle",
    "Cape Bird North",
    "Cape Crozier West",
    "Cape Crozier East",
]
ANCHORS = [1999, 2001, 2002, 2012]

def effective(values):
    total=sum(values)
    p=[x/total for x in values]
    return 1.0/sum(x*x for x in p)

def aggregate3(row):
    return [
        row["Cape Royds"],
        row["Cape Bird South"]+row["Cape Bird Middle"]+row["Cape Bird North"],
        row["Cape Crozier West"]+row["Cape Crozier East"],
    ]

def main():
    path=Path("external/ross_island_v2_frozen_counts.csv")
    rows={}
    with path.open(newline="",encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            year=int(r["year"])
            if year in ANCHORS:
                rows[year]={k:int(r[k]) for k in SIX}

    for year in ANCHORS:
        six=[rows[year][k] for k in SIX]
        three=aggregate3(rows[year])
        print(year, sum(six), effective(three), effective(six), *three)

    for a,b in zip(ANCHORS[:-1],ANCHORS[1:]):
        va=[rows[a][k] for k in SIX]
        vb=[rows[b][k] for k in SIX]
        ta,tb=aggregate3(rows[a]),aggregate3(rows[b])
        print(
            f"{a}->{b}",
            f"N={sum(vb)/sum(va)-1:+.6f}",
            f"E3={effective(tb)/effective(ta)-1:+.6f}",
            f"E6={effective(vb)/effective(va)-1:+.6f}",
            "factors3="+",".join(f"{y/x:.6f}" for x,y in zip(ta,tb)),
        )

if __name__=="__main__":
    main()
