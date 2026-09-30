from pathlib import Path
import re

MANUSCRIPT = Path("docs/MANUSCRIPT_INTEGRATED_JBI_V0_3.md")
CAPTIONS = Path("docs/INTEGRATED_FIGURE_CAPTIONS_V0_1.md")


def _text():
    return MANUSCRIPT.read_text(encoding="utf-8")


def test_jbi_title_and_running_title_limits():
    text=_text()
    title=text.splitlines()[0].removeprefix("# ").strip()
    assert len(title) <= 115
    match=re.search(r"\*\*Running title:\*\*\s*(.+)",text)
    assert match
    assert len(match.group(1).strip()) < 40


def test_jbi_structured_abstract_and_word_limit():
    text=_text()
    abstract=text.split("## Abstract",1)[1].split("**Keywords:**",1)[0]
    for heading in ("Aim","Location","Taxon","Methods","Results","Main conclusions"):
        assert f"**{heading}:**" in abstract
    assert len(abstract.split()) <= 300


def test_jbi_keywords_count_and_order():
    text=_text()
    line=next(x for x in text.splitlines() if x.startswith("**Keywords:**"))
    keywords=[x.strip() for x in line.split(":",1)[1].split(";") if x.strip()]
    # Current manuscript uses semicolons; fall back to commas if needed.
    if len(keywords)==1:
        keywords=[x.strip() for x in line.split(":",1)[1].split(",") if x.strip()]
    assert 6 <= len(keywords) <= 10
    assert [x.casefold() for x in keywords] == sorted(x.casefold() for x in keywords)


def test_anonymous_main_separates_author_identifying_sections():
    text=_text()
    assert "## Data Accessibility Statement" in text
    assert "## Acknowledgements" not in text
    assert "## Author contributions" not in text
    assert "## Conflict of interest statement" not in text
    assert "## Anonymous-review note" in text


def test_jbi_figure_caption_format():
    text=CAPTIONS.read_text(encoding="utf-8")
    assert "**A.**" not in text
    assert "**B.**" not in text
    assert "**(a)**" in text
    assert "**(b)**" in text
    assert "EPSG:4326" in text
    assert "2-km scale bar" in text
