"""Original source years, source identity and paired satellite ice precision."""
import unittest,importlib.util,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"research/climate-penguin/work/climate_penguin/observed_SIC_prior_to_primary_krill_acoustic_v1.py"
s=importlib.util.spec_from_file_location("o",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
base=ROOT/"research/climate-penguin"
class OriginalObserved(unittest.TestCase):
    def input(self):
        return m.join(base/"outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv",
          base/"outputs/climate_penguin/daily_ice_locations.csv",
          base/"inputs/skaret_2023_krill_stratum_table3_reconciled_v2.csv",
          base/"inputs/IMR_annual_overall_acoustic_2011_2025_v1.csv")
    def test_ice_source_and_2013_combined_gap(self):
        rows,dist=self.input()
        self.assertEqual(len(rows),18)
        self.assertGreater(dist,0)
        self.assertLess(dist,10)
        self.assertEqual({r["survey_year"] for r in rows},set(m.YEARS))
        self.assertTrue(all(r["satellite_source_year_prior"]==r["survey_year"]-1 for r in rows))
        self.assertEqual([r["survey_year"] for r in rows if r["source_survey_ice_limited_south"]],[2015,2015])
    def test_fixed_two_radii_and_no_false_prediction(self):
        models,forward=m.analyze(self.input()[0])
        self.assertEqual(len(models),2)
        self.assertEqual(len(forward),10)
        a={r["source_inner_km"]:r for r in models}
        self.assertTrue(math.isclose(a[100]["Pearson_r"],.5191601860504838,abs_tol=1e-10))
        self.assertTrue(math.isclose(a[0]["Pearson_r"],.412306903577957,abs_tol=1e-10))
        self.assertGreater(a[100]["Holm_two_correlated_exposure_Pearson_p_descriptive"],.3)
        self.assertEqual(a[100]["rolling_origin_test_years"],[2016,2017,2018,2019,2020])
    def test_original_three_posttraining_acoustic_without_ice_not_joined(self):
        self.assertNotIn(2013,m.YEARS)
        self.assertNotIn(2023,m.YEARS)
        self.assertEqual(m.SHA["skaret"],"be611777250cd0fe1dfaffffc156cdd8301246cc")
if __name__=="__main__":unittest.main()
