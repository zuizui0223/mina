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
        self.assertIn("structured_linear_shift_null", primary)
        self.assertNotIn("trajectory_drift_null", primary)
        self.assertIn("Delta_linear", primary["support"])

    def test_active_docs_do_not_use_superseded_null_names(self):
        paths = [
            ROOT / "docs" / "ONE_PAPER_SPATIAL_RECOVERY_DECISION_TABLE_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_EXECUTION_MANIFEST_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_LITERATURE_POSITION_V1.md",
            ROOT / "docs" / "REGISTERED_INTEGRATED_MANUSCRIPT_SPINE_HYSTERESIS_V1.md",
            ROOT / "docs" / "SMP_SPATIAL_RECOVERY_HYSTERESIS_PROTOCOL_V1.md",
        ]
        text = "\n".join(p.read_text(encoding="utf-8") for p in paths).casefold()
        self.assertNotIn("trajectory-phase circular-shift", text)
        self.assertNotIn("common-phase null", text)
        self.assertNotIn("elapsed-time trajectory-drift null", text)

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
