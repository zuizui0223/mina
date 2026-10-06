from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SI = ROOT / "submission" / "SUPPLEMENT_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"
SI_CAPTION = ROOT / "submission" / "SUPPLEMENTARY_FIGURE_CAPTION_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"
MAIN = ROOT / "submission" / "MANUSCRIPT_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"
BUILDER = ROOT / "scripts" / "build_ecology_cross_scale_si.py"


def test_appendix_s1_header_and_item_naming():
    text = SI.read_text(encoding="utf-8")
    assert text.startswith("# Appendix S1")
    assert "**Authors:** [SAME AUTHOR LIST AS MAIN MANUSCRIPT]" in text
    assert "**Manuscript title:** Breeding-component concentration recurs across spatial scales in Antarctic penguins" in text
    assert "**Journal:** Ecology" in text

    for i in range(1, 11):
        assert f"## Section S{i}:" in text

    for i in range(1, 6):
        assert f"**Table S{i}." in text

    assert "**Equation S1." in text


def test_figure_s1_is_defined_once_for_appendix():
    source = SI.read_text(encoding="utf-8")
    caption = SI_CAPTION.read_text(encoding="utf-8")
    assert "Figure S1" not in source
    assert caption.count("## Figure S1.") == 1


def test_main_document_references_supporting_information():
    main = MAIN.read_text(encoding="utf-8")
    assert "Appendix S1" in main
    assert "Table S4" in main
    assert "Table S5" in main
    assert "Appendix S1: Section S9 and Figure S1" in main


def test_appendix_builder_exists():
    assert BUILDER.exists()
