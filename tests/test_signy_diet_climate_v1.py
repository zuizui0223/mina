"""Synthetic tests for honest Signy diet sample-level aggregation."""
import importlib.util,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"research/climate-penguin/work/signy_diet_climate_v1/analyze.py"
spec=importlib.util.spec_from_file_location("diet_vs_ice",SCRIPT)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class FoodSourceTest(unittest.TestCase):
 def test_calendar_season(self):
  self.assertEqual(mod.season(mod.timestamp("2002-01-13")),2001)
  self.assertEqual(mod.season(mod.timestamp("13/02/2002")),2001)
  self.assertEqual(mod.season(mod.timestamp("2002-12-15")),2002)
  self.assertIsNone(mod.season(mod.timestamp("2002-08-13")))
 def test_missing_and_zero_separate(self):
  self.assertIsNone(mod.num(""))
  self.assertIsNone(mod.num("NaN"))
  self.assertEqual(mod.num("0"),0)
  self.assertIsNone(mod.num("-1"))
  self.assertEqual(mod.num("1,200"),1200)
 def test_single_stomach_is_independent_grain(self):
  x=[{"preceding_sep_sic_pct":30,"fish_share_gap_b_minus_a":.3},
     {"preceding_sep_sic_pct":40,"fish_share_gap_b_minus_a":.2}]
  self.assertIsNone(mod.corr(x,"preceding_sep_sic_pct","fish_share_gap_b_minus_a"))
if __name__=="__main__":unittest.main()
