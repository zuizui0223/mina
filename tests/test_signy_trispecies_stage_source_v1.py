import importlib.util
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
path=ROOT/"research/climate-penguin/work/climate_penguin/signy_trispecies_stage_source_v1.py"
spec=importlib.util.spec_from_file_location("signy_tri",path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class SignyStageSourceTests(unittest.TestCase):
    def test_malformed_publisher_season_quarantined(self):
        self.assertIsNone(module.strict_season_start("1998-8895"))
        self.assertEqual(module.strict_season_start("1998-1999"), 1998)
        self.assertEqual(module.strict_season_start("1998/99"), 1998)
        self.assertEqual(module.strict_season_start("1999-2000"), 1999)

    def test_nonnegative_and_missing(self):
        self.assertIsNone(module.number(""))
        self.assertIsNone(module.number("-1"))
        self.assertEqual(module.number("0"),0)
        self.assertAlmostEqual(module.number("3.2"),3.2)

    def test_original_source_pins(self):
        self.assertEqual(module.SOURCE["Adelie"]["prior_csv_sha256"], "585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62")
        self.assertEqual(module.SOURCE["Chinstrap"]["prior_csv_sha256"], "e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b")

    def test_no_annual_zeros_from_missing(self):
        r=[dict(species="Adelie",season_start=2017,colony="A1",
                pairs=10,chicks=15,recorded_fledglings_per_pair=None,source_spatial_unit="source_colony",reported_chicks_per_pair=1.5,nest_before_chicks=True)]
        annual,common=module.summarize(r)
        self.assertEqual(len(annual),1)
        self.assertEqual(annual[0]["strict_date_colonies"],1)
        self.assertAlmostEqual(annual[0]["median_recorded_chicks_per_pair"],1.5)
        self.assertEqual(common,[])

    def test_no_duplicate_colony_year(self):
        import pandas as pd
        z=pd.DataFrame([{"SEASON":"2017-2018","COLONY":"A1",
                         "TOTAL_NUMBER_OF_PAIRS":10,"TOTAL_NUMBER_OF_CHICKS":11},
                        {"SEASON":"2017-2018","COLONY":"A1",
                         "TOTAL_NUMBER_OF_PAIRS":12,"TOTAL_NUMBER_OF_CHICKS":13}])
        old=module.read_official_zip
        try:
            module.read_official_zip=lambda path:(z,{"selected_csv_sha256":module.SOURCE["Adelie"]["prior_csv_sha256"],"selected_csv":"mock.csv"})
            with self.assertRaisesRegex(ValueError,"duplicate literal"):
                module.source_extract("Adelie",__file__)
        finally:
            module.read_official_zip=old

if __name__=="__main__":
    unittest.main()
