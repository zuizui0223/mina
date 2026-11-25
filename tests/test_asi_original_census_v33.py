"""Offline original ASI 2013 source census stage and accuracy QA tests."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_asi_original_census_v33 import (
    parse_original_rows,source_record_audit,accuracy_code,parse_number
)


def test_counted_object_N_is_not_chick_C_and_accuracy_3_is_not_primary():
    assert accuracy_code("1")==1
    assert accuracy_code("2.0")==2
    assert accuracy_code("5")==5
    assert accuracy_code("none") is None
    assert parse_number("3,000")==3000
    assert parse_number("-1") is None


def test_complete_source_grid_region_stage_and_source_history_not_113_islands():
    raw=[]
    for i in range(1124):
        k=i%113
        taxa=("ADPE","CHPE","GEPE","MCPE","BESH","KEGU","SOGP")
        region=("CW","EI","NE","NW","SH","SO","SW")
        raw.append({
            "Site_ID":f"I{k:03d}",
            "Region":region[i%7],
            "Site_name":"test",
            "Latitude":"-65",
            "Longitude":"-63",
            "Species":taxa[i%7],
            "Date":"12/xx/2012" if i==0 else "12/21/2012",
            "Season":"2012" if i%2 else "2011",
            "Count":"100" if i>1 else "0",
            "Counted_object":"C" if i==1 else "N",
            "Accuracy":"3" if i==2 else "1",
            "Notes":"",
            "Source":"Other author" if i==3 else "ASI"
        })
    rpt=source_record_audit(raw,list(raw[0]))
    assert rpt["original_first_party_publisher_site_census_rows"]==1124
    assert rpt["original_source_unique_author_site_IDs"]==113
    assert rpt["original_counted_object_stage_literal_counts"]["C"]==1
    assert rpt["original_accuracy_literal_code_counts"]["3"]==1
    assert rpt["source_original_literal_zeros_not_assumed_survey_absence"]==2
    assert rpt["source_original_asi_primary_nest_accuracy_1_or_2_positive_eligible_rows_before_duplicate_gate"]<1124
    assert rpt["original_secondhand_source_records_count_as_ASI_new_field_observation"] is False
    assert rpt["new_island_breeding_ecological_effect_fit"] is False


def test_original_column_schema_not_inferred_from_other_papers():
    contents=(
        "Site ID,Region,Site name,Latitude,Longitude,Species,Date,Season,Count,"
        "Counted object,Accuracy,Notes,Source\n"
        "SITE,CW,Test,-68,59,ADPE,xx/xx/2012,2012,100,N,1,,ASI\n"
    ).encode("utf-8")
    rows,headers=parse_original_rows(contents)
    assert rows[0]["Site_ID"]=="SITE"
    assert rows[0]["Counted_object"]=="N"
    assert len(headers)==13
