#!/usr/bin/env python3
"""Non-overlapping original ocean cell SIC unit tests; no biological inference."""
from __future__ import annotations
import importlib.util
import math
import unittest
from pathlib import Path
import numpy as np

spec=importlib.util.spec_from_file_location("excl",Path(__file__).resolve().parent/
    "extract_exclusive_ocean_original_SIC_120months.py")
excl=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(excl)


class TestOriginalExclusiveSIC(unittest.TestCase):
    def test_disjoint_ocean_reference_exact_original_mean(self):
        sic=np.array([0,10,20,30,40,50,60,70,80],dtype=float)
        valid=np.array([True]*9)
        a=np.array([1,2,3],dtype=np.int32)
        b=np.array([6,7,8],dtype=np.int32)
        self.assertEqual(excl.subset_source_mean(sic,valid,a),20)
        self.assertEqual(excl.subset_source_mean(sic,valid,b),70)

    def test_source_min_three_and_80pct_quality(self):
        sic=np.array([0,10,20,30,40,50],dtype=float)
        bad=np.array([True,True,False,False,True,True])
        self.assertIsNone(excl.subset_source_mean(sic,bad,np.array([0,1,2,3,4])))
        good=np.array([True,True,True,True,False,True])
        self.assertEqual(excl.subset_source_mean(sic,good,np.array([0,1,2,3,4])),15.)
        self.assertIsNone(excl.subset_source_mean(sic,good,np.array([0,1])))
        allbad=np.array([False]*6)
        self.assertIsNone(excl.subset_source_mean(sic,allbad,np.array([0,1,2])))

    def test_real_zero_sic_not_missing(self):
        sic=np.zeros(10)
        valid=np.ones(10,dtype=bool)
        self.assertEqual(excl.subset_source_mean(sic,valid,np.array([3,4,5])),0.)

    def test_full_aug_nov_original_year_only(self):
        year=2008
        entries={(year,m):{"l":float(m),"r":float(2*m),"s":10.0}
                 for m in (8,9,10,11)}
        r=excl.annual_four_month_means(entries,year)
        self.assertEqual(r["left"],9.5)
        self.assertEqual(r["right"],19.0)
        self.assertEqual(r["shared"],10.0)
        self.assertIsNone(excl.annual_four_month_means(entries,2012))
        entries[year,10]["r"]=None
        self.assertIsNone(excl.annual_four_month_means(entries,year))

    def test_means_from_partial_source_months_refused(self):
        sic=np.array([1,2,3,4,5],dtype=float)
        valid=np.array([True,False,True,False,True])
        self.assertIsNone(excl.subset_source_mean(sic,valid,np.array([0,1,2,3,4])))

    def test_original_source_sha_manifest_period_has_120_events(self):
        dates=[(year,month) for year in excl.YEARS for month in excl.MONTHS]
        self.assertEqual(len(dates),120)
        self.assertEqual(len(set(dates)),120)
        self.assertEqual(dates[0],(1991,8))
        self.assertEqual(dates[-1],(2020,11))


if __name__=="__main__":
    unittest.main()
