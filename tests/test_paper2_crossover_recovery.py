import unittest

import numpy as np
import pandas as pd

from scripts.build_paper2_coupling_frame import (
    build_primary_coupling_frame,
    design_diagnostics,
)
from scripts.simulate_paper2_crossover_recovery import (
    oracle_crossover_estimate,
)


class CouplingFrameTests(unittest.TestCase):
    def test_uncovered_zero_sentinel_is_missing_not_ecological_zero(self):
        forcing = pd.DataFrame([
            {"unit_id":"ADPE|A","site_id":"A","species_id":"ADPE","region":"R1","ccamlr_id":"48.1","seasons":"1980;1985;1990;1995;2000"},
            {"unit_id":"ADPE|B","site_id":"B","species_id":"ADPE","region":"R1","ccamlr_id":"48.1","seasons":"1980;1985;1990;1995;2000"},
            {"unit_id":"ADPE|C","site_id":"C","species_id":"ADPE","region":"R2","ccamlr_id":"88.1","seasons":"1980;1985;1990;1995;2000"},
        ])
        result = {
            "decision":{"modeling_eligibility_by_species":{
                "ADPE":{"level":"ccamlr","covered_units":["ADPE|A","ADPE|B","ADPE|C"]}
            }}
        }
        hierarchy = pd.DataFrame([
            {"site_id":"A","mapped_ice_free_pixel_count_2000m":10,"mapped_ice_free_area_ha_2000m":100.0,"tier2_richness_2000m":2},
            {"site_id":"B","mapped_ice_free_pixel_count_2000m":0,"mapped_ice_free_area_ha_2000m":0.0,"tier2_richness_2000m":0},
            {"site_id":"C","mapped_ice_free_pixel_count_2000m":20,"mapped_ice_free_area_ha_2000m":200.0,"tier2_richness_2000m":4},
        ])
        terrain = pd.DataFrame([
            {"site_id":"A","elevation_relief_p90_p10_m_2000m":10.0},
            {"site_id":"B","elevation_relief_p90_p10_m_2000m":20.0},
            {"site_id":"C","elevation_relief_p90_p10_m_2000m":30.0},
        ])
        frame, audit = build_primary_coupling_frame(
            forcing, result, hierarchy, terrain, standardize=False
        )
        self.assertEqual(audit["eligible_coupling_units"], 3)
        self.assertEqual(audit["predictor_complete_units"], 2)
        self.assertEqual(audit["uncovered_breeding_option_units"], ["ADPE|B"])
        self.assertNotIn("ADPE|B", set(frame["unit_id"]))

    def test_standardizes_frozen_predictors_within_species(self):
        rows=[]
        h=[]
        t=[]
        for sp in ("ADPE","CHPE"):
            for i in range(6):
                uid=f"{sp}|S{sp[-1]}{i}"
                site=f"S{sp[-1]}{i}"
                rows.append({"unit_id":uid,"site_id":site,"species_id":sp,"region":"R1" if i<3 else "R2","ccamlr_id":"48.1" if i<3 else "88.1","seasons":"1980;1985;1990;1995;2000"})
                h.append({"site_id":site,"mapped_ice_free_pixel_count_2000m":10+i,"mapped_ice_free_area_ha_2000m":10.0*(i+1),"tier2_richness_2000m":1+i})
                t.append({"site_id":site,"elevation_relief_p90_p10_m_2000m":5.0*(i+1)})
        result={"decision":{"modeling_eligibility_by_species":{
            sp:{"level":"ccamlr","covered_units":[r["unit_id"] for r in rows if r["species_id"]==sp]}
            for sp in ("ADPE","CHPE")
        }}}
        frame,_=build_primary_coupling_frame(pd.DataFrame(rows),result,pd.DataFrame(h),pd.DataFrame(t))
        for sp,local in frame.groupby("species_id"):
            for col in ("A","H","R"):
                self.assertAlmostEqual(float(local[col].mean()),0.0,places=10)
                self.assertAlmostEqual(float(local[col].std(ddof=1)),1.0,places=10)
        np.testing.assert_allclose(frame["AH"], frame["A"]*frame["H"])

    def test_design_diagnostics_detect_full_rank_interaction(self):
        rng=np.random.default_rng(3)
        n=30
        frame=pd.DataFrame({
            "species_id":["ADPE"]*n,
            "forcing_group":["g1"]*15+["g2"]*15,
            "A":rng.normal(size=n),
            "H":rng.normal(size=n),
            "R":rng.normal(size=n),
        })
        frame["AH"]=frame["A"]*frame["H"]
        d=design_diagnostics(frame)["ADPE"]
        self.assertTrue(d["full_rank"])
        self.assertLess(d["max_vif"],10.0)
        self.assertLess(d["condition_number"],10.0)


class CrossoverRecoveryTests(unittest.TestCase):
    def test_oracle_recovery_recovers_strong_negative_interaction_without_noise(self):
        rows=[]
        for i in range(12):
            a=(i-5.5)/3.0
            h=((i*5)%12-5.5)/3.0
            rows.append({
                "unit_id":f"u{i}",
                "forcing_group":"g1" if i<6 else "g2",
                "A":a,"H":h,"R":((i*7)%12-5.5)/3.0,"AH":a*h,
                "seasons":"1980;1982;1984;1986;1988;1990;1992;1994;1996;1998;2000;2002;2004;2006;2008;2010;2012;2014;2016;2018;2020;2022;2024",
            })
        frame=pd.DataFrame(rows)
        estimate=oracle_crossover_estimate(
            frame,
            gamma=np.array([-0.1,0.0,-0.05,-0.5]),
            seed=11,
            forcing_sd=0.1,
            site_loading_sd=0.0,
            process_sd=0.0,
            observation_sd=0.0,
        )
        self.assertAlmostEqual(float(estimate["gamma_hat"][3]),-0.5,places=8)


if __name__=="__main__":
    unittest.main()
