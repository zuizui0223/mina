from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOLUTION = ROOT / "contracts" / "ECOLOGY_CROSS_SCALE_CANONICAL_TARGET_V1.json"
ARTICLE = ROOT / "contracts" / "ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
REPORT = ROOT / "contracts" / "ECOLOGY_REPORT_CROSS_SCALE_SUBMISSION_V1.json"
ARTICLE_CAPTIONS = ROOT / "submission" / "FIGURE_CAPTIONS_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"
COVER = ROOT / "submission" / "COVER_LETTER_ECOLOGY_ARTICLE_CROSS_SCALE_V0_1.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_exactly_one_canonical_initial_ecology_package():
    resolution = load(RESOLUTION)
    article = load(ARTICLE)
    report = load(REPORT)

    assert resolution["status"] == "canonical_target_resolved"
    assert resolution["canonical_initial_submission"]["submission_type"] == "Article"
    assert (
        resolution["canonical_initial_submission"]["contract"]
        == "contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
    )

    assert (
        article["status"]
        == "canonical_package_visual_qa_pass_author_metadata_pending"
    )
    assert (
        report["status"]
        == "alternate_compact_package_not_canonical_for_initial_submission"
    )
    assert (
        report["canonical_initial_submission"]
        == "contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
    )


def test_article_uses_valid_over_30_page_route():
    resolution = load(RESOLUTION)
    article = load(ARTICLE)
    metrics = article["submission_metrics"]
    policy = article["page_policy"]
    cover = COVER.read_text(encoding="utf-8")

    assert resolution["canonical_initial_submission"]["rationale"]
    assert metrics["rendered_main_document_pages"] == 29
    assert metrics["main_figures"] == 3
    assert metrics["rendered_total_pages_including_main_figures"] == 32
    assert metrics["ecology_standard_article_page_limit"] == 30
    assert metrics["pages_over_standard_limit"] == 2
    assert metrics["overlength_cover_letter_justification_added"] is True

    assert policy["rendered_complete_article_pages"] == 32
    assert policy["standard_article_page_limit"] == 30
    assert policy["under_50_page_extended_article_ceiling"] is True
    assert policy["required_two_part_cover_letter_justification_present"] is True
    assert policy["status"] == "ELIGIBLE_FOR_OVER_30_PAGE_ARTICLE_ROUTE"

    assert "**1. Contribution to the broad field of ecology.**" in cover
    assert "**2. Value provided by the additional length.**" in cover


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
