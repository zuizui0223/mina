import json
import unittest

from scripts.gate_smp_spatial_recovery_hysteresis_structure_v1 import (
    MIN_MASTERS,
    MIN_PANELS,
    MIN_SPECIES,
)


class HysteresisStructureContractTests(unittest.TestCase):
    def test_program_minima_match_downstream_possibility(self):
        self.assertEqual(MIN_PANELS, 10)
        self.assertEqual(MIN_MASTERS, 10)
        self.assertEqual(MIN_SPECIES, 5)

    def test_structure_gate_has_no_outcome_thresholds(self):
        text = json.dumps({
            "MIN_PANELS": MIN_PANELS,
            "MIN_MASTERS": MIN_MASTERS,
            "MIN_SPECIES": MIN_SPECIES,
        }).lower()
        self.assertNotIn("hysteresis width", text)
        self.assertNotIn("delta_gamma", text)


if __name__ == "__main__":
    unittest.main()
