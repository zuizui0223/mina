from pathlib import Path
import json
import re

MANUSCRIPT = Path("docs/MANUSCRIPT_INTEGRATED_JBI_V0_4.md")
CAPTIONS = Path("docs/INTEGRATED_FIGURE_CAPTIONS_V0_1.md")
SUPPLEMENT = Path("docs/SUPPLEMENT_INTEGRATED_V0_2.md")


def _text():
    return MANUSCRIPT.read_text(encoding="utf-8")


def test_jbi_title_and_running_title_limits():
    text=_text()
    title=text.splitlines()[0].removeprefix("# ").strip()
    assert len(title) <= 115
    match=re.search(r"\*\*Running title:\*\*\s*(.+)",text)
    assert match
    assert len(match.group(1).strip()) < 40


def test_jbi_main_text_stays_within_research_article_target():
    words=re.findall(r"\S+",_text())
    assert len(words) <= 6000


def test_jbi_structured_abstract_and_word_limit():
    text=_text()
    abstract=text.split("## Abstract",1)[1].split("**Keywords:**",1)[0]
    for heading in ("Aim","Location","Taxon","Methods","Results","Main conclusions"):
        assert f"**{heading}:**" in abstract
    assert len(abstract.split()) <= 300
    assert "Signy" in abstract
    assert "0.279" in abstract


def test_jbi_keywords_count_and_order():
    text=_text()
    line=next(x for x in text.splitlines() if x.startswith("**Keywords:**"))
    keywords=[x.strip() for x in line.split(":",1)[1].split(";") if x.strip()]
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


def test_all_jbi_citation_keys_exist_in_frozen_bibliography():
    text=_text()
    cited=set(re.findall(r"@([A-Za-z0-9_:-]+)",text))
    bib=Path("docs/REFERENCES_V6.bib").read_text(encoding="utf-8")
    keys=set(re.findall(r"@\w+\{([^,]+),",bib))
    assert cited
    assert cited <= keys, sorted(cited-keys)


def test_scientific_boundaries_are_retained():
    text=_text()
    low=text.lower()
    for required in ("0.0947","0.0810","0.498","0.539","0.0409","0.00327","0.0213","0.279","0.0603","0.0207"):
        assert required in text
    assert "marginally significant" not in low
    assert "near significant" not in low
    assert "approached significance" not in low
    assert "did not replicate" in low
    assert "cannot replace the null primary replication" in low
    assert "simple win-stay/lose-switch mechanism" in low


def test_integrated_supplement_preserves_dynamic_transfer_boundary():
    text=SUPPLEMENT.read_text(encoding="utf-8")
    low=text.lower()
    for required in ("0.0947","0.0810","0.4977","0.5386","0.0409","0.00327","0.0213","0.279","0.0603","0.0207"):
        assert required in text
    assert "do not call signy a positive independent replication" in low
    assert "cannot replace the null frozen signy primary result" in low


def test_submission_manifest_points_to_v03_science_and_v04_jbi():
    manifest=json.loads(Path("contracts/INTEGRATED_JBI_SUBMISSION_PACKAGE_V0_4.json").read_text())
    assert manifest["anonymous_review_files"]["main_manuscript"] == "docs/MANUSCRIPT_INTEGRATED_JBI_V0_4.md"
    assert manifest["anonymous_review_files"]["supporting_information"] == "docs/SUPPLEMENT_INTEGRATED_V0_2.md"
    assert manifest["scientific_source_of_truth"]["integrated_manuscript"] == "docs/MANUSCRIPT_INTEGRATED_V0_3.md"
    assert manifest["scientific_source_of_truth"]["signy_replication"] == "results/SIGNY_PERFORMANCE_REDISTRIBUTION_REPLICATION_RESULT_V1.json"
