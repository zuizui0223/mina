import unittest

import pandas as pd

from scripts.finalize_smp_spatial_recovery_hysteresis_support_v2 import (
    common_noncircular_shifts,
)
from scripts.run_smp_spatial_recovery_hysteresis_v2 import (
    noncircular_common_shift_null,
)


class HysteresisV2Tests(unittest.TestCase):
    def test_common_shifts_do_not_wrap(self):
        base = {
            "master_site_key": "M1",
            "phase_block_start": 2000,
            "phase_block_end": 2009,
            "phase_block_years": list(range(2000, 2010)),
        }
        spells = [
            {
                **base,
                "abandon_from": 2002,
                "abandon_to": 2003,
                "recolonize_from": 2006,
                "recolonize_to": 2007,
            },
            {
                **base,
                "abandon_from": 2003,
                "abandon_to": 2004,
                "recolonize_from": 2006,
                "recolonize_to": 2007,
            },
        ]
        shifts = common_noncircular_shifts(spells)
        self.assertIn(0, shifts)
        self.assertEqual(shifts, [-2, -1, 0, 1, 2])

    def test_monotonic_linear_path_is_not_special_under_same_gap_shifts(self):
        years = list(range(2000, 2010))
        parent = [100 + 20 * i for i in range(len(years))]
        mat = pd.DataFrame(
            {
                "background": parent,
                "S0": [2] * len(years),
                "S1": [2] * len(years),
                "S2": [2] * len(years),
            },
            index=years,
        )
        cache = {("sp0", "m0", "AON"): mat}
        base = {
            "species": "sp0",
            "master_site": "M0",
            "master_site_key": "M0",
            "unit": "AON",
            "phase_block_start": 2000,
            "phase_block_end": 2009,
            "phase_block_years": years,
            "state_complete_years": years,
            "shift_group_id": "M0|2000|2009",
        }
        local = []
        for site in ("S0", "S1", "S2"):
            local.append({
                **base,
                "site_id": site,
                "abandon_from": 2001,
                "abandon_to": 2002,
                "recolonize_from": 2005,
                "recolonize_to": 2006,
            })
        shifts = common_noncircular_shifts(local)
        spells = [
            {**sp, "eligible_common_shifts": shifts, "n_common_shifts": len(shifts)}
            for sp in local
        ]
        rows = []
        from scripts.run_smp_spatial_recovery_hysteresis_v1 import H_from_years
        for sp in spells:
            H = H_from_years(
                mat, sp["site_id"],
                sp["abandon_from"], sp["abandon_to"],
                sp["recolonize_from"], sp["recolonize_to"],
            )
            rows.append({**sp, "H": H})
        out = noncircular_common_shift_null(
            pd.DataFrame(rows),
            spells,
            cache,
            B=1000,
            seed=7,
        )
        self.assertGreater(out["upper_tail_p"], 0.1)


if __name__ == "__main__":
    unittest.main()
