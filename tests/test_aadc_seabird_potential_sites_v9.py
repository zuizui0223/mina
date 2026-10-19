"""Synthetic source containers only: no Antarctic occupancy outcomes are opened."""
import importlib.util
import io
from pathlib import Path
import zipfile

import pytest
pytest.importorskip("requests")

p=Path(__file__).resolve().parents[1]/"scripts"/"audit_aadc_seabird_potential_sites_v9.py"
spec=importlib.util.spec_from_file_location("aadc",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_original_archive_csv_headers_without_site_species_counts():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("sample/search_events.csv",
                   "site_id,species,year,certainty,presence\nA1,Adelie,1980,H,0\n")
        z.writestr("sample/site_land_areas.csv",
                   "site_id,area_km2,land_class\nA1,2.1,island\n")
    detail=m.payload_structure(buf.getvalue(),"fake")
    assert detail["format"]=="zip_archive"
    assert detail["original_archive_member_count"]==2
    assert detail["biological_record_rows_opened"]==0
    assert detail["original_archived_member_schema"][0]["first_line_column_headers"]==[
        "site_id","species","year","certainty","presence"]
    assert "A1" not in str(detail)


def test_genuine_spreadsheet_workbook_metadata_only_no_sheet_cell_values():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
        z.writestr("xl/workbook.xml",
                   '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<sheets><sheet name="Search Events" sheetId="1" />'
                   '<sheet name="Geographic Sites" sheetId="2" /></sheets></workbook>')
        z.writestr("xl/worksheets/sheet1.xml",'<worksheet><sheetData><row><c><v>999999</v></c></row></sheetData></worksheet>')
    result=m.payload_structure(buf.getvalue(),"fake workbook")
    assert result["format"]=="xlsx_zip"
    assert result["workbook"]["source_record_rows_opened"]==0
    assert [s["sheet_name"] for s in result["workbook"]["sheets"]]==["Search Events","Geographic Sites"]
    assert "999999" not in str(result)


def test_raw_html_redirect_not_an_original_download():
    with pytest.raises(ValueError,match="HTML"):
        m.payload_structure(b"<!doctype html><body>Please log in</body>","original")


def test_zip_path_traversal_is_source_stop():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w") as z:
        z.writestr("../private.csv","site,occupancy\nno,no\n")
    with pytest.raises(ValueError,match="unsafe"):
        m.payload_structure(buf.getvalue(),"original")


def test_original_dataset_DOIs_not_confused_with_2023_APBP():
    assert m.DATASETS["all_potential_icefree_sites_4884"]["doi"]=="10.26179/53yk-8z83"
    assert m.DATASETS["eight_seabirds_effort_occupancy"]["doi"]=="10.26179/5n29-r073"
    assert m.MAX_BYTES<=100_000_000
