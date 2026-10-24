"""Synthetic original source fixtures only."""
import io
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_bas_south_georgia_source_v21 as v
import pytest

def test_schema_columns_and_no_biology_from_source():
    raw=b"YEAR,COLONY,NESTS,CHICKS,PAIRS\n2000,A,1000,500,900\n2001,A,,600,950\n"
    r=v.parse_source(raw)
    assert r["original_rows"]==2
    assert r["per_column_nonempty"]["NESTS"]==1
    assert r["source_year_column_candidates"]==["YEAR"]
    assert r["original_breeding_count_values_read"]==0
    assert "1000" not in str(r)

def test_duplicate_header_fails_closed():
    with pytest.raises(ValueError,match="duplicate"):
        v.parse_source(b"YEAR,NESTS,NESTS\n2000,1,1\n")

def test_untrusted_host_fails_before_fetch():
    with pytest.raises(ValueError,match="publisher"):
        v.get_raw("https://example.org/raw.csv")

def test_versions_fixed_not_pretended_identical():
    assert v.SOURCES["bird_island_v1"]["doi"]!="10.5285/8fedb5a0-b98c-4457-9d86-aae9c6d3ed8e"
    assert "Maiviken" in v.SOURCES["south_georgia_maiviken"]["description"]
