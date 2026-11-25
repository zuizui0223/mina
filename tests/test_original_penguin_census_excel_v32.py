"""Offline original legacy Excel source signature unit tests."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from probe_original_penguin_census_excel_v32 import response_kind,SOURCE_URL,MAX_PROBE_BYTES


def test_source_signature_never_confuses_HTML_with_Excel_quality_column():
    assert response_kind(b"PK\x03\x04test")=="POSSIBLE_XLSX_OR_ZIP"
    assert response_kind(bytes.fromhex("D0CF11E0A1B11AE1")+b"test")=="LEGACY_XLS_COMPOUND_BINARY"
    assert response_kind(b"<!DOCTYPE html><html><head>SPA</head></html>")=="HTML_OR_XML_NOT_EXCEL"
    assert response_kind(b'{"message":"unauthorized"}')=="JSON_NOT_EXCEL"
    assert MAX_PROBE_BYTES==128*1024
    assert SOURCE_URL=="https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216"
