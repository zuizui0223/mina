import unittest

import pandas as pd

from scripts.audit_signy_replication_support import audit_table, season_start


class SeasonParsingTests(unittest.TestCase):
    def test_parse_season(self):
        self.assertEqual(season_start("1996-1997"),1996)
        self.assertEqual(season_start("1998/99"),1998)
        self.assertIsNone(season_start("A41"))


class SupportAuditTests(unittest.TestCase):
    def test_synthetic_support_passes_without_effect(self):
        rows=[]
        for t in range(1996,2008):
            season=f"{t}-{t+1}"
            for colony in ("A1 + A60","A2","A3","A4","A41"):
                rows.append({
                    "Colony":colony,
                    "Season":season,
                    "Total number of nests":100,
                    "Total number of chicks":50,
                    "Comments":"",
                })
        out=audit_table(pd.DataFrame(rows))
        self.assertEqual(out["status"],"support_audited")
        self.assertTrue(out["gate"]["passes"])
        self.assertFalse(out["effect_computed"])
        self.assertTrue(out["nonmissing_support"]["pooled_label_enters_primary"])

    def test_missing_chick_column_fails_schema(self):
        frame=pd.DataFrame({
            "Colony":["A1","A2"],
            "Season":["1996-1997","1996-1997"],
            "Total number of nests":[1,2],
        })
        out=audit_table(frame)
        self.assertEqual(out["status"],"schema_unresolved")
        self.assertIn("chicks_col",out["missing_roles"])
        self.assertFalse(out["effect_computed"])


if __name__=="__main__":
    unittest.main()
