"""Synthetic HTML only AADC first-party public download landing-page tests."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_paper2_macquarie_AADC_download_landing_v56a as m


def test_frozen_only_two_original_downloader_targets():
    assert set(m.SOURCES)=={
      "2023_24_wildlife_both_flight_guilds",
      "original_Macquarie_1_to_50k_coast"}
    assert m.MAX_REDIRECTS==4
    assert m.MAX_HTML_BYTES==200000


def test_official_aadc_https_only():
    assert m.official("https://data.aad.gov.au/eds/6113/download")
    assert m.official("https://transfer.data.aad.gov.au/file")
    assert not m.official("http://data.aad.gov.au/eds/6113/download")
    assert not m.official("https://data.aad.gov.au.evil.org/file")


def test_public_html_landing_detects_no_file_and_consent_form_without_clicking():
    html=b"""<!doctype html><html><head><title>Download dataset</title></head>
    <body><form action='/consent' method='post'>
    <input type='checkbox' name='agree'><button>Continue</button></form>
    <a href='/downloadfile.zip?private=SECRET_TOK'>zip</a></body></html>"""
    x=m.source_page_structure(html,"https://data.aad.gov.au/eds/6113/download")
    assert x["response_kind"]=="HTML_OFFICIAL_LANDING_PAGE"
    assert x["classified_page_title"]=="DOWNLOAD_PAGE_TITLE"
    assert x["html_form_count"]==1
    assert x["html_input_type_counts"]["checkbox"]==1
    assert x["direct_official_public_file_links_n"]==1
    assert "SECRET_TOK" not in str(x)
    assert not x["user_consents_forms_submitted"]


def test_external_download_links_cannot_pass_first_party_filters():
    html=b"""<html><head><title>Dataset</title></head><body>
    <a href='https://example.org/private.zip'>external file</a></body></html>"""
    q=m.source_page_structure(html,"https://data.aad.gov.au/eds/6113/download")
    assert q["all_HTML_anchor_links_n"]==1
    assert q["direct_official_public_file_links_n"]==0


def test_non_html_original_zip_is_not_landing_page():
    q=m.source_page_structure(b"PK\x03\x04some bytes",
                              "https://data.aad.gov.au/eds/6113/download")
    assert q["response_kind"]=="NON_HTML_BINARY_OR_OTHER"


def test_not_prelisted_AADC_dataset_endpoint_cannot_be_probed():
    with pytest.raises(ValueError,match="NOT_EXACT_FROZEN"):
        m.metadata_only("https://data.aad.gov.au/eds/7777/download")
