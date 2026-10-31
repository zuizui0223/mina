"""IMR official overall-stratum annual acoustic source grain and time gap guards."""
import unittest,sys,importlib.util,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"research/climate-penguin/work/climate_penguin/imr_krill_independent_acoustic_2023_2025_v1.py"
spec=importlib.util.spec_from_file_location("acoustic",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
PATH=ROOT/"research/climate-penguin/inputs/IMR_annual_overall_acoustic_2011_2025_v1.csv"
class IMRAcoustic(unittest.TestCase):
    def test_source_years_and_missing_preserved(self):
        rows,sha=m.source_rows(PATH)
        self.assertEqual(len(rows),13)
        self.assertEqual(len(sha),64)
        self.assertFalse(any(x["year"] in (2021,2022) for x in rows))
    def test_historical_vs_independent_posttrain_strata(self):
        a,j=m.run(PATH)
        self.assertEqual(j["Freer_2011_2020_historical_training_overlap_n"],10)
        self.assertEqual(j["original_out_of_training_survey_years"],[2023,2024,2025])
        self.assertEqual(j["kHz120_only_n"],9)
    def test_observational_statistics_without_causal_promotion(self):
        _,j=m.run(PATH)
        self.assertTrue(math.isclose(j["overall_stratum_density_Kendall_tau"],
            0.03871048305693819,abs_tol=1e-11))
        self.assertGreater(j["overall_stratum_density_Kendall_p_descriptive"],.8)
        self.assertEqual(j["posttraining_yearly_original_acoustic_estimates"][-1]["cv"],.75)
        self.assertTrue(j["no_attribution_to_ice_or_salinity_or_future_nesting"])
if __name__=="__main__":unittest.main()
