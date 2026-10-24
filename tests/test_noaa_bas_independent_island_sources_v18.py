"""No real bird counts in test data. Source gate only."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_noaa_bas_independent_island_sources_v18 as v
import pytest

def test_csv_columns_and_completeness_no_magnitudes_disclosed():
    raw=b"Season,Colony,Nests,Chicks\n2000,Alpha,1,0\n2001,Alpha,1000,\n"
    qa=v.check_bas(raw)
    assert qa["original_data_rows"]==2
    assert qa["per_column_nonblank_cells"]["Chicks"]==1
    assert qa["numeric_stage_value_cells_opened"]==0
    assert "1000" not in str(qa)

def test_html_stopped_before_false_source_success():
    with pytest.raises(ValueError,match="HTML"):
        v.check_bas(b"<html><body>2003,4,5</body></html>")

def test_noaa_schema_source_missing_fails_closed():
    with pytest.raises(ValueError,match="non-XLSX"):
        v.check_noaa(b"<html>not an xlsx</html>")

def test_source_url_and_five_column_contract():
    assert v.NOAA_URL.startswith("https://www.ncei.noaa.gov/")
    assert len(v.EXPECTED_NOAA)==5
    assert "CapeShirreff_Chinstrap" in v.EXPECTED_NOAA
    assert v.normal_header("Copa_Adelie")=="copaadelie"

def test_duplicate_original_BAS_columns_rejected():
    with pytest.raises(ValueError,match="SCHEMA_STOP"):
        v.check_bas(b"Season,Nests,Nests\n2000,1,2\n")
