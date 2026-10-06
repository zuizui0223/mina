#!/usr/bin/env python3
"""Audit whether Cimino 2025 active physical subcolonies crosswalk to LTER Torgersen colony codes by 1993 counts."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

TARGETS=(953.0,397.0,254.0,999.0,1271.0)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    rows=[]
    with a.census.open("r",encoding="utf-8-sig",newline="") as h:
        for r in csv.DictReader(h):
            if str(r.get("island_name","")).strip()!="TOR":
                continue
            time=str(r.get("time",""))
            if not time.startswith("1993"):
                continue
            try:
                count=float(r.get("num_breeding_pairs",""))
            except Exception:
                continue
            rows.append({
                "colony_code":str(r.get("colony_code","")).strip(),
                "count":count,
            })
    rows=sorted(rows,key=lambda x:(x["count"],x["colony_code"]))
    matches={}
    for target in TARGETS:
        exact=[r for r in rows if r["count"]==target]
        matches[str(int(target))]=exact
    out={
        "schema_version":1,
        "analysis_id":"mina-torgersen-active-crosswalk-audit-v1",
        "source_year":1993,
        "physical_active_subcolony_1993_counts_from_cimino2025_table2":[int(x) for x in TARGETS],
        "lter_torgersen_1993_rows":rows,
        "exact_matches":matches,
        "all_five_unique_exact_matches":all(len(matches[str(int(t))])==1 for t in TARGETS),
        "interpretation_boundary":[
            "Count identity alone is a candidate identifier bridge, not final spatial validation.",
            "A one-to-one count match must be combined with physical polygon labels or an independent year/count signature before a full crosswalk claim.",
            "No extinction or habitat effect is tested here."
        ]
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
