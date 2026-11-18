import importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/chinstrap_300tag_original_source_flags_v1.py"
s=importlib.util.spec_from_file_location("src",P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class SourceFlagTests(unittest.TestCase):
 def test_original_fixed_receipts(self):
    self.assertEqual(len(m.HARD),6)
    self.assertEqual(m.EXPECTED["no_flag"],52)
    self.assertEqual(m.EXPECTED["n"],300)
 def test_timestamp_conflicts_held_not_nondive(self):
    v={"original_deployment_id":"PI009","original_island":"PI",
    "q01_hourly_range_dbar":"0.3","q05_hourly_range_dbar":"0.4",
    "fraction_TDR_time_inside_GPS_window":"1",
    "GPS_time_fraction_recorded_gaps_10min_or_less":"1",
    "source_pressure_n_original":"10","source_pressure_n_duplicate_timestamp":"8",
    "source_qa_status":"SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED"}
    a=m.classify(v,{"same_timestamp_different_pressure_from_first":"6"})
    self.assertTrue(a["needs_publisher_original_trace_review"])
    self.assertFalse(a["ecologically_approved_dive_or_foraging_track"])
 def test_source_complete_does_not_certify_foraging(self):
    v={"original_deployment_id":"LIC095","original_island":"LI",
    "q01_hourly_range_dbar":"0.4","q05_hourly_range_dbar":"0.6",
    "fraction_TDR_time_inside_GPS_window":"1",
    "GPS_time_fraction_recorded_gaps_10min_or_less":"1",
    "source_pressure_n_original":"10","source_pressure_n_duplicate_timestamp":"0",
    "source_qa_status":"SENSOR_SOURCE_COMPUTED_NOT_CALIBRATED"}
    a=m.classify(v)
    self.assertTrue(a["none_of_these_automated_warnings"])
    self.assertFalse(a["ecologically_approved_dive_or_foraging_track"])
 def test_real_source_artifact_if_present(self):
    root=Path(__file__).resolve().parents[1]
    x=root/"build/source300/all_300_original_sensor_QA.csv"
    y=root/"build/source6/original_source_6tag_anomalies.csv"
    if not(x.exists() and y.exists()):self.skipTest("original source CI results not installed")
    rows,status=m.run(x,y)
    self.assertEqual(len(rows),300)
    self.assertEqual(status["counts"]["no_flag"],52)
if __name__=="__main__":unittest.main()
