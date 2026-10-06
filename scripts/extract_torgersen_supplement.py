#!/usr/bin/env python3
"""Extract searchable text and table content from the Cimino et al. 2025 DOCX supplement."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from docx import Document


def clean(x: str) -> str:
    return re.sub(r"\s+", " ", str(x)).strip()


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--docx",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-text",required=True,type=Path)
    a=p.parse_args()

    doc=Document(a.docx)

    paragraphs=[]
    for i,p0 in enumerate(doc.paragraphs):
        t=clean(p0.text)
        if t:
            paragraphs.append({"index":i,"text":t})

    tables=[]
    for ti,table in enumerate(doc.tables):
        rows=[]
        for ri,row in enumerate(table.rows):
            vals=[clean(cell.text) for cell in row.cells]
            rows.append(vals)
        flat=" | ".join(" | ".join(r) for r in rows)
        tables.append({
            "table_index":ti,
            "n_rows":len(rows),
            "n_cols_max":max((len(r) for r in rows),default=0),
            "rows":rows,
            "matches_s13":bool(re.search(r"\bS13\b|sub.?col|extinct|breeding pairs|colony",flat,re.I)),
        })

    # Context windows around S3/S13/Table 2/extinction terms.
    keys=re.compile(r"S13|Supplemental Information S3|Table S2|Table S13|extinction|sub-?colon",re.I)
    hits=[]
    for j,item in enumerate(paragraphs):
        if keys.search(item["text"]):
            lo=max(0,j-4); hi=min(len(paragraphs),j+5)
            hits.append({
                "paragraph_index":item["index"],
                "window":[x["text"] for x in paragraphs[lo:hi]],
            })

    selected_tables=[t for t in tables if t["matches_s13"]]
    out={
        "schema_version":1,
        "paragraph_count":len(paragraphs),
        "table_count":len(tables),
        "context_hits":hits,
        "selected_tables":selected_tables,
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    lines=[]
    lines.append("=== CONTEXT HITS ===")
    for h in hits:
        lines.append(f"\n--- paragraph {h['paragraph_index']} ---")
        lines.extend(h["window"])
    lines.append("\n=== SELECTED TABLES ===")
    for t in selected_tables:
        lines.append(f"\n--- TABLE {t['table_index']} ({t['n_rows']} rows) ---")
        for r in t["rows"]:
            lines.append("\t".join(r))
    a.out_text.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({
        "paragraph_count":len(paragraphs),
        "table_count":len(tables),
        "context_hits":len(hits),
        "selected_tables":[
            {"table_index":t["table_index"],"n_rows":t["n_rows"],"n_cols_max":t["n_cols_max"]}
            for t in selected_tables
        ]
    },indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
