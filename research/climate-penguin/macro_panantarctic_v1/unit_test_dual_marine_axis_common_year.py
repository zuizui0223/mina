#!/usr/bin/env python3
"""Source-free test of site+year weighted residualization and missingness semantics."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np

spec=importlib.util.spec_from_file_location("calendar",Path(__file__).resolve().parent/
    "audit_dual_marine_axis_calendar_year.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


def row(site,region,block,year,pc1,pc2,y):
    return {
        "site_id":site,"source_region":region,"source_250km_block":block,
        "year":year,
        "PC1_warm_low_ice_global_source_SD":pc1,
        "PC2_saline_global_source_SD":pc2,
        "observed_log1p_second_minus_first_nest_ratio":y,
    }


class TestSourceTrueYearFWL(unittest.TestCase):
    def test_exact_within_both_site_and_calendar_year_controls(self):
        rows=[]
        years=[1993,1997,2001,2005,2010,2018,2020]
        for i in range(5):
            for j,year in enumerate(years):
                pc1=np.sin((i+1)*(j+2)*.73)+.2*i+.1*j
                pc2=np.cos((i+2)*(j+1)*.39)+.3*i-.1*j
                y=5*i+0.8*j+0.65*pc1-0.29*pc2
                rows.append(row(f"S{i}",f"R{i%3}",f"B{i}",year,pc1,pc2,y))
        fit=m.FWL_twice(rows)
        self.assertEqual(fit["status"],"POST_RESULT_DESCRIPTIVE_SITE_AND_YEAR_FWL_TWO_SOURCE_MARINE_PCS")
        self.assertEqual(fit["n_repeated_original_colony_sites"],5)
        self.assertEqual(fit["n_actual_source_years"],len(years))
        self.assertAlmostEqual(fit["PC1_warm_low_ice_coef_per_original_global_source_SD"],.65,places=11)
        self.assertAlmostEqual(fit["PC2_saline_coef_per_original_global_source_SD"],-.29,places=11)
        self.assertAlmostEqual(fit["source_year_and_site_partialled_in_sample_R2_NOT_FORECAST"],1.,places=11)
        self.assertGreaterEqual(fit["effective_unclustered_residual_degrees_of_freedom_NOT_INDEPENDENT"],5)
        region=m.geographic_year_FWL_sensitivity(rows,fit,"source_region")
        block=m.geographic_year_FWL_sensitivity(rows,fit,"source_250km_block")
        self.assertTrue(region["PC2"]["every_supported_omission_preserves_original_sign"])
        self.assertTrue(block["PC2"]["every_supported_omission_preserves_original_sign"])

    def test_unobserved_years_not_counted(self):
        rows=[row(f"S{i}","R","B",1993+i,i,i,5+i) for i in range(8)]
        result=m.FWL_twice(rows)
        self.assertEqual(result["status"],"SOURCE_TOO_FEW_REPEATED_COCENSUS_SITES_OR_YEARS")
        self.assertEqual(result["n_repeated_siteyear_rows_used"],0)

    def test_disconnected_site_year_components_recorded(self):
        rows=[row(site,"R","B",year,1,2,3) for site,years in [
            ("S1",(1993,2000)),("S2",(1993,2000)),
            ("S3",(2010,2011)),("S4",(2010,2011))] for year in years]
        d=m.source_year_graph_components(rows)
        self.assertEqual(d["n_components"],2)
        self.assertEqual(d["n_components_with_2plus_original_census_sites"],2)
        self.assertEqual(d["n_years_observed_from_2plus_original_source_colonies"],4)

    def test_sign_not_significance_test(self):
        self.assertEqual(m.sign(None),"UNIDENTIFIED")
        self.assertEqual(m.sign(-.2),"NEGATIVE")
        self.assertEqual(m.sign(.2),"POSITIVE")
        self.assertEqual(m.sign(1e-12),"NEAR_ZERO")

    def test_original_three_co_count_source_coefficients_pinned(self):
        self.assertEqual(len(m.SOURCE_EXPECTED_BASELINE_COEF),3)
        self.assertLess(m.SOURCE_EXPECTED_BASELINE_COEF["CHPE__GEPE"][1],0)
        self.assertEqual(sum(m.EXPECTED_ORIGINAL_PAIR_ROWS.values()),351)


if __name__=="__main__":
    unittest.main()
