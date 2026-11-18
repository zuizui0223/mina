import importlib.util,unittest,tempfile
from pathlib import Path
F=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/scar_external_diet_v1/audit.py"
s=importlib.util.spec_from_file_location("scar",F);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Checks(unittest.TestCase):
 def test_grain(self):
  self.assertEqual(m.species({"predator_name":"Pygoscelis papua"}),"Gentoo")
  self.assertEqual(m.group({"prey_name":"Euphausia superba"}),"crustacean")
  self.assertEqual(m.group({"prey_worms_class":"Actinopterygii"}),"fish")
  self.assertIsNone(m.year({"date_start":"2001-05-03","date_end":"2002-03-05"}))
  self.assertIsNone(m.num("NA"))
 def test_sha_guard(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"fake.csv";f.write_text("x,y\n1,2")
   with self.assertRaisesRegex(ValueError,"source blob drift"):m.main(f,Path(d)/"out")
if __name__=="__main__":unittest.main()
