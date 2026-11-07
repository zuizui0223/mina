import importlib.util,os,tempfile,unittest
from pathlib import Path
FILE=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_species_trophic_forward_v1/analyze.py"
sp=importlib.util.spec_from_file_location("signyforward",FILE)
a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
class TestTemporal(unittest.TestCase):
 def test_ols(self):
  b,inter=a.fit([1.,2.,3.],[3.,5.,7.])
  self.assertAlmostEqual(b,2);self.assertAlmostEqual(inter,1)
  self.assertAlmostEqual(a.pearson([1,2,3],[3,2,1]),-1)
 def test_source_checked(self):
  file=os.getenv("SIGNY_NINE_YEAR_SOURCE")
  if not file:self.skipTest("CI must generate pinned original stomach data")
  with tempfile.TemporaryDirectory() as directory:
   z=a.run(file,directory)
   self.assertEqual(z["n_original_9yr_valid_stomachs"],{"adelie":349,"chinstrap":350,"gentoo":73})
   self.assertEqual(z["n_heldout_chronological_years"],4)
   gentoo=next(x for x in z["metrics"] if x["window"]=="aug_nov_sic_pct" and x["response"]=="gentoo_fish")
   self.assertAlmostEqual(gentoo["rolling_ice_MAE"],.16800575348294394,places=10)
   self.assertAlmostEqual(gentoo["rolling_historical_mean_MAE"],.3113850020021918,places=10)
   self.assertTrue((Path(directory)/"species_four_year_chronological_predictions.csv").exists())
if __name__=="__main__":unittest.main()
