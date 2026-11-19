import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import pandas as pd
from scripts.audit_glims_rocktime_mapppd_survey_support import run

class TestSurveyMetadataOnly(unittest.TestCase):
    def test_no_row_and_numeric_zero_do_not_infer_absence(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"rocksite.csv"
            rows=[{"site_id":f"S{i}","near_1km_source_only":True,
                   "rock_source_year":2024,"glims_late_year":2005,
                   "land_source_feature_id":11,"bbox_region":"example"} for i in range(25)]
            pd.DataFrame(rows).to_csv(path,index=False)
            fake=pd.DataFrame([
                {"site_id":"S0","species_id":"ADPE","type":"nests","count":1,"season":2000},
                {"site_id":"S0","species_id":"ADPE","type":"nests","count":0,"season":2001},
                {"site_id":"S0","species_id":"ADPE","type":"nests","count":4,"season":2025},
                {"site_id":"S1","species_id":"GEPE","type":"nests","count":1,"season":2024},
                {"site_id":"OTHER","species_id":"ADPE","type":"nests","count":1,"season":2025}
            ])
            with patch("scripts.audit_glims_rocktime_mapppd_survey_support.original_rda",return_value=fake):
                r,detail=run(path,Path(tmp))
            self.assertEqual(r["candidate_site_ids"],25)
            self.assertEqual(r["site_ids_with_any_nest_count_record"],2)
            self.assertEqual(r["site_ids_with_strictly_post_rock_source_year_nest_records"],1)
            self.assertEqual(r["site_ids_with_any_numeric_zero_count_record"],1)
            self.assertIsNone(r["n_verified_A_to_P_events"])
            self.assertFalse(detail["earliest_positive_is_colonization"].any())

if __name__=="__main__":
    unittest.main()
