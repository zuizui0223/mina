import importlib.util,os,tempfile,unittest
from pathlib import Path
S=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_chinstrap_arrival_multiaxis_v1/analyze.py"
sp=importlib.util.spec_from_file_location("arrival_multiaxis",S)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class TestSourceBound(unittest.TestCase):
 def test_365_day_index(self):
  self.assertEqual(m.doy_no_leap("2004-11-01"),m.doy_no_leap("2005-11-01"))
  self.assertEqual(m.doy_no_leap("2016-11-19"),m.doy_no_leap("2017-11-19"))
 def test_partial_first_date(self):
  self.assertAlmostEqual(m.corr([1.,2.,3.],[3.,2.,1.]),-1.)
  self.assertIsNone(m.partial([1,2,3],[3,2,1],[1,1,1]))
 def test_original_source(self):
  a=os.getenv("SIGNY_ARRIVAL_EFFORT");d=os.getenv("SIGNY_DIET_DERIVED");s=os.getenv("SIGNY_STAGE_DERIVED")
  if not a or not d or not s:self.skipTest("BAS original seven archives rebuilt by CI")
  with tempfile.TemporaryDirectory() as tmp:
   r=m.run(a,d,s,tmp)
   self.assertEqual(r["n_same_island_years_with_diet_and_recorded_chick_stage"],13)
   self.assertEqual(len(r["original_calendar_years_with_at_least_four_sessions"]),16)
   self.assertTrue((Path(tmp)/"same_island_year_arrival_effort_diet_chick.csv").exists())
   m1=r["metrics"][0]
   self.assertAlmostEqual(m1["correlation_with_observed_weighted_chinstrap_count_date"],.5269795199523822,places=9)
   self.assertAlmostEqual(m1["association_conditioned_on_first_available_survey_date"],.34667888839563654,places=9)
if __name__=="__main__":unittest.main()
