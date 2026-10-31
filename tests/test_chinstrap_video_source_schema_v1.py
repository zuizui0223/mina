import importlib.util,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_video_source_schema_v1.py"
s=importlib.util.spec_from_file_location("cam",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class CameraTests(unittest.TestCase):
    def test_publisher_source_contract(self):
        self.assertEqual(m.DOI,"10.5061/dryad.x69p8czmk")
        self.assertEqual(m.NAME,"ChinstrapForagingDiveOutcomesVariables.csv")
    def test_synthetic_770_rows(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"data.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr(m.NAME,"Bird_ID,Time,Krill_encounter,Depth,Speed\n"+"B1,2019-01-01,0,15,3\n"*770)
                z.writestr("README_file.txt","README")
            result=m.audit(p)
            self.assertEqual(result["source_n_dives"],770)
            self.assertFalse(result["raw_outcome_values_opened"])
            self.assertEqual(result["id_candidate_columns"],["Bird_ID"])
    def test_incomplete_source_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"bad.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr(m.NAME,"a,b,c,d,e\n0,0,0,0,0\n")
            with self.assertRaisesRegex(ValueError,"rows changed"):m.audit(p)
    def test_nonzip_fails(self):
        with self.assertRaisesRegex(ValueError,"not ZIP"):m.audit(Path(__file__))
if __name__=="__main__":unittest.main()
