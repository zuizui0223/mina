#!/usr/bin/env python3
"""Independent, pure standard-library checks of geographic source diagnostics."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import math
import unittest

p=Path(__file__).resolve().parent/"diagnose_geographic_climate_legacy_mismatch.py"
spec=importlib.util.spec_from_file_location("geo",p)
geo=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(geo)

class TestGeographicMismatch(unittest.TestCase):
    def test_pooled_equal_source_regions_not_first_region_only(self):
        rows=[]
        for region,blockshift in (("A",0),("B",100)):
            for j in range(3):
                rows.append({"source_region":region,"polar_250km_block":f"{region}{j}",
                             "x":blockshift+j,"y":3*j+blockshift})
        got=geo.pooled_region_center(rows,"x","y")
        self.assertEqual(got["n_informative_sites"],6)
        self.assertEqual(got["n_informative_regions"],2)
        self.assertAlmostEqual(got["r"],1)
        self.assertAlmostEqual(sum(z["signed_covariance_numerator"] for z in got["contributions"].values()),got["numerator"])

    def test_singleton_does_not_create_pseudoreplication(self):
        r=[{"source_region":"X","polar_250km_block":"a","x":1,"y":2},
           {"source_region":"Y","polar_250km_block":"b","x":2,"y":3}]
        q=geo.pooled_region_center(r,"x","y")
        self.assertEqual(q["n_informative_sites"],0)
        self.assertIsNone(q["r"])

    def test_sector_matches_both_ice_and_survey_sites_or_flags_missing(self):
        r=[]
        for sid,lat,n0,n1 in (
            ("a",-60.,30,10),("b",-65.,10,30),("c",-62.,10,10)
        ):
            sec=0 if sid!="c" else 2
            r.append({
             "site_id":sid,"source_region":"R","polar_250km_block":sid,
             "longitude_sector_10deg":sec,"latitude":lat,
             "median_original_nest_count_0":n0,
             "median_original_nest_count_1":n1,
             "median_original_nest_count_2":n1
            })
        fronts=[{
            "start_period":geo.PERIODS[0],
            "end_period":geo.PERIODS[1],
            "climate_month_basis":"aug_nov",
            "longitude_sector_10deg":0,"status":"PAIRED_ORIGINAL_MARINE_FRONT",
            "southward_positive_ice_edge_meridional_km":12.0
        }]
        details,summary=geo.sector_mismatch(r,fronts,"ADPE")
        sector0=[q for q in details if q["period_start"]==geo.PERIODS[0] and q["basis"]=="aug_nov" and q["sector"]==0][0]
        self.assertEqual(sector0["support"],"SUPPORTED_TWO_PLUS_OBSERVED_SITES_DESCRIPTIVE_ONLY")
        self.assertEqual(sector0["direction"],"SAME_SIGN")
        self.assertGreater(sector0["within_sector_nest_weighted_southward_km"],0)
        sector2=[q for q in details if q["period_start"]==geo.PERIODS[0] and q["basis"]=="aug_nov" and q["sector"]==2][0]
        self.assertEqual(sector2["support"],"NO_VALID_ORIGINAL_MARINE_60PCT_FRONT")
        self.assertEqual([z for z in summary if z["basis"]=="aug_nov" and z["period_start"]==geo.PERIODS[0]][0]["sector_level_macro_replication"],"NO_MACRO_SECTOR_REPLICATION")

    def test_zero_movement_is_indeterminate_not_pseudomatch(self):
        r=[
            {"site_id":"a","source_region":"R","polar_250km_block":"X",
             "longitude_sector_10deg":0,"latitude":-62.0,
             "median_original_nest_count_0":10,"median_original_nest_count_1":10,
             "median_original_nest_count_2":10},
            {"site_id":"b","source_region":"R","polar_250km_block":"Y",
             "longitude_sector_10deg":0,"latitude":-63.0,
             "median_original_nest_count_0":10,"median_original_nest_count_1":10,
             "median_original_nest_count_2":10},
        ]
        f=[{"start_period":"1991-2000","end_period":"2001-2010","climate_month_basis":"aug_nov",
            "longitude_sector_10deg":0,"status":"PAIRED_ORIGINAL_MARINE_FRONT",
            "southward_positive_ice_edge_meridional_km":10.0}]
        rows,_=geo.sector_mismatch(r,f,"ADPE")
        x=[z for z in rows if z["period_start"]=="1991-2000" and z["basis"]=="aug_nov" and z["sector"]==0][0]
        self.assertEqual(x["direction"],"INDETERMINATE_WITHIN_1KM")

if __name__=="__main__":
    unittest.main()
