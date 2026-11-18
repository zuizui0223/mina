import importlib.util,unittest,tempfile,csv,zipfile
from pathlib import Path
F=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_chinstrap_arrival_source_gate_v1/inspect.py"
sp=importlib.util.spec_from_file_location("arrival",F);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class TestArrivalSource(unittest.TestCase):
 def test_year_guess_ambiguous(self):
  self.assertEqual(m.year_from("2016-11-05"),2016)
  self.assertIsNone(m.year_from("2016/17"))
  self.assertIsNone(m.year_from("2016-11-05 to 2017-12-01"))
 def test_original_schema_only(self):
  with tempfile.TemporaryDirectory() as t:
   file=Path(t)/"source.zip"
   with zipfile.ZipFile(file,"w") as z:
    z.writestr("a.csv","Survey_Date,COUNT\n2016-11-08,20\n2016-11-12,30\n")
   x=m.audit(file,Path(t)/"result")
   self.assertEqual(x["n_original_csv"],1)
   self.assertEqual(x["files"][0]["n_rows"],2)
   self.assertIn("NOT_phenology_response",x["status"])
if __name__=="__main__":unittest.main()
