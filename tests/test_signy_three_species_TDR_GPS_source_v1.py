import importlib.util,unittest,tempfile,zipfile
from pathlib import Path
F=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_three_species_TDR_GPS_source_v1/audit.py"
sp=importlib.util.spec_from_file_location("sources",F);a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
class Tests(unittest.TestCase):
 def test_header_and_id(self):
  with tempfile.TemporaryDirectory() as dir:
   p=Path(dir)/"x.zip"
   with zipfile.ZipFile(p,"w") as z:
    z.writestr("Data/SIA001_TDR.csv","DateTime,Pressure [dBars],Temperature\n2013-12-01T12:00:00,5,3\n")
    z.writestr("Data/SIC001_TDR.csv","DateTime,Pressure [dBars]\n2013-12-01,0\n")
   r=a.source_track_roster(p,"SIA","TDR")
   self.assertEqual(len(r),1)
   self.assertEqual(r[0]["id"],"SIA001")
   self.assertTrue(r[0]["header_ok"])
   self.assertEqual(r[0]["source_datetime_first"],"2013-12-01T12:00:00")
 def test_extra_publisher_filename_tokens(self):
  with tempfile.TemporaryDirectory() as dir:
   p=Path(dir)/"x.zip"
   with zipfile.ZipFile(p,"w") as z:
    z.writestr("source/SIA001_2013_GPS.csv","DateTime,Latitude_degrees_north,Longitude_degrees_east\n2013-12-01T12:00:00,-60,-45\n")
    z.writestr("source/SIA001_GPS.csv","DateTime,Latitude_degrees_north,Longitude_degrees_east\n2013-12-01T12:00:00,-61,-44\n")
    z.writestr("source/SIA002_metadata_GPS.csv","DateTime,Latitude_degrees_north,Longitude_degrees_east\n2013-12-01T12:00:00,-60,-45\n")
   with self.assertRaisesRegex(ValueError,"Conflicting duplicate"):
    a.source_track_roster(p,"SIA","GPS")
 def test_id_token_without_duplicate(self):
  with tempfile.TemporaryDirectory() as dir:
   p=Path(dir)/"x.zip"
   with zipfile.ZipFile(p,"w") as z:
    z.writestr("SIA001_2013_GPS.csv","DateTime,Latitude_degrees_north,Longitude_degrees_east\n2013-12-01T12:00:00,-60,-45\n")
    z.writestr("SIA002_GPS.csv","DateTime,Latitude_degrees_north,Longitude_degrees_east\n2013-12-01T12:00:00,-60,-45\n")
   rows=a.source_track_roster(p,"SIA","GPS")
   self.assertEqual({r["id"] for r in rows},{"SIA001","SIA002"})

if __name__=="__main__":unittest.main()
