from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOLUTION = ROOT / "contracts" / "ECOLOGY_CROSS_SCALE_CANONICAL_TARGET_V1.json"
ARTICLE = ROOT / "contracts" / "ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
REPORT = ROOT / "contracts" / "ECOLOGY_REPORT_CROSS_SCALE_SUBMISSION_V1.json"
ARTICLE_CAPTIONS = ROOT / "submission" / "FIGURE_CAPTIONS_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_exactly_one_canonical_initial_ecology_package():
    resolution = load(RESOLUTION)
    article = load(ARTICLE)
    report = load(REPORT)

    assert resolution["status"] == "canonical_target_resolved"
    assert resolution["canonical_initial_submission"]["submission_type"] == "Article"
    assert resolution["canonical_initial_submission"]["contract"] == "contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"

    assert article["status"] == "canonical_target_retained_scientific_text_revised_packaging_must_regenerate"
    assert report["status"] == "alternate_compact_package_not_canonical_for_initial_submission"
    assert report["canonical_initial_submission"] == "contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"


def test_article_expected_page_count_is_inside_limit():
    resolution = load(RESOLUTION)
    article = load(ARTICLE)
    assert resolution["canonical_initial_submission"]["rationale"]
    assert article["submission_metrics"]["expected_total_pages_with_three_separate_figure_pages"] == 27
    assert article["journal_fit"]["article_page_limit"] == 30
    assert 27 <= 30


def test_ecology_figure_captions_do_not_contain_equation_definitions():
    text = ARTICLE_CAPTIONS.read_text(encoding="utf-8")
    forbidden = [
        "Σ",
        "\\sum",
        "Δκ =",
        "Delta\\kappa=",
        "\\mathrm{median}",
    ]
    for token in forbidden:
        assert token not in text
