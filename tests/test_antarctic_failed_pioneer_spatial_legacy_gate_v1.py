"""Keep novel failed-pioneer legacy a future hypothesis, not Cox 2024 result."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"contracts/ANTARCTIC_FAILED_PIONEER_SPATIAL_LEGACY_CAUSAL_GATE_V1.json"


def test_three_competing_processes_and_real_controls():
    d=json.loads(CONTRACT.read_text())
    assert len(d["alternative_hypotheses"])==3
    assert all(x in d["alternative_hypotheses"] for x in
               ("H1_physical_legacy_without_success","H2_social_success_only",
                "H3_static_habitat_sorting"))
    assert d["primary_unit"].startswith("independently identified")
    assert len(d["prior_class_labels_fixed_before_future_settlement"])==4
    assert any("never used" in x.lower() for x in d["minimum_data_gate"])
    assert d["decision"]=="PROSPECTIVE_DESIGN_ONLY_HOLD_CAUSAL_DATA"


def test_prior_art_novelty_and_safeguards_remain_strict():
    d=json.loads(CONTRACT.read_text())
    assert any("Cox et al 2024" in x for x in d["prior_art_beyond_which_novelty_is_required"])
    assert any("1968" in x for x in d["forbidden"])
    assert "approvals" in d["no_experiment_authorized"].lower()
    assert "PR189" in " ".join(d["forbidden"])
    assert "PR142" in " ".join(d["forbidden"])
    assert "AFTER seeing data" in d["prior_observational_dataset_status"]
    assert "Never label 2021 nonbreeder site" in d["forbidden"][0]
