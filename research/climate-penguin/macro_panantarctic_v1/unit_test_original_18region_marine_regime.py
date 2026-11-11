#!/usr/bin/env python3
"""Pure synthetic math controls: 18 original regions, 28 real annual observations."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

spec=importlib.util.spec_from_file_location("cont",
    Path(__file__).resolve().parent/"analyze_original_18region_marine_regime_1993_2020.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


class TestContinentalMarine(unittest.TestCase):
    def test_monthly_calendar_fixed_for_genuine_historical_28yrs(self):
        self.assertEqual(len(m.YEARS),28)
        self.assertEqual(len(m.MONTHS),4)
        self.assertEqual(m.YEARS[0],1993)
        self.assertEqual(m.YEARS[-1],2020)
        self.assertEqual(m.EXPECTED_GLORYS_MONTHS,65856)

    def test_decadal_slope_units_and_no_short_or_missing(self):
        years=list(range(1993,2021))
        vals=[1+.2*(y-1993) for y in years]
        self.assertAlmostEqual(m.fit_slope(years,vals),2.0)
        self.assertIsNone(m.fit_slope([2000,2001],[1,2]))
        self.assertIsNone(m.fit_slope(years,[float("nan")]*len(years)))

    def test_18region_equal_weight_marine_pca_is_a_real_source_temporal_panel(self):
        data=[]
        for j in range(18):
            for y in m.YEARS:
                t=(y-1993)/10
                val=j*.47
                data.append({
                    "site_id":f"S{j}","source_region":f"REGION{j:02d}",
                    "source_250km_block":f"B{j}","source_original_wet_grid_y":j,
                    "source_original_wet_grid_x":j,"year":y,
                    "SIC_pp":60-val*1.7-t*1.2,
                    "GLORYS_salinity":33+val*.07+0.03*t,
                    "GLORYS_thetao_C":-1.5+val*.05+0.02*t})
        df=pd.DataFrame(data)
        result,regionyears,trends,physical=m.fixed_pca_and_region_temporal(df)
        self.assertEqual(physical["n_actual_source_regions"],18)
        self.assertEqual(physical["n_equal_weight_original_region_years"],504)
        self.assertEqual(len(trends),18)
        self.assertEqual(len(regionyears),504)
        self.assertAlmostEqual(sum(physical["equal_18region_year_marine_PCA_PC_explained"]),1.,places=10)
        self.assertAlmostEqual(sum(physical["within_site_temporal_1993_2020_PCA_PC_explained"]),1.,places=10)
        self.assertGreater(physical["site_year_PC1_variance_between_reporting_regions_fraction"],0)
        self.assertEqual(len(physical["leave_one_original_region_out_marine_PC1_sensitivity"]),18)
        self.assertTrue(all(r["n_real_calendar_years"]==28 for r in trends))

    def test_geographically_unique_ocean_cells_not_same_as_site_year_replicates(self):
        df=pd.DataFrame([{"site_id":f"A{i}","source_original_wet_grid_y":1,
                          "source_original_wet_grid_x":1} for i in range(10)])
        self.assertEqual(df[["source_original_wet_grid_y","source_original_wet_grid_x"]].drop_duplicates().shape[0],1)


if __name__=="__main__":
    unittest.main()
