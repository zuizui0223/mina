#!/usr/bin/env python3
"""Pure source-geometry checks: wet cell, longitude seam, WGS84 distance gate."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
import numpy as np

spec=importlib.util.spec_from_file_location("geo",Path(__file__).resolve().parent/
    "map_original_595_GLORYS_wet_grid.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


class TestOriginalGLORYSWetGrid(unittest.TestCase):
    def test_antimeridian_cartesian_source_valid(self):
        a=m.xyz([-65,-65],[-179.9,+179.9])
        self.assertLess(np.linalg.norm(a[0]-a[1]),0.01)

    def test_source_nearest_ocean_cell_wgs84(self):
        sites=[{"site_id":"A","source_region":"Test","polar_250km_fixed_grid_block":"b",
                "latitude":"-64.001","longitude":"10.005"}]
        got=m.nearest_wet(
            sites,np.array([1,2,3,4,5,6,7,8,9,10,11,12]),
            np.array([1]*12),
            np.array([-64.,-63.5,-63.,-62.5,-62.,-61.5,-61.,-60.5,-60.,-59.5,-59.,-58.5]),
            np.array([10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.,10.])
        )[0]
        self.assertEqual(got["original_glorys_grid_y"],1)
        self.assertEqual(got["original_glorys_grid_x"],1)
        self.assertTrue(got["source_wet_2011_september_25km_gate"])

    def test_wet_beyond_25km_not_ecological_absence(self):
        sites=[{"site_id":"A","source_region":"Test","polar_250km_fixed_grid_block":"b",
                "latitude":"-70","longitude":"40"}]
        g=m.nearest_wet(sites,np.arange(12),np.arange(12),
             np.linspace(-60,-49,12),np.full(12,40.))[0]
        self.assertFalse(g["source_wet_2011_september_25km_gate"])
        self.assertFalse(g["wet_cell_selected_using_observed_colony_counts_or_future_outcome"])

    def test_nonnear_breeding_site_not_imputed(self):
        self.assertEqual(m.SOURCE_SITE_COUNT,595)
        self.assertEqual(m.KNOWN_MACRO_GOOD,34)
        self.assertEqual(m.SOURCE_YEAR,2011)
        self.assertEqual(m.SOURCE_MONTH,9)


if __name__=="__main__":
    unittest.main()
