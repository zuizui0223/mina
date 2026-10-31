"""Primary paper Table3 source-year ordering and informative-2026-missingness."""
import unittest,importlib.util,math
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
P=BASE/"research/climate-penguin/work/climate_penguin/imr_krill_independent_acoustic_2023_2025_v1.py"
spec=importlib.util.spec_from_file_location("imr",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA=BASE/"research/climate-penguin/inputs/IMR_annual_overall_acoustic_2011_2025_v1.csv"
class AcousticPrimary(unittest.TestCase):
    def test_primary_2013_missing_no_shift(self):
        rows,sha=m.source_rows(DATA)
        self.assertEqual(len(rows),12)
        self.assertEqual(len(sha),64)
        self.assertNotIn(2013,[r["year"] for r in rows])
        self.assertEqual(next(r["density_g_m2"] for r in rows if r["year"]==2017),23.2)
        self.assertEqual(next(r["density_g_m2"] for r in rows if r["year"]==2020),38.8)
    def test_2026_ice_and_operational_censoring_not_zero(self):
        _,d=m.run(DATA)
        self.assertIn(2026,d["missing_or_not_estimable_years"])
        self.assertFalse(d["2026_survey_full_area_density_is_not_estimable"]["overall_stratum_density_estimable"])
        self.assertIsNone(d["2026_survey_full_area_density_is_not_estimable"]["region_wide_krill_biomass_Mt"])
        self.assertEqual(d["source_year_reprint_discrepancy"]["n_reprint_conflicts"],8)
    def test_original_authority_trend_and_120kHz(self):
        _,d=m.run(DATA)
        t=d["descriptive_trends"]
        self.assertEqual(t["primary_2011_2020"]["n"],9)
        self.assertTrue(math.isclose(t["primary_2011_2020"]["Kendall_p_descriptive"],.18018077601410934,abs_tol=1e-10))
        self.assertEqual(t["all_corrected_2011_2025"]["Kendall_tau"],0.)
        self.assertEqual(t["all_corrected_2011_2025"]["Kendall_p_descriptive"],1.)
        self.assertTrue(math.isclose(t["kHz120_only"]["Kendall_tau"],1/9,abs_tol=1e-10))
    def test_new_source_survey_high_CV_not_positive_trend(self):
        _,d=m.run(DATA)
        x=d["annual_posttraining_CV_and_SE"]
        self.assertEqual([(r["year"],r["density_g_m2"],r["source_CV"]) for r in x],
                          [(2023,36.7,.51),(2024,80.5,.11),(2025,102.,.75)])
        self.assertEqual(x[-1]["derived_approx_SE_g_m2"],76.5)
        self.assertTrue(d["no_2023_2025_Freer_prediction_to_score"])
if __name__=="__main__":unittest.main()
