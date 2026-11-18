"""Check source-bound TDR/GPS pilot independent of raw protected data."""
import importlib.util,unittest,datetime
from pathlib import Path
F=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_three_tdr_gps_pilot_v1/analyze.py"
sp=importlib.util.spec_from_file_location("tdr3pil",F);a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
class Tests(unittest.TestCase):
 def test_invalid_source_baseline_QA_threshold(self):
  with self.assertRaisesRegex(ValueError,"max baseline drift"):
   a.run("/no-source","/no-output",999,-0.1)
 def test_invalid_source_tag_cap_stops_before_loading_archives(self):
  with self.assertRaisesRegex(ValueError,"Source tag cap"):
   a.select_source_tags("/does-not-exist",0)
 def test_spatial_and_clock_invariants(self):
  self.assertEqual(a.time_hour(1700001000),"2023-11-14T22:00Z")
  self.assertAlmostEqual(a.sep_km((0,0),(0,0)),0)
  self.assertEqual(a.jaccard({(1,1)},set()),0.)
  self.assertEqual(a.jaccard(set(),set()),None)
  self.assertEqual(a.percentile([1,2,3,4],.25),1.75)
 def test_original_source_can_run(self):
  import os,tempfile
  path=os.environ.get("SIGNY_TDR_GPS_SOURCE")
  if not path:self.skipTest("Six BAS original ZIPs required")
  with tempfile.TemporaryDirectory() as t:
   res=a.run(path,t)
   self.assertEqual(res["n_years"],2)
   self.assertEqual(res["original_gps_three_species_SHA256"],a.gps.TRACK_SHA)
   self.assertGreater(res["n_source_selected_tags"],6)
   self.assertTrue((Path(t)/"by_year_summary.csv").exists())
if __name__=="__main__":unittest.main()
