#!/usr/bin/env python3
"""Synthetic QA: exact count-year SIC, missing sea ice and geographic pairing."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("near",Path(__file__).resolve().parent/
    "audit_neighbor_colony_vs_local_ice.py")
near=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(near)


class TestNeighborIce(unittest.TestCase):
    def test_distance_ross_island_not_pseudotravel(self):
        self.assertEqual(near.distance_km(-77,-166,-77,-166),0.)
        self.assertGreater(near.distance_km(-77,-166,-77,-165),0)
        self.assertLess(near.distance_km(-77,-166,-77,-165),100)

    def test_original_ice_slope_arithmetic(self):
        v=[(1991,5),(1996,10),(2001,15),(2010,24),(2020,34)]
        self.assertAlmostEqual(near.linear_value_slope(v),10.)
        self.assertIsNone(near.linear_value_slope([(1991,1),(1996,2)]))

    def test_ice_only_on_common_counted_years(self):
        years=[1991,1995,2000,2005,2010,2020]
        pair={"status":"EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED","years":years}
        ice={}
        for year in range(1991,2021):
            ice["A",year]=40+(year-1991)*.5
            ice["B",year]=42+(year-1991)*.5
        r=near.pair_climate(pair,ice,"A","B")
        self.assertEqual(r["n_paired_valid_climate_years"],6)
        self.assertAlmostEqual(r["mean_absolute_site_sic_difference_pp"],2)
        self.assertAlmostEqual(r["site_minus_peer_SIC_slope_difference_pp_per_decade"],0,places=10)
        self.assertAlmostEqual(r["focal_SIC_slope_pp_per_decade_on_exact_count_years"],5,places=10)

    def test_missing_source_sea_ice_not_recast_zero(self):
        years=[1991,1995,2000,2005,2010,2020]
        pair={"status":"EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED","years":years}
        ice={("A",y):0 for y in years}
        ice.update({("B",y):10 for y in years})
        del ice["B",2020]
        r=near.pair_climate(pair,ice,"A","B")
        self.assertEqual(r["status"],"SOURCE_MISSING_AUG_NOV_SIC_ON_ONE_OR_MORE_EXACT_SHARED_COUNT_YEARS")
        self.assertEqual(r["n_paired_valid_climate_years"],5)

    def test_true_zero_ice_not_source_missing(self):
        years=[1991,1995,2000,2005,2010,2020]
        pair={"status":"EXACT_SOURCE_COMMON_YEAR_PAIR_ESTIMATED","years":years}
        ice={("A",y):0 for y in years}
        ice.update({("B",y):0 for y in years})
        r=near.pair_climate(pair,ice,"A","B")
        self.assertEqual(r["status"],"EXACT_ORIGINAL_MATCHED_COUNT_YEAR_LOCAL_MARINE_SIC")
        self.assertAlmostEqual(r["mean_absolute_site_sic_difference_pp"],0,places=12)


if __name__=="__main__":
    unittest.main()
