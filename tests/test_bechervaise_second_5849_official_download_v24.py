"""Synthetic public metadata link extraction; zero original wildlife tag rows."""
import importlib.util,json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"scripts/probe_bechervaise_second_5849_official_download_v24.py"
spec=importlib.util.spec_from_file_location("bechraw24",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_second_publisher_source_download_is_not_same_as_technical_guide():
    urls=m.SOURCE_URLS
    assert urls["AAS4086_TECHNICAL_GUIDE_5228"]=="https://data.aad.gov.au/eds/5228/download"
    assert urls["AAS4086_SECOND_OFFICIAL_LINK_5849"]=="https://data.aad.gov.au/eds/5849/download"
    assert urls["AAS4518_ORIGINAL_NEST_RESIGHTS_5516"]=="https://data.aad.gov.au/eds/5516/download"
    assert len(set(urls.values()))==3
    assert all(m.original.official(url) for url in urls.values())

def test_metadata_link_parser_distinguishes_guide_new_data_link_and_nest_resights():
    html=(
      '<a href="https://data.aad.gov.au/eds/5228/download">Weighbridge technical guide</a>'
      '<a href="https://data.aad.gov.au/eds/5849/download">2006–2018 weighbridge files</a>'
      '<a href="https://data.aad.gov.au/eds/5516/download">Nest resight package</a>'
      '<a href="https://example.org/eds/5849/download">untrusted copy</a>'
    )
    r=m.original_publisher_data_anchors(html)
    assert r["metadata_ref_technical_5228"]
    assert r["metadata_ref_additional_5849"]
    assert r["source_metadata_html_anchors_observed"]==3
    assert any(x["text"]=="2006–2018 weighbridge files" for x in r["publisher_original_anchor_labels"])
    assert not any("example.org" in x["url"] for x in r["publisher_original_anchor_labels"])

def test_absence_of_plain_page_anchor_does_not_disprove_browser_rendered_link():
    r=m.original_publisher_data_anchors("<html><body>Web app needs JS</body></html>")
    assert r["source_metadata_html_anchors_observed"]==0
    assert r["never_interpret_missing_static_HTML_anchor_as_absence_of_browser_link"]

def test_javascript_download_response_never_called_binary_source():
    z=m.original.classify_head(b'<!doctype html><html>Enable JavaScript</html>',
                               "text/html","AAS4086_SECOND_OFFICIAL_LINK_5849")
    assert z["record_state"]=="HOLD_JS_HTML_APPLICATION_OR_LOGIN_NOT_DATA"
    assert z["penguin_identifiers_read"]==0
    assert not z["file_body_parsed"]

def test_official_source_contract_scopes_scientific_2026_prior_art_and_no_data():
    j=json.loads((ROOT/"contracts/BECHERVAISE_AADC_5849_RAW_LINK_SOURCE_V24.json").read_text())
    assert j["current_identifiability"]["publisher_second_link_verified_in_public_metadata"]
    assert not j["current_identifiability"]["download_5849_original_raw_data_verified"]
    assert j["current_identifiability"]["tag_records_read"]==0
    assert j["existing_2026_Ross_prior_art"]["prior_crosscolony_first_recruitment"].startswith("Movement")
    assert j["pr189_frozen"] and j["pr142_frozen"] and j["pr195_frozen"]
