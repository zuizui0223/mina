#!/usr/bin/env python3
"""Audit Antarctic Ecosystem Inventory VAT schema before hierarchical trait mapping."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dbfread import DBF


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--vat-dbf",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()

    table=DBF(str(a.vat_dbf),load=True,ignore_missing_memofile=True,char_decode_errors="ignore")
    fields=[f.name for f in table.fields]
    rows=[dict(r) for r in table]
    sample=rows[:20]

    unique_counts={}
    for field in fields:
        vals=[]
        for row in rows:
            v=row.get(field)
            if v not in (None,""):
                vals.append(str(v))
        unique_counts[field]=len(set(vals))

    result={
        "schema_version":1,
        "audit_id":"mina-aei-vat-schema-audit-v1",
        "row_count":len(rows),
        "fields":fields,
        "unique_counts":unique_counts,
        "sample_rows":sample,
        "outcome_blind":True,
        "purpose":"Identify explicit Tier 1/2/3 classification fields before mapping raster values to ecological hierarchy."
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True,default=str))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
