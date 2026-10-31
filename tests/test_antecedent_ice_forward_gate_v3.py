"""Regression checks for source-backed antecedent SIC count hindcast."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"research/climate-penguin/work/scenario_support_v1"))
import antecedent_ice_forward_gate_v3 as v3


class AntecedentIceGate(unittest.TestCase):
    def test_source_months_and_folds(self):
        rows,audit=v3.load()
        self.assertEqual(audit["raw_ice_records"],9600)
        self.assertEqual(audit["count_records"],301)
        self.assertEqual(len(rows),264)
        out=v3.analyze(rows)
        ref=json.loads(v3.EXPECTED.read_text(encoding="utf-8"))
        v3.verify(out,ref)
        self.assertEqual(out["groups"]["all"]["n"],126)
        self.assertEqual(out["groups"]["timing"]["n"],95)

    def test_solver(self):
        b=v3.solve([[4.,1.],[1.,3.]],[1.,2.])
        self.assertAlmostEqual(b[0],1/11)
        self.assertAlmostEqual(b[1],7/11)

    def test_no_future_growth_leakage(self):
        rows,_=v3.load()
        original=[r for r in v3.analyze(rows)["predictions"] if r["t"]==2005]
        other=copy.deepcopy(rows)
        for r in other:
            if r["t"]>=2005:
                r["y"]+=10.0
        changed=[r for r in v3.analyze(other)["predictions"] if r["t"]==2005]
        for a,b in zip(original,changed):
            self.assertEqual(a["id"],b["id"])
            for key in v3.SPECS:
                self.assertAlmostEqual(a[key],b[key],places=10)

    def test_antecedent_exposure_only(self):
        rows,_=v3.load()
        self.assertGreaterEqual(min(r["t"] for r in rows),1994)
        self.assertTrue(all(0<=r["lag1"]<=100 and 0<=r["lag3"]<=100 for r in rows))
        for r in rows:
            self.assertGreaterEqual(r["lag3sd"],0)
        a=v3.analyze(rows)["predictions"]
        self.assertNotAlmostEqual(a[0]["lag1_raw"],a[0]["lag3_raw"],places=7)

    def test_within_site_scaling_different_from_raw(self):
        r,_=v3.load()
        out=v3.analyze(r)["groups"]["all"]
        self.assertNotAlmostEqual(out["lag3_raw_mae"],out["lag3_within_mae"],places=7)


if __name__=="__main__":
    unittest.main()
