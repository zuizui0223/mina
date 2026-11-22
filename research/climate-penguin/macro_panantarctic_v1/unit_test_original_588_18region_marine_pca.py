#!/usr/bin/env python3
"""Source-free arithmetic and counting semantics tests of 18-region marine PCA."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np

spec=importlib.util.spec_from_file_location("allregion",
    Path(__file__).resolve().parent/"analyze_original_588_18region_marine_pca.py")
m=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)


class Original18RegionMarinePCA(unittest.TestCase):
    def test_original_calendar_and_temporal_slope(self):
        self.assertEqual(len(m.YEARS),28)
        self.assertEqual(m.YEARS[0],1993)
        self.assertEqual(m.YEARS[-1],2020)
        self.assertEqual(m.DECADES,((1993,2000),(2001,2010),(2011,2020)))
        data=[(year,2.0+(year-1993)*.3) for year in m.YEARS]
        self.assertAlmostEqual(m.slope_year(data),3.0,places=10)
        self.assertIsNone(m.slope_year(data[:3]))

    def test_no_ambiguous_source_boolean_or_count_zero(self):
        self.assertTrue(m.flag("True"))
        self.assertFalse(m.flag("False"))
        with self.assertRaises(ValueError):m.flag("likely")
        self.assertEqual(len(m.PAIRS),3)

    def test_fixed_axis_region_year_and_temporal_PCA(self):
        rows=[]
        for i in range(4):
            for y in m.YEARS:
                t=y-1993
                rows.append({
                    "site_id":"S"+str(i),"source_region":"R"+str(i),
                    "source_250km_block":"B"+str(i),
                    "GLORYS_cell_y":i,"GLORYS_cell_x":i,
                    "year":y,
                    "mean_source_SIC_pp":85-i*11-.6*t+.0007*t*t*(i+1),
                    "mean_GLORYS_salinity":34+i*.4-.04*t+.00012*t*t*i,
                    "mean_GLORYS_thetao_C":-2+i*.32+.02*t+.00011*t*t*(i+1)
                })
        summary,ry=m.marine_pca(rows)
        self.assertEqual(summary["observed_source_siteyear_rows"],4*28)
        self.assertEqual(summary["n_original_source_regions"],4)
        self.assertEqual(len(ry),4*28)
        self.assertAlmostEqual(sum(summary["spatial_siteyear_PC_explained"]),1.,places=11)
        self.assertAlmostEqual(sum(summary["within_source_site_28year_temporal_anomaly_PC_explained"]),1.,places=11)
        self.assertAlmostEqual(summary["source_region_mean_difference_fraction_of_PC1_variance"]+
                               summary["source_region_within_fraction_of_PC1_variance"],1.,places=11)
        self.assertEqual(len(summary["leave_one_original_region_out_PC1"]),4)
        region=m.original_region_temporal_change(rows,ry)
        self.assertEqual(len(region),4)
        for r in region:
            self.assertEqual(r["1993_2000_n_original_years"],8)
            self.assertEqual(r["2001_2010_n_original_years"],10)
            self.assertEqual(r["2011_2020_n_original_years"],10)

    def test_only_real_source_both_species_counts_enter_ratio(self):
        siteyears=[
            {"site_id":"A","year":2000,"source_region":"R1",
             "source_250km_block":"B1","GLORYS_cell_y":1,"GLORYS_cell_x":1,
             "warm_direction_three_var_marine_PCA_score":1.},
            {"site_id":"A","year":2001,"source_region":"R1",
             "source_250km_block":"B1","GLORYS_cell_y":1,"GLORYS_cell_x":1,
             "warm_direction_three_var_marine_PCA_score":2.},
            {"site_id":"B","year":2000,"source_region":"R2",
             "source_250km_block":"B2","GLORYS_cell_y":2,"GLORYS_cell_x":1,
             "warm_direction_three_var_marine_PCA_score":3.},
        ]
        counts=[
            {"site_id":"A","season":"2000","species":"ADPE",
             "observed_nest_count":"10","original_survey_method":"ground"},
            {"site_id":"A","season":"2000","species":"GEPE",
             "observed_nest_count":"0","original_survey_method":"ground"},
            {"site_id":"A","season":"2001","species":"GEPE",
             "observed_nest_count":"17","original_survey_method":"ground"},
            {"site_id":"B","season":"2000","species":"ADPE",
             "observed_nest_count":"12","original_survey_method":"aerial"}
        ]
        rows,report=m.true_observed_penguin_pairs(siteyears,counts)
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0]["original_source_same_method_both_species"])
        self.assertEqual(rows[0]["nests_second_species_actual_source_count"],0)
        self.assertEqual(report["ADPE__GEPE"]["n_actual_original_same_site_same_breeding_year_pair_records"],1)
        self.assertEqual(report["CHPE__GEPE"]["n_actual_original_same_site_same_breeding_year_pair_records"],0)

    def test_static_mapped_area_only_positive_and_not_annual(self):
        rows=[{
            "site_id":"Site1","source_region":"R1",
            "warm_direction_three_var_marine_PCA_score":0.5
        }]
        modern=[{"site_id":"Site1","region":"R1",
                 "mapped_terrestrial_union_area_2km_m2":"150",
                 "positive_mapped_detection":"True"},
                {"site_id":"Site1","region":"R1",
                 "mapped_terrestrial_union_area_2km_m2":"150",
                 "positive_mapped_detection":"True"}]
        modern += [{"site_id":"site_"+str(i),"region":"R1",
                    "mapped_terrestrial_union_area_2km_m2":"0",
                    "positive_mapped_detection":"False"} for i in range(244)]
        self.assertEqual(len(modern),246)
        mapped,report=m.mapped_static_land(rows,modern)
        self.assertEqual(len(mapped),1)
        self.assertTrue(mapped[0]["not_true_plant_absence_when_no_polygon"])
        self.assertTrue(report["map_is_static_2017_2023_composite_no_greening_time_change"])


if __name__=="__main__":
    unittest.main()
