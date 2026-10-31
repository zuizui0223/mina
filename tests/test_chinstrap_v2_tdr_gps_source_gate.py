import importlib.util,io,unittest,zipfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_v2_tdr_gps_source_gate.py"
spec=importlib.util.spec_from_file_location("tdr_source",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class TDRSourceTests(unittest.TestCase):
    def test_filename_schemas_from_BAS_publisher(self):
        self.assertEqual(m.get_id("LIC078_GPS.csv","GPS"),("LIC078","LI"))
        with self.assertRaises(ValueError):
            m.get_id("PIC078_GPS.csv","GPS") 
    def test_publisher_Powell_PI_without_C(self):
        self.assertEqual(m.get_id("PI001_TDR.csv","TDR"),("PI001","PI"))
        self.assertEqual(m.get_id("SIC005_TDR.csv","TDR"),("SIC005","SI"))
        with self.assertRaises(ValueError):
            m.get_id("XIC005_TDR.csv","TDR")
    def test_date_and_pressure_header(self):
        raw=b"DateTime,Pressure_dbar,Temperature_C\n2015-12-31T10:00:00,8.5,-1.5\n"
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"raw.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("SIC007_TDR.csv",raw)
            with zipfile.ZipFile(p) as z:
                o=m.member_head(z,z.infolist()[0])
            self.assertTrue(o["has_pressure"])
            self.assertTrue(o["first_datetime_python_iso"])
            self.assertTrue(o["has_datetime_col"])
    def test_original_uncompressed_does_not_force_full_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"fake.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("SIC007_TDR.csv",b"DateTime,Pressure_dbar\n2014-01-01,2.0\n")
            r=m.scan(p,"TDR")
            self.assertEqual(r["source_member_count"],1)
            self.assertEqual(r["distinct_deployment_ids"],1)
            self.assertTrue(r["rows"][0]["has_pressure"])
if __name__=="__main__":
    unittest.main()
