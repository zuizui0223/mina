import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SpatialRecoveryDocContractTests(unittest.TestCase):
    def test_effect_contract_uses_only_structured_linear_shift_null(self):
        effect = json.loads(
            (ROOT / "contracts" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_EFFECT_V1.json")
            .read_text(encoding="utf-8")
        )
        primary = effect["primary_inference"]
        self.assertIn("physical_master_site_sign_flip", primary)
        self.assertIn("structured_linear_shift_null", primary)
        self.assertNotIn("trajectory_drift_null", primary)
        self.assertIn("T_obs > 0", primary["support"])
        self.assertIn("physical-MasterSite sign-flip", primary["support"])
        self.assertIn("Delta_linear", primary["support"])

    def test_active_docs_do_not_use_superseded_null_names(self):
        paths = [
            ROOT / "docs" / "ONE_PAPER_SPATIAL_RECOVERY_DECISION_TABLE_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_EXECUTION_MANIFEST_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_LITERATURE_POSITION_V1.md",
            ROOT / "docs" / "REGISTERED_INTEGRATED_MANUSCRIPT_SPINE_HYSTERESIS_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_PROTOCOL_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_RUNBOOK_V1.md",
        ]
        text = "\n".join(p.read_text(encoding="utf-8") for p in paths).casefold()
        self.assertNotIn("trajectory-phase circular-shift", text)
        self.assertNotIn("common-phase null", text)
        self.assertNotIn("elapsed-time trajectory-drift null", text)
        self.assertNotIn("common circular phase-null", text)
        self.assertNotIn("draw one common circular shift", text)

    def test_active_docs_require_geographic_replication(self):
        paths = [
            ROOT / "docs" / "ONE_PAPER_SPATIAL_RECOVERY_DECISION_TABLE_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_EXECUTION_MANIFEST_V1.md",
            ROOT / "docs" / "REGISTERED_INTEGRATED_MANUSCRIPT_SPINE_HYSTERESIS_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_PROTOCOL_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_RUNBOOK_V1.md",
        ]
        text = "\n".join(p.read_text(encoding="utf-8") for p in paths)
        self.assertIn("physical-MasterSite", text)
        self.assertIn("p_{\\mathrm{master}}", text)

    def test_provider_template_matches_zero_semantics_contract(self):
        contract = json.loads(
            (ROOT / "contracts" / "SMP_SPATIAL_RECOVERY_ZERO_SEMANTICS_V1.json")
            .read_text(encoding="utf-8")
        )
        template = json.loads(
            (ROOT / "submission" / "SMP_ZERO_SEMANTICS_PROVIDER_CONFIRMATION_TEMPLATE_V1.json")
            .read_text(encoding="utf-8")
        )
        required = set(contract["required_confirmation_fields"])
        supplied = set(template["provider_confirmation_required"]) - {"notes"}
        self.assertEqual(required, supplied)
        self.assertEqual(
            template["status"],
            "template_only_not_provider_confirmation",
        )

    def test_provider_evidence_ledger_preserves_unresolved_missing_row_semantics(self):
        text = (
            ROOT / "docs" / "SMP_PROVIDER_EVIDENCE_LEDGER_V1.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Missing-row semantics", text)
        self.assertIn("requiring provider confirmation", text)
        self.assertIn("absence of a SiteID × species × year row", text)

    def test_execution_manifest_points_to_registered_spine(self):
        text = (
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_EXECUTION_MANIFEST_V1.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "docs/REGISTERED_INTEGRATED_MANUSCRIPT_SPINE_HYSTERESIS_V1.md",
            text,
        )
        self.assertNotIn("INTEGRATED_COLLAPSE_RECOVERY_MANUSCRIPT_SPINE_V1.md", text)

if __name__ == "__main__":
    unittest.main()
