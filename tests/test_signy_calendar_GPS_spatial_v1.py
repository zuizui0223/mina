"""GPS location within same source clock-hour, source-backed not prey."""
import importlib.util,unittest,os,tempfile,datetime
from pathlib import Path
SRC=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_calendar_GPS_spatial_v1/analyze.py"
sp=importlib.util.spec_from_file_location("gps_calendar",SRC)
a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
class Tests(unittest.TestCase):
 def test_same_hour_rounding(self):
  t=datetime.datetime(2020,1,22,9,55,41,tzinfo=datetime.timezone.utc)
  self.assertEqual(a.hour_of(t),datetime.datetime(2020,1,22,9))
 def test_jaccard_and_distance(self):
  self.assertAlmostEqual(a.jaccard({1,2},{2,3}),1/3)
  self.assertEqual(a.jaccard(set(),set()),None)
  self.assertAlmostEqual(a.distance_km((0,0),(0,0)),0)
 def test_original_BAS_GPS(self):
  path=os.getenv("SIGNY_THREE_SOURCE_GPS")
  if not path:self.skipTest("CI downloads original BAS archive and verifies all content")
  with tempfile.TemporaryDirectory() as tmp:
   z=a.run(path,tmp)
   self.assertEqual(z["n_original_tracking_deployments"],168)
   self.assertEqual(z["original_source_shared_years"],[2011,2013,2015])
   self.assertTrue((Path(tmp)/"gps_two_species_by_season.csv").exists())
   data={v["season_start"]:v for v in z["year_summary"]}
   self.assertEqual(data[2013]["n_joint_days_with_at_least_2_deployments_each"],24)
   self.assertEqual(data[2015]["n_joint_days_with_at_least_2_deployments_each"],16)
   self.assertEqual(data[2013]["n_both_species_same_clock_hour_bins"],672)
   self.assertEqual(data[2015]["n_both_species_same_clock_hour_bins"],440)
   self.assertAlmostEqual(data[2013]["strict_2plus_tag_joint_day_median_Chinstrap_minus_Adelie_km"],49.960171272,places=5)
   self.assertAlmostEqual(data[2015]["strict_2plus_tag_joint_day_median_Chinstrap_minus_Adelie_km"],-5.592767248,places=5)
if __name__=="__main__":unittest.main()
