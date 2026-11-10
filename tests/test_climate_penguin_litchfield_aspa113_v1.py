"""Primary-source zero chronology and no-date-imputation tests."""
from pathlib import Path
import csv
import importlib.util
import json
import math

BASE=Path(__file__).resolve().parents[1]
SCRIPT=BASE/"research/climate-penguin/work/climate_penguin/audit_litchfield_aspa113_v1.py"

def mod():
    spec=importlib.util.spec_from_file_location("litchfield_aspa113",SCRIPT)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def test_original_aspa_count_source_and_fixed_mapppd_agreement():
    m=mod();r,priority,climate=m.audit()
    assert r["positive_seasons"]==16 and r["explicit_zero_seasons"]==6
    assert r["last_positive_season_start"]==2006
    assert r["published_2006_breeding_pairs"]==4
    assert r["first_zero_season_start"]==2007
    assert r["mapppd_exact_matches"]==17 and r["mapppd_count_disagreements"]==0
    assert r["published_only_seasons"]==[2006,2009,2010,2011,2012]
    assert r["last_positive_mapppd"]==2005
    assert r["survey_month_resolved"] is False
    assert r["static_point_buffer_only"]["time_indexed_vegetation"] is False
    assert climate is None
    assert r["source_priority"]=={"outside_victoria_rows":181,
                                   "unresolved_month_rows":120,"known_month_rows":61}
    assert priority[0]["citekey"]=="barbraud2020population"
    assert priority[0]["unknown_month_rows"]==26
    assert not any(x["source_date_verified"] for x in priority)

def test_missing_dates_cannot_be_made_up():
    m=mod()
    rows=m.read_csv(m.INPUT)
    rows[0]["census_month"]="12"
    try:
        m.values_by_year(rows)
        assert False,"calendar imputation must fail"
    except AssertionError as e:
        assert "Never infer" in str(e)

def test_explicit_zero_cannot_be_coerced_to_missing():
    m=mod()
    rows=m.read_csv(m.INPUT)
    assert len(rows)==22
    for r in rows:
        if int(r["season_start"])>=2007:
            assert int(r["breeding_pairs"])==0
    rows[-1]["breeding_pairs"]=""
    try:
        m.values_by_year(rows)
        assert False,"empty observed zero must fail"
    except ValueError:
        pass
