#!/usr/bin/env python3
"""Independent arithmetic smoke tests of symmetric decadal decomposition."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("decade", ROOT / "analyze_decadal_fixed_network_reweighting.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def rows(n0, n1, s0, s1):
    return [{
        "site_id": str(i), "species": "ADPE",
        "source_region": "R1" if i < 2 else "R2",
        "polar_250km_block": "B" + str(i),
        "latitude": lat,
        "n_original_count_years_early": 1,
        "n_original_count_years_late": 1,
        "site_median_observed_nests_early": a,
        "site_median_observed_nests_late": b,
        "decadal_original_aug_nov_SIC_early_pp": x,
        "decadal_original_aug_nov_SIC_late_pp": y
    } for i, (lat, a, b, x, y) in enumerate(zip((-61., -64., -67.), n0, n1, s0, s1))]


class TestDecades(unittest.TestCase):
    def test_ice_only(self):
        d = module.decompose(rows((10,20,30),(10,20,30),(50,60,70),(40,50,60)),0,1)
        self.assertAlmostEqual(d["physical_SIC_change_component_pp"], -10)
        self.assertAlmostEqual(d["count_reweighting_component_pp"], 0)
        self.assertAlmostEqual(d["southward_positive_latitudinal_reweighting_km"], 0)

    def test_reweight_only_and_shift_south(self):
        d = module.decompose(rows((30,20,10),(10,20,30),(30,60,90),(30,60,90)),0,1)
        self.assertAlmostEqual(d["physical_SIC_change_component_pp"], 0)
        self.assertGreater(d["count_reweighting_component_pp"], 0)
        self.assertGreater(d["southward_positive_latitudinal_reweighting_km"], 0)

    def test_both_terms_sum_and_offset(self):
        d = module.decompose(rows((30,20,10),(10,20,30),(30,60,90),(20,50,80)),0,1)
        self.assertAlmostEqual(d["physical_SIC_change_component_pp"], -10)
        self.assertGreater(d["count_reweighting_component_pp"], 0)
        self.assertAlmostEqual(d["experienced_SIC_change_pp"],
            d["physical_SIC_change_component_pp"]+d["count_reweighting_component_pp"])
        self.assertGreater(d["observational_compensation_fraction"], 0)

    def test_zero_counts_not_invented(self):
        self.assertIsNone(module.decompose(rows((0,0,0),(10,20,30),(20,40,60),(10,30,50)),0,1))

    def test_calendar_and_mixed_support_csv(self):
        self.assertIsNone(module.period_index(1989))
        self.assertEqual([module.period_index(v) for v in (1991,2000,2001,2020,2021)], [0,0,1,2,None])
        with tempfile.TemporaryDirectory() as tmp:
            fn=Path(tmp)/"mixed.csv"
            module.write_csv(fn,[{"a":1},{"a":2,"b":3}])
            self.assertTrue(fn.read_text().startswith("a,b\n"))


if __name__ == "__main__":
    unittest.main()
