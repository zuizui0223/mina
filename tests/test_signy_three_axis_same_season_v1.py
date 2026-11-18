"""Original same-camera plus BAS diet/stage three-axis alignment tests."""
import importlib.util,unittest,os,tempfile
from pathlib import Path
F=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_three_axis_same_season_v1/analyze.py"
spec=importlib.util.spec_from_file_location("signy3axis",F)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestThreeAxis(unittest.TestCase):
 def test_exact_24(self):
  a=m.exact_perm([70.9,60.3,23.6,71.4],[18,29,29,19])
  self.assertEqual(a["n_permutations"],24)
  self.assertEqual(a["extreme"],6)
  self.assertAlmostEqual(a["two_sided"],.25)
  self.assertAlmostEqual(a["r"],-.7451417026286243)
 def test_original_same_island_year(self):
  d=os.getenv("SIGNY_ORIGINAL_DIET_DERIVED");s=os.getenv("SIGNY_ORIGINAL_STAGE_DERIVED")
  if not d or not s:self.skipTest("Six SHA-pinned original BAS ZIPs required")
  with tempfile.TemporaryDirectory() as tmp:
   z=m.run(d,s,tmp)
   self.assertEqual(z["all_Signy_three_axis_breeding_season_start_years"],[2016,2017,2018,2019])
   self.assertEqual(z["n_three_axis_years"],4)
   d2={a["comparison"]:a for a in z["metrics"]}
   self.assertEqual(d2["camera_timing_vs_fish_share_gap"]["n_permutations"],24)
   self.assertAlmostEqual(d2["camera_timing_vs_fish_share_gap"]["r"],.614968,places=4)
   self.assertAlmostEqual(d2["fish_share_gap_vs_early_chick_gap"]["r"],-.90073,places=4)
   self.assertEqual(d2["camera_timing_vs_early_chick_gap"]["extreme"],18)
   self.assertTrue((Path(tmp)/"source_matched_four_breeding_seasons.csv").exists())
if __name__=="__main__":
 unittest.main()
