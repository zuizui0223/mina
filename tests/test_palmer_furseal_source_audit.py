"""Offline original-file metadata audit unit tests; no network or ecological inference."""
import importlib.util
from pathlib import Path

SCRIPT = (Path(__file__).resolve().parents[1] /
          "research/climate-penguin/work/abandonment/audit_furseal_2020_source.py")
spec = importlib.util.spec_from_file_location("seal_audit", SCRIPT)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def test_file_ids_and_year_contract():
    assert list(a.FILE_IDS) == [
        "drone_survey_dates_times.csv",
        "fur_seal_locations_all_surveys.csv",
        "fur_seal_locations_d72_d46.csv",
    ]
    assert a.DOI == "10.5061/dryad.qv9s4mwp0"


def test_csv_rejects_html_and_bad_rows():
    def fake(url):
        if "/api/v2/" in url:
            return b"<html>Not data</html>"
        return b"date,site,x,y\n2020-01-17,Litchfield,200,100\n"
    data, raw = a.download_public_csv("t.csv", 3801884, getter=fake)
    assert len(data["rows"]) == 1 and data["rows"][0]["site"] == "Litchfield"
    assert data["source_url"].endswith("3801884")
    assert raw.startswith(b"date,site")


def test_no_site_name_is_not_verified_absence():
    support = a.field_support([{"x": "1", "y": "2", "date": "2020-01-01"},
                               {"x": "2", "y": "3", "date": "2020-01-03"}])
    assert support["named_island_record_matches"]["litchfield"] == 0
    assert support["site_label_columns"] == []
    assert support["coordinate_support"]["n_numeric"] == 2


def test_repeat_records_not_independent_islands():
    s = a.field_support([{"site": "Litchfield", "easting": "100", "northing": "200"},
                         {"site": "Litchfield", "easting": "101", "northing": "201"},
                         {"site": "Torgersen", "easting": "102", "northing": "199"}])
    assert s["named_island_record_matches"]["litchfield"] == 2
    assert s["named_island_record_matches"]["torgersen"] == 1
    assert s["coordinate_support"]["bounds"] == [100, 199, 102, 201]
