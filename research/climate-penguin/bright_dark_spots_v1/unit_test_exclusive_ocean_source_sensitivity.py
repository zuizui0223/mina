#!/usr/bin/env python3
"""Independent source-grid depth and original-pair aggregate arithmetic guards."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("depth",Path(__file__).resolve().parent/
    "summarize_exclusive_ocean_source_sensitivity.py")
depth=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(depth)

class TestOriginalExclusiveSourceDepth(unittest.TestCase):
    def test_strict_source_booleans(self):
        self.assertTrue(depth.boolean("True"))
        self.assertFalse(depth.boolean("false"))
        with self.assertRaises(ValueError):
            depth.boolean("perhaps")

    def test_zero_supported_pairs_not_a_ecological_zero(self):
        x=depth.summarize_group([],"none")
        self.assertEqual(x["n_original_source_pairs"],0)
        self.assertTrue(x["cannot_claim_any_source_conclusion"])

    def test_original_signed_absolute_and_median_not_misinterpreted(self):
        rows=[
            {
                "species":"ADPE","source_region":"Victoria Land",
                "original_polar_250km_block":"1:-6",
                "left_site_id":"A","right_site_id":"B",
                "delta":1.0,
                "original_full_buffer_abs_SIC_diff_on_exclusive_years_pp":"2.0",
                "exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp":"3.0",
                "exclusive_divided_by_full_buffer_abs_difference_ratio":"1.5"
            },
            {
                "species":"ADPE","source_region":"Victoria Land",
                "original_polar_250km_block":"1:-6",
                "left_site_id":"A","right_site_id":"C",
                "delta":-0.5,
                "original_full_buffer_abs_SIC_diff_on_exclusive_years_pp":"2.5",
                "exclusive_nonoverlapping_SIC_abs_diff_on_same_years_pp":"2.0",
                "exclusive_divided_by_full_buffer_abs_difference_ratio":"0.8"
            }
        ]
        d=depth.summarize_group(rows,"toy")
        self.assertEqual(d["n_original_pairs_exclusive_SIC_difference_larger_than_full"],1)
        self.assertEqual(d["n_original_pairs_exclusive_SIC_difference_smaller_than_full"],1)
        self.assertEqual(d["n_source_region_species_250km_blocks"],1)
        self.assertEqual(d["n_unique_breeding_colony_species_site_IDS"],3)
        self.assertAlmostEqual(d["median_pairwise_exclusive_to_full_ratio"],1.15)

if __name__=="__main__":
    unittest.main()
