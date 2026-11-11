#!/usr/bin/env python3
"""Independent source-free tests of Antarctic physical region-year synchrony."""
from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

import numpy as np

spec=importlib.util.spec_from_file_location("climate",Path(__file__).resolve().parent/
    "analyze_original_18region_marine_time_synchrony.py")
a=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(a)


class RegionalMarineSourceSynchronyTests(unittest.TestCase):
    def test_perfectly_synchronous_climate_region_years(self):
        x=np.linspace(0,3*np.pi,28)
        base=np.sin(x)+np.cos(.4*x)
        m=np.column_stack([base*scale+different
                           for scale,different in [(1,0),(.2,3),(2,-4),
                                                   (3,2),(.5,8),(.7,-2)]])
        z=a.anomaly_standardized(m)
        out,common=a.synchrony_metrics(z)
        self.assertAlmostEqual(out["mean_region_temporal_anomaly_common_year_variance_fraction"],1,places=12)
        self.assertAlmostEqual(out["first_source_temporal_EOF_explained_fraction"],1,places=12)
        self.assertEqual(out["n_regions_temporal_EOF1_positive_loading"],6)
        self.assertEqual(out["n_regions_temporal_EOF1_negative_loading"],0)
        self.assertAlmostEqual(out["regional_anomaly_correlation_median"],1,places=12)
        self.assertEqual(len(common),28)

    def test_opposite_regions_are_EOF_not_all_direction_synchrony(self):
        base=np.sin(np.linspace(0,3*np.pi,28))
        m=np.column_stack([base]*3+[-base]*3)
        z=a.anomaly_standardized(m)
        result,common=a.synchrony_metrics(z)
        self.assertAlmostEqual(result["mean_region_temporal_anomaly_common_year_variance_fraction"],0.,places=12)
        self.assertAlmostEqual(result["first_source_temporal_EOF_explained_fraction"],1.,places=12)
        self.assertEqual(result["n_regions_temporal_EOF1_positive_loading"],3)
        self.assertEqual(result["n_regions_temporal_EOF1_negative_loading"],3)
        self.assertAlmostEqual(float(np.max(np.abs(common))),0.,places=12)
        self.assertEqual(result["n_positive_region_anomaly_correlations"],6)
        self.assertEqual(result["n_negative_region_anomaly_correlations"],9)

    def test_original_source_phase_offset_reference_is_deterministic(self):
        base=np.cos(np.linspace(0,2*np.pi,28))
        matrix=np.column_stack([base]*5)
        z=a.anomaly_standardized(matrix)
        first=a.circular_phase_reference(z,seed=20261112,n=60)
        second=a.circular_phase_reference(z,seed=20261112,n=60)
        self.assertEqual(first,second)
        self.assertLess(first["common_year_fraction_reference"]["offset_median"],.7)
        self.assertAlmostEqual(first["common_year_fraction_reference"]["observed"],1.,places=12)
        self.assertTrue(first["not_pvalues_and_not_a_prospective_causal_significance_test"])

    def test_source_region_period_peak_with_8_10_10_year_calendar(self):
        source={}
        region={"R0":{"n_source_colonies":5,"n_original_250km_blocks":2,
                      "n_unique_wet_GLORYS_cells":3,
                      "geographically_supported_region":True}}
        for year in a.YEARS:
            mid=3. if 2001<=year<=2010 else 1. if year<=2000 else 2.
            source["R0",year]={
                "site_equal_PC1":mid,
                "site_equal_PC2":year/500,
                "wet_cell_equal_PC1":mid/2,
                "wet_cell_equal_PC2":year/800
            }
        period=a.period_regime_support(source,region,"site_equal","PC1")[0]
        self.assertTrue(period["original_midperiod_mean_strict_peak"])
        self.assertFalse(period["original_midperiod_mean_strict_trough"])
        self.assertAlmostEqual(period["mean_1993_2000_8yr"],1.)
        self.assertAlmostEqual(period["mean_2001_2010_10yr"],3.)
        self.assertAlmostEqual(period["mean_2011_2020_10yr"],2.)

    def test_full_source_colony_weighted_vs_unique_marine_grid_cell_weight(self):
        # 588 original known sites in 18 source regions, all with 28 real source
        # years. A single region contains 547 site IDs but only TWO wet cells:
        # test that reanalysis cell mean is not accidentally site-number weighted.
        yearly=[]
        physical={}
        for ri in range(18):
            n=547 if ri==0 else 3 if ri<13 else 1
            for j in range(n):
                site=f"R{ri:02d}_s{j:03d}"
                cell=1 if j==n-1 and n>1 else 0
                block="B1" if j==n-1 and n>1 else "B0"
                for year in a.YEARS:
                    value=(10. if cell==1 else 0.)+.01*(year-1993)
                    row={
                        "site_id":site,"year":year,
                        "source_region":f"R{ri:02d}",
                        "source_250km_block":f"R{ri:02d}_{block}",
                        "GLORYS_cell_y":ri,
                        "GLORYS_cell_x":cell,
                        "mean_source_SIC_pp":40.+value,
                        "mean_GLORYS_salinity":30.+.1*value,
                        "mean_GLORYS_thetao_C":-1.+.2*value
                    }
                    yearly.append(row)
                    physical[site,year]={
                        "PC1_warm_low_ice_original_score":value,
                        "PC2_saline_original_score":value*.25,
                        "source_region":row["source_region"],
                        "GLORYS_cell":f"{ri}:{cell}"
                    }
        self.assertEqual(len(yearly),588*28)
        aggregated,geography,report=a.aggregate_regional(yearly,physical)
        self.assertEqual(len(aggregated),18*28)
        self.assertEqual(report["n_real_original_sites"],588)
        self.assertEqual(report["n_geographically_supported_source_regions"],13)
        r=aggregated["R00",1993]
        self.assertGreater(r["wet_cell_equal_PC1"]-r["site_equal_PC1"],4.)
        self.assertEqual(r["n_wet_cells"],2)
        old=[]
        for (region,year),z in aggregated.items():
            old.append({
                "source_region":region,"year":str(year),
                "mean_marine_PC1_fixed_original_global_loadings":str(z["site_equal_PC1"]),
                "mean_source_SIC_pp":str(z["site_equal_SIC"]),
                "mean_GLORYS_salinity":str(z["site_equal_salinity"]),
                "mean_GLORYS_thetao_C":str(z["site_equal_thetao"]),
                "n_source_colonies":str(z["n_colonies"]),
                "n_unique_ocean_GLORYS_cells":str(z["n_wet_cells"])
            })
        self.assertEqual(
            a.verify_original_region_year(old,aggregated)[
                "n_original_source_region_years_exactly_reproduced"],504)
        old[0]["mean_source_SIC_pp"]="999"
        with self.assertRaises(ValueError):
            a.verify_original_region_year(old,aggregated)


if __name__=="__main__":
    unittest.main()
