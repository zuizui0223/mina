import unittest

try:
    import numpy as np
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("latent-factor recovery tests require numpy/pandas") from exc

from scripts.simulate_paper2_latent_factor_recovery import (
    evaluate_recovery_gate,
    fit_unknown_factor,
    select_recovered_scale,
    simulate_latent_schedule,
)


def dense_frame():
    rows = []
    seasons = ";".join(str(y) for y in range(1980, 2026))
    vals = [
        (-1.5, -1.2), (-1.0, 1.1), (-0.5, -0.8), (-0.2, 1.4),
        (0.2, -1.1), (0.6, 0.7), (1.0, -0.4), (1.4, 1.0),
    ]
    for i, (a, h) in enumerate(vals):
        rows.append({
            "unit_id": f"u{i}",
            "species_id": "TEST",
            "forcing_group": "G1" if i < 4 else "G2",
            "A": a,
            "H": h,
            "AH": a * h,
            "seasons": seasons,
        })
    return pd.DataFrame(rows)


class LatentFactorRecoveryTests(unittest.TestCase):
    def test_noiseless_dense_schedule_recovers_negative_interaction(self):
        frame = dense_frame()
        sim = simulate_latent_schedule(
            frame,
            gamma_ah=-0.40,
            seed=11,
            forcing_sd=0.10,
            loading_sd=0.0,
            process_sd=0.0,
            drift_mean=-0.01,
            drift_sd=0.0,
        )
        fit = fit_unknown_factor(frame, sim["intervals"], iterations=8)
        self.assertLess(abs(fit["gamma_ah"] + 0.40), 0.05)
        for value in fit["forcing_correlation"].values():
            self.assertGreater(value, 0.98)

    def test_estimated_loadings_are_normalized_within_group(self):
        frame = dense_frame()
        sim = simulate_latent_schedule(
            frame,
            gamma_ah=-0.35,
            seed=19,
            forcing_sd=0.08,
            loading_sd=0.10,
            process_sd=0.02,
            drift_mean=-0.01,
            drift_sd=0.01,
        )
        fit = fit_unknown_factor(frame, sim["intervals"], iterations=8)
        out = frame.assign(lambda_hat=fit["lambda_hat"])
        means = out.groupby("forcing_group")["lambda_hat"].mean()
        for value in means:
            self.assertAlmostEqual(float(value), 1.0, places=8)

    def test_recovery_gate_requires_factor_and_interaction_recovery(self):
        passing = {
            "forcing_groups": {
                "G1": {"median_corr": 0.90, "q05_corr": 0.70},
                "G2": {"median_corr": 0.80, "q05_corr": 0.40},
            },
            "crossover": {"median_gamma_ah": -0.34, "negative_fraction": 0.98},
            "null": {"median_gamma_ah": 0.01, "q05_gamma_ah": -0.10, "q95_gamma_ah": 0.12},
        }
        self.assertTrue(evaluate_recovery_gate(passing, crossover_truth=-0.35)["passes"])

        failing = {
            **passing,
            "forcing_groups": {
                "G1": {"median_corr": 0.90, "q05_corr": 0.70},
                "G2": {"median_corr": 0.45, "q05_corr": 0.05},
            },
        }
        self.assertFalse(evaluate_recovery_gate(failing, crossover_truth=-0.35)["passes"])

    def test_scale_selection_falls_back_to_species_wide(self):
        regional = {"passes": False}
        specieswide = {"passes": True}
        self.assertEqual(
            select_recovered_scale("apbp_region", regional, specieswide),
            "species_wide",
        )
        self.assertIsNone(
            select_recovered_scale(
                "apbp_region",
                {"passes": False},
                {"passes": False},
            )
        )


if __name__ == "__main__":
    unittest.main()
