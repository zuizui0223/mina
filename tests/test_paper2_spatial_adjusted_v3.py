import unittest
import numpy as np
import pandas as pd
from scripts.simulate_paper2_spatial_adjusted_v3 import center_within_block, solve_site_gamma_block

class CenterTests(unittest.TestCase):
    def test_traits_center_within_block(self):
        f=pd.DataFrame({
            "trait_block":["A","A","B","B"],
            "A":[1.,3.,10.,14.],"H":[2.,4.,5.,9.],"AH":[2.,12.,50.,126.]
        })
        x=center_within_block(f)
        for _,g in x.groupby("trait_block"):
            self.assertAlmostEqual(float(g.Ac.mean()),0,places=12)
            self.assertAlmostEqual(float(g.Hc.mean()),0,places=12)
            self.assertAlmostEqual(float(g.AHc.mean()),0,places=12)

class LoadingConstraintTests(unittest.TestCase):
    def test_block_residual_means_and_weighted_alpha_identification(self):
        frame=pd.DataFrame({
            "Ac":[-1.,1.,-1.,1.],"Hc":[-1.,1.,1.,-1.],"AHc":[1.,1.,-1.,-1.],
            "trait_block":["A","A","B","B"]
        })
        intervals=[
            {"site":0,"group":"G","first":1980,"last":1981,"duration":1.,"delta":.2,"obs_var":.01},
            {"site":1,"group":"G","first":1980,"last":1981,"duration":1.,"delta":-.1,"obs_var":.01},
            {"site":2,"group":"G","first":1980,"last":1981,"duration":1.,"delta":.1,"obs_var":.01},
            {"site":3,"group":"G","first":1980,"last":1981,"duration":1.,"delta":-.2,"obs_var":.01},
        ]
        forcing={"G":np.r_[np.array([.1]),np.zeros(44)]}
        mu,lam,gamma,alpha,resid,sd=solve_site_gamma_block(
            intervals,frame,forcing,0.04,0.15
        )
        self.assertAlmostEqual(float(resid[:2].mean()),0,places=8)
        self.assertAlmostEqual(float(resid[2:].mean()),0,places=8)
        self.assertAlmostEqual(float(alpha.mean()),0,places=8)
        self.assertAlmostEqual(float(lam.mean()),1,places=8)

if __name__=="__main__":
    unittest.main()
