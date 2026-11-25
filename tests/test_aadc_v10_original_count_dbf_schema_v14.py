"""Pure source-schema semantics: field names do not prove nest count values."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_aadc_v10_original_count_dbf_schema_v14 import (
    normalized,STRONG_COUNT_FIELDS,summarize_source_fields
)


def records():
    out=[]
    for i in range(13):
        years=(2012,2013,2015,2016) if i==0 else (2013,2015)
        for year in years:
            candidate=["nest_count"] if i==0 else ["Shape_Area","SiteID"]
            out.append({
                "site_id":str(74000+i),
                "source_group":"HBE" if i<6 else "HBW",
                "season_start_year":year,
                "original_DBf_field_names":candidate,
                "definite_semantic_count_candidate_columns":[
                    normalized(x) for x in candidate if normalized(x) in STRONG_COUNT_FIELDS],
                "vague_count_like_columns_not_assumed_nest_counts":[],
                "any_strong_semantic_field_name":i==0
            })
    assert len(out)==28
    return out


def test_evidence_field_presence_never_verifies_actual_breeding_pairs():
    result=summarize_source_fields(records())
    assert result["original_source_repeat_polygon_layers"]==28
    assert result["original_source_repeat_site_IDs"]==13
    assert result["original_original_source_15_observed_pair_count"]==15
    assert result["original_source_yearfiles_with_strong_named_count_field"]==4
    assert result["successive_source_site_pair_with_same_strong_count_field"]==3
    assert result["actual_breeding_pair_count_data_available_verified"] is False
    assert result["original_count_values_read"]==0
    assert result["V10_original_polygon_area_ratio_is_breeding_pair_count_change"] is False


def test_count_aliases_conservative_and_area_not_a_nest_measurement():
    assert normalized("Number occupied nests")=="number_occupied_nests"
    assert normalized("number-occupied nests") in STRONG_COUNT_FIELDS
    assert normalized("Shape_Area") not in STRONG_COUNT_FIELDS
    assert normalized("total") not in STRONG_COUNT_FIELDS
    assert normalized("n") not in STRONG_COUNT_FIELDS
