"""Fixed cohort and source-hash guards for original Signy cross-axis audit."""
import importlib.util,os,unittest,tempfile
from pathlib import Path
S=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_trophic_productivity_ice_v1/analyze.py"
sp=importlib.util.spec_from_file_location("signy_trophic_productivity_v1",S)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class Test(unittest.TestCase):
 def test_partial_correlation(self):
  self.assertAlmostEqual(m.corr([1,2,3],[3,2,1]),-1)
  self.assertIsNone(m.corr([1,1,1],[2,3,4]))
  self.assertIsNone(m.partial([1,2,3],[3,2,1],[1,1,1]))
 def test_exact_small_n_gate(self):
  with self.assertRaisesRegex(ValueError,"exact 9"):
   m.exact_year_permutation([{"sep_sic_pct":1}], [{"Adelie":1}])
 def test_publisher_original(self):
  dd=os.environ.get("SIGNY_SOURCE_DIET");sd=os.environ.get("SIGNY_SOURCE_STAGE")
  if not dd or not sd:self.skipTest("Original publisher ZIPs run on CI")
  with tempfile.TemporaryDirectory() as d:
   v=m.run(dd,sd,d)
   self.assertEqual(v["n_temporal_replications"],9)
   self.assertEqual(v["n_independent_geographic_islands"],1)
   p=v["exact_joint_9_year_permutations"]
   self.assertEqual(p["n_exact_permutations"],362880)
   self.assertAlmostEqual(p["joint_six_comparison_fraction"],.08140156525573192,places=10)
   self.assertEqual((Path(d)/"strict_nine_years_three_species.csv").exists(),True)
   a=next(x for x in v["metrics"] if x["species"]=="Gentoo" and x["ice_window"]=="sep_sic_pct")
   self.assertAlmostEqual(a["r_ice_fish"],.7141071407852608,places=10)
   self.assertAlmostEqual(a["r_ice_recorded_chicks"],-.7041437525127027,places=10)
   self.assertAlmostEqual(a["r_fish_recorded_chicks_partial_ice"],.15367379691876412,places=10)
if __name__=="__main__":unittest.main()
