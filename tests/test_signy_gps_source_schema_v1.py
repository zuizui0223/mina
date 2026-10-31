import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/signy_gps_source_schema_v1.py"
spec=importlib.util.spec_from_file_location("signy_gps_schema",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class GPSOriginalSourceTests(unittest.TestCase):
    def test_csv_header_only(self):
        data=b"Datetime,Latitude,Longitude\n2016-01-01,-60.7,-45.6\n"
        p=m.metadata_csv(data,"SIC001_GPS.csv")
        self.assertTrue(p["header_has_datetime_candidate"])
        self.assertTrue(p["header_has_lat_candidate"])
        self.assertTrue(p["header_has_lon_candidate"])
        self.assertFalse(p["original_position_numeric_values_opened"])
        self.assertEqual(p["nonempty_rows"],1)
    def test_metadata_without_coordinates(self):
        p=m.metadata_csv(b"deployment_id,gender,breeding_status\nSIC001,F,incubating\n","Bird_Metadata.csv")
        self.assertFalse(p["header_has_lon_candidate"])
        self.assertFalse(p["header_has_lat_candidate"])
    def test_current_original_version2(self):
        self.assertEqual(m.SOURCES["Chinstrap"]["entry_id"],"8f8ccba5-01af-4b00-8a3b-c3c85b24bf92")
        self.assertEqual(m.SOURCES["Gentoo"]["species_code"],"G")
    def test_missing_zip_fails(self):
        with self.assertRaisesRegex(ValueError,"invalid"):
            m.visit("Adelie",Path(__file__))
if __name__=="__main__":
    unittest.main()
