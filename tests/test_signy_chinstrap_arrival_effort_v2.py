import importlib.util,unittest
from pathlib import Path
F=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_chinstrap_arrival_effort_v2/analyze.py"
sp=importlib.util.spec_from_file_location("chinstrap_arrival_v2",F);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class TestArrivalEffort(unittest.TestCase):
 def test_weighted_median(self):
  import datetime
  a=datetime.date(2001,11,12);b=datetime.date(2001,11,20)
  self.assertEqual(m.median_weighted([(a,3),(b,1)]),a)
  self.assertIsNone(m.median_weighted([(a,0)]))
  self.assertEqual(m.median_weighted([(a,1),(b,3)]),b)
 def test_expected_year_list(self):
  self.assertEqual(len(m.YEARS),17)
  self.assertNotIn(2010,m.YEARS)
  self.assertNotIn(2012,m.YEARS)
if __name__=="__main__":unittest.main()
