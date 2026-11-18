import importlib.util,unittest,tempfile,os,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_diving_hatching_phase_v1/summary.py"
s=importlib.util.spec_from_file_location("phase",P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_hatching_stage_boundary(self):
  a=datetime.date(2015,12,14);c=datetime.date(2016,1,12)
  self.assertEqual(m.period(datetime.date(2016,1,11),a,c),"between-hatching")
  self.assertEqual(m.period(c,a,c),"post-Chinstrap")
 def test_original_derived_sources(self):
  d=os.getenv("DIVE_SOURCE");g=os.getenv("GPS_SOURCE");h=os.getenv("HATCH_SOURCE")
  if not all((d,g,h)):self.skipTest("Original-source CI artifacts required")
  with tempfile.TemporaryDirectory() as t:
   z=m.run(d,g,h,t)
   self.assertEqual(z["strict_2plus_tags_each_hour_bins"],171)
   self.assertEqual(z["strictly_source_matched_days"],19)
   self.assertTrue((Path(t)/"source_hatching_phase_annual_summary.csv").exists())
if __name__=="__main__":unittest.main()
