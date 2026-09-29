import math
import unittest

import numpy as np
import pandas as pd

from scripts.run_paper2_coupling_diagnostic import (
    estimate_image_offsets,
    leave_one_out_forcing,
    estimate_lambda,
    fit_trait_regression,
)


class ObservationHarmonizationTests(unittest.TestCase):
    def test_species_image_offset_recovers_multiplicative_bias(self):
        rows = []
        # log1p(image) is exactly log1p(direct) + log(2) in each mixed season.
        for season, base in [(2000, 9.0), (2001, 19.0), (2002, 39.0)]:
            direct_log = math.log1p(base)
            image_count = math.exp(direct_log + math.log(2.0)) - 1.0
            rows.extend([
                {"site_id":"S1","species_id":"ADPE","season":season,"count":base,"vantage":"ground"},
                {"site_id":"S1","species_id":"ADPE","season":season,"count":image_count,"vantage":"uav"},
            ])
        offsets = estimate_image_offsets(pd.DataFrame(rows))
        self.assertAlmostEqual(offsets["ADPE"], math.log(2.0), places=10)


class LeaveOneOutTests(unittest.TestCase):
    def test_focal_unit_never_enters_its_forcing(self):
        residuals = pd.DataFrame([
            {"species_id":"ADPE","forcing_group":"G","unit_id":"u1","season":2000,"residual":100.0},
            {"species_id":"ADPE","forcing_group":"G","unit_id":"u2","season":2000,"residual":1.0},
            {"species_id":"ADPE","forcing_group":"G","unit_id":"u3","season":2000,"residual":2.0},
            {"species_id":"ADPE","forcing_group":"G","unit_id":"u4","season":2000,"residual":3.0},
        ])
        matched = leave_one_out_forcing(residuals, min_peers=3)
        u1 = matched[matched["unit_id"]=="u1"].iloc[0]
        self.assertEqual(u1["peer_n"], 3)
        self.assertAlmostEqual(u1["forcing_raw"], 2.0)

    def test_lambda_requires_six_matched_seasons(self):
        five = pd.DataFrame({
            "residual":[0,1,2,3,4],
            "forcing_raw":[0,1,2,3,4],
        })
        self.assertIsNone(estimate_lambda(five, min_n=6))


class LambdaRecoveryTests(unittest.TestCase):
    def test_lambda_recovers_known_loading_after_forcing_standardization(self):
        forcing = np.arange(-5.0, 5.0)
        z = (forcing - forcing.mean()) / forcing.std(ddof=1)
        residual = 2.5 * z + 0.3
        frame = pd.DataFrame({"residual": residual, "forcing_raw": forcing})
        result = estimate_lambda(frame, min_n=6)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["lambda"], 2.5, places=10)
        self.assertEqual(result["n_matched"], 10)


class TraitRegressionTests(unittest.TestCase):
    def test_interaction_coefficient_is_recovered(self):
        rng = np.random.default_rng(123)
        n = 60
        A = rng.normal(size=n)
        H = rng.normal(size=n)
        R = rng.normal(size=n)
        group = np.where(np.arange(n) % 2 == 0, "g1", "g2")
        lam = 0.2*A + 0.1*H - 0.05*R - 1.25*A*H + (group=="g2")*0.4
        df = pd.DataFrame({
            "lambda":lam,
            "A":A,
            "H":H,
            "R":R,
            "forcing_group":group,
        })
        fit = fit_trait_regression(df, "lambda", permutations=0)
        self.assertAlmostEqual(fit["coefficients"]["A_x_H"], -1.25, places=8)
        self.assertAlmostEqual(fit["marginal_H_at_A_minus1"], 1.35, places=8)
        self.assertAlmostEqual(fit["marginal_H_at_A_plus1"], -1.15, places=8)


if __name__ == "__main__":
    unittest.main()
