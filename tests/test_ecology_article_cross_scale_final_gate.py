from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "submission" / "ECOLOGY_ARTICLE_CROSS_SCALE_FINAL_GATE_V0_1.json"
ARTICLE = ROOT / "contracts" / "ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
RESOLUTION = ROOT / "contracts" / "ECOLOGY_CROSS_SCALE_CANONICAL_TARGET_V1.json"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def test_science_closed_and_current_package_rebuilt():
    gate=load(GATE); s=gate["statuses"]
    assert s["scientific_analysis"]=="PASS_ENDPOINTS_CLOSED_INTERPRETATION_REVISED"
    assert s["claim_boundary"]=="PASS_REVISED_FOR_INCREASING_NETWORKS"
    assert s["repository_ci"]=="PASS_CURRENT_HEAD_FOCUSED_CHECK"
    assert s["main_document_generation"]=="PASS_REVISED_DOCX_STRUCTURAL_QA"
    assert s["main_document_visual_qa"]=="PENDING_FINAL_VISUAL_QA_REVISED_DOCX"
    assert s["main_figure_visual_qa"]=="PASS_SIZE_AUDIT_PENDING_FINAL_VISUAL_QA"
    assert s["supporting_information_pdf"]=="PASS_BUILD_PENDING_FINAL_VISUAL_QA"
    assert s["generated_manuscript_page_limit"]=="PENDING_FINAL_RENDER_PAGE_COUNT"
    assert s["final_upload_readiness"]=="BLOCKED_BY_FINAL_VISUAL_QA_AND_AUTHOR_METADATA"

def test_current_artifact_provenance_is_well_formed():
    gate=load(GATE)
    docx=gate["canonical_artifacts"]["placeholder_docx"]
    figs=gate["canonical_artifacts"]["main_figures"]
    si=gate["canonical_artifacts"]["appendix_s1"]
    assert docx["workflow_run_id"]==37271645516
    assert docx["artifact_id"]==11328750641
    assert str(docx["digest"]).startswith("sha256:")
    assert figs["workflow_run_id"]==37271645669
    assert figs["count"]==3
    assert si["workflow_run_id"]==37271645474

def test_final_gate_points_to_current_ecology_article():
    gate=load(GATE); article=load(ARTICLE); resolution=load(RESOLUTION)
    assert gate["canonical_contract"]=="contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
    assert article["status"]=="canonical_revised_package_built_visual_qa_pending"
    assert resolution["canonical_initial_submission"]["submission_type"]=="Article"
    assert gate["unresolved_human_fields"]
