from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKER = ROOT / "contracts" / "PALMER_PHENOTYPE_REASSEMBLY_EXECUTION_V1.json"
WORKFLOW = ROOT / ".github" / "workflows" / "palmer-phenotype-persistence-one-shot.yml"


def test_execution_marker_is_bound_to_frozen_contract():
    marker = json.loads(MARKER.read_text(encoding="utf-8"))

    assert marker["execution_id"] == "mina-palmer-phenotype-persistence-one-shot-v1"
    assert marker["contract_id"] == "mina-palmer-phenotype-reassembly-v1"
    assert marker["contract_merge_sha"] == (
        "7b7e96d29938aa08581f2da814e07bf66e2c16a1"
    )
    assert marker["workflow_dispatch_enabled"] is False
    assert marker["rerun_same_v1_after_material_failure_allowed"] is False


def test_one_shot_workflow_has_no_manual_or_pull_request_trigger():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch" not in text
    assert "pull_request:" not in text
    assert "push:" in text
    assert "branches:" in text
    assert "- main" in text


def test_one_shot_workflow_fetches_pinned_source_and_runs_only_frozen_analysis():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "scripts/fetch_palmer_raw.py" in text
    assert "scripts/run_palmer_persistence.py" in text
    assert "PALMER_PHENOTYPE_PERSISTENCE_RESULT_V1.json" in text
    assert "PALMER_PHENOTYPE_PERSISTENCE_EXECUTION_V1.json" in text
    assert "alternate" not in text.lower()
