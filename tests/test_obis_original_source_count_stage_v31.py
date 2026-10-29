"""Synthetic original Woehler/OBIS source count-stage eligibility tests.

Source sample quantity in older IPT archive is unverified breeding-pair stage.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_obis_original_source_count_stage_v31 import (
    source_year,source_count,audit_historical_source,source_literal_context
)


def historical_synthetic():
    rows=[]
    for i in range(2787):
        year=1940+i%3
        count=str(i%9+1) if i<2377 else ""
        if i<23:
            count="0"
        site="Islet Alpha" if i%2==0 else "Islet Beta"
        rows.append({
            "scientificName":"Pygoscelis adeliae",
            "year":str(year),
            "eventDate":f"{year}-01-01",
            "individualCount":count,
            "waterBody":"South Ocean",
            "stateProvince":"East Antarctica",
            "county":"Region1",
            "locality":site,
            "lifeStage":"adult" if i<2000 else "",
            "basisOfRecord":"HumanObservation",
            "catalogNumber":f"A-{i}",
            "occurrenceRemarks":"",
            "dynamicProperties":"",
            "coordinatePrecision":"0.01",
        })
    return rows


def test_zero_is_not_inferred_independently_surveyed_absence():
    assert source_count({"individualCount":"0"})==(0.0,"NUMERIC_NONNEGATIVE_INTEGER")
    assert source_count({"individualCount":""})==(None,"MISSING")
    assert source_count({"individualCount":"unknown"})==(None,"NONNUMERIC")
    assert source_count({"individualCount":"-1"})==(None,"NONFINITE_OR_NEGATIVE")
    assert source_count({"individualCount":"1.25"})==(1.25,"FINITE_NONINTEGER")


def test_original_exact_locality_stage_repeat_cannot_claim_independent_field_surveys():
    rows=historical_synthetic()
    z=audit_historical_source(rows)
    assert z["original_source_publisher_record_n"]==2787
    assert z["original_source_numeric_integer_count_field_n"]==2377
    assert z["source_integer_counts_which_are_zero_n"]==23
    assert z["original_exact_locality_taxon_stage_candidate_groups_with_2plus_years"]>=2
    assert z["original_year_location_stage_groups_with_2plus_count_records"]>0
    assert z["original_individualCount_is_verified_breeding_pair_count"] is False
    assert z["original_numeric_zero_is_independently_surveyed_absence"] is False
    assert z["original_locality_text_is_verified_unique_island"] is False
    assert z["new_ecological_island_time_series_effect_fitted"] is False


def test_original_year_date_and_unknown_stage_handling():
    assert source_year({"year":"1901","eventDate":""})==1901
    assert source_year({"year":"","eventDate":"1895-01-01"})==1895
    assert source_year({"year":"2001","eventDate":"1990-03-01"})==1990
    assert source_year({"year":"","eventDate":"strange"}) is None
    fields=source_literal_context([{"lifeStage":"adult","occurrenceRemarks":"survey"},
                                    {"lifeStage":"","occurrenceRemarks":""}])
    assert fields["lifeStage"]["original_nonblank_rows"]==1
    assert fields["occurrenceRemarks"]["original_nonblank_rows"]==1
