import json
from pathlib import Path

from scripts.audit_jbi_submission_readiness import audit


def test_current_jbi_package_is_scientifically_ready_but_not_upload_ready():
    result=audit(Path("."))
    assert result["scientific_package_ready"] is True
    assert result["upload_ready"] is False
    assert result["status"] == "SCIENTIFIC_PACKAGE_READY_UPLOAD_BLOCKED"
    assert result["upload_blockers"]["open_checklist_items"]
    assert result["scientific_guards"]["signy_nonreplication_explicit"] is True
    assert result["scientific_guards"]["signy_sensitivity_not_promoted"] is True


def test_manifest_points_to_current_jbi_files():
    result=audit(Path("."))
    assert result["files"]["main_manuscript"]["path"] == "docs/MANUSCRIPT_INTEGRATED_JBI_V0_4.md"
    assert result["files"]["scientific_source"]["path"] == "docs/MANUSCRIPT_INTEGRATED_V0_3.md"
