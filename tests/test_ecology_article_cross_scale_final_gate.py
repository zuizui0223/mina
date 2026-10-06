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
    gate = load(GATE)
    s = gate["statuses"]
    assert s["scientific_analysis"] == "PASS_ENDPOINTS_CLOSED_SOURCE_PROVENANCE_WORDING_CORRECTED"
    assert s["claim_boundary"] == "PASS_REVISED_FOR_SAMPLE_COLONY_SCOPE_AND_INCREASING_NETWORKS"
    assert s["repository_ci"] == "PENDING_AFTER_SOURCE_PROVENANCE_CORRECTION"
    assert s["main_document_generation"] == "PENDING_REGENERATION_AFTER_SOURCE_PROVENANCE_CORRECTION"
    assert s["main_document_visual_qa"] == "PENDING_NEW_RENDER"
    assert s["main_figure_visual_qa"] == "PASS_ALL_THREE_MAIN_FIGURES"
    assert s["supporting_information_pdf"] == "PENDING_REGENERATION_AND_VISUAL_QA"
    assert s["generated_manuscript_page_limit"] == "PENDING_NEW_RENDER_PAGE_COUNT"
    assert (
        s["final_upload_readiness"]
        == "BLOCKED_BY_AUTHOR_METADATA_AND_POST_CORRECTION_REGENERATION_QA"
    )


def test_current_artifact_provenance_is_well_formed():
    gate = load(GATE)
    artifacts = gate["canonical_artifacts"]
    docx = artifacts["placeholder_docx"]
    figs = artifacts["main_figures"]
    si = artifacts["appendix_s1"]

    assert docx["workflow_run_id"] == 37391673031
    assert docx["artifact_id"] == 11381845511
    assert docx["rendered_pages"] == 29
    assert str(docx["digest"]).startswith("sha256:")
    assert "SUPERSEDED" in docx["status"]

    assert figs["workflow_run_id"] == 37391673074
    assert figs["artifact_id"] == 11381685529
    assert figs["count"] == 3
    assert str(figs["digest"]).startswith("sha256:")

    assert si["workflow_run_id"] == 37391672322
    assert si["artifact_id"] == 11381457683
    assert si["rendered_pages"] == 9
    assert str(si["digest"]).startswith("sha256:")
    assert "SUPERSEDED" in si["status"]

    assert artifacts["rendered_main_document_pages"] == 29
    assert artifacts["separate_main_figure_pages"] == 3
    assert artifacts["complete_article_pages"] == 32
    assert artifacts["ecology_standard_article_page_limit"] == 30
    assert artifacts["overlength_justification_present"] is True


def test_final_gate_points_to_current_ecology_article():
    gate = load(GATE)
    article = load(ARTICLE)
    resolution = load(RESOLUTION)

    assert (
        gate["canonical_contract"]
        == "contracts/ECOLOGY_ARTICLE_CROSS_SCALE_SUBMISSION_V1.json"
    )
    assert article["status"] == "canonical_package_source_provenance_corrected_rebuild_pending"
    assert resolution["canonical_initial_submission"]["submission_type"] == "Article"
    assert gate["unresolved_human_fields"]
