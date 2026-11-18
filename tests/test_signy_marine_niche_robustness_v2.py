"""Check source-derived Signy cross-species marine-niche result."""
from __future__ import annotations
import importlib.util,os,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
F=HERE/"research/climate-penguin/work/signy_marine_niche_robustness_v2/analyze.py"
spec=importlib.util.spec_from_file_location("signy_marine_v2",F)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestMarineNiche(unittest.TestCase):
 def test_exact_three_year_permutation_generic(self):
  self.assertRaises(ValueError,m.exact2,[1,2,3],[3,1,2],[1,2,3])
  self.assertAlmostEqual(m.corr([1,2,3],[3,2,1]),-1)
  self.assertEqual(len(m.daymatch([{"date":"2002-01-07"},{"date":"2002-01-21"},{"date":"2002-01-23"}],[{"date":"2002-01-14"}],7)),2)
 def test_vetted_original_data(self):
  sourced=os.getenv("SIGNY_DIET_DERIVED_DIR")
  if not sourced:self.skipTest("Requires BAS source-derived fixture from CI")
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   r=m.run(sourced,Path(tmp),bootstrap=20)
   self.assertEqual(r["n_years"],9)
   self.assertEqual(r["positive_fish_gap_years"],8)
   self.assertEqual(r["n_stomachs_in_all_three_species_years"],{"Adelie":349,"Chinstrap":350,"Gentoo":73})
   self.assertAlmostEqual(r["correlation"]["aug_nov"]["pearson_r"],0.7838587732429944,places=10)
   self.assertEqual(r["exact_two_window_permutation"]["max_two_extreme"],7944)
   self.assertEqual(r["date_matched"]["7day_adelie_gentoo"]["n_years"],8)
   self.assertTrue((Path(tmp)/"nine_year_fish_gap.csv").exists())
if __name__=="__main__":unittest.main()
