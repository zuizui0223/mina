import unittest

try:
    import pandas as pd
    import pyreadr  # noqa: F401
except ModuleNotFoundError as exc:
    raise unittest.SkipTest(
        "Paper 2 forcing-support tests require pandas and pyreadr"
    ) from exc

from scripts.audit_paper2_forcing_support import (
    evaluate_group,
    select_level,
    select_modeling_level,
    build_frozen_unit_rows,
    summarize_forcing_support,
    validate_frozen_cohort,
)


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


class CohortAndAuditTests(unittest.TestCase):
    def test_frozen_cohort_drift_fails_closed(self):
        validate_frozen_cohort(152, 107)
        with self.assertRaises(ValueError):
            validate_frozen_cohort(151, 107)
        with self.assertRaises(ValueError):
            validate_frozen_cohort(152, 106)



    def test_build_frozen_rows_reproduces_107_without_count_leakage(self):
        gate0 = {"ADPE": 57, "CHPE": 46, "GEPE": 49}
        bridged = {"ADPE": 44, "CHPE": 34, "GEPE": 29}
        obs_rows = []
        site_rows = []
        unit_index = 0
        for species_id in ("ADPE", "CHPE", "GEPE"):
            for j in range(gate0[species_id]):
                site_id = f"S{unit_index:03d}"
                site_rows.append(
                    {
                        "site_id": site_id,
                        "region": "R1",
                        "ccamlr_id": "48.1",
                    }
                )
                years = [1980, 1985, 1990, 1995, 2000]
                seasons = (
                    [1980, 1990, 2000, 2010, 2020]
                    if j < bridged[species_id]
                    else [1995, 2000, 2005, 2010, 2015]
                )
                for k, (year, season) in enumerate(zip(years, seasons)):
                    obs_rows.append(
                        {
                            "site_id": site_id,
                            "species_id": species_id,
                            "type": "nests",
                            "count": 100000 + unit_index * 10 + k,
                            "year": year,
                            "season": season,
                        }
                    )
                unit_index += 1

        rows = build_frozen_unit_rows(
            pd.DataFrame(obs_rows),
            pd.DataFrame(site_rows),
        )
        self.assertEqual(len(rows), 107)
        by_species = {}
        for row in rows:
            by_species[row["species_id"]] = by_species.get(row["species_id"], 0) + 1
            self.assertNotIn("count", row)
            self.assertNotIn("abundance", row)
        self.assertEqual(by_species, bridged)

    def test_missing_apbp_label_forces_coarser_complete_level(self):
        seasons = list(range(1980, 2026, 3))
        rows = []
        for i in range(5):
            rows.append(
                {
                    "unit_id": f"ADPE|u{i}",
                    "species_id": "ADPE",
                    "region": "A" if i < 4 else None,
                    "ccamlr_id": "48.1",
                    "seasons": seasons,
                }
            )
        result = summarize_forcing_support(rows, 1980, 2025)
        self.assertEqual(result["species"]["ADPE"]["selected_level"], "ccamlr")
        self.assertEqual(
            result["species"]["ADPE"]["levels"]["apbp_region"]["missing_label_units"],
            1,
        )

    def test_support_summary_contains_no_demographic_count_magnitude(self):
        seasons = list(range(1980, 2026, 3))
        rows = [
            {
                "unit_id": f"GEPE|u{i}",
                "species_id": "GEPE",
                "region": "A",
                "ccamlr_id": "48.1",
                "seasons": seasons,
            }
            for i in range(5)
        ]
        result = summarize_forcing_support(rows, 1980, 2025)
        rendered = repr(result).lower()
        self.assertNotIn("'count'", rendered)
        self.assertNotIn("'abundance'", rendered)

    def test_selected_level_is_deterministic_from_support_metadata(self):
        seasons = list(range(1980, 2026, 3))
        rows = [
            {
                "unit_id": f"CHPE|u{i}",
                "species_id": "CHPE",
                "region": "A",
                "ccamlr_id": "48.1",
                "seasons": seasons,
            }
            for i in range(5)
        ]
        first = summarize_forcing_support(rows, 1980, 2025)
        second = summarize_forcing_support(list(reversed(rows)), 1980, 2025)
        self.assertEqual(first, second)


class ModelingLevelSelectionTests(unittest.TestCase):
    def test_allows_fine_scale_when_two_groups_cover_at_least_95_percent(self):
        units = {f"u{i}" for i in range(34)}
        levels = {
            "apbp_region": {
                "groups": [
                    {"group": "A", "unit_ids": [f"u{i}" for i in range(18)], "qualifies": True},
                    {"group": "B", "unit_ids": [f"u{i}" for i in range(18, 33)], "qualifies": True},
                    {"group": "C", "unit_ids": ["u33"], "qualifies": False},
                ]
            },
            "ccamlr": {
                "groups": [{"group": "48.1", "unit_ids": sorted(units), "qualifies": True}]
            },
            "species_wide": {
                "groups": [{"group": "all", "unit_ids": sorted(units), "qualifies": True}]
            },
        }
        result = select_modeling_level(levels, units, 0.95)
        self.assertEqual(result["level"], "apbp_region")
        self.assertEqual(len(result["covered_units"]), 33)
        self.assertEqual(result["excluded_units"], ["u33"])

    def test_falls_to_ccamlr_when_apbp_coverage_is_below_95_percent(self):
        units = {f"u{i}" for i in range(44)}
        levels = {
            "apbp_region": {
                "groups": [
                    {"group": "A", "unit_ids": [f"u{i}" for i in range(6)], "qualifies": True},
                    {"group": "B", "unit_ids": [f"u{i}" for i in range(6, 33)], "qualifies": True},
                ]
            },
            "ccamlr": {
                "groups": [
                    {"group": "48.1", "unit_ids": [f"u{i}" for i in range(15)], "qualifies": True},
                    {"group": "88.1", "unit_ids": [f"u{i}" for i in range(15, 42)], "qualifies": True},
                    {"group": "48.2", "unit_ids": ["u42"], "qualifies": False},
                    {"group": "58.4.1", "unit_ids": ["u43"], "qualifies": False},
                ]
            },
            "species_wide": {
                "groups": [{"group": "all", "unit_ids": sorted(units), "qualifies": True}]
            },
        }
        result = select_modeling_level(levels, units, 0.95)
        self.assertEqual(result["level"], "ccamlr")
        self.assertEqual(len(result["covered_units"]), 42)
        self.assertEqual(set(result["excluded_units"]), {"u42", "u43"})

    def test_species_wide_is_last_resort(self):
        units = {f"u{i}" for i in range(10)}
        levels = {
            "apbp_region": {"groups": []},
            "ccamlr": {
                "groups": [{"group": "48.1", "unit_ids": [f"u{i}" for i in range(9)], "qualifies": True}]
            },
            "species_wide": {
                "groups": [{"group": "all", "unit_ids": sorted(units), "qualifies": True}]
            },
        }
        result = select_modeling_level(levels, units, 0.95)
        self.assertEqual(result["level"], "species_wide")
        self.assertEqual(result["coverage_fraction"], 1.0)


if __name__ == "__main__":
    unittest.main()
