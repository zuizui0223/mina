"""V33 source metadata only: no real Ross Sea penguin count values."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from collections import defaultdict
import audit_nz_ross_sea_census_source_v33 as a

def synthetic_wide():
    sheet={0:{0:"Colony"}}
    sheet[0].update({i+1:1981+i for i in range(25)})
    for idx in range(30):
        sheet[idx+1]={0:"Synthetic Colony "+str(idx),
                      **{col:100+idx+col for col in range(1,26) if (idx+col)%5!=0}}
    return sheet

def synthetic_tall():
    sheet={0:{0:"Year",**{i+1:"Colony "+str(i) for i in range(39)}}}
    for yy in range(1981,2025):
        sheet[yy-1980]={0:yy,**{col:(100+col+yy if yy!=2020 else None)
                       for col in range(1,40)}}
    return sheet

def test_original_wide_colony_by_year_source_support_only():
    s=a.summarize_matrix(synthetic_wide())
    assert s["source_year_colony_orientation"]=="ROWS_COLONY_COLUMNS_YEAR"
    assert s["n_distinct_colony_labels"]==30
    assert s["predeclared_source_colony_and_year_support_pass"]
    assert s["count_or_population_magnitudes_used"]==0
    assert "1000" not in str(s)

def test_original_vertical_year_by_colony_and_covid_missing_not_zero():
    s=a.summarize_matrix(synthetic_tall())
    assert s["source_year_colony_orientation"]=="ROWS_YEAR_COLUMNS_COLONY"
    assert s["n_distinct_colony_labels"]==39
    assert s["original_source_2020_number_of_explicit_numeric_cells"]==0
    assert s["n_colonies_with_ge5_measured_years"]==39
    assert s["source_records_are_not_confirmed_independent_physical_islands"]

def test_missing_and_negative_raw_source_value_are_not_numeric_observation():
    assert a.num_present(0)
    assert a.num_present("0")
    assert not a.num_present(None)
    assert not a.num_present("NA")
    assert not a.num_present(-999)
    assert not a.num_present("not surveyed")
    assert not a.num_present(float("nan"))

def test_original_calendar_codes_and_zero_not_fabricated():
    assert a.parse_year(1981.)==1981
    assert a.parse_year("2019/20")==2019
    assert a.parse_year("2024")==2024
    assert a.parse_year("2020-21")==2020
    assert a.parse_year("2020-25") is None
    assert a.parse_year("2019/XX") is None

def test_publisher_fingerprint_not_1000_independent_islands():
    assert a.RESOURCES["census"][0]=="5fd490e5-92c4-4f2c-a82e-c66db2320eb1"
    assert a.RESOURCES["census"][2]=="195a9027a0d18012812b09fb345ac60e"
    assert a.MIN_COLONIES_WITH_5YEARS==20
    assert a.MIN_YEARS_WITH_5COLONIES==10
