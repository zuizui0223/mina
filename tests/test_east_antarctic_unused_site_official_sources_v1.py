"""Synthetic source-link and magic-class tests. No biological records opened."""
import importlib.util
from pathlib import Path
import pytest

P=Path(__file__).resolve().parents[1]/"scripts/probe_east_antarctic_unused_site_official_sources_v1.py"
spec=importlib.util.spec_from_file_location("aadc_source",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_official_links_locked_and_exactly_three():
    assert len(m.SOURCES)==3
    assert [int(x[1].split("/")[-2]) for x in m.SOURCES]==[4344,4345,5959]
    assert all(m.valid_official_url(url) for _,url in m.SOURCES)
    assert not m.valid_official_url("https://elsewhere.example/eds/5959/download")
    assert not m.valid_official_url("http://data.aad.gov.au/eds/5959/download")

def test_bounded_magic_never_treats_html_as_csv():
    assert m.classify_signature(b"PK\x03\x04something")=="ZIP_ARCHIVE_MAGIC"
    assert m.classify_signature(b"\x1f\x8binfo")=="GZIP_MAGIC"
    assert m.classify_signature(b"Rar!\x1a\x07info")=="RAR_ARCHIVE_MAGIC"
    assert m.classify_signature(b"<html>service unavailable</html>")=="HTML_NOT_DATA_ARCHIVE"
    assert m.classify_signature(b"\n<!doctype html>")=="HTML_NOT_DATA_ARCHIVE"
    assert m.classify_signature(b"error=blocked")=="UNRECOGNIZED_PREFIX_NOT_DATA_CONFIRMED"

def test_nonofficial_redirection_rejected():
    with pytest.raises(ValueError):
        m.BoundedOfficialRedirect().redirect_request(
            None,None,302,"redirection",{},
            "https://unrelated.example/penguins.csv")
