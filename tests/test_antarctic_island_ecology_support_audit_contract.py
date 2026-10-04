import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "ANTARCTIC_ISLAND_ECOLOGY_PAPER2_SUPPORT_AUDIT_V1.json"


def test_support_audit_contract_is_outcome_blind():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert c["status"] == "outcome_blind_support_audit_only"

    prohibited = {x.lower() for x in c["source_roster"]["prohibited_demographic_fields_during_audit"]}
    assert any("count magnitude" in x for x in prohibited)
    assert any("population trend" in x for x in prohibited)
    assert any("effective component" in x for x in prohibited)
    assert any("concentration" in x for x in prohibited)

    allowed = {x.lower() for x in c["source_roster"]["allowed_demographic_fields"]}
    assert all("magnitude" not in x for x in allowed)
    assert all("trend" not in x for x in allowed)


def test_support_audit_defers_outcome_model_until_second_contract():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    stages = " ".join(c["staged_design"]).lower()
    assert "separate outcome contract" in stages
    assert "only then join demographic magnitudes" in stages
    assert "cannot report any association" in c["no_outcome_rule"].lower()


def test_support_audit_preserves_paper1_boundary():
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert "do not modify" in c["paper1_boundary"].lower()
    assert "paper 1" in c["paper1_boundary"].lower()
