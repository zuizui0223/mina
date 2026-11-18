"""Checks external Palmer isotope source and nearshore spatial pseudoreplication."""
import importlib.util,os,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/"research/climate-penguin/work/palmer_original_isotope_niche_v1/analyze.py"
s=importlib.util.spec_from_file_location("palmer_iso",F);a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class OriginalIsotopes(unittest.TestCase):
 def test_spatial_support(self):
  self.assertAlmostEqual(a.dist(a.ISLANDS["Biscoe"],(-64.8114,-63.7775)),1.3674135476,places=6)
  self.assertAlmostEqual(a.diskoverlap(0),1.)
  self.assertEqual(a.diskoverlap(201),0.)
 def test_bad_source_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"bad.csv";p.write_text("no",encoding="utf-8")
   with self.assertRaisesRegex(ValueError,"Frozen source blob"):a.run(p,Path(d)/"out")
 def test_real_source(self):
  f=os.environ.get("PALMER_RAW_SOURCE")
  if not f:self.skipTest("CI downloads pinned public original source")
  with tempfile.TemporaryDirectory() as d:
   x=a.run(f,Path(d))
   self.assertEqual((x["n_original_records"],x["n_two_isotopes"],x["n_two_isotopes_and_sex"]),(344,330,324))
   self.assertEqual((x["n_species_island_year"],x["n_same_island_year_pairs"]),(15,6))
   self.assertEqual(x["marine_proxy_by_island"],{"Biscoe":"BISC","Dream":"LITC","Torgersen":"LITC"})
   self.assertFalse(x["signy_ice_to_stomach_fish_gap_independently_replicated"])
   self.assertTrue((Path(d)/"isotope_within_island_pair_year.csv").exists())
if __name__=="__main__":unittest.main()
