import unittest

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("hierarchical integrated recovery tests require numpy/pandas") from exc

from scripts.simulate_paper2_integrated_hierarchical_recovery import (
    fit_hierarchical_dataset,
    group_center_traits,
    profile_process_sd,
)
from scripts.simulate_paper2_integrated_recovery import (
    simulate_integrated_dataset,
)


def dense_fixture():
    seasons=";".join(str(y) for y in range(1980,2026))
    vals=[
        (-1.5,-1.2),(-1.0,1.1),(-0.5,-0.8),(-0.2,1.4),
        (0.2,-1.1),(0.6,0.7),(1.0,-0.4),(1.4,1.0),
    ]
    frame=pd.DataFrame([
        {
            "unit_id":f"TEST|S{i}","site_id":f"S{i}","species_id":"TEST",
            "forcing_group":"G1" if i<4 else "G2",
            "A":a,"H":h,"AH":a*h,"seasons":seasons,
        }
        for i,(a,h) in enumerate(vals)
    ])
    rows=[]
    for _,row in frame.iterrows():
        for season in range(1980,2026):
            gid=f"{row['site_id']}|TEST|{season}"
            for family,accuracy in (
                ("direct","1"),("image_based","1"),
                ("direct","2-5"),("image_based","2-5"),
            ):
                rows.append({
                    "group_id":gid,"site_id":row["site_id"],"species_id":"TEST",
                    "season":season,"vantage_family":family,"accuracy_group":accuracy,
                })
    return {"TEST":frame},pd.DataFrame(rows)


class TraitCenteringTests(unittest.TestCase):
    def test_traits_are_centered_within_forcing_group(self):
        frames,_=dense_fixture()
        centered=group_center_traits(frames["TEST"])
        for _,g in centered.groupby("forcing_group"):
            self.assertAlmostEqual(float(g["Ac"].mean()),0.0,places=12)
            self.assertAlmostEqual(float(g["Hc"].mean()),0.0,places=12)
            self.assertAlmostEqual(float(g["AHc"].mean()),0.0,places=12)


class ProcessProfileTests(unittest.TestCase):
    def test_profile_process_sd_respects_frozen_bounds(self):
        residual=np.zeros(20)
        duration=np.ones(20)
        obs_var=np.repeat(0.01,20)
        estimate=profile_process_sd(
            residual,duration,obs_var,
            min_sd=0.005,max_sd=0.30,grid_size=80,
        )
        self.assertGreaterEqual(estimate,0.005)
        self.assertLessEqual(estimate,0.30)


class DenseHierarchicalRecoveryTests(unittest.TestCase):
    def test_dense_count_pipeline_recovers_crossover(self):
        frames,metadata=dense_fixture()
        sim=simulate_integrated_dataset(
            frames,metadata,
            gamma_a=0.0,gamma_ah=-0.35,seed=222,
            forcing_sd=0.08,loading_sd=0.10,process_sd=0.02,
            drift_mean=-0.01,drift_sd=0.005,
            delta_image=np.log(1.15),
            sigma1=np.log(1.05),sigma2plus=np.log(1.25),
        )
        fit=fit_hierarchical_dataset(frames,sim["observations"],sim["truth"])
        species=fit["species"]["TEST"]
        self.assertLess(abs(species["gamma_ah"]+0.35),0.10)
        self.assertGreater(species["lambda_correlation"],0.75)
        for value in species["forcing_correlation"].values():
            self.assertGreater(value,0.80)
        for value in species["group_mean_lambda"].values():
            self.assertAlmostEqual(value,1.0,places=8)
        self.assertNotAlmostEqual(species["process_sd_initial"],0.02,places=8)
        self.assertTrue(np.isfinite(species["process_sd"]))

    def test_dense_simple_buffering_does_not_invent_crossover(self):
        frames,metadata=dense_fixture()
        sim=simulate_integrated_dataset(
            frames,metadata,
            gamma_a=-0.25,gamma_ah=0.0,seed=333,
            forcing_sd=0.08,loading_sd=0.10,process_sd=0.02,
            drift_mean=-0.01,drift_sd=0.005,
            delta_image=np.log(1.15),
            sigma1=np.log(1.05),sigma2plus=np.log(1.25),
        )
        fit=fit_hierarchical_dataset(frames,sim["observations"],sim["truth"])
        species=fit["species"]["TEST"]
        self.assertLess(abs(species["gamma_a"]+0.25),0.12)
        self.assertLess(abs(species["gamma_ah"]),0.10)


if __name__=="__main__":
    unittest.main()
