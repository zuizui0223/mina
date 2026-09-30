import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd

from scripts.audit_signy_replication_support import (
    audit_table,
    read_official_zip,
    season_from_date,
    season_start,
)


class SeasonParsingTests(unittest.TestCase):
    def test_parse_season(self):
        self.assertEqual(season_start("1996-1997"),1996)
        self.assertEqual(season_start("1998/99"),1998)
        self.assertIsNone(season_start("A41"))
        self.assertEqual(season_from_date("15/12/1996"),1996)
        self.assertEqual(season_from_date("19/01/1998"),1997)


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


    def test_date_only_schema_can_reconstruct_season(self):
        rows=[]
        for t in range(1996,2008):
            for colony in ("A1 + A60","A2","A3","A4","A41"):
                rows.append({
                    "Season":colony,
                    "Date of nest count":f"15/12/{t}",
                    "Total number of nests":100,
                    "Date chick count":f"20/01/{t+1}",
                    "Total number of chicks":50,
                    "Comments":"",
                })
        out=audit_table(pd.DataFrame(rows))
        self.assertEqual(out["status"],"support_audited")
        self.assertTrue(out["gate"]["passes"])
        self.assertEqual(out["primary_window"]["seasons_present"][0],1996)


class OfficialZipTests(unittest.TestCase):
    def test_breeding_csv_selected_by_schema_not_filename(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"signy.zip"
            breeding=pd.DataFrame({
                "Colony":["A2","A3"],
                "Season":["1996-1997","1996-1997"],
                "Total number of pairs":[10,20],
                "Total number of chicks":[5,10],
            })
            gps=pd.DataFrame({"Latitude":[-60.7],"Longitude":[-45.6]})
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("weird_name.csv",breeding.to_csv(index=False))
                z.writestr("coordinates.csv",gps.to_csv(index=False))
            frame,meta=read_official_zip(path)
            self.assertEqual(meta["selected_csv"],"weird_name.csv")
            self.assertIn("Total number of chicks",frame.columns)
            self.assertIn("Total number of pairs",frame.columns)


    def test_unquoted_comment_commas_are_repaired_only_at_final_field(self):
        raw=(
            "Species,Colony,Season,Date pair count,Total number of pairs,"
            "Date chick count,Total number of chicks,Comments\n"
            "Adelie,A2,1996-1997,15/12/1996,100,20/01/1997,50,"
            "snow, meltwater, low area\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"signy.zip"
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("signy_adelie_breeding_success.csv",raw)
                z.writestr("GPS Adelie Colony.csv","Latitude,Longitude\n-60.7,-45.6\n")
            frame,meta=read_official_zip(path)
            self.assertEqual(frame.loc[0,"Total number of pairs"],"100")
            self.assertEqual(frame.loc[0,"Total number of chicks"],"50")
            self.assertEqual(frame.loc[0,"Comments"],"snow, meltwater, low area")
            self.assertEqual(meta["selected_overflow_comment_rows_repaired"],1)
            out=audit_table(frame)
            self.assertEqual(out["status"],"support_audited")


    def test_exact_total_pairs_header_beats_without_eggs_header(self):
        frame=pd.DataFrame({
            "SPECIES":["Adelie"],
            "SEASON":["1996-1997"],
            "COLONY":["A2"],
            "DATE_PAIR_COUNT":["15/12/1996"],
            "TOTAL_NUMBER_PAIRS_WITH_EGGS":[90],
            "TOTAL_NUMBER_OF_PAIRS_WITHOUT_EGGS":[10],
            "TOTAL_NUMBER_OF_PAIRS":[100],
            "DATE_CHICK_COUNT":["20/01/1997"],
            "TOTAL_NUMBER_OF_CHICKS":[50],
            "COMMENTS":[""],
        })
        out=audit_table(frame)
        self.assertEqual(out["semantics"]["pairs_col"],"TOTAL_NUMBER_OF_PAIRS")


if __name__=="__main__":
    unittest.main()
