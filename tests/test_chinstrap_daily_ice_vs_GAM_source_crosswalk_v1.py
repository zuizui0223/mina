"""Audit immutable post-source crosswalk, no false claim of biological forecast."""
import unittest,importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"research/climate-penguin/work/climate_penguin/chinstrap_daily_ice_vs_GAM_source_crosswalk_v1.py"
spec=importlib.util.spec_from_file_location("ice_gam_source",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestOriginalSourceCrosswalk(unittest.TestCase):
    def test_independent_derived_archive_receipts(self):
        a=ROOT/"research/climate-penguin/inputs/three_pair_original_45day_SIC_fixed_pixel_receipt.csv"
        b=ROOT/"research/climate-penguin/inputs/three_pair_original_GAM_nativepixel_receipt.csv"
        rows=m.join(m.original_receipt(a,m.EXPECTED_ICE_NORMALIZED_SHA),
                    m.original_receipt(b,m.EXPECTED_GAM_NORMALIZED_SHA))
        self.assertEqual(len(rows),3)
        self.assertEqual(sum(r["GPS_shared_Dec_dates"]+r["GPS_shared_Jan_dates"] for r in rows),45)
        for r in rows:
            self.assertGreater(r["retrospective_Tplus1_Freer_GAM_other_div_Signy_krill_model_ratio"],1)
            self.assertTrue(r["no_pretraining_out_of_time_or_independent_prey_causality"])
    def test_sample_count_cannot_be_omitted(self):
        a=[{"season_start":"2013","other_island":"PI",
             "fixed_GPS_footprint":"all_GPS_days","month":"Dec",
             "n_valid_fixed_pixel_daily_contrasts":"3",
             "n_original_shared_source_GPS_days":"3",
             "mean_Signy_minus_other_fixed_25km_cell_SIC_pp":"10.9"}]
        with self.assertRaises(KeyError):m.join(a,[])
if __name__=="__main__":unittest.main()
