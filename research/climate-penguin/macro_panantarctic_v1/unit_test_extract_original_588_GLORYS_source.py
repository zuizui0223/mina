#!/usr/bin/env python3
"""Synthetic source-grain and provenance tests for continental GLORYS extraction."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec=importlib.util.spec_from_file_location("glorys",
    Path(__file__).resolve().parent/"extract_original_588_GLORYS_1993_2020.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


class TestSourceGLORYSOriginal(unittest.TestCase):
    def test_full_historical_time_horizon_fixed(self):
        self.assertEqual(len(m.YEARS),28)
        self.assertEqual((m.YEARS.start,m.YEARS.stop),(1993,2021))
        self.assertEqual(m.MONTHS,(8,9,10,11))
        self.assertEqual(len(m.YEARS)*len(m.MONTHS),112)

    def test_legacy_source_34_sites_cannot_be_replaced(self):
        self.assertEqual(m.EXPECTED_OLD_VALID_SITES,34)
        self.assertLessEqual(m.MAX_ORIGINAL_OVERLAP_DIFFERENCE,1e-5)
        self.assertEqual(len(m.EXPECTED_OLD_GIT_BLOBS),3)

    def test_nearest_wet_fixed_25km(self):
        self.assertEqual(m.MAX_SOURCE_DISTANCE_KM,25.0)
        self.assertEqual(m.EXPECTED_SITES,595)

    def test_original_product_and_coordinates_pinned(self):
        self.assertIn("GLOBAL_MULTIYEAR_PHY_001_030",m.EXPECTED_SOURCE)
        self.assertIn("202311",m.EXPECTED_SOURCE)
        self.assertTrue(all(len(v)==40 for v in m.EXPECTED_OLD_GIT_BLOBS.values()))

if __name__=="__main__":
    unittest.main()
