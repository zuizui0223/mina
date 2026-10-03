from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "submission" / "ECOLOGY_ARTICLE_CROSS_SCALE_FINAL_GATE_V0_1.json"
ARTICLE = ROOT / "contracts" / "ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
RESOLUTION = ROOT / "contracts" / "ECOLOGY_CROSS_SCALE_CANONICAL_TARGET_V1.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_final_gate_has_no_scientific_or_format_blocker():
    gate = load(GATE)
    statuses = gate["statuses"]
    assert statuses["scientific_analysis"] == "PASS_CLOSED"
    assert statuses["claim_boundary"] == "PASS"
    assert statuses["reproducibility_receipts"] == "PASS"
    assert statuses["main_document_visual_qa"] == "PASS_24_OF_24_PAGES"
    assert statuses["main_figure_visual_qa"] == "PASS_3_OF_3"
    assert statuses["generated_manuscript_page_limit"] == "PASS_27_OF_30"
    assert statuses["canonical_package_uniqueness"] == "PASS"


def test_final_upload_is_blocked_only_by_human_metadata():
    gate = load(GATE)
    assert gate["statuses"]["final_upload_readiness"] == "BLOCKED_ONLY_BY_AUTHOR_METADATA"
    assert gate["unresolved_human_fields"]
    assert gate["optional_post_initial_submission_field"] == ["permanent archive DOI"]


def test_final_gate_points_to_canonical_article():
    gate = load(GATE)
    article = load(ARTICLE)
    resolution = load(RESOLUTION)
    assert gate["canonical_contract"] == "contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
    assert article["status"] == "canonical_initial_submission_packaging_scientific_analysis_closed"
    assert resolution["canonical_initial_submission"]["submission_type"] == "Article"


def test_final_gate_points_to_current_docx_artifact():
    gate = load(GATE)
    docx = gate["canonical_artifacts"]["placeholder_docx"]
    assert docx["workflow_run_id"] == 37117211288
    assert docx["artifact_id"] == 11271907803
    assert docx["digest"] == "sha256:310d1eb394dda79cb4d3d0552edd40f70f68f97a4598fbd41ffae6552833364b"
    assert gate["statuses"]["ai_disclosure"] == "PASS_METHODS_ACKNOWLEDGMENTS_AND_SUBMISSION_COPY"
    assert gate["statuses"]["data_provider_acknowledgments"] == "PASS"
