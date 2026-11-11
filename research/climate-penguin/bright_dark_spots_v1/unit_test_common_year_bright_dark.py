#!/usr/bin/env python3
"""Arithmetic guards: no pseudo-common-year, zero-free source check, sign."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("audit",p/"audit_common_year_bright_dark.py")
module=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class TestCommonYearPeers(unittest.TestCase):
    def test_same_observed_years_only(self):
        a={1991:2,1995:5,2000:9,2005:21,2010:41,2020:101}
        b={1991:100,1994:90,1995:75,2000:60,2005:40,2010:25,2020:10}
        r=module.pair_original_years(a,b)
        self.assertEqual(r["status"],"EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED")
        self.assertEqual(r["n_same_original_observed_years"],6)
        self.assertEqual(r["years"],[1991,1995,2000,2005,2010,2020])
        self.assertGreater(r["paired_relative_log1p_nest_decadal_slope"],0)
        self.assertAlmostEqual(
            r["paired_relative_log1p_nest_decadal_slope"],
            r["focal_log1p_nest_slope_per_decade_same_years"]
             -r["peer_log1p_nest_slope_per_decade_same_years"])

    def test_disjoint_decade_do_not_fabricate_common_time(self):
        a={1991:1,1995:2,1999:3,2003:4,2008:5}
        b={2002:1,2005:2,2008:3,2011:4,2014:5,2020:6}
        r=module.pair_original_years(a,b)
        self.assertEqual(r["n_same_original_observed_years"],1)
        self.assertEqual(r["status"],"INSUFFICIENT_FIVE_COOBSERVED_YEARS_OVER_TEN_YEAR_SPAN")

    def test_original_observed_zero_is_not_missing_and_nozero_sensitivity(self):
        a={1991:0,1995:0,1999:1,2003:20,2007:30,2011:35,2015:41,2020:45}
        b={1991:10,1995:20,1999:20,2003:15,2007:12,2011:11,2015:10,2020:9}
        r=module.pair_original_years(a,b)
        rz=module.pair_original_years(a,b,omit_real_zeros=True)
        self.assertEqual(r["n_focal_actual_zero_counts_in_common_years"],2)
        self.assertEqual(rz["n_same_original_observed_years"],6)
        self.assertNotEqual(r["paired_relative_log1p_nest_decadal_slope"],rz["paired_relative_log1p_nest_decadal_slope"])

    def test_zero_sensitivity_insufficient_is_not_false_negative(self):
        a={1991:0,1995:0,2000:0,2005:11,2010:14,2015:18}
        b={1991:3,1995:4,2000:5,2005:6,2010:7,2015:9}
        r=module.pair_original_years(a,b)
        rz=module.pair_original_years(a,b,omit_real_zeros=True)
        self.assertEqual(r["status"],"EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED")
        self.assertEqual(rz["status"],"INSUFFICIENT_FIVE_COOBSERVED_YEARS_OVER_TEN_YEAR_SPAN")

    def test_validated_original_strict_label(self):
        self.assertTrue(module.original_robust(
            {"robust_source_candidate_status":"SOURCE_ROBUST_RELATIVE_DARK_CANDIDATE"}))
        self.assertFalse(module.original_robust(
            {"robust_source_candidate_status":"SOURCE_SENSITIVITY_OR_DENSITY_INCOMPLETE_NO_ROBUST_CLAIM"}))


if __name__=="__main__":
    unittest.main()
