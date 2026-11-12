#!/usr/bin/env python3
"""Unit tests: original source handling and exact matched three-decade arithmetic."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import math
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("legacy",HERE/"test_three_decade_climate_legacy.py")
legacy=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(legacy)


class ThreeDecadeLagTests(unittest.TestCase):
    def test_region_centered_correlation_and_negative(self):
        vals=[
            ("r1","b1",1,2),("r1","b2",2,4),("r1","b3",3,6),
            ("r2","b4",10,20),("r2","b5",12,24),("r2","b6",15,30)
        ]
        rows=[{"source_region":g,"polar_250km_block":b,"ice":x,"nest":y,"negative_nest":-y}
              for g,b,x,y in vals]
        self.assertAlmostEqual(legacy.region_center_corr(rows,"ice","nest")["r"],1.0)
        self.assertAlmostEqual(legacy.region_center_corr(rows,"ice","negative_nest")["r"],-1.0)
        self.assertTrue(legacy.dropout_range(rows,"ice","nest","polar_250km_block")["n_valid_omissions"]>0)

    def test_insufficient_unobserved_singletons_are_not_zero_correlation(self):
        rows=[{"source_region":str(i),"polar_250km_block":str(i),"x":i,"y":i}
              for i in range(6)]
        record=legacy.region_center_corr(rows,"x","y")
        self.assertIsNone(record["r"])
        self.assertEqual(record["reason"],"INSUFFICIENT_MULTISITE_REGIONS")

    def test_fixed_roster_centroid_telescope_and_ice_identity(self):
        rows=[]
        for i,(lat,a,b,c,s0,s1,s2) in enumerate([
            (-61.0,10,11,12,70.,65.,60.),
            (-63.0,20,23,26,80.,70.,65.),
            (-67.0,30,31,40,90.,85.,80.)
        ]):
            rows.append({
              "site_id":str(i),"species":"ADPE","source_region":"r",
              "polar_250km_block":str(i),"latitude":lat,
              **{f"n_census_years_{j}":2 for j in range(3)},
              **{f"median_original_nest_count_{j}":n for j,n in enumerate((a,b,c))},
              **{f"mean_original_aug_nov_SIC_{j}_pp":s for j,s in enumerate((s0,s1,s2))}
            })
        d01=legacy.triple_same_roster_components(rows,0,1)
        d12=legacy.triple_same_roster_components(rows,1,2)
        d02=legacy.triple_same_roster_components(rows,0,2)
        self.assertAlmostEqual(d01["southward_positive_latitudinal_reweighting_km"]+
            d12["southward_positive_latitudinal_reweighting_km"],
            d02["southward_positive_latitudinal_reweighting_km"])
        for d in (d01,d12,d02):
            self.assertAlmostEqual(d["physical_SIC_change_component_pp"]+
                d["count_reweighting_component_pp"],d["experienced_SIC_change_pp"])

    def test_triplet_census_requires_all_three_2_years(self):
        sites={"A":{"source_region":"R1","polar_250km_fixed_grid_block":"b1",
             "longitude":-64,"latitude":-62}}
        sic={("A",k):70.0+k for k in range(3)}
        obs={("A","ADPE",0):[(1994,10),(1996,11)],
             ("A","ADPE",1):[(2003,20)],("A","ADPE",2):[(2012,30),(2015,32)]}
        self.assertEqual(legacy.site_roster(sites,obs,sic,"ADPE"),[])
        obs[("A","ADPE",1)].append((2006,21))
        cohort=legacy.site_roster(sites,obs,sic,"ADPE")
        self.assertEqual(len(cohort),1)
        self.assertEqual(cohort[0]["longitude_sector_10deg"],11)
        self.assertAlmostEqual(cohort[0]["delta_ice_pp_earlier"],1.0)


if __name__=="__main__":
    unittest.main()
