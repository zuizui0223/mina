import unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"research/climate-penguin/work/climate_penguin/imr_source_observability_2011_2026_v1.py"
spec=importlib.util.spec_from_file_location("iceobs",P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=ROOT/"research/climate-penguin/inputs"
class SourceObservationProcess(unittest.TestCase):
    def test_missingness_years_and_ice_are_explicit(self):
        r,j=m.original_coverage(base/"IMR_yearwise_acoustic_coverage_2011_2026_v1.csv",
            base/"IMR_annual_overall_acoustic_2011_2025_v1.csv",
            base/"IMR_2026_acoustic_nonestimable_and_penguin_observatory.json")
        self.assertEqual(len(r),16)
        c=j["source_coverage_counts"]
        self.assertEqual((c["audited_survey_attempts"],c["regional_estimates"],
            c["not_estimable_documented"]),(14,12,2))
        self.assertEqual((c["explicit_ice_coverage_restriction"],
            c["ice_limited_with_estimate"],c["ice_limited_no_estimate"]),(3,1,2))
    def test_2026_not_imputed_as_zero(self):
        self.assertEqual(m.CENSORED,(2013,2026))
        self.assertEqual(m.UNKNOWN,(2021,2022))
        self.assertNotIn(2026,m.primary.EXPECTED)
if __name__=="__main__":unittest.main()
