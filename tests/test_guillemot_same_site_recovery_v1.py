import unittest

import pandas as pd

from scripts.run_guillemot_same_site_recovery_v1 import analyse, extract_spells


def synthetic(aligned=True):
    rows = []
    years = list(range(2000, 2020))
    for c in range(5):
        sub = f"C{c+1}"
        for j in range(4):
            site = f"{sub}-S{j+1}"
            for year in years:
                occupied = 1
                if year in (2003, 2004, 2008, 2009):
                    occupied = 0
                size = 30
                if aligned:
                    if year in (2002, 2003, 2007, 2008):
                        size = 8
                    if year in (2004, 2005, 2009, 2010):
                        size = 120
                else:
                    size = 30
                rows.append({
                    "subcolony": sub,
                    "site_id": site,
                    "year": year,
                    "occupied": occupied,
                    "subcolony_size": size,
                })
    return pd.DataFrame(rows)


class GuillemotRecoveryTests(unittest.TestCase):
    def test_completed_spells_are_same_site_and_first_colonization_is_not_used(self):
        df = synthetic(True)
        spells = extract_spells(df)
        self.assertEqual(len(spells), 40)
        self.assertEqual(spells["site_id"].nunique(), 20)
        self.assertTrue((spells["vacancy_duration_years"] == 2).all())

    def test_strong_event_aligned_signal_is_recovered(self):
        r = analyse(synthetic(True), B=1999, seed=20261005)
        self.assertTrue(r["support"]["passed"])
        self.assertGreater(r["T_obs"], 0)
        self.assertLessEqual(r["exact_subcolony_signflip_p"], 0.05)
        self.assertGreater(r["shift_null"]["delta_shift"], 0)
        self.assertLessEqual(r["shift_null"]["upper_tail_p"], 0.05)
        self.assertTrue(r["decision"]["same_site_recovery_asymmetry_supported"])

    def test_reversible_state_is_not_supported(self):
        r = analyse(synthetic(False), B=499, seed=20261005)
        self.assertTrue(r["support"]["passed"])
        self.assertAlmostEqual(r["T_obs"], 0.0, places=12)
        self.assertFalse(r["decision"]["same_site_recovery_asymmetry_supported"])

    def test_missing_year_breaks_spell(self):
        df = synthetic(True)
        df = df.loc[~((df["site_id"] == "C1-S1") & (df["year"] == 2004))].copy()
        spells = extract_spells(df)
        # The first C1-S1 spell is broken; its second completed spell remains.
        self.assertEqual(len(spells), 39)


if __name__ == "__main__":
    unittest.main()
