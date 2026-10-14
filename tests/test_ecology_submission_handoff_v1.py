"""Ecology author-controlled release gate; source data and person metadata never printed."""
import copy
import json
from pathlib import Path

import pytest

from scripts.audit_ecology_submission_handoff_v1 import (
    FROZEN_BLOBS,
    PUBLIC_BLANK,
    TITLE,
    audit,
    freeze_integrity,
    git_blob_sha,
    metadata_checks,
    source_and_production_checks,
    word_count,
)

ROOT = Path(__file__).resolve().parents[1]


def _fake_author_only_test_fixture():
    # No real author identity, grant, or contact address.
    d = json.loads((ROOT / PUBLIC_BLANK).read_text(encoding="utf-8"))
    d["authors"] = [{
        "name": "Test Author",
        "affiliation_ids": ["1"],
        "corresponding": True,
        "email": "no-one@example.invalid",
    }]
    d["affiliations"] = {"1": "Test Department, Example Institute, Nowhere"}
    d["funding_acknowledgments"] = "Example funder only."
    d["author_contributions"] = "Test Author: Writing (example only)."
    d["conflict_of_interest"] = "No conflicts in this synthetic fixture."
    d["ai_tool_inventory_confirmed"] = True
    d["additional_ai_tools"] = []
    d["dual_publication_statement"] = "No overlapping submissions (fixture)."
    d["intended_permanent_repository"] = "Example fake archive"
    d["ai_methods_disclosure_final_text"] = "OpenAI ChatGPT assisted in this fictitious Methods example."
    d["ai_acknowledgments_disclosure_final_text"] = "OpenAI ChatGPT assisted (fake acknowledgment)."
    return d


def test_git_blob_sha_uses_native_git_header(tmp_path):
    p=tmp_path/"s.txt"
    p.write_text("hello\n")
    assert len(git_blob_sha(p)) == 40
    assert git_blob_sha(p) == "ce013625030ba8dba906f756967f9e9ca394464a"


def test_immutable_frozen_analysis_blobs_all_unchanged():
    v=freeze_integrity(ROOT)
    assert len(FROZEN_BLOBS)==8
    assert v["files_checked"]==8
    assert v["all_frozen_blobs_unchanged"] is True
    assert v["blobs"]["results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json"]["current"] == "6682dafcf49d0b9d335ce99ce0e6bb8fa6c4e5d0"


def test_original_scientific_freeze_byte_change_is_detected(tmp_path):
    p=tmp_path/"test.txt"
    p.write_text("a")
    orig=git_blob_sha(p)
    p.write_text("b")
    assert git_blob_sha(p) != orig


def test_current_submission_abstract_sources_and_mock_qa():
    v=source_and_production_checks(ROOT)
    assert v["pass"]
    assert v["journal"]=="Ecology"
    assert v["canonical_title_matches"]
    assert v["abstract_words_simple_tokenizer"]<=350
    assert v["missing_bibliography_keys_recomputed"]==[]
    assert v["previous_mock_author_complete_pages"] == 30
    assert v["real_author_complete_docx_rechecked"] is False
    assert v["AI_acknowledgment_template_present"] is True
    assert v["AI_disclosure_in_frozen_methods"] is False
    assert all(v["source_dataset_DOIs_in_open_research_document"].values())


def test_public_author_template_is_explicitly_blocked():
    result=audit(ROOT)
    assert result["result"] == "BLOCKED_BEFORE_REAL_SUBMISSION"
    assert result["not_submitted"] is True
    assert result["science_freeze"]["all_frozen_blobs_unchanged"]
    assert result["author_metadata"]["ready_for_submission_metadata"] is False
    assert "all_authors_approved_final_version" in result["author_metadata"]["unresolved_fields"]


def test_basic_metadata_does_not_override_unapproved_human_gate():
    sample=_fake_author_only_test_fixture()
    result=metadata_checks(sample)
    assert result["ready_for_submission_metadata"] is False
    assert result["author_count"]==1
    assert "all_authors_approved_final_version" in result["unresolved_fields"]


def test_all_human_signoffs_still_require_real_information_privately():
    sample=_fake_author_only_test_fixture()
    for k in sample["initial_submission_human_signoff"]:
        sample["initial_submission_human_signoff"][k]=True
    result=metadata_checks(sample)
    # Synthetic fixture demonstrates validator only; no public submission happens.
    assert result["ready_for_submission_metadata"] is True
    assert result["post_acceptance_archive_doi_still_pending"] is True
    assert "Test Author" not in json.dumps(result)
    assert "no-one@example.invalid" not in json.dumps(result)


def test_abstract_limit_simple_tokenizer():
    assert word_count("One two three.") == 3
    assert word_count("Recovery can change local composition.") == 5
