"""Tests for bounded original-publisher JNCC V33 predator-source intake."""
from pathlib import Path
import io
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_jncc_predator_island_source_v33 as a


def _xlsx_from_inline(header_label='lowid'):
    sheet = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetData>'
        '<row r="1">'
        f'<c r="A1" t="inlineStr"><is><t>{header_label}</t></is></c>'
        '<c r="B1" t="inlineStr"><is><t>Rattus norvegicus</t></is></c>'
        '<c r="C1" t="inlineStr"><is><t>mink</t></is></c>'
        '</row>'
        '<row r="2">'
        '<c r="A2"><v>13</v></c><c r="B2"><v>1</v></c>'
        '<c r="C2" t="inlineStr"><is><t>unknown</t></is></c>'
        '</row>'
        '<row r="3">'
        '<c r="A3"><v>14</v></c><c r="B3"><v>0</v></c>'
        '</row>'
        '</sheetData></worksheet>'
    )
    buf=io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("xl/worksheets/sheet1.xml", sheet)
    return buf.getvalue()


def test_rpsb_lowid_numeric_identity_is_exact_and_no_rounding():
    assert a.to_integral_key(13.0) == 13
    assert a.to_integral_key("014") == 14
    assert a.to_integral_key("13.5") is None
    assert a.to_integral_key(None) is None
    assert a.to_integral_key(True) is None


def test_excel_source_headers_join_and_unknown_never_zero_imputed():
    meta, keyed = a.sheet_rows(_xlsx_from_inline())
    assert keyed == [("xl/worksheets/sheet1.xml", {13,14})]
    s = meta["sheets"][0]
    assert s["exact_lowid_header_row_1indexed"] == 1
    assert s["exact_lowid_distinct_numeric_keys"] == 2
    assert "mink" in s["predator_header_candidates"]
    assert s["predator_column_literal_value_histograms"]["mink"]["<MISSING>"] == 1
    assert s["predator_column_literal_value_histograms"]["mink"]["unknown"] == 1
    assert s["all_predator_zero_blank_and_unknown_codes_uninterpreted"] is True


def test_spreadsheet_reader_ignores_texty_loosely_similar_island_id():
    raw=_xlsx_from_inline(header_label="island name")
    meta, keyed = a.sheet_rows(raw)
    assert keyed == []
    assert meta["sheets"][0]["exact_lowid_header_row_1indexed"] is None


def test_rejects_unapproved_download_hosts_before_network():
    with pytest.raises(ValueError, match="SOURCE_HOST_GATE"):
        a.bounded_get("https://example.com/private.xml",100)


def test_exact_publisher_sources_and_no_biological_result_import():
    assert a.RSPB_SERVICE.endswith("Islands_database/FeatureServer/0")
    assert a.DOI=="10.1007/s10344-017-1084-7"
    assert set(a.SUPPLEMENTS)=={"ESM1","ESM5"}
    assert "media.springernature.com" in a.ALLOWED_HOSTS
