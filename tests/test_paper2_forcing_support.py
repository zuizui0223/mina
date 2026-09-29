import unittest

from scripts.audit_paper2_forcing_support import evaluate_group, select_level


class EvaluateGroupTests(unittest.TestCase):
    def test_five_well_overlapped_units_qualify(self):
        seasons = list(range(1980, 2026, 3))
        unit_seasons = {f"u{i}": seasons for i in range(5)}
        result = evaluate_group(unit_seasons, 1980, 2025)
        self.assertEqual(result["n_units"], 5)
        self.assertGreaterEqual(result["observed_seasons_ge3_units"], 15)
        self.assertGreaterEqual(result["covered_seasons_ge50pct_units"], 10)
        self.assertEqual(result["spanning_first_last_thirds_units"], 5)
        self.assertTrue(result["qualifies"])

    def test_four_units_fail_minimum_unit_rule(self):
        seasons = list(range(1980, 2026, 3))
        result = evaluate_group({f"u{i}": seasons for i in range(4)}, 1980, 2025)
        self.assertFalse(result["qualifies"])
        self.assertEqual(result["n_units"], 4)

    def test_odd_group_uses_ceiling_for_half_coverage(self):
        unit_seasons = {
            "u1": [1980, 1990],
            "u2": [1980, 1990],
            "u3": [1980, 1990],
            "u4": [2000, 2010],
            "u5": [2000, 2010],
        }
        result = evaluate_group(unit_seasons, 1980, 2025)
        self.assertEqual(result["coverage_unit_threshold"], 3)
        self.assertEqual(result["covered_seasons_ge50pct_units"], 11)


class SelectLevelTests(unittest.TestCase):
    def test_selects_apbp_before_coarser_levels(self):
        units = {"u1", "u2", "u3", "u4", "u5"}
        levels = {
            "apbp_region": {
                "groups": [
                    {"group": "A", "unit_ids": sorted(units), "qualifies": True}
                ]
            },
            "ccamlr": {
                "groups": [
                    {"group": "48.1", "unit_ids": sorted(units), "qualifies": True}
                ]
            },
            "species_wide": {
                "groups": [
                    {"group": "all", "unit_ids": sorted(units), "qualifies": True}
                ]
            },
        }
        self.assertEqual(select_level(levels, units), "apbp_region")

    def test_incomplete_apbp_coverage_falls_back_to_ccamlr(self):
        units = {"u1", "u2", "u3", "u4", "u5"}
        levels = {
            "apbp_region": {
                "groups": [
                    {"group": "A", "unit_ids": ["u1", "u2", "u3", "u4"], "qualifies": True}
                ]
            },
            "ccamlr": {
                "groups": [
                    {"group": "48.1", "unit_ids": sorted(units), "qualifies": True}
                ]
            },
            "species_wide": {
                "groups": [
                    {"group": "all", "unit_ids": sorted(units), "qualifies": True}
                ]
            },
        }
        self.assertEqual(select_level(levels, units), "ccamlr")

    def test_species_wide_failure_fails_closed(self):
        units = {"u1", "u2", "u3", "u4", "u5"}
        levels = {
            "apbp_region": {"groups": []},
            "ccamlr": {"groups": []},
            "species_wide": {
                "groups": [
                    {"group": "all", "unit_ids": sorted(units), "qualifies": False}
                ]
            },
        }
        self.assertIsNone(select_level(levels, units))


if __name__ == "__main__":
    unittest.main()
