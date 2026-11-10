#!/usr/bin/env python3
"""Pure mathematical regression guards for source-backed bright/dark discovery."""
from __future__ import annotations
import importlib.util
import math
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("bright",
    Path(__file__).resolve().parent/"discover_bright_dark_colonies.py")
module=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class TestBrightDark(unittest.TestCase):
    def test_signed_log1p_slope_original_count_years(self):
        points=[(1991,0),(1995,4),(1999,14),(2003,44),(2010,199),(2020,999)]
        slope=module.slope(points)
        self.assertGreater(slope,0)
        self.assertEqual(module.sign(slope),"positive")
        self.assertIsNotNone(module.theil_sen(points))
        self.assertGreater(module.theil_sen(points),0)

    def test_original_years_cannot_be_imputed(self):
        self.assertIsNone(module.slope([(1991,1),(1992,2),(1993,3),(1994,4)]))
        self.assertIsNone(module.slope([(2000,1),(2001,2),(2002,3),(2003,4),(2004,5)]))
        self.assertIsNone(module.theil_sen([(1991,1),(1992,2),(1993,3),(1994,4)]))

    def test_peer_expectation_excludes_focal_site(self):
        group=[
            {"site_id":"bright","original_OLS_log1p_nest_slope_per_decade":100.0},
            {"site_id":"a","original_OLS_log1p_nest_slope_per_decade":-1.0},
            {"site_id":"b","original_OLS_log1p_nest_slope_per_decade":-2.0},
            {"site_id":"c","original_OLS_log1p_nest_slope_per_decade":-3.0},
            {"site_id":"d","original_OLS_log1p_nest_slope_per_decade":-4.0}
        ]
        self.assertAlmostEqual(module.peer_baseline(group,group[0],
            "original_OLS_log1p_nest_slope_per_decade"),-2.5)
        self.assertAlmostEqual(100.0-module.peer_baseline(group,group[0],
            "original_OLS_log1p_nest_slope_per_decade"),102.5)

    def test_relative_and_absolute_growth_signs_differ(self):
        full=[{"site_id":"x","slope":-0.1},
              {"site_id":"a","slope":-0.5},
              {"site_id":"b","slope":-0.6},
              {"site_id":"c","slope":-0.7},
              {"site_id":"d","slope":-0.8}]
        residual=full[0]["slope"]-module.peer_baseline(full,full[0],"slope")
        self.assertEqual(module.sign(full[0]["slope"]),"negative")
        self.assertEqual(module.sign(residual),"positive")

    def test_theilsen_flat_series_is_zero_not_bright(self):
        points=[(1991,200),(1997,200),(2003,200),(2012,200),(2020,200)]
        self.assertAlmostEqual(module.slope(points),0,places=14)
        self.assertAlmostEqual(module.theil_sen(points),0,places=14)
        self.assertEqual(module.sign(module.slope(points)),"zero")


if __name__=="__main__":
    unittest.main()
