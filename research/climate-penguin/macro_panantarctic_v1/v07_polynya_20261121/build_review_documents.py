#!/usr/bin/env python3
"""Build editable MEPS review documents from checked manuscript and figure sources.

This is deliberately a small parser for this manuscript's Markdown subset:
headings, paragraphs, inline emphasis, lists and pipe tables. Source text remains authoritative.
It does not create author names, approvals or declarations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "MANUSCRIPT_POLYNYA_FOODWEB_WORKING.md"
SUPP = ROOT / "SUPPLEMENT_POLYNYA_FOODWEB.md"


def configure(doc: Document, running: str, double: bool = True) -> None:
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin = sec.bottom_margin = Inches(0.8)
    sec.left_margin = sec.right_margin = Inches(0.9)
    sec.header_distance = sec.footer_distance = Inches(0.35)
    styles = doc.styles
    # The runtime's default template includes blue paragraph borders. Remove
    # them explicitly for a conventional black-and-white journal manuscript.
    for node in list(styles.element.iter(qn("w:pBdr"))):
        node.getparent().remove(node)
    for name in ("Normal", "Title", "Heading 1", "Heading 2", "Heading 3"):
        styles[name].font.name = "Times New Roman"
        styles[name].font.color.rgb = RGBColor(0, 0, 0)
    normal = styles["Normal"]
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 2.0 if double else 1.2
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.widow_control = True
    for name, size in (("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 12)):
        st = styles[name]
        st.font.size, st.font.bold = Pt(size), True
        st.paragraph_format.line_spacing = 1.15
        st.paragraph_format.space_before = Pt(12)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.keep_with_next = True
    styles["Title"].font.size = Pt(20)
    styles["Title"].font.bold = True
    styles["Title"].paragraph_format.line_spacing = 1.15
    h = sec.header.paragraphs[0]
    h.text = running
    h.style = styles["Normal"]
    h.paragraph_format.line_spacing = 1
    h._p.get_or_add_pPr().append(OxmlElement("w:suppressLineNumbers"))
    for r in h.runs:
        r.font.size = Pt(9)
    foot = sec.footer.paragraphs[0]
    foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    foot.paragraph_format.line_spacing = 1
    foot._p.get_or_add_pPr().append(OxmlElement("w:suppressLineNumbers"))
    r = foot.add_run("Page ")
    r.font.size = Pt(9)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    foot._p.append(field)
    doc.core_properties.title = running
    doc.core_properties.author = ""
    doc.core_properties.last_modified_by = ""
    doc.core_properties.subject = "Exploratory manuscript for author review"
    fixed = datetime(2026, 11, 21, tzinfo=timezone.utc)
    doc.core_properties.created = fixed
    doc.core_properties.modified = fixed


def line_numbers(doc: Document) -> None:
    node = OxmlElement("w:lnNumType")
    node.set(qn("w:countBy"), "1")
    node.set(qn("w:start"), "1")
    node.set(qn("w:restart"), "continuous")
    node.set(qn("w:distance"), "100")
    doc.sections[0]._sectPr.append(node)


def page_break(doc: Document) -> None:
    p = doc.add_page_break()
    p._p.get_or_add_pPr().append(OxmlElement("w:suppressLineNumbers"))


def add_inline(p, text: str) -> None:
    # Links remain visibly traceable, without depending on a remote document.
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", text)
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if part.startswith("**") and part.endswith("**"):
            p.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and part.endswith("*"):
            p.add_run(part[1:-1]).italic = True
        else:
            p.add_run(part)


def table(doc: Document, lines: list[str]) -> None:
    data = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines]
    data = [row for row in data if not all(re.fullmatch(r"[:\- ]+", c) for c in row)]
    cols = len(data[0])
    t = doc.add_table(rows=1, cols=cols)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    widths = {2: [2.0, 4.69], 3: [2.02, 1.90, 2.77],
              4: [1.70, 0.69, 2.15, 2.15]}.get(cols, [6.69 / cols] * cols)
    if data[0][0] in {"Order", "No."}:
        widths = [0.5, 2.3, 1.6, 2.29]
        for column, width in zip(t.columns, widths):
            column.width = Inches(width)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = OxmlElement("w:" + edge)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "4")
        node.set(qn("w:color"), "D9D9D9")
        borders.append(node)
    t._tbl.tblPr.append(borders)
    for i, row in enumerate(data):
        cells = t.rows[0].cells if i == 0 else t.add_row().cells
        for j, (cell, text) in enumerate(zip(cells, row)):
            cell.width = Inches(widths[j])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            add_inline(p, text)
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            for r in p.runs:
                r.font.size = Pt(10)
                r.bold = i == 0
            tcPr = cell._tc.get_or_add_tcPr()
            if i == 0:
                shading = OxmlElement("w:shd")
                shading.set(qn("w:fill"), "EDEFF0")
                tcPr.append(shading)
        trPr = t.rows[i]._tr.get_or_add_trPr()
        no_split = OxmlElement("w:cantSplit")
        trPr.append(no_split)
        if i == 0:
            repeat = OxmlElement("w:tblHeader")
            trPr.append(repeat)
    doc.add_paragraph()


def add_markdown(doc: Document, text: str, captions_page: bool = False) -> None:
    lines = text.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            table(doc, rows)
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            title = line[level:].strip()
            p = doc.add_heading(title, level=max(1, min(3, level - 1)))
            if captions_page and title == "Figure captions":
                p.paragraph_format.page_break_before = True
        elif re.match(r"^(?:[-*] |\d+[.)] )", line):
            numbered = bool(re.match(r"^\d+[.)] ", line))
            p = doc.add_paragraph(style="List Number" if numbered else "List Bullet")
            add_inline(p, re.sub(r"^(?:[-*] |\d+[.)] )", "", line))
        else:
            para = [line]
            while (i + 1 < len(lines) and lines[i + 1].strip()
                   and not lines[i + 1].lstrip().startswith(("#", "|"))
                   and not re.match(r"^(?:[-*] |\d+[.)] )", lines[i + 1].lstrip())):
                i += 1
                para.append(lines[i].strip())
            p = doc.add_paragraph()
            add_inline(p, " ".join(para))
        i += 1


def build(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    source = MAIN.read_text(encoding="utf-8")
    title = source.splitlines()[0][2:]
    abstract = source.split("## Abstract\n\n", 1)[1].split("\n\n**Keywords:", 1)[0]
    keywords = source.split("**Keywords:** ", 1)[1].split("\n", 1)[0]
    body = "## 1. Introduction" + source.split("## 1. Introduction", 1)[1]
    body = body.split("## Figure captions", 1)[0].rstrip()
    captions = source.split("## Figure captions\n\n", 1)[1].strip().split("\n\n")
    figures = sorted((ROOT / "figures").glob("Fig[1-5]_*.png"))
    assert len(figures) == len(captions) == 5
    alt = json.loads((ROOT / "figure_alt_text.json").read_text())

    def insert_figure(doc, path):
        shape = doc.add_picture(str(path), width=Mm(169))
        description = alt.get(path.stem, alt.get(path.name, ""))
        if not isinstance(description, str) or not description:
            raise ValueError(f"Missing figure alt text: {path.name}")
        shape._inline.docPr.set("descr", description)
        pic_paragraph = doc.paragraphs[-1]
        pic_paragraph.paragraph_format.line_spacing = 1
        pic_paragraph.paragraph_format.space_after = Pt(4)
        return shape
    d = Document()
    configure(d, "Winter polynyas and penguin isotopes")
    line_numbers(d)
    p = d.add_paragraph(title, style="Title")
    p.paragraph_format.space_before = Pt(36)
    d.add_paragraph("[AUTHORS IN APPROVED ORDER]")
    d.add_paragraph("[AFFILIATIONS AND AUTHOR–AFFILIATION MAPPING]")
    d.add_paragraph("Corresponding author: [NAME AND EMAIL]")
    d.add_paragraph("Version 0.7.5 · 22 November 2026 · Author review")
    d.add_paragraph("Running title: Winter polynyas and penguin isotopes")
    d.add_paragraph(f"Abstract: {len(abstract.split())} words · Five main figures")
    p = d.add_paragraph("Author details, contributions and declarations remain to be supplied by the authors. Publication status is documented separately in the review notes.")
    p.paragraph_format.line_spacing = 1.2
    for r in p.runs:
        r.font.size = Pt(10)
    page_break(d)
    d.add_heading("Abstract", level=1)
    d.add_paragraph(abstract)
    p = d.add_paragraph()
    add_inline(p, "**Keywords:** " + keywords)
    page_break(d)
    add_markdown(d, body)
    for path, caption in zip(figures, captions):
        insert_figure(d, path)
        d.paragraphs[-1].paragraph_format.page_break_before = True
        p = d.add_paragraph()
        add_inline(p, caption)
        p.paragraph_format.line_spacing = 2.0
    main_path = out / "Polynya_foodweb_manuscript_v07.docx"
    d.core_properties.modified = datetime(2026, 11, 22, tzinfo=timezone.utc)
    d.save(main_path)
    if main_path.stat().st_size >= 5_000_000:
        raise ValueError("Combined initial manuscript is not below the journal's 5 MB limit")

    s = Document()
    configure(s, "Polynya manuscript · Supplement", double=False)
    add_markdown(s, SUPP.read_text(encoding="utf-8"))
    supp_path = out / "Polynya_foodweb_supplement_v07.docx"
    s.save(supp_path)

    # An optional compact reader packet is retained alongside the required
    # combined initial manuscript. Its captions need not duplicate review spacing.
    f = Document()
    configure(f, "Polynya manuscript · Main figures", double=False)
    for i, (path, caption) in enumerate(zip(figures, captions)):
        if i:
            f.add_page_break()
        insert_figure(f, path)
        p = f.add_paragraph()
        add_inline(p, caption)
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(0)
        for r in p.runs:
            r.font.size = Pt(10)
    figure_path = out / "Polynya_foodweb_figures_v07.docx"
    f.core_properties.modified = datetime(2026, 11, 22, tzinfo=timezone.utc)
    f.save(figure_path)

    abstract_path = out / "Polynya_foodweb_abstract.txt"
    abstract_path.write_text(title + "\n\n" + abstract + "\n", encoding="utf-8")
    outputs = [main_path, supp_path, figure_path, abstract_path]

    a = Document()
    configure(a, "Alternative text for the five main figures", double=False)
    a.add_heading("Figure alternative text", level=1)
    for i, path in enumerate(figures, 1):
        a.add_heading(f"Figure {i}", level=2)
        p = a.add_paragraph(alt[path.stem])
        p.paragraph_format.keep_together = True
    alt_path = out / "Polynya_foodweb_alt_text_v07.docx"
    a.core_properties.modified = datetime(2026, 11, 22, tzinfo=timezone.utc)
    a.save(alt_path)
    outputs.append(alt_path)

    for src, filename, running in [
        ("COVER_LETTER_MEPS.md", "Polynya_MEPS_cover_letter_v07.docx", "MEPS cover letter"),
        ("AUTHOR_INFORMATION.md", "Polynya_author_information_v07.docx", "Author information and declarations"),
    ]:
        text = (ROOT / "submission_preparation" / src).read_text(encoding="utf-8")
        doc = Document()
        configure(doc, running, double=False)
        doc.styles["Normal"].font.size = Pt(11)
        doc.styles["Normal"].paragraph_format.line_spacing = 1.1
        doc.styles["Normal"].paragraph_format.space_after = Pt(5)
        add_markdown(doc, text)
        output = out / filename
        doc.save(output)
        outputs.append(output)
    receipt = {"abstract_words_whitespace": len(abstract.split()),
               "figure_count": len(figures), "date": "2026-11-22",
               "version": "0.7.5",
               "layout": "US Letter; 0.9-inch side margins; main text and figure captions 12pt double spaced; continuous line numbering; all five figures at end; 169mm figure width",
               "main_docx_contains_five_figures": len(d.inline_shapes) == 5,
               "main_docx_below_5MB": main_path.stat().st_size < 5_000_000,
               "journal_compliance": "verified current MEPS file preparation rules applied; author information, human scientific review, declarations and release decisions remain pending",
               "files": [{"name": p.name, "bytes": p.stat().st_size,
                          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs]}
    (out / "document_build_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "review_documents")
    args = parser.parse_args()
    print(json.dumps(build(args.out), indent=2))
