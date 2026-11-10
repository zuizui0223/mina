#!/usr/bin/env python3
"""Independent guards of original 25km ocean source cell overlapping buffers."""
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("marine",
    Path(__file__).resolve().parent/"audit_pair_nesting_ice_buffer_overlap.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


class TestOriginalMarineMembership(unittest.TestCase):
    def test_source_overlap_exact(self):
        rec=m.overlap({1,2,3,4},{3,4,5,6})
        self.assertEqual(rec["n_shared_native_25km_ocean_pixels"],2)
        self.assertEqual(rec["n_native_ocean_pixel_union"],6)
        self.assertAlmostEqual(rec["native_ocean_pixel_jaccard"],1/3)
        self.assertAlmostEqual(rec["fraction_of_smaller_buffer_source_pixels_shared"],.5)

    def test_identical_source_means_full_pixel_dependence(self):
        rec=m.overlap({2,3,4},{3,2,4})
        self.assertEqual(rec["native_ocean_pixel_jaccard"],1)
        self.assertTrue(rec["exact_same_original_25km_ocean_cell_set"])

    def test_nonoverlapping_source_pixels_not_same_environment(self):
        rec=m.overlap({1,2,3},{4,5,6})
        self.assertEqual(rec["native_ocean_pixel_jaccard"],0)
        self.assertFalse(rec["partial_shared_buffer_source_not_independent_ice_exposure"])

    def test_zero_pixel_source_refuses_to_invent_buffer(self):
        with self.assertRaises(ValueError):
            m.overlap([], [1,2,3])

    def test_named_pair_rank_is_descriptive_not_probability(self):
        def row(a,b,species,div,icediff,j):
            return {
                "left_site_id":a,"right_site_id":b,"species":species,
                "within_original_100km_buffer_radius":True,
                "source_method_same":True,
                "n_identical_original_observed_nest_seasons":25,
                "either_original_long_count_series_contains_real_zero_count":False,
                "absolute_nest_log1p_OLS_slope_difference_per_decade":div,
                "mean_absolute_source_original_aug_nov_sic_diff_pp":icediff,
                "native_ocean_pixel_jaccard":j}
        named=row("CRZW","ROYD","ADPE",.498,2.247,.35)
        rows=[named,row("A","B","ADPE",1.0,5.0,.20),row("C","D","GEPE",.1,.2,.75)]
        d=m.rank_named_pair(rows)
        self.assertEqual(d["original_all_source_local_same_block_pairs"]["n_original_compared_pairs"],3)
        self.assertEqual(d["original_all_source_local_same_block_pairs"]["rank_abs_nest_trend_difference_1_is_largest"],2)
        self.assertEqual(d["original_all_source_local_same_block_pairs"]["rank_original_SIC_mean_absolute_difference_1_is_most_similar"],2)

if __name__=="__main__":
    unittest.main()
