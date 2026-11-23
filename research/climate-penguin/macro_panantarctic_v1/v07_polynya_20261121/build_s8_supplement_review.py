#!/usr/bin/env python3
"""Build the unchanged v0.7.5 main text and a separate v0.7.6 S8 review supplement.
Adds ONLY the source-validated current-MPA map as a supplementary figure.
"""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from docx import Document
from docx.shared import Mm,Pt
from build_review_documents import build, ROOT

BASE_VERSION="v0.7.5; main unchanged"
PUBLISHED_AUDIT="https://github.com/zuizui0223/mina/actions/runs/45082480478"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--figure",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    image=Path(args.figure)
    if not image.exists() or image.stat().st_size<100000:
        raise ValueError("Supplement S1 original published map missing")
    output=Path(args.out);output.mkdir(parents=True,exist_ok=True)
    receipt=build(output)
    base=output/"Polynya_foodweb_supplement_v07.docx"
    mainfile=output/"Polynya_foodweb_manuscript_v07.docx"
    doc=Document(base)
    # The original lightweight Markdown parser does not interpret backtick inline code.
    # Clean only the newly added S8 review region in the Word deliverable.
    after_s8=False
    for paragraph in doc.paragraphs:
        if paragraph.text.startswith('S8. Ecological scale'):
            after_s8=True
        if after_s8:
            for run in paragraph.runs:
                if '`' in run.text:
                    run.text=run.text.replace('`','')
    matches=[p for p in doc.paragraphs if p.text.startswith("Figure S1.")]
    if len(matches)!=1:raise RuntimeError("Figure S1 citation not exactly once")
    anchor=matches[0]
    pict=doc.add_paragraph()
    pic=pict.add_run().add_picture(str(image),width=Mm(149))
    pic._inline.docPr.set("descr", "Antarctic polar map of within-colony polynya-fraction standard deviations for 79 Adélie colonies; six other colonies have grey crosses. Dark outlines are six present-day CCAMLR MPA zones. These are present-day overlaps, not historical protection effects.")
    pict.paragraph_format.page_break_before=False
    figure_headers=[p for p in doc.paragraphs if p.text.strip()=="Supplementary figure"]
    if len(figure_headers)!=1:raise RuntimeError("Missing unique figure heading")
    figure_headers[0].paragraph_format.page_break_before=True
    figure_headers[0].paragraph_format.keep_with_next=True
    pict.paragraph_format.keep_with_next=True
    pict.paragraph_format.line_spacing=1
    pict.paragraph_format.space_after=Pt(4)
    anchor._p.addprevious(pict._p)
    anchor.paragraph_format.keep_with_next=False
    anchor.paragraph_format.line_spacing=1.15
    for p in doc.paragraphs:
        if "author-review addition, 23 November 2026" in p.text:
            p.paragraph_format.page_break_before=True
    doc.core_properties.title="Polynya foodweb supplement v0.7.6 review — S8 conservation and isotope scale"
    doc.core_properties.subject="Exploratory scale translation and modern MPA geography; no new ecological model"
    doc.core_properties.modified=datetime(2026,11,23,tzinfo=timezone.utc)
    revised=output/"Polynya_foodweb_supplement_review_v076_20261123.docx"
    doc.save(revised)
    check=Document(revised)
    full="\n".join(p.text for p in check.paragraphs)
    required=["S8. Ecological scale","S8.1.","S8.2.","S8.3.","Figure S1","Table S6.","583","439","85","144","102/146","15 of 85","Hong et al."]
    missing=[s for s in required if s not in full]
    if missing:raise RuntimeError("S8 review manuscript text gate failed "+str(missing))
    if len(check.inline_shapes)!=1:raise RuntimeError("Expected exactly one supplemental map image")
    if len(Document(mainfile).inline_shapes)!=5:raise RuntimeError("Main five figures changed")
    audit={
        "status":"S8_REVIEW_DOCX_BUILT_NOT_SUBMITTED",
        "date":"2026-11-23",
        "supplement_modified_only":True,
        "main_manuscript_preserved":True,
        "s8_figure_png_sha256":hashlib.sha256(image.read_bytes()).hexdigest(),
        "supplement_docx_sha256":hashlib.sha256(revised.read_bytes()).hexdigest(),
        "main_manuscript_sha256":hashlib.sha256(mainfile.read_bytes()).hexdigest(),
        "supplement_figures":len(check.inline_shapes),
        "main_figures":5,
        "supplement_bytes":revised.stat().st_size,
        "source_audit_action":PUBLISHED_AUDIT,
        "review_gates":"Requires author scientific and final figure/layout review before submission",
    }
    (output/"SUPPLEMENT_S8_DOCX_BUILD_RECEIPT.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(audit,indent=2))

if __name__=="__main__":main()
