"""Only tests source CSV shape; no original diet values accessed."""
import importlib.util
import io
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"research/climate-penguin/work/climate_penguin/signy_prey_schema_gate_v1.py"
spec=importlib.util.spec_from_file_location("signy_prey_gate",path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class SourcePreyGateTests(unittest.TestCase):
    def test_synthetic_krill_header(self):
        csv=b"DATE_SAMPLE,ID,TOTAL_WET_MASS_G,KRILL_MASS_G,FISH_MASS_G\n1999-01-01,1,10,6,3\n"
        a=m.columns(csv)
        self.assertEqual(a["row_count"],1)
        self.assertTrue(a["has_krill_candidate"])
        self.assertTrue(a["has_weight_candidate"])
        self.assertFalse(a["outcome_values_opened"])
    def test_empty_csv(self):
        self.assertTrue(m.columns(b"").get("empty_file"))
    def test_source_catalogue_pin(self):
        self.assertEqual(m.SOURCES["Gentoo"][2],2010)
        self.assertEqual(len(m.SOURCES),3)
    def test_no_numeric_analysis_method(self):
        x=m.columns(b"SEASON,TOTAL_WEIGHT\n1999,22\n")
        self.assertFalse(x["sample_uniqueness_confirmed"])
        self.assertFalse(x["date_to_breeding_season_confirmed"])

if __name__=="__main__":
    unittest.main()
