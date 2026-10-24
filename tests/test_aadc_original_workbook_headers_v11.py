"""Only synthetic OOXML and OLE headers; absolutely no original search results."""
import importlib.util
import io
from pathlib import Path
import zipfile
import pytest
pytest.importorskip("requests")
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("aadc_header",root/"scripts/audit_aadc_original_workbook_headers_v11.py")
x=importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)


def pretend_xlsx():
    content={
        "xl/workbook.xml":(
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheets><sheet name="Site search events" sheetId="1"/></sheets></workbook>'
        ),
        "xl/worksheets/sheet1.xml":(
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<dimension ref="A1:C30000"/>'
            '<sheetData><row r="1">'
            '<c r="A1" t="inlineStr"><is><t>site_id</t></is></c>'
            '<c r="B1" t="inlineStr"><is><t>survey_year</t></is></c>'
            '<c r="C1" t="inlineStr"><is><t>occupancy</t></is></c>'
            '</row><row r="2">'
            '<c r="A2" t="inlineStr"><is><t>REAL_SITE_SECRET_SHOULD_NOT_READ</t></is></c>'
            '<c r="C2" t="inlineStr"><is><t>PRESENCE</t></is></c>'
            '</row></sheetData></worksheet>'
        ),
    }
    blob=io.BytesIO()
    with zipfile.ZipFile(blob,"w",zipfile.ZIP_DEFLATED) as archive:
        for name,data in content.items():archive.writestr(name,data)
    return blob.getvalue()


def test_exact_original_api_dataset_uuids_and_Dois_are_pinned():
    assert x.DATASETS["5959"]["uuid"].lower()=="b766a3e4-ae94-40c0-b340-9e544d8f5dc3"
    assert x.DATASETS["4344"]["doi"]=="10.26179/53yk-8z83"
    assert len(x.SOURCE_FILES)==4
    assert all(name.startswith("2_Site and search effort") for name in x.SOURCE_FILES.values())


def test_first_row_only_header_ignores_even_following_fake_observations():
    result=x.original_xlsx_sheet_headers(pretend_xlsx())
    assert result["format"]=="xlsx"
    assert result["original_biological_rows_opened"]==0
    assert result["sheets"][0]["name"]=="Site search events"
    assert result["sheets"][0]["worksheet_declared_extent"]=="A1:C30000"
    assert [r["raw_first_row_value"] for r in result["sheets"][0]["first_row_values_or_sharedString_indices"]]==[
        "site_id","survey_year","occupancy"
    ]
    assert "REAL_SITE_SECRET_SHOULD_NOT_READ" not in str(result)
    assert "PRESENCE" not in str(result)


def test_publisher_csv_renamed_xlsx_is_not_analyzed_as_excel():
    with pytest.raises(zipfile.BadZipFile):
        x.original_xlsx_sheet_headers(b"site,presence\nTEST,1\n")


def test_original_legacy_xls_requires_real_BIFF_header_and_no_rows():
    header=bytes.fromhex("D0CF11E0A1B11AE1")+b"\x00"*128
    result=x.binary_xls_source_structure(header)
    assert result["format"]=="legacy_xls_ole2"
    assert result["original_biological_rows_opened"]==0
    with pytest.raises(ValueError,match="OLE2"):
        x.binary_xls_source_structure(b"<html>not data</html>")


def test_source_link_uses_fixed_https_publisher():
    assert x.LIST_API=="https://data.aad.gov.au/eds/api/dataset?size=10000"
    assert x.HOST=="data.aad.gov.au"
