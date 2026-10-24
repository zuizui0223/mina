"""V31 isolated synthetic publisher averaged-count index fixtures."""
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import model_aadc_bv_float_nest_index_v31 as m
from openpyxl import Workbook

def source():
    wb=Workbook()
    ws=wb.active
    ws.title="Population counts"
    ws.append(["original source"])
    ws.append(["Season*","Béchervaise","Verner","Petersen","Date"])
    for i,year in enumerate(m.FROZEN_YEARS):
        b=1000+(i%5)*17.5 + i*2.5
        v=100+((i*13)%7)*3.25 + i*1.25
        ws.append([year,b,v,None,datetime(year,12,3),"occ nests"])
    return ws

def test_author_published_fractional_are_unrounded_not_fake_zeros():
    assert m.numeric_publisher_occupied_index(10.5)==10.5
    assert m.numeric_publisher_occupied_index(0.0)==0.
    assert m.numeric_publisher_occupied_index(-1) is None
    assert m.numeric_publisher_occupied_index(None) is None
    assert m.numeric_publisher_occupied_index("4.5") is None
    assert m.numeric_publisher_occupied_index(float("nan")) is None
    assert m.prior.count_int(10.5) is None

def test_original_10year_8window_index_independent_of_rounding():
    ws=source()
    rows,years,windows,qa=m.prior.source_dates_and_field_support(ws)
    assert qa["exact_V29_outcome_blind_roster_reproduced"]
    r=m.summarize(rows,years,windows)
    assert r["ecological_effect_fitted"]
    assert r["source_numeric_years"]==10
    assert r["source_numeric_consecutive_year_windows"]==8
    assert r["original_float_values_not_rounded"]
    assert r["original_source_count_values_not_reprinted"]
    assert r["source_Excel_numeric_fractional_year_island_count"]>0
    assert r["individual_island_migration_measured"] is False

def test_reject_text_and_do_not_replace_missing_with_zero():
    ws=source()
    for row in ws.iter_rows(min_row=3):
        if row[0].value==2000:
            row[2].value="NA"
    rows,years,windows,qa=m.prior.source_dates_and_field_support(ws)
    assert 2000 not in years
    out=m.summarize(rows,years,windows)
    assert not out["ecological_effect_fitted"]
    assert "STOP" in out["scientific_decision"]

def test_version_and_comparators_and_no_causal_claim():
    assert m.SHA==m.prior.SHA
    assert m.FROZEN_YEARS==m.prior.FROZEN_YEARS
    assert m.FROZEN_WINDOWS==m.prior.FROZEN_WINDOWS
    assert m.ORIGINAL_EXPECTED_FRACTIONAL==10
