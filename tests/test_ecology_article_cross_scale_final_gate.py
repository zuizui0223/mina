from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "submission" / "ECOLOGY_ARTICLE_CROSS_SCALE_FINAL_GATE_V0_1.json"
ARTICLE = ROOT / "contracts" / "ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
RESOLUTION = ROOT / "contracts" / "ECOLOGY_CROSS_SCALE_CANONICAL_TARGET_V1.json"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def test_scientific_endpoints_closed_but_packaging_reopened():
    gate=load(GATE); s=gate["statuses"]
    assert s["scientific_analysis"]=="PASS_ENDPOINTS_CLOSED_INTERPRETATION_REVISED"
    assert s["claim_boundary"]=="PASS_REVISED_FOR_INCREASING_NETWORKS"
    assert s["reproducibility_receipts"]=="PASS"
    assert s["canonical_package_uniqueness"]=="PASS"
    assert s["final_upload_readiness"]=="BLOCKED_OLD_ARTIFACTS_SUPERSEDED_PLUS_AUTHOR_METADATA"

def test_old_artifacts_are_explicitly_superseded():
    gate=load(GATE)
    assert gate["canonical_artifacts"]["placeholder_docx"]["status"]=="SUPERSEDED_DO_NOT_UPLOAD"
    assert gate["canonical_artifacts"]["main_figures"]["status"]=="SUPERSEDED_PENDING_REVISED_STORY_FIGURE_QA"
    assert gate["statuses"]["main_document_generation"].startswith("REQUIRED_REGEN")
    assert gate["statuses"]["main_document_visual_qa"].startswith("REQUIRED_REQA")
    assert gate["statuses"]["generated_manuscript_page_limit"]=="PENDING_REGENERATED_PACKAGE"

def test_final_gate_points_to_canonical_article():
    gate=load(GATE); article=load(ARTICLE); resolution=load(RESOLUTION)
    assert gate["canonical_contract"]=="contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
    assert article["status"]=="canonical_target_retained_scientific_text_revised_packaging_must_regenerate"
    assert resolution["canonical_initial_submission"]["submission_type"]=="Article"

def test_superseded_docx_record_remains_provenance():
    docx=load(GATE)["canonical_artifacts"]["placeholder_docx"]
    assert isinstance(docx["workflow_run_id"],int)
    assert isinstance(docx["artifact_id"],int)
    assert str(docx["digest"]).startswith("sha256:")
    assert docx["status"]=="SUPERSEDED_DO_NOT_UPLOAD"
