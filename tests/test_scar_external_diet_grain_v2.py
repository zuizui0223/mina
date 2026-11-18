import importlib.util,unittest,datetime
from pathlib import Path
f=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/scar_external_diet_grain_v2/inspect.py"
spec=importlib.util.spec_from_file_location("scargrain",f);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestRawSeason(unittest.TestCase):
 def test_breeding_season(self):
  self.assertEqual(m.season_start("2008-01-01","2008-02-29"),2007)
  self.assertEqual(m.season_start("2007-12-15","2008-02-02"),2007)
  self.assertEqual(m.season_start("2008-11-01","2008-12-31"),2008)
  self.assertIsNone(m.season_start("2008-08-01","2008-09-01"))
  self.assertIsNone(m.season_start("2007-12-01","2009-02-01"))
if __name__=="__main__":unittest.main()
