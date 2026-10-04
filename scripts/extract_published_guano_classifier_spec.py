#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def extract_docx_text(path: Path) -> str:
    if not zipfile.is_zipfile(path):
        head = path.read_bytes()[:200]
        raise ValueError(f"Supplement is not a DOCX zip archive; first bytes={head!r}")
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n == "word/document.xml" or n.startswith("word/header")]
        if "word/document.xml" not in names:
            raise ValueError("word/document.xml missing")
        root = ET.fromstring(z.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    lines = []
    for p in root.findall(".//w:p", ns):
        parts = [t.text or "" for t in p.findall(".//w:t", ns)]
        text = "".join(parts).strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def summarize(text: str) -> dict:
    low = text.lower()
    number_tokens = re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)
    return {
        "characters": len(text),
        "lines": len(text.splitlines()),
        "numeric_tokens": len(number_tokens),
        "mentions_transition_matrix": "transition matrix" in low,
        "mentions_decision": "decision" in low,
        "mentions_band_1": "band 1" in low or "band-1" in low,
        "mentions_band_7": "band 7" in low or "band-7" in low,
        "mentions_ellipsoid": "ellipsoid" in low,
        "mentions_peninsula": "peninsula" in low
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--docx", required=True, type=Path)
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-text", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    a=p.parse_args()

    contract=json.loads(a.contract.read_text(encoding="utf-8"))
    text=extract_docx_text(a.docx)
    summary=summarize(text)
    summary.update({
        "schema_version": 1,
        "result_id": "mina-paper2-published-guano-classifier-spec-recovery-result-v1",
        "contract_id": contract["contract_id"],
        "source_supplement_doi": contract["source"]["supplement_doi"],
        "recovery_passed": bool(summary["numeric_tokens"] >= 20 and summary["lines"] >= 5),
        "boundary": "Text extraction only; no coefficient is changed or fitted."
    })
    a.out_text.parent.mkdir(parents=True, exist_ok=True)
    a.out_text.write_text(text+"\n", encoding="utf-8")
    a.out_json.write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("--- EXTRACTED TEXT ---")
    print(text)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
