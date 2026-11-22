#!/usr/bin/env python3
"""Source-and-publisher-aware editorial gate for working v0.6.

This verifies descriptive manuscript consistency, not genuine scientific
replication, publication, data licensing, or author consent. Retains
NO_GO_SUBMISSION until external/manual metadata are supplied.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
MS=HERE/"MANUSCRIPT_V06_MARINE_AXES_NESTING_ISOTOPE_CMIP6_WORKING.md"
REVIEW=HERE/"SUBMISSION_AND_NOVELTY_GATE_20261121_JA.md"
FIG=HERE/"render_four_original_source_paper_figures.py"
REPORT="SUBMISSION_NOT_READY_EXTERNAL_DEPENDENCIES"


def extract(txt, first, last):
    if txt.count(first)!=1 or txt.count(last)<1:
        raise ValueError(f"Missing/ambiguous section delimiters: {first}")
    start=txt.index(first)+len(first)
    end=txt.index(last,start)
    return txt[start:end].strip()


def audit():
    text=MS.read_text(encoding="utf-8")
    assert REVIEW.is_file()
    plot=FIG.read_text(encoding="utf-8")
    title=text.splitlines()[0]
    assert title=="# Nest-weighted geography changes estimated marine climate exposure of Antarctic penguins"
    abstract=extract(text,"## Abstract\n\n","**Keywords:**")
    abstract_words=len(re.findall(r"\S+",abstract))
    assert 250<=abstract_words<=350,abstract_words
    assert not re.search(r"\b(?:CMIP\d+|PCA|SIC|SSP\d+(?:[-–]\d+(?:\.\d+)?)?|CI|DOI|PLSR|GLORYS|WAIC)\b",abstract), "Publisher requests no abbreviations in abstract"
    assert "http" not in abstract and not re.search(r"\b(?:et al|doi)\b",abstract,re.I)
    kwline=text.split("**Keywords:**",1)[1].splitlines()[0].strip().rstrip(".")
    kw=[p.strip() for p in kwline.split(";") if p.strip()]
    assert 1<=len(kw)<=6 and len(set(kw))==len(kw)
    # Explicit within-271 comparison and mismatch guard.
    for required in ("271 sites","28.63","13.28","15.36","15.66","−0.30","23-site",
                     "17 marine-complete","inconclusive","do not identify"):
        assert required in abstract, "Abstract source claim missing: "+required
    expected_figures={
       1:"Antarctic colony source footprint",
       2:"Nest-weighted spatial change",
       3:"Salinity-associated predicted Adélie isotope",
       4:"Same-site nest-weighted climate exposure",
    }
    for num,head in expected_figures.items():
        assert text.count(f"**Figure {num}. ")==1, "Main figure numbering drift"
        assert f"**Figure {num}. {head}" in text, "Wrong figure caption="+str(num)
    assert text.count("**Figure 5.")==0
    assert "271_source_counted_colonies_equal_site" in plot
    assert "271_source_counted_colonies_nest_proxy_weight" in plot
    assert "same_271_counted_sites_late_sic_weighting_gap_pp" in plot
    assert "Fig4_Same271_weighting_and_model_coupling" in plot
    doi={
        "Youngflesh_2026":"10.1016/j.cub.2026.06.028",
        "Ramirez_2026":"10.1111/ddi.70233",
        "DuVivier_2026":"10.1038/s41467-026-69011-0",
        "Ratcliffe_2026":"10.1016/j.cub.2026.09.010",
    }
    for label,ref in doi.items():
        assert ref in text, "Missing high-overlap literature: "+label
    for required in ("mean projected sea-ice loss","−28.63 percentage points",
                     "−13.276 percentage points","+15.36", "+15.66",
                     "−0.30", "spatial denominator","source-counted"):
        # Reports descriptive cross-check rather than new data.
        # Exact manuscript phrasing intentionally consistent with figure receipt.
        if required not in text:
            raise AssertionError("Manuscript core physical claim absent: "+required)
    # One manuscript, four figures and no false biological forecasts.
    assert "not a map of future colony persistence" in text
    assert "never predicted" not in text or "no new forecast" in text
    assert "**Editorial freeze:** one candidate paper" in text
    manual=[
        {"id":"author_approval","status":"OPEN","reason":"No final authors, affiliation, correspondence, funding and COI approvals"},
        {"id":"durable_source_archive","status":"OPEN","reason":"Actions ZIP artifacts expire; no DOI for reproducible derived archive and licence permissions"},
        {"id":"publisher_word_layout","status":"OPEN","reason":"No title/author page and required Word submission layout"},
        {"id":"figure_print_and_alt","status":"OPEN","reason":"No final 84/170 mm print-size check, geographic map scale bar or figure alt text review"},
        {"id":"complete_bibliography","status":"OPEN","reason":"References are source-checked core list, not final publisher-formatted full bibliography"},
        {"id":"coauthor_scientific_acceptance","status":"OPEN","reason":"Novelty judged narrower than causal/macroecological mechanism; authors have not approved focus"},
    ]
    verdict={
        "gate":REPORT,
        "source_repo":"zuizui0223/mina",
        "manuscript":MS.name,
        "title":title[2:],
        "abstract_word_count":abstract_words,
        "keyword_count":len(kw),
        "keywords":kw,
        "main_figure_count":len(expected_figures),
        "original_same_271_source_claim":{
          "site_equal_late_sic_pp":-28.63413394176649,
          "source_nest_weight_late_sic_pp":-13.276240917274327,
          "difference_pp":15.357893024492162,
          "between_region_pp":15.656,
          "within_region_pp":-0.298,
          "not_projected_breeding":True
        },
        "overlap_literature_present":doi,
        "automated_text_checks":"PASS",
        "manual_submission_blockers":manual,
        "source_data_recomputed_by_this_script":False,
        "no_permission_to_submit":True,
        "publisher_guidelines":{
          "source":"https://www.cambridge.org/core/journals/antarctic-science/information/author-instructions/preparing-your-materials",
          "abstract_approx_words":300,
          "maximum_keywords":6,
        }
    }
    assert len(manual)>=5 and all(x["status"]=="OPEN" for x in manual)
    return verdict


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result=audit()
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["gate"],
        "abstract_words":result["abstract_word_count"],
        "keywords":result["keyword_count"],
        "main_figures":result["main_figure_count"],
        "auto_checks":result["automated_text_checks"],
        "unresolved_manual_gates":len(result["manual_submission_blockers"]),
    },ensure_ascii=False,indent=2))
