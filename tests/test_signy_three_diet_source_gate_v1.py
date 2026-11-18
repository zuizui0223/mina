"""Synthetic-only safeguards for BAS ZIP inventory."""
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"research/climate-penguin/work/signy_three_diet_source_gate_v1/audit.py"
spec=importlib.util.spec_from_file_location("diet_inventory",FILE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class SourceQuality(unittest.TestCase):
 def test_three_species_and_years(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d)
   for name in ("adelie","chinstrap","gentoo"):
    with zipfile.ZipFile(base/(name+".zip"),"w") as z:
     z.writestr("measurements.csv","DATE,FISH_MASS,KRILL_MASS\n1999-01-10,2,8\n2000-02-12,3,7\n")
   out=mod.run(base,base/"out")
   self.assertTrue(out["no_trophic_or_causal_claim"])
   self.assertEqual(len(out["by_species"]),3)
   x=out["by_species"]["Gentoo"]["files"][0]
   self.assertEqual(x["n_nonempty_rows"],2)
   self.assertEqual(x["candidate_year_columns"]["DATE"]["min"],1999)
   self.assertEqual(x["candidate_year_columns"]["DATE"]["max"],2000)
   self.assertFalse(x["data_grain_assigned"])
   self.assertTrue((base/"out/source_inventory.json").exists())
 def test_reject_unsafe_zip(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"bad.zip"
   with zipfile.ZipFile(f,"w") as z:z.writestr("../bad.csv","X\n2\n")
   with self.assertRaisesRegex(ValueError,"Unsafe"):mod.inspect_archive(f)
 def test_reject_duplicate_names(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"dup.zip"
   with zipfile.ZipFile(f,"w") as z:
    z.writestr("a.csv","X\n2\n")
    z.writestr("a.csv","X\n3\n")
   with self.assertRaisesRegex(ValueError,"Duplicate"):mod.inspect_archive(f)
if __name__=="__main__":
 unittest.main()
