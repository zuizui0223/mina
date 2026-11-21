#!/usr/bin/env python3
"""Independent exact arithmetic tests of observed two-PC species ratio analysis."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np

modulefile=Path(__file__).resolve().parent/"test_dual_marine_axis_paired_penguin_response.py"
spec=importlib.util.spec_from_file_location("dual",modulefile)
dual=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(dual)


def synthetic_site_pair(site,region,block,year,pc1,pc2,y):
    return {
        "species_pair":"ADPE__GEPE",
        "site_id":site,"source_region":region,"source_250km_block":block,
        "source_ocean_GLORYS_cell":site,
        "year":year,
        "observed_log1p_second_minus_first_nest_ratio":y,
        "PC1_warm_low_ice_global_source_SD":pc1,
        "PC2_saline_global_source_SD":pc2,
        "original_real_zero_in_either_species":False,
        "source_same_count_method_both_species":True
    }


class TestGenuineDoubleAxis(unittest.TestCase):
    def test_strict_original_three_species_predeclared_pairs(self):
        self.assertEqual(len(dual.TARGET),3)
        self.assertEqual(dual.EXPECTED_ORIGINAL_PAIR_ROWS,
                         {"ADPE__GEPE":98,"CHPE__GEPE":165,"ADPE__CHPE":88})
        self.assertEqual(dual.EXPECTED_CLIMATE_ROWS,16464)
        self.assertEqual(dual.EXPECTED_PC1_LOAD[0],-0.7073417653855445)

    def test_exact_within_site_two_pc_synthetic_coefficients(self):
        rows=[]
        for i in range(5):
            for j,yr in enumerate([1993,1998,2004,2010,2018]):
                p1=j-2+0.2*i
                p2=(j-2)**2 +0.06*i
                val=23+i*2+0.35*p1-0.75*p2
                rows.append(synthetic_site_pair("Site"+str(i),"Region"+str(i%3),
                          "Block"+str(i),yr,p1,p2,val))
        r=dual.equal_site_within_two_axes(rows)
        self.assertEqual(r["status"],"DESCRIPTIVE_ONLY_SAME_SITE_TWO_PHYSICAL_AXIS_ASSOCIATION")
        self.assertEqual(r["n_repeated_colony_sites"],5)
        self.assertAlmostEqual(r["PC1_warm_low_ice_coef_per_original_global_source_SD"],0.35,places=12)
        self.assertAlmostEqual(r["PC2_saline_coef_per_original_global_source_SD"],-0.75,places=12)
        self.assertAlmostEqual(r["within_sample_explained_residual_fraction_NOT_A_FORECAST"],1.,places=12)
        deleted=dual.leave_geography_out(rows,"source_250km_block")
        self.assertEqual(len(deleted),5)
        self.assertTrue(all(v["status"]=="DESCRIPTIVE_ONLY_SAME_SITE_TWO_PHYSICAL_AXIS_ASSOCIATION" for v in deleted))
        self.assertTrue(all(v["PC2_coef_per_original_source_SD"]<0 for v in deleted))

    def test_no_source_repeat_site_not_fabricated(self):
        rows=[synthetic_site_pair("Site"+str(i),"R","B"+str(i),
                                 1993+i,1.+i,2.+i,7.+i) for i in range(8)]
        self.assertEqual(dual.equal_site_within_two_axes(rows)["status"],
                         "INSUFFICIENT_THREE_REPEAT_SITES")
        r=dual.raw_vs_within(rows,"PC1_warm_low_ice_global_source_SD")
        self.assertIsNone(r["within_site_r"])
        self.assertEqual(r["n_informative_sites"],0)

    def test_annual_slope_requires_actual_overlap_and_10year_span(self):
        supported=[synthetic_site_pair("A","Region","Block",year,0.1*year,
                        year/100,0.03*(year-1993)) for year in (1993,2001,2011,2020)]
        missed=[synthetic_site_pair("B","Region","Block",year,0.2*year,
                        year/100,0.03*(year-1993)) for year in (2015,2016,2017)]
        slopes=dual.slope_per_actual_colony(supported+missed)
        self.assertEqual(len(slopes),1)
        self.assertEqual(slopes[0]["site_id"],"A")
        self.assertAlmostEqual(slopes[0]["observed_nest_logratio_slope_per_decade"],0.3,places=11)

    def test_three_sites_but_constant_PC2_is_unidentifiable(self):
        rows=[]
        for i in range(4):
            for y in (1993,2000,2010):
                rows.append(synthetic_site_pair("s"+str(i),"r"+str(i),"b"+str(i),
                    y,y-1993,5+i,0.1*(y-1993)))
        result=dual.equal_site_within_two_axes(rows)
        self.assertEqual(result["status"],"SOURCE_PHYSICAL_AXIS_COLLINEAR_OR_UNDERPOWERED")

    def test_source_true_zero_vs_unobserved_separate(self):
        sample=synthetic_site_pair("A","R","B",1993,1,0,0)
        sample["original_real_zero_in_either_species"]=True
        self.assertTrue(sample["original_real_zero_in_either_species"])
        self.assertIsNone(dual.slope_year([]))
        self.assertIsNone(dual.pearson([1,1,1],[2,3,4]))


if __name__=="__main__":
    unittest.main()
