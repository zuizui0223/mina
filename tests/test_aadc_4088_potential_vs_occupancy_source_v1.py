"""Synthetic source-only AADC archive detection and no observed penguin records."""
import importlib.util
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

FILE=Path(__file__).resolve().parents[1]/"scripts/probe_aadc_4088_potential_vs_occupancy_source_v1.py"
spec=importlib.util.spec_from_file_location("aadc_archive",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

URL="https://data.aad.gov.au/eds/4345/download"

def test_real_zip_structure_has_member_names_but_no_member_rows_read():
    buf=BytesIO()
    with ZipFile(buf,"w") as out:
        out.writestr("site_lookup.csv","site_id,island_name\nA,Island 1\n")
        out.writestr("occupancy.csv","site_id,season,known_present\nA,2009,yes\n")
    result=m.classify_archive(buf.getvalue(),"application/zip",URL)
    assert result["source_file_valid"]
    assert result["type"]=="STRUCTURALLY_VALID_ZIP_OR_XLSX"
    assert {x["name"] for x in result["archive_members"]}=={"site_lookup.csv","occupancy.csv"}
    assert result["record_rows_opened"]==0
    assert result["sample_rows_read"]==0

def test_app_javascript_shell_is_not_a_download():
    result=m.classify_archive(b'<!doctype html><html>JavaScript required</html>',
                              "text/html",URL)
    assert not result["source_file_valid"]
    assert result["type"]=="HOLD_HTML_APPLICATION_NOT_SOURCE_DATA"

def test_unofficial_or_plain_http_source_not_accepted():
    for bad in ("http://data.aad.gov.au/eds/4345/download",
                "https://example.org/data.csv"):
        assert not m._official(bad)
        assert m.classify_archive(b"site_id,data\nA,yes\n","text/csv",bad)["source_file_valid"] is False

def test_bounded_source_and_no_bird_status_logic():
    empty=m.classify_archive(b"","text/csv",URL)
    assert empty["type"]=="HOLD_EMPTY_OR_OVERSIZED_INPUT"
    csv=m.classify_archive(b"key,value\na,1\n","text/csv",URL)
    assert csv["source_file_valid"]
    assert csv["type"]=="TEXT_TABULAR_CANDIDATE_UNREAD"
    assert csv["record_rows_opened"]==0

def test_semantic_guard_in_contract():
    contract=Path(__file__).resolve().parents[1]/"contracts/AADC_4088_POTENTIAL_SITES_VS_OCCUPANCY_SOURCE_GATE_V1.json"
    import json
    d=json.loads(contract.read_text())
    assert d["outcome_records_opened"]==0
    assert d["causal_model_fitted"] is False
    assert d["ecology_PR189_untouched"]
    assert "island" in d["system"].lower() or "geographic" in d["system"].lower()
