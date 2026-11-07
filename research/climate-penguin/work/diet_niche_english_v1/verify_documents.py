#!/usr/bin/env python3
"""Read-only checks of the English Word delivery; emit JSON to stdout.

This verifies source preservation and document structure, not scientific models
or page layout. Run after build_documents.py and inspect rendered pages separately.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "research/climate-penguin/outputs/diet_niche_english_v1"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
EXPECTED = {
    "MANUSCRIPT_EN.md": ("Signy_diet_manuscript.docx", 4),
    "SUPPLEMENT_EN.md": ("Signy_diet_supplement.docx", 2),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def nodes(value):
    if isinstance(value, dict):
        if "t" in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def ast_display_text(value) -> str:
    """Visible AST text, excluding metadata, URLs, image alt text and raw HTML."""
    if isinstance(value, list):
        return "".join(ast_display_text(child) for child in value)
    if not isinstance(value, dict):
        return ""
    kind, content = value.get("t"), value.get("c")
    if kind == "Str":
        return content
    if kind in {"Space", "SoftBreak", "LineBreak"}:
        return " "
    if kind == "Math":
        return "[[MATH]]"
    if kind == "Image":
        return "[[IMAGE]]"
    if kind in {"RawBlock", "RawInline"}:
        return ""
    if kind == "Link":
        return ast_display_text(content[1])
    if kind in {"Code", "CodeBlock"}:
        return content[1] + (" " if kind == "CodeBlock" else "")
    text = "".join(ast_display_text(child) for child in value.values())
    return text + (" " if kind in {"Para", "Plain", "Header"} else "")


def word_display_text(element) -> str:
    if element.tag == "{" + NS["m"] + "}oMath":
        return "[[MATH]]"
    if element.tag == "{" + NS["w"] + "}drawing":
        return "[[IMAGE]]"
    if element.tag == "{" + NS["w"] + "}t":
        return element.text or ""
    if element.tag in {"{" + NS["w"] + "}br", "{" + NS["w"] + "}tab"}:
        return " "
    text = "".join(word_display_text(child) for child in element)
    return text + (" " if element.tag == "{" + NS["w"] + "}p" else "")


def normalize_space(text: str) -> str:
    return " ".join(text.split())


def verify(folder: Path) -> dict:
    checks = []
    details = []

    def check(name, passed, **evidence):
        checks.append({"check": name, "passed": bool(passed), **evidence})

    pinned = json.loads((folder / "SOURCE_MANIFEST.json").read_text())["files"]
    check("source_manifest_contains_30_inputs", len(pinned) == 30, count=len(pinned))
    for entry in pinned:
        path = REPO / entry["path"]
        data = path.read_bytes() if path.is_file() else None
        check("pinned_input", data is not None and sha(data) == entry["sha256"]
              and len(data) == entry["bytes"], path=entry["path"])

    manifest = json.loads((folder / "BUILD_MANIFEST.json").read_text())
    documents = manifest["documents"]
    check("two_expected_documents", len(documents) == 2
          and {d["source"] for d in documents} == set(EXPECTED))
    total_figures = 0
    for entry in documents:
        source, target = folder / entry["source"], folder / entry["output"]
        expected_target, expected_figures = EXPECTED[entry["source"]]
        check("document_output_name", entry["output"] == expected_target,
              source=entry["source"])
        check("markdown_build_hash", sha(source.read_bytes()) == entry["source_sha256"],
              source=entry["source"])
        check("docx_build_hash", sha(target.read_bytes()) == entry["docx_sha256"],
              output=entry["output"])
        parsed = json.loads(subprocess.check_output([
            "pandoc", "--from=markdown+tex_math_dollars+pipe_tables+raw_html-smart-implicit_figures",
            "--to=json", str(source)], text=True))
        all_nodes = list(nodes(parsed))
        maths = [n for n in all_nodes if n["t"] == "Math"]
        tables = [n for n in all_nodes if n["t"] == "Table"]
        images = [n for n in all_nodes if n["t"] == "Image"]
        for n in all_nodes:
            if n["t"] not in {"Link", "Image"}:
                continue
            link = n["c"][2][0]
            if re.match(r"^[a-z][a-z0-9+.-]*:", link, re.I) or link.startswith("#"):
                continue
            check("local_link_exists", (source.parent / link.split("#")[0]).exists(),
                  source=entry["source"], link=link)
        expected_hashes = [sha((source.parent / n["c"][2][0]).read_bytes()) for n in images]
        with ZipFile(target) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
            rels = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
            relation_targets = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
            embedded_hashes = []
            for blip in document.findall(".//a:blip", NS):
                relationship_id = blip.attrib.get("{" + NS["r"] + "}embed")
                if relationship_id is None:
                    continue
                image_path = posixpath.normpath(posixpath.join("word", relation_targets[relationship_id]))
                embedded_hashes.append(sha(archive.read(image_path)))
            math_count = len(document.findall(".//m:oMath", NS))
            table_count = len(document.findall(".//w:tbl", NS))
        ast_text = normalize_space(ast_display_text(parsed))
        docx_text = normalize_space(word_display_text(document))
        text_evidence = {"source": entry["source"], "ast_characters": len(ast_text),
                         "docx_characters": len(docx_text),
                         "ast_text_sha256": sha(ast_text.encode()),
                         "docx_text_sha256": sha(docx_text.encode())}
        if ast_text != docx_text:
            mismatch = next((i for i, (a, b) in enumerate(zip(ast_text, docx_text)) if a != b),
                            min(len(ast_text), len(docx_text)))
            text_evidence.update(first_mismatch_offset=mismatch,
                                 ast_context=ast_text[max(0, mismatch-80):mismatch+120],
                                 docx_context=docx_text[max(0, mismatch-80):mismatch+120])
        check("complete_visible_text_order", ast_text == docx_text, **text_evidence)
        check("native_math_count", len(maths) == math_count == entry["native_equations"],
              source=entry["source"], ast=len(maths), docx=math_count,
              manifest=entry["native_equations"])
        check("table_count", len(tables) == table_count == entry["tables"],
              source=entry["source"], ast=len(tables), docx=table_count,
              manifest=entry["tables"])
        check("embedded_figure_bytes_and_order", expected_hashes == embedded_hashes
              == [f["sha256"] for f in entry["figures"]]
              and len(images) == expected_figures,
              source=entry["source"], figure_count=len(images), hashes=embedded_hashes)
        check("figure_manifest_paths", [str((source.parent / n["c"][2][0]).resolve().relative_to(REPO))
              for n in images] == [f["path"] for f in entry["figures"]], source=entry["source"])
        total_figures += len(images)
        details.append({"source": entry["source"], "output": entry["output"],
                        "source_sha256": sha(source.read_bytes()), "docx_sha256": sha(target.read_bytes()),
                        "native_equations": math_count, "tables": table_count,
                        "figures": len(images)})
    check("six_figures_total", total_figures == 6, count=total_figures)
    manuscript = (folder / "MANUSCRIPT_EN.md").read_text()
    abstract = manuscript.split("## Abstract", 1)[1].split("**Keywords:", 1)[0]
    abstract_words = len(abstract.split())
    check("abstract_at_most_250_words", 0 < abstract_words <= 250, count=abstract_words)
    return {"status": "pass" if all(c["passed"] for c in checks) else "fail",
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "Pinned inputs, build hashes, complete whitespace-normalized visible-text order (math/image placeholders), native equations, tables, image bytes/order, local links and abstract length; excludes visual layout and scientific reanalysis.",
            "checks_passed": sum(c["passed"] for c in checks), "checks_total": len(checks),
            "documents": details, "checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    try:
        report = verify(args.out)
    except Exception as error:
        report = {"status": "error", "error_type": type(error).__name__, "message": str(error)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["status"] == "pass" else 1)
