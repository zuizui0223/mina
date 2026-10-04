#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _text_nodes_in_order(element) -> list[str]:
    """Recover ordinary Word text and Office-Math text in document order."""
    out = []
    for node in element.iter():
        if node.tag in {f"{{{W_NS}}}t", f"{{{M_NS}}}t"} and node.text:
            out.append(node.text)
    return out


def extract_docx_text(path: Path) -> str:
    if not zipfile.is_zipfile(path):
        head = path.read_bytes()[:200]
        raise ValueError(f"Supplement is not a DOCX zip archive; first bytes={head!r}")
    with zipfile.ZipFile(path) as z:
        if "word/document.xml" not in z.namelist():
            raise ValueError("word/document.xml missing")
        root = ET.fromstring(z.read("word/document.xml"))
    ns = {"w": W_NS}
    lines = []
    for p in root.findall(".//w:p", ns):
        text = "".join(_text_nodes_in_order(p)).strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def _numeric_tokens(text: str) -> list[str]:
    return re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)


def _between(text: str, start_pattern: str, end_pattern: str) -> str:
    start = re.search(start_pattern, text, flags=re.I | re.S)
    if not start:
        return ""
    tail = text[start.end():]
    end = re.search(end_pattern, tail, flags=re.I | re.S)
    return tail[:end.start()] if end else tail


def summarize(text: str) -> dict:
    low = text.lower()
    matrix_block = _between(
        text,
        r"transition matrix\s*,?\s*T\s*,?\s*was generated.*?T\s*=",
        r"the vector\s+V",
    )
    vector_block = _between(text, r"the vector\s+V", r"and so on")
    matrix_numbers = _numeric_tokens(matrix_block)
    vector_numbers = _numeric_tokens(vector_block)
    all_numbers = _numeric_tokens(text)
    # A 6-band transformation matrix should expose substantially more than
    # the incidental numbers in prose/table coordinates. We do not infer or
    # refit missing coefficients.
    matrix_coefficients_recovered = len(matrix_numbers) >= 30
    return {
        "characters": len(text),
        "lines": len(text.splitlines()),
        "numeric_tokens": len(all_numbers),
        "mentions_transition_matrix": "transition matrix" in low,
        "mentions_toa_reflectance": "top of the atmosphere" in low or "toa reflectance" in low,
        "mentions_band_7": "band 7" in low or "band-7" in low,
        "matrix_block_characters": len(matrix_block),
        "matrix_numeric_tokens": len(matrix_numbers),
        "vector_block_characters": len(vector_block),
        "vector_numeric_tokens": len(vector_numbers),
        "matrix_coefficients_recovered": matrix_coefficients_recovered,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--docx", required=True, type=Path)
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-text", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()

    contract = json.loads(a.contract.read_text(encoding="utf-8"))
    text = extract_docx_text(a.docx)
    summary = summarize(text)
    summary.update({
        "schema_version": 2,
        "result_id": "mina-paper2-published-guano-classifier-spec-recovery-result-v2",
        "contract_id": contract["contract_id"],
        "source_supplement_doi": contract["source"]["supplement_doi"],
        "recovery_passed": bool(
            summary["mentions_transition_matrix"]
            and summary["mentions_toa_reflectance"]
            and summary["matrix_coefficients_recovered"]
        ),
        "boundary": (
            "Document/Office-Math extraction only; no coefficient is changed, "
            "inferred, imputed, or fitted. Failure means the published numeric "
            "classifier specification has not been reproducibly recovered."
        ),
    })
    a.out_text.parent.mkdir(parents=True, exist_ok=True)
    a.out_text.write_text(text + "\n", encoding="utf-8")
    a.out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("--- EXTRACTED TEXT ---")
    print(text)
    if not summary["recovery_passed"]:
        raise SystemExit("Published numeric classifier specification was not fully recovered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
