#!/usr/bin/env python3
"""Exact synthetic geometry guards, not empirical Antarctic penguin evidence."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
import numpy as np

root = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ice", root / "compute_original_60pct_marine_front.py")
ice = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(ice)


class TestOriginalMarineFront(unittest.TestCase):
    def test_fixed_sector_wrapping(self):
        self.assertEqual(
            ice.sector_indices([-180, -170, -0.01, 0.01, 179.9, 180]).tolist(),
            [0, 1, 17, 18, 35, 0]
        )

    def test_actual_contour_synthetic_closed_ring_and_lat(self):
        r, c = np.indices((120, 120))
        dr, dc = r.astype(float)-59.5, c.astype(float)-59.5
        rr = np.hypot(dr,dc)
        sic = np.where(rr<40, 100.0, 0.0)
        lat = -90.0 + rr*.27
        lon = np.rad2deg(np.arctan2(dc, dr))
        valid = np.ones(rr.shape, dtype=bool)
        front, report = ice.continuous_front(
            sic, valid, lat, np.sin(np.deg2rad(lon)), np.cos(np.deg2rad(lon))
        )
        self.assertEqual(report["status"], "CONTIGUOUS_60PCT_MARINE_RING_CANDIDATE")
        self.assertGreaterEqual(report["selected_contour_sectors"], 24)
        self.assertGreaterEqual(len(front), 24)
        self.assertLess(abs(float(np.median([z["lat_median"] for z in front.values()]))-(-79.2)), .5)

    def test_no_cross_source_mask_as_real_edge(self):
        r,c=np.indices((120,120))
        rr=np.hypot(r-59.5,c-59.5)
        sic=np.where(rr<40,100.0,0.0)
        lat=-90.0+rr*.27
        lon=np.rad2deg(np.arctan2(c-59.5,r-59.5))
        mask=np.ones(rr.shape,dtype=bool)
        # Remove the eastern half, forcing an open contour and therefore NO ring.
        mask[:,:60]=False
        front, report=ice.continuous_front(
            sic,mask,lat,np.sin(np.deg2rad(lon)),np.cos(np.deg2rad(lon))
        )
        self.assertIsNone(front)
        self.assertEqual(report["status"],"NO_SINGLE_CONTIGUOUS_60PCT_FRONTRING")

    def test_front_join_same_roster_no_fabricated_ice(self):
        # Different covered sectors: unsupported source is excluded, not SIC=0.
        rows=[
            {
              "start_period":"1991-2000", "end_period":"2011-2020",
              "climate_month_basis":"aug_nov",
              "longitude_sector_10deg": 0,
              "status":"PAIRED_ORIGINAL_MARINE_FRONT",
              "southward_positive_ice_edge_meridional_km": 20.
            }
        ]
        siteids=[
            {"site_id":"A","longitude":-179.5},
            {"site_id":"B","longitude":-179.0},
            {"site_id":"C","longitude":-169.0}
        ]
        # Mirror the required frozen atlas shape without fabricating observed censuses.
        siteids.extend({"site_id":f"D{i:03d}", "longitude":0.}
                       for i in range(592))
        matched=[]
        for sid in ("A","B","C"):
            matched.append({
                "site_id":sid,"species":"ADPE",
                "first_window":"1991-2000","last_window":"2011-2020",
                "n_original_count_years_early":2,
                "n_original_count_years_late":2,
                "source_region":"R1" if sid=="A" else "R2",
                "polar_250km_block":sid,
                "site_median_observed_nests_early":5,
                "site_median_observed_nests_late":8,
                "latitude":-65.0,
            })
        result=ice.biological_overlap(rows,matched,siteids)
        focus=[z for z in result if z["species"]=="ADPE"
               and z["start_period"]=="1991-2000"
               and z["end_period"]=="2011-2020"
               and z["climate_month_basis"]=="aug_nov"][0]
        self.assertEqual(focus["original_strict_two_year_paired_site_count"],3)
        self.assertEqual(focus["front_supported_matched_site_count"],2)
        self.assertEqual(focus["status"],"INSUFFICIENT_PAIRS_FOR_DESCRIPTIVE_COMPARISON")
        self.assertEqual(focus["unmatched_site_codes"],"C")


if __name__ == "__main__":
    unittest.main()
