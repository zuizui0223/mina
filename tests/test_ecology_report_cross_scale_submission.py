from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "submission" / "MANUSCRIPT_ECOLOGY_REPORT_CROSS_SCALE_V1.md"
TITLE = ROOT / "submission" / "TITLE_PAGE_ECOLOGY_REPORT_CROSS_SCALE_TEMPLATE_V1.md"
LETTER = ROOT / "submission" / "COVER_LETTER_ECOLOGY_REPORT_CROSS_SCALE_V1.md"
APPENDIX = ROOT / "submission" / "APPENDIX_S1_ECOLOGY_REPORT_CROSS_SCALE_V1.md"
CAPTIONS = ROOT / "submission" / "FIGURE_CAPTIONS_ECOLOGY_REPORT_CROSS_SCALE_V1.md"
CONTRACT = ROOT / "contracts" / "ECOLOGY_REPORT_CROSS_SCALE_SUBMISSION_V1.json"
BIB = ROOT / "docs" / "REFERENCES_V6.bib"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def words(value: str) -> int:
    clean = re.sub(r"[\\*_`#>|\[\]{}()]", " ", value)
    return len([x for x in clean.split() if x])


def test_ecology_report_format_limits():
    main = text(MAIN)
    contract = json.loads(text(CONTRACT))
    title = main.splitlines()[0].removeprefix("# ").strip()
    abstract = re.search(r"## Abstract\n\n([\s\S]*?)\n\n## Introduction", main)
    assert abstract is not None

    assert len(title) <= contract["guideline_snapshot"]["title_character_limit"]
    assert words(abstract.group(1)) <= contract["guideline_snapshot"]["report_abstract_word_limit"]
    assert contract["submission_metrics"]["main_figures"] == 2

    captions = text(CAPTIONS)
    assert len(re.findall(r"^## Figure \d+$", captions, flags=re.MULTILINE)) == 2


def test_title_page_has_required_ecology_fields():
    title = text(TITLE)
    assert "**Journal:** Ecology" in title
    assert "**Manuscript type:** Report" in title
    assert "## Open Research Statement" in title
    assert "## Key words/phrases" in title
    keyword_block = title.split("## Key words/phrases", 1)[1].strip().splitlines()[0]
    n_keywords = len([x for x in keyword_block.split(";") if x.strip()])
    assert 6 <= n_keywords <= 12


def test_ai_disclosure_is_present_in_methods_and_acknowledgments():
    main = text(MAIN)
    methods = main.split("### Reproducibility and computational assistance", 1)[1].split("## Results", 1)[0]
    ack = main.split("## Acknowledgments", 1)[1].split("## Author Contributions", 1)[0]
    assert "OpenAI ChatGPT (GPT-5.6 Sol)" in methods
    assert "OpenAI ChatGPT (GPT-5.6 Sol)" in ack


def test_main_text_preserves_claim_boundaries():
    main = text(MAIN)
    assert "no family-wide regional rejection criterion" in main
    assert "MAPPPD as a scale-transfer test rather than an additional independent geographic replication" in main
    assert "We therefore do not pool effect sizes or p-values across scales" in main
    assert "These constraints prevent a seabird-wide or Antarctic-wide law" in main
    assert "quarter-power" not in main
    assert "hysteresis" not in main.lower()


def test_appendix_contains_posthoc_context_not_main_rescue():
    appendix = text(APPENDIX)
    assert "Direction rather than a universal exponent" in appendix
    assert "Increasing regional networks" in appendix
    assert "Component-level route boundary" in appendix
    assert "No alternate regional definitions" in appendix


def test_all_main_citation_keys_exist():
    main = text(MAIN)
    bib = text(BIB)
    cited = set(re.findall(r"@([A-Za-z0-9_:-]+)", main))
    available = set(re.findall(r"@[A-Za-z]+\{([^,]+),", bib))
    missing = sorted(cited - available)
    assert not missing, f"missing bibliography keys: {missing}"


def test_cover_letter_matches_active_claim_and_report_metrics():
    letter = text(LETTER)
    contract = json.loads(text(CONTRACT))
    assert "publication as a **Report** in *Ecology*" in letter
    assert "approximately 2,250 words" in letter
    assert "abstract is 168 words" in letter
    assert "two main figures" in letter
    assert "MAPPPD tests whether the **direction** survives a change in spatial level" in letter
    assert contract["status"] == "journal_targeted_packaging_no_new_ecological_endpoints"
