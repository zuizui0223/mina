import json
import tempfile
import unittest
from pathlib import Path
from scripts.check_paper2_real_unlock import assert_real_outcome_unlocked

class UnlockTests(unittest.TestCase):
    def test_missing_receipts_lock_outcomes(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                assert_real_outcome_unlocked(Path(d))

    def test_false_gate_locks_outcomes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"results").mkdir()
            (root/"results/PAPER2_SPATIAL_ADJUSTED_V3_RESULT_V1.json").write_text(json.dumps({"decision":{"spatially_adjusted_core_passed":False,"no_real_count_magnitudes_opened":True}}))
            (root/"results/PAPER2_V3_SOURCE_SENSITIVITY_RESULT_V1.json").write_text(json.dumps({"decision":{"source_sensitivity_passed":True,"no_real_count_magnitudes_opened":True}}))
            with self.assertRaises(RuntimeError):
                assert_real_outcome_unlocked(root)

    def test_both_pass_unlock(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"results").mkdir()
            (root/"results/PAPER2_SPATIAL_ADJUSTED_V3_RESULT_V1.json").write_text(json.dumps({"decision":{"spatially_adjusted_core_passed":True,"no_real_count_magnitudes_opened":True}}))
            (root/"results/PAPER2_V3_SOURCE_SENSITIVITY_RESULT_V1.json").write_text(json.dumps({"decision":{"source_sensitivity_passed":True,"no_real_count_magnitudes_opened":True}}))
            self.assertTrue(assert_real_outcome_unlocked(root)["unlocked"])
if __name__=="__main__":unittest.main()
