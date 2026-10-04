import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import shapefile

from scripts.audit_emperor_tracking_schema import (
    parse_colony_year,
    choose_date_field,
    inspect_archive,
)


class EmperorTrackingSchemaTests(unittest.TestCase):
    def test_filename_parser(self):
        self.assertEqual(parse_colony_year("Atka/Atka2017.shp"), ("Atka", 2017))
        self.assertEqual(parse_colony_year("x/Coulman_2024.shp"), ("Coulman", 2024))
        self.assertEqual(parse_colony_year("Washington2020.shp"), ("Washington", 2020))

    def test_date_field_detection(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "Atka2017"
            w = shapefile.Writer(str(base), shapeType=shapefile.POINT)
            w.field("Date", "C", size=20)
            w.field("Satellite", "C", size=20)
            for i, d in enumerate(("2017-04-01", "2017-05-01", "2017-06-01")):
                w.point(-8.2 + i*0.01, -70.6)
                w.record(d, "S1")
            w.close()
            r = shapefile.Reader(str(base) + ".shp")
            info = choose_date_field(r)
            self.assertEqual(info["selected"], "Date")
            self.assertEqual(info["distinct_dates"], 3)
            self.assertEqual(info["parsed_fraction"], 1.0)

    def test_archive_audit_synthetic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for colony in ("Atka", "Coulman", "Washington"):
                for year in range(2017, 2024):
                    base = root / f"{colony}{year}"
                    w = shapefile.Writer(str(base), shapeType=shapefile.POINT)
                    w.field("Date", "C", size=20)
                    for j, d in enumerate((f"{year}-04-01", f"{year}-05-01", f"{year}-06-01")):
                        w.point(10 + j*0.01, -70)
                        w.record(d)
                    w.close()
                    base.with_suffix(".prj").write_text(
                        'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
                        'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],'
                        'AUTHORITY["EPSG","4326"]]',
                        encoding="utf-8",
                    )
            bio = io.BytesIO()
            with zipfile.ZipFile(bio, "w") as z:
                for p in root.iterdir():
                    if p.suffix.lower() in {".shp", ".shx", ".dbf", ".prj"}:
                        z.write(p, p.name)
            contract = {
                "pass_gate": {
                    "minimum_named_colonies": 3,
                    "minimum_seasons_per_colony": 7,
                    "minimum_dates_in_at_least_n_seasons": 3,
                    "seasons_meeting_minimum_dates_per_colony": 6,
                }
            }
            out = inspect_archive(bio.getvalue(), contract)
            self.assertTrue(out["schema_gate_passed"])
            self.assertEqual(out["mapped_tracking_shapefiles"], 21)


if __name__ == "__main__":
    unittest.main()
