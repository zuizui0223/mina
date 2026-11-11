#!/usr/bin/env python3
"""Independent geometry/record identity checks for original Antarctic map layers."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("mapgeo",
    Path(__file__).resolve().parent/"build_spot_and_neighbor_map_geojson.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)

class TestSourceMap(unittest.TestCase):
    def test_original_lat_lon_order_and_ranges(self):
        self.assertEqual(m.coords({"latitude":"-77.4536","longitude":"169.2377"}),
                         [169.2377,-77.4536])
        with self.assertRaises(ValueError):
            m.coords({"latitude":"-40","longitude":"10"})

    def test_unobserved_species_region_does_not_become_bright(self):
        row={
          "source_peer_eligibility":"NO_COMPARABLE_REGIONAL_PEERS",
          "relative_direction":"positive"
        }
        self.assertEqual(m.source_point_status(row,{}),"NOT_COMPARABLE_REGION_SPECIES")

    def test_weak_yearly_support_does_not_become_strong(self):
        row={"source_peer_eligibility":"SAME_SPECIES_REGION_PAIRED_REFERENCE_AVAILABLE",
             "relative_direction":"positive","robust_source_candidate_status":"SOURCE_ROBUST_RELATIVE_BRIGHT_CANDIDATE"}
        self.assertEqual(m.source_point_status(row,{"same_year_sign_qualified_candidate":"False"}),
                         "INITIAL_STRICT_ONLY_POSITIVE")
        self.assertEqual(m.source_point_status(row,{"same_year_sign_qualified_candidate":"True"}),
                         "COMMON_YEAR_SUPPORTED_POSITIVE")
        self.assertEqual(m.source_point_status(row,{"outside_spatial_block_replicated_lead":"True"}),
                         "EXTERNAL_BLOCK_SUPPORTED_POSITIVE")

    def test_invalid_boolean_not_silently_accepted(self):
        with self.assertRaises(ValueError):
            m.boolean("yes, probable")
        self.assertFalse(m.boolean(""))
        self.assertTrue(m.boolean("True"))

if __name__=="__main__":
    unittest.main()
