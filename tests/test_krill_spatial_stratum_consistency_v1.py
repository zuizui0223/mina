import importlib.util
import math
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"research/climate-penguin/work/climate_penguin/krill_spatial_stratum_consistency_v1.py"
s=importlib.util.spec_from_file_location("krill_spatial_stratum",P)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

class SpatialStratumTests(unittest.TestCase):
    def test_original_2013_combined_missing(self):
        source=m.acoustic(m.SOURCE)
        self.assertNotIn((2013,"South"),source)
        self.assertNotIn((2013,"Combined"),source)
        self.assertEqual(len({yr for yr,grp in source if grp=="North"}),10)
    def test_no_independent_observation_claim(self):
        self.assertEqual(m.BANDS,("0-50","50-100","100-150"))
        self.assertEqual(m.YEARS,(2011,2012,2014,2015,2016,2017,2018,2019,2020))
    def test_internal_grid_source_compatibility(self):
        f=ROOT/"build/bas_spatial_krill/breeding_result/annual_spatial_bands.csv"
        if not f.exists():
            self.skipTest("requires verified BAS original GeoTIFF workflow source")
        vals=m.model_bands(f)
        self.assertEqual(len(vals),90)
    def test_source_breeding_stage_internal(self):
        f=ROOT/"build/bas_spatial_krill/breeding_result/annual_spatial_bands.csv"
        s=ROOT/"build/signy_stage_derived/species_annual_stage_summary.csv"
        if not f.exists() or not s.exists():
            self.skipTest("requires verified original BAS source dates")
        all,contr,stages=m.compute(m.acoustic(m.SOURCE),m.model_bands(f),s)
        self.assertTrue(m.verify(all,contr,stages))
        self.assertEqual(next(x["n_distinct_calendar_survey_years"] for x in contr if x["scope"]=="all_years"),9)
        self.assertEqual({x["n_calendar_years"] for x in stages},{8})
    def test_centered_correlation(self):
        self.assertAlmostEqual(m.correlation([1,2,3,4],[2,4,6,8]),1.0)

if __name__=="__main__":
    unittest.main()
