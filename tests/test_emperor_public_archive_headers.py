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
    assert sheet["status"] == "HEADER_CANDIDATE_ROW_1"
    assert sheet["headers"] == [
        "Image Date","Sea Ice","Ice Shelf"
    ]
    assert "TEST_OUTCOME_NOT_TO_BE_LEAKED" not in json.dumps(d)
    assert d["outcome_rows_decoded"] == 0


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


def test_old_v1_sanae_name_requires_same_md5_before_access():
    prior_version = {
        "file_names_and_hashes": {
            "SanaeDataUpload2.xlsx": {
                "size": 52700,
                "checksum": "md5:13d916e08387d94ae448e129aa8aa442",
            }
        }
    }
    item = a.resolve_manifest_name("SanaeDataUpload.xlsx", prior_version)
    assert item["status"] == "SOURCE_IDENTITY_VERIFIED"
    assert item["name"] == "SanaeDataUpload2.xlsx"
    altered = {
        "file_names_and_hashes": {
            "SanaeDataUpload2.xlsx": {"size": 52700, "checksum": "md5:" + "0"*32}
        }
    }
    item2 = a.resolve_manifest_name("SanaeDataUpload.xlsx", altered)
    assert item2["status"] == "PINNED_CHECKSUM_DISAGREES_WITH_PUBLISHED_MANIFEST"


def test_absent_or_ambiguous_v3_file_fails_closed():
    none = a.resolve_manifest_name("SanaeDataUpload.xlsx", {"file_names_and_hashes": {}})
    assert none["status"] == "NAME_MISSING_OR_AMBIGUOUS_IN_PINNED_RECORD"
    both = a.resolve_manifest_name("SanaeDataUpload.xlsx", {
        "file_names_and_hashes": {
            "SanaeDataUpload.xlsx": {"size": 20000, "checksum": "md5:" + a.FILES["SanaeDataUpload.xlsx"]},
            "SanaeDataUpload2.xlsx": {"size": 20000, "checksum": "md5:13d916e08387d94ae448e129aa8aa442"},
        }
    })
    assert both["status"] == "NAME_MISSING_OR_AMBIGUOUS_IN_PINNED_RECORD"


def test_even_header_like_text_in_row2_must_remain_unread(tmp_path):
    path = tmp_path / "fake.xlsx"
    make_fake(path)
    # The synthetic workbook's second row contains a true date and a secret
    # text; neither appears in the JSON receipt.
    output = json.dumps(a.inspect_headers_only(path))
    assert "2019-11-30" not in output
    assert "TEST_OUTCOME_NOT_TO_BE_LEAKED" not in output


def test_manifest_error_stops_without_download(monkeypatch, tmp_path):
    monkeypatch.setattr(a, "metadata_for_pinned_record",
                        lambda: {"status": "RECORD_METADATA_BLOCKED"})
    monkeypatch.setattr(a, "download_public",
                        lambda *_: (_ for _ in ()).throw(AssertionError("download happened")))
    result = a.run(tmp_path)
    assert result["all_three_verified"] is False
    assert result["outcome_rows_read"] == 0
    assert all(
        obj["status"] == "RECORD_METADATA_BLOCKED_NO_DOWNLOAD"
        for obj in result["files"].values()
    )
