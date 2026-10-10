"""Source-only Bechervaise weighed arrivals, no fabricated own-egg matching."""
import importlib.util,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/probe_bechervaise_original_rfid_vs_nest_resights_v20.py"
spec=importlib.util.spec_from_file_location("bechsource",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_publisher_resight_source_and_guide_are_different_data_products():
    assert set(m.SOURCE_ENDPOINTS)=={
      "AAS_4518_1991_2019_DEMOGRAPHY_AND_RE-SIGHT_ARCHIVE",
      "AAS_4086_2006_2018_WEIGHBRIDGE_TECHNICAL_GUIDE_ONLY"}
    assert all(m.official(x) for x in m.SOURCE_ENDPOINTS.values())
    assert not m.official("http://data.aad.gov.au/eds/5516/download")
    assert not m.official("https://example.org/data.zip")

def test_javascript_html_source_not_live_bird_data():
    z=m.classify_head(b"<!doctype html><html>Enable JavaScript</html>","text/html","resights")
    assert z["record_state"]=="HOLD_JS_HTML_APPLICATION_OR_LOGIN_NOT_DATA"
    assert z["penguin_identifiers_read"]==0
    assert not z["file_body_parsed"]

def test_legacy_excel_pdf_zip_source_signatures_not_parsed():
    for prefix,expect in [
      (b"%PDF-1.4 beginning","PDF_DOCUMENT_PREFIX"),
      (b"PK\x03\x04not-actually-validated","ZIP_ARCHIVE_HEADER_CANDIDATE_UNPARSED"),
      (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1","LEGACY_XLS_BIFF_PREFIX_NOT_PARSED"),
      (b"animalID,date\nX,2020\n","TEXT_TABLE_PREFIX_DO_NOT_PARSE_ANIMAL_RECORDS"),
    ]:
        r=m.classify_head(prefix,"application/octet-stream","original")
        assert r["record_state"]==expect
        assert r["penguin_identifiers_read"]==0
        assert r["unprocessed_weighbridge_records_opened"]==0

def test_contract_blocks_inference_and_identifies_already_published_feedback():
    z=json.loads((ROOT/"contracts/BECHERVAISE_RFID_GATE_TO_NEST_SAME_ID_SOURCE_V20.json").read_text())
    assert not z["currently_identified"]["stable_animal_ID_join_verified"]
    assert not z["currently_identified"]["all_candidate_nonbreeders_at_risk_sampled"]
    assert not z["currently_identified"]["novel_causal_adaptive_memory_mechanism_found"]
    assert z["Ecology_PR189_frozen"]
    assert z["USAP_PR142_frozen"]
