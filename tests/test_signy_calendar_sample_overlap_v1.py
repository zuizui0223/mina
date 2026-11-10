"""Original BAS calendar overlap and 14-year mean hatch stage guards."""
import importlib.util,os,unittest,tempfile
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/signy_calendar_sample_overlap_v1/audit.py"
sp=importlib.util.spec_from_file_location("sample_calendar",SCRIPT)
a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
class Source(unittest.TestCase):
 def test_calendar_window_selection(self):
  x=[{"date":"2002-01-01","fish_within_fish_plus_crust":.1}]
  y=[{"date":"2002-01-04","fish_within_fish_plus_crust":.2}]
  self.assertEqual([len(t) for t in a.selectable(x,y,2)],[0,0])
  self.assertEqual([len(t) for t in a.selectable(x,y,3)],[1,1])
 def test_publisher_original(self):
  diet=os.getenv("ORIGINAL_SIGNY_DIET_DERIVED")
  hatch=os.getenv("ORIGINAL_SIGNY_HATCH_DERIVED")
  if not diet or not hatch:self.skipTest("CI reconstructs official four BAS ZIPs")
  with tempfile.TemporaryDirectory() as root:
   r=a.run(diet,hatch,root)
   self.assertEqual(r["n_original_diet_stomachs"],1364)
   self.assertEqual(r["n_total_paired_species_years"],37)
   self.assertEqual(r["all_seasons_with_exact_same_day_stomachs"],0)
   self.assertEqual(r["calendar_pair_support"]["Adelie-Chinstrap"]["n_paired_breeding_seasons"],19)
   self.assertEqual(r["calendar_pair_support"]["Adelie-Chinstrap"]["within_7_days"]["n_breeding_seasons_with_3_stomachs_each"],11)
   self.assertEqual(r["calendar_pair_support"]["Adelie-Gentoo"]["within_7_days"]["n_breeding_seasons_with_3_stomachs_each"],8)
   self.assertEqual(r["calendar_pair_support"]["Chinstrap-Gentoo"]["within_7_days"]["n_breeding_seasons_with_3_stomachs_each"],3)
   self.assertEqual(r["hatching_14_season_support"]["n_calendar_date_range_overlapping_seasons"],0)
   self.assertEqual(r["hatching_14_season_support"]["n_relative_hatch_stage_within_7days"],13)
   self.assertEqual(r["hatching_14_season_support"]["closest_collection_date_gap_min_days"],3)
   self.assertEqual(r["hatching_14_season_support"]["closest_collection_date_gap_max_days"],19)
   self.assertEqual(r["hatching_14_season_support"]["n_hatching_years_with_7day_nearest_calendar_stomach_samples_both_species"],8)
   self.assertAlmostEqual(r["hatching_14_season_support"]["near_calendar7_induced_breeding_stage_age_difference_mean_days"],-25.25)
   self.assertTrue((Path(root)/"hatching_14_seasons_sampling_stage_and_calendar.csv").exists())
if __name__=="__main__":unittest.main()
