"""Synthetic XLSX verifies structural row-layout scan without any value decoding."""
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/"scripts"))
import audit_emperor_archive_row_layout_v3 as AUDIT


def make_workbook(path):
    workbook = """<?xml version="1.0"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
     xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
     <sheets><sheet name="2019_20" sheetId="1" r:id="rId1"/></sheets></workbook>"""
    rels = """<?xml version="1.0"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
     <Relationship Id="rId1" Target="worksheets/sheet1.xml"
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>
    </Relationships>"""
    sheet = """<?xml version="1.0"?>
    <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
     <sheetData>
      <row r="1"><c r="A1" t="s"><v>0</v></c></row>
      <row r="2"><c r="A2" t="s"><v>1</v></c><c r="B2" t="s"><v>2</v></c>
       <c r="C2" t="inlineStr"><is><t>SECRET_OUTCOME_NEVER_EXPOSED</t></is></c></row>
      <row r="3"><c r="A3" t="s"><v>3</v></c><c r="B3"><v>42</v></c></row>
      <row r="13"><c r="A13" t="s"><v>4</v></c></row>
     </sheetData>
    </worksheet>"""
    with ZipFile(path,"w") as z:
        z.writestr("xl/workbook.xml",workbook)
        z.writestr("xl/_rels/workbook.xml.rels",rels)
        z.writestr("xl/worksheets/sheet1.xml",sheet)
        z.writestr("xl/sharedStrings.xml",
                   '<sst><si><t>LEAKED_HIDDEN_BIOLOGICAL_STATE</t></si></sst>')


def test_detect_row2_structural_header_candidate_without_content(tmp_path):
    xlsx=tmp_path/"test.xlsx"
    make_workbook(xlsx)
    data=AUDIT.inspect_row_shapes(xlsx)
    assert data["n_sheets"]==1
    assert data["decoded_row_values"]==0
    assert data["shared_strings_dictionary_read"] is False
    record=data["sheets"][0]
    assert record["sheet"]=="2019_20"
    assert record["first_multi_string_row_candidate_UNVERIFIED"]==2
    assert [r["row"] for r in record["rows"]]==[1,2,3]
    assert record["rows"][1]["n_shared_string_cells"]==2
    assert record["rows"][1]["n_inline_string_cells"]==1
    assert record["rows"][2]["n_numeric_or_generic_type_cells"]==1
    assert "SECRET_OUTCOME_NEVER_EXPOSED" not in json.dumps(data)
    assert "LEAKED_HIDDEN_BIOLOGICAL_STATE" not in json.dumps(data)


def test_offline_stage_fails_closed(tmp_path):
    result=AUDIT.run(tmp_path,no_network=True)
    assert result["metadata_status"]=="SKIPPED_NO_NETWORK"
    assert result["decoded_cell_values"]==0
    assert result["decoded_outcome_rows"]==0
    assert result["all_three_downloads_verified"] is False
    assert result["all_fifty_one_sheet_layouts_sketchable"] is False
