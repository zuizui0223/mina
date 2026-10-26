"""First-party source control when original count-stage spreadsheet available."""
from __future__ import annotations

import io,zipfile,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from probe_original_woehler_spreadsheet_aadc_v32 import (
    identify_source_binary,bounded_zip_members,diagnose_original_response,trusted_official_url
)


def test_original_excel_and_html_are_distinct_and_no_count_values_interpreted():
    assert identify_source_binary(bytes.fromhex("d0cf11e0a1b11ae1"))=="EXCEL_OLD_XLS_OLE"
    assert identify_source_binary(b"<html>Please email for access</html>")=="HTML_XML_NOT_ORIGINAL_EXCEL"
    out=diagnose_original_response(b"<html>Login</html>",{"HTTP_status":200})
    assert out["status"]=="ACCESS_HOLD_FIRST_PARTY_NOT_SPREADSHEET"
    assert out["original_Woehler_quality_code_rows_read"]==0
    assert out["source_original_spreadsheet_obtained"] is False
    assert "Login" in out["source_HTML_page_excerpt_no_secrets"]


def test_zip_source_versions_not_independent_field_censuses():
    blob=io.BytesIO()
    with zipfile.ZipFile(blob,"w") as f:
        f.writestr("original.xls",b"original")
        f.writestr("modified.xls",b"modified")
    x=diagnose_original_response(blob.getvalue(),{"HTTP_status":200})
    assert x["status"]=="ACCESS_PASS_FIRST_PARTY_ORIGINAL_SPREADSHEET_BINARY"
    assert len(x["original_source_zip_member_names"])==2
    assert x["original_census_Stage_NA_CB_recovered"] is False


def test_zip_path_escape_and_unauthorized_host_stop():
    blob=io.BytesIO()
    with zipfile.ZipFile(blob,"w") as f:
        f.writestr("../not-original.xls","x")
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        bounded_zip_members(blob.getvalue())
    assert trusted_official_url("https://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216")
    assert not trusted_official_url("http://data.aad.gov.au/aadc/portal/download_file.cfm?file_id=2216")
    assert not trusted_official_url("https://data.aad.gov.au.evil.example/22")
