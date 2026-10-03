from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "submission" / "MANUSCRIPT_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"
COVER = ROOT / "submission" / "COVER_LETTER_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"
COPY = ROOT / "submission" / "ECOLOGY_ARTICLE_CROSS_SCALE_COPY_FIELDS_V0_1.md"
CAPTIONS = ROOT / "submission" / "FIGURE_CAPTIONS_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"
SUPP_CAPTION = ROOT / "submission" / "SUPPLEMENTARY_FIGURE_CAPTION_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"
CONTRACT = ROOT / "contracts" / "ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"


def _abstract(text: str) -> str:
    m = re.search(r"^## Abstract\s*$\n(.*?)(?=^\*\*Keywords:|^## )", text, flags=re.M | re.S)
    assert m, "abstract not found"
    return m.group(1).strip()


def test_ecology_article_limits_and_labels():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# ").strip()
    abstract = _abstract(text)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert len(title) == 77
    assert len(title) <= 120
    assert len(abstract.split()) == 256
    assert len(abstract.split()) <= 350
    assert contract["submission_type"] == "Article"
    assert "**Ecology Article candidate" in text
    assert "Ecology Report candidate" not in text


def test_keywords_are_valid_and_alphabetized():
    copy = COPY.read_text(encoding="utf-8")
    m = re.search(r"^## Keywords\s*$\n\n(.+)$", copy, flags=re.M)
    assert m
    keywords = [x.strip() for x in m.group(1).split(";")]
    assert 6 <= len(keywords) <= 12
    assert keywords == sorted(keywords, key=lambda s: s.casefold())


def test_submission_package_has_three_main_figure_captions():
    text = CAPTIONS.read_text(encoding="utf-8")
    assert "## Figure 1." in text
    assert "## Figure 2." in text
    assert "## Figure 3." in text
    assert "## Figure S1." not in text
    supp = SUPP_CAPTION.read_text(encoding="utf-8")
    assert "## Figure S1." in supp


def test_cover_letter_matches_article_and_claim_boundary():
    text = COVER.read_text(encoding="utf-8")
    assert "for publication as an **Article** in *Ecology*" in text
    assert "Report format" not in text
    assert "MAPPPD provides the cross-scale transfer test" in text
    assert "do not claim a universal scaling exponent" in text


def test_open_research_not_duplicated_in_manuscript_body():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    assert "## Data availability" not in text
    assert "## References" in text


def test_ai_disclosure_is_present_in_methods_and_acknowledgments():
    text = MANUSCRIPT.read_text(encoding="utf-8")
    assert "### Reproducibility and computational assistance" in text
    methods = text.split("### Reproducibility and computational assistance", 1)[1].split("### Descriptive internal pathways", 1)[0]
    assert "OpenAI ChatGPT (GPT-5.6 Sol)" in methods
    copy = COPY.read_text(encoding="utf-8")
    assert "OpenAI ChatGPT (GPT-5.6 Sol)" in copy
