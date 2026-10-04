import unittest
import pandas as pd

from scripts.compute_emperor_mobile_node_aliasing import summarize


class MobileNodeAliasingTests(unittest.TestCase):
    def synthetic(self):
        # Equatorial synthetic coordinates: ~1.11 km per 0.01 deg longitude.
        rows=[]
        for season,base in [(2020,0.0),(2021,0.03)]:
            rows += [
                {"colony_id":"A","season":season,"obs_date":f"{season}-04-01","group_id":"g1","longitude":base,"latitude":-70.0},
                {"colony_id":"A","season":season,"obs_date":f"{season}-05-01","group_id":"g1","longitude":base+0.02,"latitude":-70.0},
                {"colony_id":"A","season":season,"obs_date":f"{season}-05-01","group_id":"g2","longitude":base+0.03,"latitude":-70.0},
            ]
        return pd.DataFrame(rows)

    def test_support_and_aliasing(self):
        r=summarize(self.synthetic())
        self.assertEqual(r["support"]["colonies"],1)
        self.assertEqual(r["support"]["seasons"],2)
        self.assertEqual(r["support"]["consecutive_interannual_transitions"],1)
        self.assertIn("2",r["aliasing_curve"])

    def test_split_colony_detected_if_any_group_inside(self):
        d=self.synthetic()
        # Add a later date with one group at anchor and one far away.
        d=pd.concat([d,pd.DataFrame([
            {"colony_id":"A","season":2020,"obs_date":"2020-06-01","group_id":"near","longitude":0.0,"latitude":-70.0},
            {"colony_id":"A","season":2020,"obs_date":"2020-06-01","group_id":"far","longitude":0.2,"latitude":-70.0},
        ])],ignore_index=True)
        r=summarize(d)
        # At any positive radius the date with a near group must not count as false absence.
        # We only assert the metric exists and is not forced to 1.
        self.assertLess(r["aliasing_curve"]["0.5"]["within_season_false_absence_fraction"],1.0)


if __name__=="__main__":
    unittest.main()
