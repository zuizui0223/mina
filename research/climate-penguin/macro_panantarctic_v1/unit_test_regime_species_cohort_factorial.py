#!/usr/bin/env python3
"""Pure PCA score projection and actual co-census source-case regression QA."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path
import numpy as np
import pandas as pd

spec=importlib.util.spec_from_file_location("factor",
    Path(__file__).resolve().parent/"diagnose_regime_species_source_cohort_factorial.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


class TestRegimeSourceFactorial(unittest.TestCase):
    def test_pca_fit_is_physical_only_then_score_frozen_for_source_site_years(self):
        data=np.asarray([[20,33.,-2.],[40,34.,-1.],[60,35.,0.],[80,36.,1.]])
        fit=m.pca(data)
        d=pd.DataFrame(data,columns=list(m.COLUMNS))
        score=m.marine_PC1_transformed(d,fit)
        self.assertTrue(np.allclose(score,fit["scores"][:,0]))
        self.assertAlmostEqual(float(np.mean(score)),0.,places=12)

    def test_common_year_site_centered_source_relation_not_unknown_absence(self):
        rows=[]
        for i in range(3):
            for year in (2011,2015,2020):
                q=year-2011
                rows.append({"site_id":f"site{i}",
                    "source_region":f"region{i}",
                    "source_250km_block":f"block{i}",
                    "frozen_projected_PC1":i*3.0+q/9,
                    "log1p_B_minus_A_observed_nests":i*5.0+q/3})
        v=m.source_co_census_correlation(pd.DataFrame(rows))
        self.assertEqual(v["n_true_same_colony_species_year_pairs"],9)
        self.assertEqual(v["n_original_colony_ids"],3)
        self.assertEqual(v["n_original_250km_blocks"],3)
        self.assertAlmostEqual(v["within_site_r"],1.,places=12)

    def test_no_pseudoreplicate_from_single_same_year(self):
        rows=pd.DataFrame([{"site_id":"A",
            "source_region":"r","source_250km_block":"b",
            "frozen_projected_PC1":1.,
            "log1p_B_minus_A_observed_nests":2.}])
        self.assertIsNone(m.source_co_census_correlation(rows)["within_site_r"])

if __name__=="__main__":
    unittest.main()
