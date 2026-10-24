"""Fictional original-Excel containers. Never open real AADC occupancy rows."""
import importlib.util,io,sys
from pathlib import Path
import zipfile
import pytest
pytest.importorskip("requests")
pytest.importorskip("xlrd")
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"scripts"))
import decode_aadc_original_site_occupancy_headers_v12 as m


def pretend_real_ooXml_two_sheets_swapped():
    book=(
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="1_metadata" sheetId="2" r:id="rIdB"/>'
        '<sheet name="2_search events" sheetId="1" r:id="rIdA"/></sheets></workbook>'
    )
    relationships=(
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rIdA" Target="worksheets/sheet1.xml" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>'
        '<Relationship Id="rIdB" Target="worksheets/sheet2.xml" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>'
        '</Relationships>'
    )
    sites=(
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<dimension ref="A1:B30000"/><sheetData><row r="1">'
        '<c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c>'
        '</row><row r="2"><c r="A2" t="inlineStr">'
        '<is><t>THIS_SENSITIVE_FAKE_OCCUPANCY_SITE_MUST_NOT_BE_PARSED</t></is></c>'
        '</row></sheetData></worksheet>'
    )
    metadata=(
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<dimension ref="A1:B4"/><sheetData><row r="1">'
        '<c r="A1" t="s"><v>2</v></c></row></sheetData></worksheet>'
    )
    strings=(
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<si><t>site_id</t></si><si><t>reported_presence</t></si>'
        '<si><t>metadata_key</t></si>'
        '<si><t>THIS_POST_HEADER_SHARED_STRING_IS_NOT_FOR_OUTPUT</t></si></sst>'
    )
    files={
        "xl/workbook.xml":book,
        "xl/_rels/workbook.xml.rels":relationships,
        "xl/worksheets/sheet1.xml":sites,
        "xl/worksheets/sheet2.xml":metadata,
        "xl/sharedStrings.xml":strings,
    }
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as z:
        for name,source in files.items():z.writestr(name,source)
    return b.getvalue()


def test_actual_excel_sheet_relationships_not_assumed_sequential():
    ans=m.original_sheet_headers_xlsx(pretend_real_ooXml_two_sheets_swapped())
    assert len(ans["original_sheets"])==2
    meta,events=ans["original_sheets"]
    assert meta["sheet_name"]=="1_metadata"
    assert meta["real_original_sheet_path"]=="xl/worksheets/sheet2.xml"
    assert meta["original_first_row_headers"]==["metadata_key"]
    assert events["sheet_name"]=="2_search events"
    assert events["real_original_sheet_path"]=="xl/worksheets/sheet1.xml"
    assert events["original_first_row_headers"]==["site_id","reported_presence"]
    assert ans["original_biological_rows_parsed"]==0
    assert "THIS_SENSITIVE_FAKE_OCCUPANCY_SITE_MUST_NOT_BE_PARSED" not in str(ans)
    assert "THIS_POST_HEADER_SHARED_STRING_IS_NOT_FOR_OUTPUT" not in str(ans)


def test_wrong_zip_missing_relations_fails_closed():
    original=pretend_real_ooXml_two_sheets_swapped()
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        parts={x:z.read(x) for x in z.namelist() if x!="xl/_rels/workbook.xml.rels"}
    output=io.BytesIO()
    with zipfile.ZipFile(output,"w") as z:
        for name,content in parts.items():z.writestr(name,content)
    with pytest.raises(ValueError,match="relationships missing"):
        m.original_sheet_headers_xlsx(output.getvalue())


def test_input_source_fingerprints_and_original_workbook_ids_are_fixed():
    assert m.PINNED_FILES["flying_seabird_original_occupancy"]=="4a03d8efc8f1579b2eafd982811c39edc00d2c87d49e990f93c6411db6860360"
    assert m.PINNED_FILES["penguin_original_occupancy"]=="8b38aa86f0ef2a0a9fe8c5bb13da904a9f2431cd503644b962b6e116ac3187ac"
    assert len(m.SOURCE_FILES)==4
    assert m.ADDITIONAL_GEO_NAME.endswith(".xlsx")
