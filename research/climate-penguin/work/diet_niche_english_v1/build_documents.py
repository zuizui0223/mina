#!/usr/bin/env python3
"""Build the two English manuscripts without changing any scientific input.

Run with CODEX_PRIMARY_RUNTIME_PYTHON. Pandoc supplies a Markdown AST and native
Word equations; python-docx authors all document text, tables, links and images.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import quote
from zipfile import ZipFile

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from lxml import etree
from PIL import Image

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "research/climate-penguin/outputs/diet_niche_english_v1"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
LINK_BASE = "https://github.com/zuizui0223/mina/blob/codex/climate-penguin-progress/"
WIDTH = 6.9


def plain(inlines: list) -> str:
    result = []
    for node in inlines:
        t, c = node["t"], node.get("c")
        if t == "Str": result.append(c)
        elif t in {"Space", "SoftBreak", "LineBreak"}: result.append(" ")
        elif t in {"Code", "Math"}: result.append(c[1])
        elif t in {"Link", "Image"}: result.append(plain(c[1]))
        elif t in {"Span", "Cite", "Quoted"}: result.append(plain(c[1]))
        elif t in {"Strong", "Emph", "Underline", "Strikeout", "Superscript", "Subscript", "SmallCaps"}: result.append(plain(c))
    return "".join(result)


def ast(path: Path) -> dict:
    return json.loads(subprocess.check_output([
        "pandoc", "--from=markdown+tex_math_dollars+pipe_tables+raw_html-smart-implicit_figures",
        "--to=json", str(path)], text=True))


def collect_math(value) -> list[str]:
    formulas = []
    if isinstance(value, dict):
        if value.get("t") == "Math": formulas.append(value["c"][1])
        for item in value.values(): formulas.extend(collect_math(item))
    elif isinstance(value, list):
        for item in value: formulas.extend(collect_math(item))
    return list(dict.fromkeys(formulas))


def native_math(formulas: list[str]) -> dict:
    if not formulas: return {}
    with tempfile.TemporaryDirectory(prefix="signy_word_math_") as folder:
        target = Path(folder) / "equations.docx"
        # Pandoc retains boundary newlines in display-math AST values. Keeping
        # them here would introduce blank lines inside $$ and destroy parsing.
        source = "\n\n".join("$$\n" + f.strip() + "\n$$" for f in formulas)
        subprocess.run(["pandoc", "-f", "markdown+tex_math_dollars", "-t", "docx", "-o", str(target)], input=source, text=True, check=True)
        with ZipFile(target) as z:
            tree = etree.fromstring(z.read("word/document.xml"))
        equations = tree.xpath("//m:oMath", namespaces=NS)
        if len(equations) != len(formulas):
            raise ValueError(f"Native math conversion produced {len(equations)} equations for {len(formulas)} formulas")
        return dict(zip(formulas, equations))


def black_font(style, size, bold=False):
    style.font.name = "Times New Roman"
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.font.underline = False
    pr = style.element.get_or_add_rPr()
    fonts = pr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts"); pr.append(fonts)
    for key in ["ascii", "hAnsi", "cs"]: fonts.set(qn("w:" + key), "Times New Roman")
    for key in ["asciiTheme", "hAnsiTheme", "csTheme", "eastAsiaTheme"]: fonts.attrib.pop(qn("w:" + key), None)


def initialize(title: str) -> Document:
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.left_margin = sec.right_margin = Inches(0.8)
    sec.top_margin = sec.bottom_margin = Inches(0.75)
    sec.footer_distance = Inches(0.3)
    for name, size, bold in [("Normal", 11.5, False), ("Title", 19, True),
                             ("Subtitle", 12.5, False), ("Caption", 10.5, False),
                             ("Heading 1", 14, True), ("Heading 2", 12, True),
                             ("Heading 3", 11.5, True), ("Heading 4", 11.5, True)]:
        style = doc.styles[name]
        black_font(style, size, bold)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.line_spacing = 1.12
        style.paragraph_format.widow_control = True
        if name.startswith("Heading"):
            style.paragraph_format.space_before = Pt(12)
            style.paragraph_format.keep_with_next = True
        ppr = style.element.find(qn("w:pPr"))
        if ppr is not None:
            for border in list(ppr.findall(qn("w:pBdr"))): ppr.remove(border)
    doc.styles["Title"].paragraph_format.space_after = Pt(10)
    reference = doc.styles.add_style("Dataset Reference", 1)
    reference.base_style = doc.styles["Normal"]
    black_font(reference, 10.5)
    reference.paragraph_format.space_after = Pt(3)
    reference.paragraph_format.keep_together = True
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run(); run.font.size = Pt(9)
    field = OxmlElement("w:fldSimple"); field.set(qn("w:instr"), "PAGE")
    run._r.addnext(field)
    props = doc.core_properties
    props.title = title
    props.subject = "Sea ice and dietary separation among sympatric penguins at Signy Island"
    props.author = ""
    props.last_modified_by = ""
    props.keywords = "Pygoscelis; Signy Island; diet; sea ice; conditional scenarios"
    props.created = props.modified = datetime(2026, 11, 6, tzinfo=timezone.utc)
    return doc


class Builder:
    def __init__(self, path: Path, parsed: dict, maths: dict):
        self.path, self.parsed, self.maths = path, parsed, maths
        title = next(plain(b["c"][2]) for b in parsed["blocks"] if b["t"] == "Header")
        self.doc = initialize(title)
        self.figures, self.tables, self.equation_count, self.links = [], [], 0, []
        self.pending_page_break = False

    def paragraph(self, style=None):
        p = self.doc.add_paragraph(style=style)
        if self.pending_page_break:
            # Attach the break to its content, avoiding an empty break paragraph
            # that can overflow to a blank page at a natural page boundary.
            p.paragraph_format.page_break_before = True
            self.pending_page_break = False
        return p

    def link_url(self, raw):
        if re.match(r"^[a-z][a-z0-9+.-]*:", raw, re.I) or raw.startswith("#"): return raw
        target, _, fragment = raw.partition("#")
        resolved = (self.path.parent / target).resolve()
        if not resolved.exists(): raise FileNotFoundError(f"Broken link in {self.path.name}: {raw}")
        return LINK_BASE + quote(str(resolved.relative_to(REPO)), safe="/") + ("#" + quote(fragment) if fragment else "")

    def inlines(self, paragraph, nodes, bold=False, italic=False, container=None):
        container = container if container is not None else paragraph._p
        for node in nodes:
            t, c = node["t"], node.get("c")
            if t in {"Subscript", "Superscript"}:
                before = len(container)
                self.inlines(paragraph, c, bold, italic, container)
                for child in list(container)[before:]:
                    if child.tag != qn("w:r"): continue
                    pr = child.find(qn("w:rPr"))
                    if pr is None: pr=OxmlElement("w:rPr"); child.insert(0,pr)
                    valign=OxmlElement("w:vertAlign")
                    valign.set(qn("w:val"),"subscript" if t == "Subscript" else "superscript")
                    pr.append(valign)
            elif t in {"Strong", "Emph", "Span", "Cite", "Quoted", "SmallCaps", "Underline", "Strikeout"}:
                children = c[1] if t in {"Span", "Cite", "Quoted"} else c
                self.inlines(paragraph, children, bold or t == "Strong", italic or t == "Emph", container)
            elif t == "Math":
                container.append(deepcopy(self.maths[c[1]])); self.equation_count += 1
            elif t == "Link":
                url = self.link_url(c[2][0]); self.links.append(url)
                hyperlink = OxmlElement("w:hyperlink")
                hyperlink.set(qn("r:id"), paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True))
                container.append(hyperlink)
                self.inlines(paragraph, c[1], bold, italic, hyperlink)
            elif t == "Image": self.add_image(c, paragraph)
            elif t == "Note":
                text = " (" + " ".join(plain(b.get("c", [])) for b in c if b["t"] in {"Para", "Plain"}) + ")"
                run = paragraph.add_run(text); run.bold, run.italic = True if bold else None, True if italic else None
                if container is not paragraph._p: container.append(run._r)
            else:
                if t == "Str": text = c
                elif t in {"Space", "SoftBreak"}: text = " "
                elif t == "LineBreak": text = "\n"
                elif t == "Code": text = c[1]
                elif t == "RawInline": text = ""
                else: raise ValueError(f"Unsupported inline {t}")
                run = paragraph.add_run(text); run.bold, run.italic = True if bold else None, True if italic else None
                if t == "Code": run.font.name = "Courier New"; run.font.size = Pt(10)
                if container is not paragraph._p: container.append(run._r)

    def add_image(self, c, paragraph):
        path = (self.path.parent / c[2][0]).resolve()
        if not path.is_file(): raise FileNotFoundError(path)
        with Image.open(path) as im: width, height = im.size
        display_width = min(WIDTH, 6.1 * width / height)
        picture = paragraph.add_run().add_picture(str(path), width=Inches(display_width))
        picture._inline.docPr.set("descr", plain(c[1]))
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.keep_with_next = True
        paragraph.paragraph_format.space_after = Pt(6)
        self.figures.append({"path":str(path.relative_to(REPO)), "sha256":hashlib.sha256(path.read_bytes()).hexdigest(), "width_inches":display_width})

    def table(self, c):
        _, caption, specs, head, bodies, foot = c
        rows = head[1] + [row for body in bodies for row in body[2] + body[3]] + foot[1]
        if not rows: return
        cells = [row[1] for row in rows]
        ncols = len(specs)
        if any(len(row) != ncols for row in cells): raise ValueError("Spanning table cells require explicit support")
        if ncols > 8: raise ValueError(f"Split the {ncols}-column table for readable portrait layout")
        texts = [[" ".join(plain(b["c"]) for b in cell[4] if b["t"] in {"Para", "Plain"}) for cell in row] for row in cells]
        self.tables.append(texts)
        table = self.doc.add_table(rows=0, cols=ncols)
        table.autofit = False
        sizes = [max(5, min(30, max(len(row[j]) for row in texts))) for j in range(ncols)]
        weights = [x ** 0.6 for x in sizes]
        widths = [WIDTH * x / sum(weights) for x in weights]
        for col, w in zip(table.columns, widths): col.width = Inches(w)
        pr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
            e=OxmlElement("w:"+edge); e.set(qn("w:val"),"single"); e.set(qn("w:sz"),"4"); e.set(qn("w:color"),"D9D9D9"); borders.append(e)
        pr.append(borders)
        for i, row in enumerate(cells):
            tr = table.add_row()
            trpr = tr._tr.get_or_add_trPr()
            trpr.append(OxmlElement("w:cantSplit"))
            if i < len(head[1]): trpr.append(OxmlElement("w:tblHeader"))
            for j, source in enumerate(row):
                cell = tr.cells[j]; cell.width = Inches(widths[j]); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                tcpr = cell._tc.get_or_add_tcPr()
                margins = OxmlElement("w:tcMar")
                for edge in ["top", "bottom", "left", "right"]:
                    e=OxmlElement("w:"+edge); e.set(qn("w:w"),"80"); e.set(qn("w:type"),"dxa"); margins.append(e)
                tcpr.append(margins)
                if i < len(head[1]):
                    shading=OxmlElement("w:shd"); shading.set(qn("w:fill"),"E8EEF5"); tcpr.append(shading)
                for k, block in enumerate(source[4]):
                    p = cell.paragraphs[0] if k == 0 else cell.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_after = Pt(1)
                    p.paragraph_format.line_spacing = 1.0
                    # A short table is one reading unit; do not orphan its total
                    # or final data row on the next page. Longer tables retain
                    # repeated headers and may break between complete rows.
                    if len(rows) <= 6:
                        p.paragraph_format.keep_with_next = i < len(rows) - 1
                    self.inlines(p, block["c"], bold=i < len(head[1]))
                    for run in p.runs: run.font.size = Pt(10 if ncols <= 6 else 9.5)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(1)

    def blocks(self, blocks):
        for b in blocks:
            t, c = b["t"], b.get("c")
            if t == "Header":
                level, _, inline = c
                p = self.paragraph(style="Title" if level == 1 else "Heading " + str(min(level-1, 4)))
                self.inlines(p, inline)
            elif t in {"Para", "Plain"}:
                is_caption = re.match(r"^(?:Figure|Table)\s+(?:S?\d)", plain(c))
                is_dataset_reference = re.match(r"^C[1-9]\. ", plain(c))
                style = "Caption" if is_caption else "Dataset Reference" if is_dataset_reference else "Normal"
                p = self.paragraph(style=style)
                if is_caption and plain(c).startswith("Table"): p.paragraph_format.keep_with_next = True
                self.inlines(p, c)
                if len(c) == 1 and c[0]["t"] == "Math" and c[0]["c"][0]["t"] == "DisplayMath":
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif t == "Table": self.table(c)
            elif t == "RawBlock":
                if "PAGEBREAK" in c[1]: self.pending_page_break = True
            elif t in {"BulletList", "OrderedList"}:
                items = c if t == "BulletList" else c[1]
                for index, item in enumerate(items):
                    for j, block in enumerate(item):
                        if block["t"] not in {"Para", "Plain"}: self.blocks([block]); continue
                        p=self.doc.add_paragraph(style="List Bullet" if t == "BulletList" and j == 0 else "Normal")
                        if t == "OrderedList" and j == 0: p.add_run(str(c[0][0]+index)+". ")
                        self.inlines(p, block["c"])
            elif t == "BlockQuote": self.blocks(c)
            elif t == "CodeBlock":
                p=self.doc.add_paragraph(); p.add_run(c[1]).font.name="Courier New"
            elif t == "HorizontalRule": self.doc.add_paragraph()
            elif t == "Div": self.blocks(c[1])
            elif t == "Null": pass
            else: raise ValueError(f"Unsupported block {t}")

    def save(self, destination: Path):
        self.blocks(self.parsed["blocks"])
        self.doc.save(destination)
        return {"source":self.path.name, "output":destination.name,
                "source_sha256":hashlib.sha256(self.path.read_bytes()).hexdigest(),
                "docx_sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
                "figures":self.figures, "tables":len(self.tables),
                "native_equations":self.equation_count, "hyperlinks":len(self.links)}


def run(folder: Path):
    sources = [(folder/"MANUSCRIPT_EN.md", folder/"Signy_diet_manuscript.docx"),
               (folder/"SUPPLEMENT_EN.md", folder/"Signy_diet_supplement.docx")]
    parsed = [ast(source) for source, _ in sources]
    formulas = list(dict.fromkeys(f for data in parsed for f in collect_math(data)))
    maths = native_math(formulas)
    results = [Builder(source, data, maths).save(target) for (source,target),data in zip(sources,parsed)]
    (folder/"BUILD_MANIFEST.json").write_text(json.dumps({"builder":"python-docx with Pandoc native math", "documents":results}, ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(results,ensure_ascii=False))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    run(parser.parse_args().out)
