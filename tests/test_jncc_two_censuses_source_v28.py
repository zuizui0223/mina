"""Only synthetic XLSX fixtures; preserve source numeric magnitudes unopened."""
import io,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_two_censuses_source_v28 as v
import pytest

def sample():
    buf=io.BytesIO()
    book='<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="OriginalSites" sheetId="1" r:id="rId1"/></sheets></workbook>'
    rels='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="x" Target="worksheets/sheet1.xml"/></Relationships>'
    sheet='<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:C2"/><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>SiteID</t></is></c><c r="B1" t="inlineStr"><is><t>Species</t></is></c><c r="C1" t="inlineStr"><is><t>Census2000</t></is></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>FakeSite</t></is></c><c r="B2" t="inlineStr"><is><t>FakeBird</t></is></c><c r="C2"><v>999999</v></c></row></sheetData></worksheet>'
    with zipfile.ZipFile(buf,"w") as z:
        z.writestr("xl/workbook.xml",book)
        z.writestr("xl/_rels/workbook.xml.rels",rels)
        z.writestr("xl/worksheets/sheet1.xml",sheet)
    return buf.getvalue()

def test_correct_xlsx_source_only_structure_and_headers():
    qa=v.inspect_source(sample())
    assert qa["original_sheet_count"]==1
    assert qa["sheets"][0]["original_nonempty_xml_rows"]==2
    assert qa["sheets"][0]["original_numeric_cell_presence_by_column"]["C"]==1
    assert qa["sheets"][0]["source_animal_count_magnitudes_accessed"]==0
    assert "999999" not in str(qa)
    assert qa["sheets"][0]["first_12_source_text_rows"][0]["source_text_cells"][0]["source_text"]=="SiteID"

def test_unsafe_source_cannot_masquerade_as_xlsx():
    with pytest.raises(ValueError,match="ZIP"):
        v.inspect_source(b"<html>not an XLSX</html>")

def test_official_url_does_not_select_older_files():
    assert "revised-20240708.xlsx" in v.URL
    assert "data.jncc.gov.uk" in v.URL
    assert v.MAX_SOURCE<=12*1024*1024
