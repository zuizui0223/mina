"""Tests for the metadata-only GLIMS WFS source gate; no live HTTP required."""
import unittest
from scripts.audit_glims_antarctic_island_source import (
    audit_features, feature_types, select_layer, years_from_properties,
)

class TestGlimsGate(unittest.TestCase):
    def test_featuretype_xml_with_namespaces(self):
        xml = (b'<wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs">'
               b'<wfs:FeatureTypeList><wfs:FeatureType>'
               b'<wfs:Name>glims:glacier_outlines</wfs:Name>'
               b'</wfs:FeatureType></wfs:FeatureTypeList></wfs:WFS_Capabilities>')
        self.assertEqual(feature_types(xml), ["glims:glacier_outlines"])
        self.assertEqual(select_layer(feature_types(xml)), "glims:glacier_outlines")

    def test_ambiguity_not_rescued(self):
        self.assertIsNone(select_layer(["a:glims_outline", "b:glims_glacier"]))
        self.assertIsNone(select_layer(["other:rgi_glacier"]))

    def test_only_original_acquisition_year(self):
        self.assertEqual(years_from_properties({"source_date": "2018-12-31",
                                                 "creation_date": "2026-05-01"}), [2018])
        self.assertEqual(years_from_properties({"copyright": "2022", "date_available": "2025"}), [])
        self.assertEqual(years_from_properties({"src_date": "scene_Landsat_1998winter"}), [1998])

    def test_geojson_limited_page_is_not_complete_inventory(self):
        a = audit_features({
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": {"type": "Polygon", "coordinates": []},
                          "properties": {"source_date": "2005-01-01",
                                         "glims_id": "x"}},
                         {"type": "Feature", "geometry": None,
                          "properties": {"source_date": "2018-01-01",
                                         "glims_id": "x"}}],
        }, limit=2)
        self.assertEqual(a["features_returned"], 2)
        self.assertTrue(a["limited_page_possible"])
        self.assertEqual(a["years_sample_histogram"], {2005: 1, 2018: 1})
        self.assertEqual(a["features_with_geometry"], 1)
        self.assertEqual(a["distinct_glacier_ids_in_sample"], 1)
        self.assertEqual(a["glacier_ids_with_two_or_more_source_years"], 1)
        self.assertEqual(a["glacier_ids_with_year_span_ge_5"], 1)
        self.assertTrue(a["sample_only"])


if __name__ == "__main__":
    unittest.main()
