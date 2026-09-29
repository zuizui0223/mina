import unittest

import pandas as pd

from scripts.audit_paper2_integrated_sensitivity_support import (
    filter_process_support,
)


class SensitivitySupportTests(unittest.TestCase):
    def test_ground_only_uses_raw_ground_not_all_direct(self):
        frame=pd.DataFrame([
            {"unit_id":"ADPE|A","site_id":"A","species_id":"ADPE"},
            {"unit_id":"ADPE|B","site_id":"B","species_id":"ADPE"},
        ])
        rows=[]
        for season in (1980,1990,2000,2010,2020):
            rows.append({
                "site_id":"A","species_id":"ADPE","season":season,
                "vantage_family":"direct","vantage_raw":"ground",
            })
            rows.append({
                "site_id":"B","species_id":"ADPE","season":season,
                "vantage_family":"direct","vantage_raw":"aerial",
            })
        kept,summary=filter_process_support(
            frame,pd.DataFrame(rows),mode="ground_only"
        )
        self.assertEqual(set(kept["unit_id"]),{"ADPE|A"})
        self.assertEqual(summary["supported_units"],1)

    def test_exclude_unknown_keeps_long_known_series(self):
        frame=pd.DataFrame([
            {"unit_id":"GEPE|A","site_id":"A","species_id":"GEPE"},
        ])
        rows=[
            {
                "site_id":"A","species_id":"GEPE","season":season,
                "vantage_family":"unknown" if season==2000 else "direct",
                "vantage_raw":"missing" if season==2000 else "ground",
            }
            for season in (1980,1990,2000,2010,2020,2025)
        ]
        kept,summary=filter_process_support(
            frame,pd.DataFrame(rows),mode="exclude_unknown"
        )
        self.assertEqual(len(kept),1)
        self.assertEqual(summary["supported_units"],1)


if __name__=="__main__":
    unittest.main()
