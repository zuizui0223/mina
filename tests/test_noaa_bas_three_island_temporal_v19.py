"""Synthetic-only, no actual original count values."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_noaa_bas_three_island_temporal_v19 as v

def test_source_year_exact_austral_format():
    assert v.source_year("1977-78")==1977
    assert v.source_year("2008/09")==2008
    assert v.source_year("2008-2009")==2008
    assert v.source_year("2008")==2008
    assert v.source_year("2008-10") is None
    assert v.source_year("unknown") is None

def test_lexical_zero_valid_but_missing_not_zero():
    assert v.lexical_numeric("0")
    assert v.lexical_numeric(0)
    assert v.lexical_numeric("12345")
    assert not v.lexical_numeric("")
    assert not v.lexical_numeric("NA")
    assert not v.lexical_numeric("unavailable")
    assert not v.lexical_numeric(None)

def test_three_island_date_support_uses_exact_same_year_not_neighbour():
    noa={}
    bas={}
    for year in range(1990,2000):
        noa[year]={k:True for k in v.NOAA_COLS}
        bas[year]=True
    result=v.compare_sources(noa,bas)
    assert result["all_three_island_gentoo_numeric_lexical_common_seasons"]==10
    assert result["all_three_island_gentoo_consecutive_year_windows"]==9
    assert result["prespecified_three_island_temporal_source_support_pass"]
    assert not result["source_count_units_fully_harmonized"]

def test_noaa_gentoo_missing_year_reduces_common_panel():
    noa={yr:{k:(yr!=1994 if k=="CapeShirreff_Gentoo" else True) for k in v.NOAA_COLS}
         for yr in range(1990,2001)}
    bas={yr:True for yr in range(1990,2001)}
    r=v.compare_sources(noa,bas)
    assert r["all_three_island_gentoo_numeric_lexical_common_seasons"]==10
    assert r["all_three_island_gentoo_consecutive_year_windows"]==8

def test_one_island_not_claimed_as_many_from_repeated_records():
    noa={1999:{k:True for k in v.NOAA_COLS}}
    bas={1999:True}
    r=v.compare_sources(noa,bas)
    assert r["physical_island_n"]==3
    assert r["all_three_island_gentoo_numeric_lexical_common_seasons"]==1
    assert not r["prespecified_three_island_temporal_source_support_pass"]
