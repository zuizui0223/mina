import unittest
from scripts.audit_aadc_2025_seabird_riskset_original_schema import (
    SETS,PUBLISHER_EDS_MANIFESTS,formatted_header
)

class TestAADCSourceSchema(unittest.TestCase):
    def test_source_matches_verified_inventory(self):
        self.assertEqual(len(SETS),5)
        self.assertEqual(
            SETS["2025_seabird"]["name"],
            "2_Site and search effort and occupancy data/occupancy_seabird.xls")
        self.assertEqual(SETS["2025_seabird"]["bytes"],5259776)
        self.assertEqual(SETS["2016_icefree_site_atlas"]["bytes"],336800)
        self.assertEqual(len(PUBLISHER_EDS_MANIFESTS),2)
    def test_biological_numbers_redacted_header_preview(self):
        got=formatted_header([
            ["geog_site_id","season","occupancy",103.5],
            [123,1998,0.0,"source reviewer name"]
        ])
        self.assertIn("geog_site_id",
            [x["text"] for x in got[0]["text_only_cells"] if "text" in x])
        self.assertTrue(any(x.get("type")=="NUMERIC_CELL_REDACTED"
                            for x in got[0]["text_only_cells"]))
        self.assertNotIn(1998,str(got))
        self.assertNotIn("103.5",str(got))
if __name__=="__main__":
    unittest.main()
