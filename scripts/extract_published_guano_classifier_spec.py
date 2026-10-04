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
NS = {"w": W_NS, "m": M_NS}


def _text_nodes_in_order(element) -> list[str]:
    out = []
    for node in element.iter():
        if node.tag in {f"{{{W_NS}}}t", f"{{{M_NS}}}t"} and node.text:
            out.append(node.text)
    return out


def load_document_root(path: Path):
    if not zipfile.is_zipfile(path):
        head = path.read_bytes()[:200]
        raise ValueError(f"Supplement is not a DOCX zip archive; first bytes={head!r}")
    with zipfile.ZipFile(path) as z:
        if "word/document.xml" not in z.namelist():
            raise ValueError("word/document.xml missing")
        return ET.fromstring(z.read("word/document.xml"))


def extract_docx_text(root) -> str:
    lines = []
    for p in root.findall(".//w:p", NS):
        text = "".join(_text_nodes_in_order(p)).strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def _numeric_tokens(text: str) -> list[str]:
    return re.findall(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)


def _as_float_cell(text: str):
    cleaned = text.replace("−", "-").replace("–", "-").replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_numeric_math_matrices(root) -> list[dict]:
    """Recover OMML matrices using cell boundaries rather than plain-text spacing."""
    matrices = []
    for mi, matrix in enumerate(root.findall(".//m:m", NS)):
        rows = []
        numeric = True
        for row in matrix.findall("./m:mr", NS):
            cells = []
            for cell in row.findall("./m:e", NS):
                raw = "".join(_text_nodes_in_order(cell)).strip()
                value = _as_float_cell(raw)
                if value is None:
                    numeric = False
                cells.append({"raw": raw, "value": value})
            rows.append(cells)
        if rows:
            matrices.append({
                "matrix_index": mi,
                "n_rows": len(rows),
                "row_lengths": [len(r) for r in rows],
                "numeric": bool(numeric),
                "cells": rows,
            })
    return matrices


def select_transition_matrix(matrices: list[dict]):
    candidates = [
        m for m in matrices
        if m["numeric"]
        and m["n_rows"] == 6
        and m["row_lengths"] == [6, 6, 6, 6, 6, 6]
    ]
    if len(candidates) == 1:
        return candidates[0]
    return None


def summarize(text: str, matrices: list[dict]) -> dict:
    low = text.lower()
    transition = select_transition_matrix(matrices)
    values = None
    if transition is not None:
        values = [[cell["value"] for cell in row] for row in transition["cells"]]
    return {
        "characters": len(text),
        "lines": len(text.splitlines()),
        "numeric_tokens_in_plain_text": len(_numeric_tokens(text)),
        "mentions_transition_matrix": "transition matrix" in low,
        "mentions_toa_reflectance": "top of the atmosphere" in low or "toa reflectance" in low,
        "mentions_band_7": "band 7" in low or "band-7" in low,
        "omml_matrix_count": len(matrices),
        "omml_matrix_shapes": [
            {"rows": m["n_rows"], "row_lengths": m["row_lengths"], "numeric": m["numeric"]}
            for m in matrices
        ],
        "transition_matrix_recovered": transition is not None,
        "transition_matrix_shape": [6, 6] if transition is not None else None,
        "transition_matrix_values": values,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--docx", required=True, type=Path)
    p.add_argument("--contract", required=True, type=Path)
    p.add_argument("--out-text", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    a = p.parse_args()

    contract = json.loads(a.contract.read_text(encoding="utf-8"))
    root = load_document_root(a.docx)
    text = extract_docx_text(root)
    matrices = extract_numeric_math_matrices(root)
    summary = summarize(text, matrices)
    summary.update({
        "schema_version": 3,
        "result_id": "mina-paper2-published-guano-classifier-spec-recovery-result-v3",
        "contract_id": contract["contract_id"],
        "source_supplement_doi": contract["source"]["supplement_doi"],
        "recovery_passed": bool(
            summary["mentions_transition_matrix"]
            and summary["mentions_toa_reflectance"]
            and summary["transition_matrix_recovered"]
        ),
        "boundary": (
            "OMML cell-boundary extraction only; no coefficient is changed, "
            "split by guesswork, inferred, imputed, or fitted. Success requires "
            "exactly one numeric 6x6 Office-Math matrix."
        ),
    })
    a.out_text.parent.mkdir(parents=True, exist_ok=True)
    a.out_text.write_text(text + "\n", encoding="utf-8")
    a.out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["recovery_passed"]:
        raise SystemExit("Published numeric classifier specification was not fully recovered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
