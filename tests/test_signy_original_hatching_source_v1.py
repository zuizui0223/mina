"""Source archiving tests for original public Signy laying/hatching dates."""
import importlib.util,unittest,tempfile,zipfile
from pathlib import Path
FILE=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_original_hatching_source_v1/inspect.py"
sp=importlib.util.spec_from_file_location("hatch_source",FILE);a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
class TestHatchSource(unittest.TestCase):
 def test_source_csv_structure(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"example.zip"
   with zipfile.ZipFile(path,"w") as z:z.writestr("hatching.csv","year,species,date\n1996,Adelie,1996-12-17\n")
   x=a.run(path,Path(d)/"out")
   self.assertEqual(x["n_files"],1)
   self.assertEqual(x["files"][0]["columns"],["year","species","date"])
 def test_html_no_zip(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"download.zip";path.write_bytes(b"<html>request access</html>")
   with self.assertRaisesRegex(ValueError,"did not return"):a.run(path,Path(d)/"out")
if __name__=="__main__":unittest.main()
