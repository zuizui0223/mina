import importlib.util,unittest,os,tempfile
from pathlib import Path
SRC=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_hatching_diet_chick_v1/join.py"
spec=importlib.util.spec_from_file_location("joined",SRC);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class TestOriginalJoin(unittest.TestCase):
 def test_abstract(self):
  self.assertAlmostEqual(a.pearson([1,2,3],[3,2,1]),-1)
  self.assertEqual(len(a.EXPECTED),14)
 def test_publisher_source(self):
  hh=os.getenv("SIGNY_HATCH_DATA");dd=os.getenv("SIGNY_DIET_DATA");ss=os.getenv("SIGNY_STAGE_DATA")
  if not all((hh,dd,ss)):self.skipTest("Requires all 7 official BAS archives regenerated in CI")
  with tempfile.TemporaryDirectory() as t:
   r=a.run(hh,dd,ss,t)
   self.assertEqual(r["n_matched_years"],14)
   self.assertEqual(r["n_matched_species_years"],28)
   self.assertEqual(r["n_diet_median_after_mean_hatching"],28)
   self.assertGreaterEqual(r["n_same_stage_within_7days"],12)
   self.assertAlmostEqual(r["mean_adelie_stomach_days_after_mean_hatching"],32.142857,delta=.7)
   self.assertAlmostEqual(r["mean_chinstrap_stomach_days_after_mean_hatching"],31.214286,delta=.7)
   self.assertTrue((Path(t)/"fourteen_hatching_food_chicks_years.csv").exists())
if __name__=="__main__":unittest.main()
