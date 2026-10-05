import unittest

import pandas as pd

from scripts.gate_smp_spatial_recovery_hysteresis_support_v1 import (
    completed_spells_for_site,
    pseudo_start_years,
)
from scripts.run_smp_spatial_recovery_hysteresis_v1 import (
    H_at_start,
    hierarchical_means,
    trajectory_drift_null,
)


class HysteresisTests(unittest.TestCase):
    def test_completed_spell_requires_consecutive_zero_run(self):
        years = [2000, 2001, 2002, 2003, 2004]
        states = [
            "observed_positive",
            "explicit_zero",
            "explicit_zero",
            "observed_positive",
            "observed_positive",
        ]
        out = completed_spells_for_site(years, states)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["abandon_from"], 2000)
        self.assertEqual(out[0]["recolonize_from"], 2002)
        self.assertEqual(out[0]["recolonize_to"], 2003)
        self.assertEqual(out[0]["transition_gap_years"], 2)

    def test_gap_breaks_spell(self):
        years = [2000, 2001, 2003]
        states = ["observed_positive", "explicit_zero", "observed_positive"]
        self.assertEqual(completed_spells_for_site(years, states), [])

    def test_pseudo_placements_preserve_elapsed_time(self):
        years = list(range(2000, 2011))
        starts = pseudo_start_years(years, transition_gap_years=2)
        self.assertEqual(starts, list(range(2000, 2008)))

    def test_H_at_start_positive_when_later_parent_state_is_higher(self):
        mat = pd.DataFrame(
            {
                "focal": [10, 0, 0, 5],
                "other1": [40, 35, 80, 90],
                "other2": [20, 20, 30, 40],
            },
            index=[2000, 2001, 2002, 2003],
        )
        self.assertGreater(H_at_start(mat, "focal", 2000, 2), 0)

    def test_hierarchical_means_equal_weight_species(self):
        rows = []
        for s in range(6):
            species = f"sp{s}"
            for m in range(2):
                rows.append(
                    {
                        "species": species,
                        "master_site": f"M{s}-{m}",
                        "site_id": f"S{s}-{m}",
                        "H": 0.2 + 0.01 * s,
                    }
                )
        out = hierarchical_means(pd.DataFrame(rows))
        self.assertGreater(out["T"], 0)
        self.assertEqual(len(out["species"]), 6)

    def test_trajectory_null_uses_frozen_pseudo_starts(self):
        years = list(range(2000, 2008))
        mat = pd.DataFrame(
            {
                "focal": [5, 0, 0, 4, 4, 4, 4, 4],
                "other": [10, 11, 12, 13, 14, 15, 16, 17],
            },
            index=years,
        )
        spell = {
            "species": "sp1",
            "master_site": "M1",
            "unit": "AON",
            "site_id": "focal",
            "transition_gap_years": 2,
            "pseudo_start_years": [2000, 2001, 2002, 2003, 2004],
        }
        observed = pd.DataFrame(
            [{
                "species": "sp1",
                "master_site": "M1",
                "site_id": "focal",
                "H": H_at_start(mat, "focal", 2000, 2),
            }]
        )
        cache = {("sp1", "m1", "AON"): mat}
        out = trajectory_drift_null(observed, [spell], cache, B=200, seed=9)
        self.assertEqual(out["simulations"], 200)
        self.assertIn("upper_tail_p", out)
        self.assertIn("delta_T_observed_minus_median", out)


if __name__ == "__main__":
    unittest.main()
