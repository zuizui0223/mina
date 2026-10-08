"""Only synthetic tiny XLSX schema tests; no real response outcomes imported."""
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "audit", ROOT / "scripts" / "audit_emperor_public_archive_headers.py"
)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def make_fake(path: Path):
    wb = '''<?xml version="1.0"?>
    <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
     xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
     <sheets><sheet name="Data" sheetId="1" r:id="rId1"/></sheets></workbook>'''
    rel = '''<?xml version="1.0"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Target="worksheets/sheet1.xml"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>
    </Relationships>'''
    shared = '''<?xml version="1.0"?>
    <sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
    <si><t>Image Date</t></si><si><t>Sea Ice</t></si><si><t>Ice Shelf</t></si>
    <si><t>2019-11-30</t></si><si><t>TEST_OUTCOME_NOT_TO_BE_LEAKED</t></si>
    </sst>'''
    sheet = '''<?xml version="1.0"?>
    <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
    <sheetData>
    <row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c>
      <c r="C1" t="s"><v>2</v></c></row>
    <row r="2"><c r="A2" t="s"><v>3</v></c><c r="B2" t="s"><v>4</v></c>
      <c r="C2"><v>12</v></c></row>
    </sheetData></worksheet>'''
    with ZipFile(path,"w") as z:
        z.writestr("xl/workbook.xml",wb)
        z.writestr("xl/_rels/workbook.xml.rels",rel)
        z.writestr("xl/sharedStrings.xml",shared)
        z.writestr("xl/worksheets/sheet1.xml",sheet)


def test_extracts_only_header_row(tmp_path):
    path=tmp_path/"test.xlsx"
    make_fake(path)
    d=a.inspect_headers_only(path)
    assert d["sheet_count"] == 1
    sheet=d["sheets"][0]
    assert sheet["status"] == "HEADER_CANDIDATE"
    assert sheet["header_candidates"][0]["header"] == [
        "Image Date","Sea Ice","Ice Shelf"
    ]
    assert "TEST_OUTCOME_NOT_TO_BE_LEAKED" not in json.dumps(d)


def test_urls_pin_v3_and_names_and_checksums():
    assert len(a.FILES) == 3
    for name, digest in a.FILES.items():
        assert name.endswith(".xlsx")
        assert len(digest) == 32
        assert "17390368" in a.urls_for(name)[0]


def test_no_network_gate_does_not_claim_source_data(tmp_path):
    result=a.run(tmp_path,no_network=True)
    assert result["outcome_rows_read"] == 0
    assert result["effect_fitted"] is False
    assert result["all_three_verified"] is False
    assert all(item["status"] == "SKIPPED_NO_NETWORK" for item in result["files"].values())


def test_date_rows_not_mislabelled_as_header():
    assert not a._safe_header_candidate(["2018-11-10", "x", "x"])
    assert a._safe_header_candidate(["Image date", "sea ice", "ice shelf"])
