"""Synthetic original island observation rows only, never actual AADC counts."""
import sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import model_aadc_adelie_bv_nest_growth_v30 as m
from openpyxl import Workbook

def synthetic_sheet():
    wb=Workbook()
    ws=wb.active;ws.title="Population counts"
    ws.append(["original AADC source text"])
    ws.append(["Season*","Béchervaise","Verner","Petersen","Date",""])
    for year in m.FROZEN_YEARS:
        ws.append([year,1000+(year-1990)*4,90+((year-1980)*7)%21,
                   None,datetime(year,12,1),"occ nests"])
    return ws

def test_stage_qualifies_and_recovers_exact_frozen_years():
    ws=synthetic_sheet()
    unique,years,windows,qa=m.source_dates_and_field_support(ws)
    assert years==list(m.FROZEN_YEARS) and windows==list(m.FROZEN_WINDOWS)
    assert qa["exact_V29_outcome_blind_roster_reproduced"]
    assert qa["stage_qualified_support_gate"] and not qa["source_count_magnitudes_opened"]

def test_missing_absence_distinguished_from_recorded_zero():
    assert m.count_int(0)==0 and m.count_int("0")==0
    assert m.count_int(None) is None
    assert m.count_int("NA") is None
    assert m.count_int(-1) is None
    assert m.count_int("2.5") is None

def test_stage_and_date_bad_data_are_stopped():
    ws=synthetic_sheet()
    ws.append([1990,999,999,999,datetime(1990,12,1),"adults"])
    unique,years,windows,qa=m.source_dates_and_field_support(ws)
    assert qa["source_stage_or_date_excluded_rows"]["source_unit_not_literal_occ_nests"]==1
    assert years==list(m.FROZEN_YEARS)

def test_primary_effect_is_not_displaced_bird_migration_or_climate():
    ws=synthetic_sheet()
    unique,years,windows,qa=m.source_dates_and_field_support(ws)
    result=m.real_growth(unique,years,windows)
    assert result["ecological_effect_fitted"]
    assert result["nearby_physical_island_log1p_nest_growth_pearson_r"] is not None
    assert result["individual_penguin_exchange_or_recruitment_inferred"] is False
    assert result["marine_climate_ice_effect_estimated"] is False
    assert result["source_original_absolute_occupied_nest_counts_omitted"] is True

def test_source_excel_numeric_diagnostic_distinguishes_fractional_and_missing():
    assert m.original_count_type(4)=="EXCEL_NUMERIC_NONNEGATIVE_INTEGER"
    assert m.original_count_type(4.5)=="EXCEL_NUMERIC_FRACTIONAL"
    assert m.original_count_type(-99)=="EXCEL_NUMERIC_NEGATIVE"
    assert m.original_count_type("4.75")=="TEXT_FRACTIONAL"
    assert m.original_count_type("NA")=="TEXT_NONNUMERIC"
    assert m.original_count_type(None)=="MISSING_CELL"
    assert m.count_int(4.5) is None
    assert m.count_int(4)==4

def test_source_cell_quality_receipt_contains_no_count_magnitudes():
    src=synthetic_sheet()
    unique,years,windows,qa=m.source_dates_and_field_support(src)
    res=m.real_growth(unique,years,windows)
    cells=res["source_publisher_cell_quality_by_year_island"]
    assert set(cells)=={str(year) for year in m.FROZEN_YEARS}
    assert all(v.endswith("NONNEGATIVE_INTEGER") for row in cells.values() for v in row.values())
    assert "1000" not in str(cells)
