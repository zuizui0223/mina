"""V32 synthetic AADC workbook: 1000 bootstrap ROWS are not 1000 islands."""
import io
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from openpyxl import Workbook
import audit_aadc_regional_bootstrap_grain_v32 as audit

def test_bootstrap_rows_not_counted_as_islands():
    workbook=Workbook()
    sheet=workbook.active
    sheet.title="regional metapop bootstrap"
    sheet.append(["bootstrapped population estimates 2009 and 2019","regional total"])
    for i in range(1000):
        sheet.append([90000+i,110000+i])
    b=io.BytesIO();workbook.save(b)
    data=audit.inspect(b.getvalue())
    assert data["original_island_identity_rows_verified"]==0
    assert data["original_geographically_distinct_physical_islands_verified"]==0
    assert data["original_publisher_workbook_sheets"][0]["declared_source_rows"]==1001
    assert "110000" not in str(data)
    assert data["census_population_or_bootstrap_numeric_magnitudes_opened"]==0

def test_header_field_is_not_proof_of_geographically_independent_1990s_islands():
    w=Workbook();s=w.active
    s.append(["island_name","2009 nest count","2019 nest count"])
    s.append(["Dummy Island",10000.75,10100.25])
    b=io.BytesIO();w.save(b)
    x=audit.inspect(b.getvalue())
    assert "island_name" in x["literal_original_geography_field_names"]
    assert not x["original_island_geography_crosswalk_verified"]
    assert x["original_island_identity_rows_verified"]==0
    assert x["ecological_effects_computed"]==0

def test_numeric_source_values_are_never_text_header_labels():
    assert audit.safe_label(10000) is None
    assert audit.safe_label(3.1415) is None
    assert audit.safe_label("9999.50")=="[NUMERIC_TEXT_REDACTED]"
    assert audit.safe_label("island_id")=="island_id"
    assert audit.GATE_MIN_PHYSICAL_ISLANDS==10
    assert audit.GATE_MIN_REGIONS==3

def test_binary_or_html_not_original_excel():
    try:
        audit.inspect(b"<html>untrusted</html>")
        assert False
    except ValueError as e:
        assert "not Excel" in str(e)
