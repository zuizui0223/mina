import unittest
from scripts.audit_aadc_2025_occupancy_riskset_sources import (
    select_exact_catalog_entries,object_manifest
)

class TestAADC2025SurveySource(unittest.TestCase):
    def test_exact_records_and_metadata(self):
        rows=[
            {"eds_id":"5959","metadata_entry_id":"AAS_4518_Seabird_Breeding_Occupancy",
             "dataset_name":"Mapping knowledge of seabird breeding occupancy across East Antarctica",
             "uuid":"aaaaaaaa-1111-2222-3333-444444444444"},
            {"eds_id":"4344","metadata_entry_id":"AAS_4088_Spatial_reference_system_coastal_east_Antarctica",
             "dataset_name":"A spatial reference system for coastal ice-free land in East Antarctica",
             "uuid":"bbbbbbbb-1111-2222-3333-444444444444"},
        ]
        picked=select_exact_catalog_entries(rows)
        self.assertEqual(picked["5959"]["status"],"EXACT_PUBLISHER_IDENTITY")
        self.assertEqual(picked["4344"]["status"],"EXACT_PUBLISHER_IDENTITY")
        broken=[dict(x) for x in rows]
        broken[0]["dataset_name"]="other study"
        broken[0]["metadata_entry_id"]="independent biological report"
        self.assertEqual(
            select_exact_catalog_entries(broken)["5959"]["status"],
            "HOLD_PUBLISHER_IDENTITY_MISMATCH")

    def test_duplicate_eds_id_must_hold(self):
        entry={"eds_id":"5959","metadata_entry_id":"AAS_4518_Seabird_Breeding_Occupancy",
               "dataset_name":"breeding occupancy","uuid":"aaaaaaaa-1111-2222-3333-444444444444"}
        out=select_exact_catalog_entries([entry,entry])
        self.assertEqual(out["5959"]["status"],"HOLD_MISSING_OR_DUPLICATE_EDS_ID")

    def test_unknown_file_extension_is_not_original_survey(self):
        raw=[{"name":"survey_visit_2025.csv","size":15000},
             {"name":"screenshot.png","size":1200},
             {"name":"icefree_habitat_regions.gpkg","size":460000},
             {"name":"survey_visit_2025.csv","size":15000}]
        m=object_manifest(raw)
        self.assertEqual(m["source_objects_eligible_for_later_schema_audit"],2)
        self.assertFalse(m["has_firsthand_survey_negative_proof"])
        self.assertEqual(
            [x["name"] for x in m["potential_original_data_objects"]],
            ["survey_visit_2025.csv","icefree_habitat_regions.gpkg"])

if __name__=="__main__":
    unittest.main()
