from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "submission" / "ECOLOGY_ARTICLE_CROSS_SCALE_FINAL_GATE_V0_1.json"
ARTICLE = ROOT / "contracts" / "ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
RESOLUTION = ROOT / "contracts" / "ECOLOGY_CROSS_SCALE_CANONICAL_TARGET_V1.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_scientific_and_canonical_gate_never_reopens():
    gate = load(GATE)
    statuses = gate["statuses"]
    assert statuses["scientific_analysis"] == "PASS_CLOSED"
    assert statuses["claim_boundary"] == "PASS"
    assert statuses["reproducibility_receipts"] == "PASS"
    assert statuses["canonical_package_uniqueness"] == "PASS"
    assert statuses["ai_disclosure"] == "PASS_METHODS_ACKNOWLEDGMENTS_AND_SUBMISSION_COPY"
    assert statuses["data_provider_acknowledgments"] == "PASS"


def test_packaging_gate_state_is_internally_consistent():
    gate = load(GATE)
    statuses = gate["statuses"]

    allowed_doc = {
        "PASS_24_OF_24_PAGES",
        "PENDING_REQA_AFTER_APPENDIX_REFERENCES",
    }
    allowed_fig = {
        "PASS_3_OF_3",
        "PENDING_ECOLOGY_PUBLICATION_SIZE_RERENDER",
    }
    allowed_pages = {
        "PASS_27_OF_30",
        "PENDING_AFTER_PUBLICATION_SIZE_FIGURES",
    }
    allowed_si = {
        "PASS",
        "PENDING_BUILD_AND_VISUAL_QA",
    }

    assert statuses["main_document_visual_qa"] in allowed_doc
    assert statuses["main_figure_visual_qa"] in allowed_fig
    assert statuses["generated_manuscript_page_limit"] in allowed_pages
    assert statuses.get("supporting_information_pdf", "PENDING_BUILD_AND_VISUAL_QA") in allowed_si

    all_packaging_pass = (
        statuses["main_document_visual_qa"] == "PASS_24_OF_24_PAGES"
        and statuses["main_figure_visual_qa"] == "PASS_3_OF_3"
        and statuses["generated_manuscript_page_limit"] == "PASS_27_OF_30"
        and statuses.get("supporting_information_pdf") == "PASS"
    )

    if all_packaging_pass:
        assert statuses["final_upload_readiness"] == "BLOCKED_ONLY_BY_AUTHOR_METADATA"
    else:
        assert statuses["final_upload_readiness"] == "BLOCKED_BY_PACKAGING_QA_AND_AUTHOR_METADATA"

    assert gate["unresolved_human_fields"]
    assert gate["optional_post_initial_submission_field"] == ["permanent archive DOI"]


def test_final_gate_points_to_canonical_article():
    gate = load(GATE)
    article = load(ARTICLE)
    resolution = load(RESOLUTION)
    assert gate["canonical_contract"] == "contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
    assert article["status"] == "canonical_initial_submission_packaging_scientific_analysis_closed"
    assert resolution["canonical_initial_submission"]["submission_type"] == "Article"


def test_docx_artifact_record_is_well_formed_when_present():
    gate = load(GATE)
    docx = gate["canonical_artifacts"]["placeholder_docx"]
    assert isinstance(docx["workflow_run_id"], int)
    assert isinstance(docx["artifact_id"], int)
    assert str(docx["digest"]).startswith("sha256:")
    assert docx["pages"] >= 1
