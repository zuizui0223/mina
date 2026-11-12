#!/usr/bin/env python3
"""Arithmetic tests: original marine PCA, same-site co-census and static map."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

import numpy as np

spec=importlib.util.spec_from_file_location(
    "regime",Path(__file__).resolve().parent/"test_joint_marine_regime_axis.py")
regime=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(regime)


class MarineRegimeIndependentQA(unittest.TestCase):
    def test_strong_one_axis_in_three_collinear_physical_values(self):
        x=np.array([
            [0.,30.,-2.], [10.,31.,-1.], [20.,32.,0.],
            [30.,33.,1.], [40.,34.,2.], [50.,35.,3.]
        ],dtype=float)
        q=regime.pca(x)
        self.assertAlmostEqual(q["explained"][0],1.,places=12)
        self.assertAlmostEqual(sum(q["explained"]),1.,places=12)
        self.assertGreater(q["loadings"][2,0],0)
        self.assertEqual(q["scores"].shape,(6,3))
        self.assertAlmostEqual(float(np.mean(q["scores"][:,0])),0.,places=12)

    def test_reversed_salt_sign_must_remain_not_force_freshening(self):
        x=np.array([
            [90.,35.,-2.],[80.,34.,-1.],[70.,33.,0.],
            [60.,32.,1.],[50.,31.,2.],[40.,30.,3.]
        ])
        fit=regime.pca(x)
        load=fit["loadings"][:,0]
        self.assertGreater(load[2],0)
        self.assertLess(load[1],0)
        self.assertLess(load[0],0)

    def test_site_year_centered_annual_changes_not_same_as_site_geography(self):
        xs=[]
        for site,base in (("A",0.),("B",15.),("C",25.),("D",37.)):
            for year in range(2011,2021):
                y=year-2011
                xs.append({
                    "site_id":site,"source_region":"Region-"+site,
                    "year":year,
                    "source_SIC_pp":50.+base+y*.3,
                    "source_glorys_salinity":33.+base*.03-y*.01,
                    "source_glorys_thetao_C":-1.+base*.02+y*.09})
        out,seq=regime.fit_regime(xs)
        self.assertEqual(out["source_site_year_count"],40)
        self.assertEqual(len(seq),40)
        self.assertAlmostEqual(sum(out["pooled_standardized_PCA_explained"]),1.,places=12)
        self.assertAlmostEqual(sum(out["within_site_temporal_PCA_explained"]),1.,places=12)
        self.assertAlmostEqual(sum(out["region_equal_site_year_PCA_explained"]),1.,places=12)
        self.assertAlmostEqual(sum(out["equal_six_source_region_decadal_climatology_PCA_explained"]),1.,places=12)
        self.assertEqual(len(out["region_equal_site_year_PC1_loadings"]),3)
        dec=out["region_difference_decomposition"]
        self.assertAlmostEqual(
            dec["between_source_regions_fraction_of_pooled_original_PC1_variance"]
            +dec["within_source_regions_fraction"],1.,places=12)

    def test_true_cocensus_only_not_missing_species_zero(self):
        siteyears=[
            {"site_id":"A","year":2015,"source_region":"One",
             "source_250km_block":"1","empirical_warm_oriented_marine_PC1":1.},
            {"site_id":"A","year":2016,"source_region":"One",
             "source_250km_block":"1","empirical_warm_oriented_marine_PC1":2.},
            {"site_id":"B","year":2015,"source_region":"One",
             "source_250km_block":"2","empirical_warm_oriented_marine_PC1":3.}
        ]
        counts=[
            {"site_id":"A","season":"2015","species":"ADPE","observed_nest_count":"10"},
            {"site_id":"A","season":"2015","species":"GEPE","observed_nest_count":"0"},
            {"site_id":"A","season":"2016","species":"GEPE","observed_nest_count":"20"},
            {"site_id":"B","season":"2015","species":"ADPE","observed_nest_count":"5"}]
        observed,metadata=regime.penguin_composition(siteyears,counts)
        self.assertEqual(len(observed),1)
        self.assertEqual(metadata["ADPE__GEPE"]["n_exact_source_same_site_same_season_pairs"],1)
        self.assertEqual(observed[0]["nests_source_gentoo"],0)
        self.assertEqual(observed[0]["nests_source_baseline_species"],10)

    def test_static_vegetation_zero_is_detection_not_absence(self):
        sites=[{"site_id":"A","source_region":"One","empirical_warm_oriented_marine_PC1":0.2}]
        veg=[{"site_id":"A","cohort":"macro_40","radius_m":"2000",
              "vegetation_class":"Vegetation","mapped_area_m2":"0.0",
              "time_support":"2017-2023_composite",
              "annual_change_available":"False"}]+[
              {"site_id":f"other-{k}","cohort":"macro_40","radius_m":"2000",
               "vegetation_class":"Vegetation","mapped_area_m2":"2",
               "time_support":"2017-2023_composite","annual_change_available":"False"}
               for k in range(39)]
        points,record=regime.static_plants(sites,veg)
        self.assertEqual(record["n_sites_with_positive_mapped_vegetation_polygon_detection"],0)
        self.assertTrue(points[0]["zero_mapped_polygons_is_not_vegetation_absence"])
        self.assertFalse(record["vegetation_1986_to_2021_year_change_inferred"])


if __name__=="__main__":
    unittest.main()
