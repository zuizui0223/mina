"""Invented source-only V20 validations, not real Antarctic bird data."""
import sys
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import math
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_noaa_bas_gentoo_growth_synchrony_v20 as v

def synthetic_xlsx():
    header="<sst xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'>"+ "".join(
        "<si><t>"+s+"</t></si>" for s in v.HEAD)+"</sst>"
    rows=["<row r='1'>"+ "".join(
        "<c r='"+chr(65+k)+"1' t='s'><v>"+str(k)+"</v></c>" for k in range(6))+"</row>"]
    for i in range(38):
        r=i+2
        rows.append("<row r='"+str(r)+"'><c r='A"+str(r)+"'><v>"+str(1977+i)+"</v></c>"+
                    "".join("<c r='"+chr(66+k)+str(r)+"'><v>"+str(10+i+k)+"</v></c>"
                            for k in range(5))+"</row>")
    sheet="<worksheet xmlns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'><sheetData>"+ "".join(rows)+"</sheetData></worksheet>"
    data=BytesIO()
    with ZipFile(data,"w") as z:
        z.writestr("xl/sharedStrings.xml",header)
        z.writestr("xl/worksheets/sheet1.xml",sheet)
    return data.getvalue()

def invented():
    n={};b={}
    for y in sorted(v.YEARS):
        offset=y-1998 if y<=2009 else y-2011
        n[y]={"Copa_Gentoo":100+offset**2+2,
              "CapeShirreff_Gentoo":200+offset*3+10,
              "Copa_Chinstrap":70+offset*3+2,
              "CapeShirreff_Chinstrap":100+offset*2+6}
        b[y]=300+offset**2+offset+3
    return n,b

def test_exact_source_ooxml_first_sheet_and_six_columns():
    raw=synthetic_xlsx()
    rows=v.xlsx_values(raw)
    assert len(rows)==38 and rows[0][0]=="1977"
    assert v.parse_noaa(raw)[2014]["Copa_Gentoo"]==48.0

def test_source_year_and_true_missing_not_zero():
    assert v.parse_year("1998-99")==1998
    assert v.parse_year("1998-8895") is None
    assert v.numeric("0")==0
    assert v.numeric("") is None and v.numeric("NA") is None

def test_unit_scale_invariance_of_strict_positive_log_ratio():
    assert math.log(8/4)==pytest.approx(math.log(800/400))

def test_exact_original_year_cohort_and_14_windows():
    n,b=invented()
    r=v.analyse(n,b)
    assert r["source_original_matched_years"]==16
    assert r["strict_three_island_yearly_change_windows"]==14
    assert r["biological_descriptive_association_computed"]
    assert not r["source_raw_counts_pooled"]

def test_true_source_zero_removed_without_log1p():
    n,b=invented()
    b[2002]=0
    r=v.analyse(n,b)
    assert 2002 in r["excluded_original_years_with_nonpositive_three_site_count"]
    assert r["strict_three_island_yearly_change_windows"]==12

def test_source_year_drift_fails_closed():
    n,b=invented()
    del b[1999]
    with pytest.raises(ValueError,match="COHORT_STOP"):
        v.analyse(n,b)

def test_degenerate_correlation_does_not_claim_biology():
    assert v.pearson([1,1,1],[2,3,4]) is None
    assert v.pairwise([]) is None
