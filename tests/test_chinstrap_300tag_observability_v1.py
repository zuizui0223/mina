import importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/chinstrap_300tag_observability_v1.py"
spec=importlib.util.spec_from_file_location("sensor_gate",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Source300QA(unittest.TestCase):
    def test_original_source_sha_fixed(self):
        self.assertEqual(m.INPUT_SHA,"a985b036716bf18f1356988ccba08374ab3b0b97c579f53a86f5bef07f4207fc")
    def test_synthetic_gps_coverage(self):
        x={"original_source_id":"PI001","original_deployment_id":"PI001",
           "original_island":"PI","q01_hourly_range_dbar":"1.0",
           "q05_hourly_range_dbar":"0.9","source_pressure_n_duplicate_timestamp":"0",
           "fraction_TDR_time_inside_GPS_window":"0.95",
           "GPS_time_fraction_recorded_gaps_10min_or_less":"0.22"}
        z=m.evaluate([x])[0]
        self.assertTrue(z["primary_source_observability"])
        self.assertFalse(z["strict_GPS_sensitivity"])
        x["source_pressure_n_duplicate_timestamp"]="2"
        self.assertFalse(m.evaluate([x])[0]["primary_source_observability"])
    def test_original_300_when_available(self):
        p=Path(__file__).resolve().parents[1]/"build/original300/all_300_original_sensor_QA.csv"
        if not p.exists():self.skipTest("requires reproducible original BAS 300tag artifact")
        x=m.evaluate(m.read(p))
        count,islands=m.summary(x)
        self.assertTrue(m.verify(count,islands))
        self.assertEqual(len(x),300)
        self.assertEqual(sum(z["primary_source_observability"] for z in x),190)
if __name__=="__main__":unittest.main()
