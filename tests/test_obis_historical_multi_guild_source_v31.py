"""Synthetic original IPT penguin / flying petrel source eligibility audit V31."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_obis_historical_multi_guild_source_v31 import (
    source_group_audit,source_species_guild,original_year_value,
    finite_nonnegative_original_quantity
)


def build():
    original=[]
    for j in range(2787):
        species="Pygoscelis adeliae" if j<1400 else "Pagodroma nivea"
        original.append({
            "scientificName":species,
            "year":str(1900+j%95),
            "eventDate":"",
            "locality":f"Island {j%10}",
            "individualCount":"0" if j==4 else ("5400000" if j==5 else str(j%100+1)),
            "decimalLatitude":str(-64 if j%2 else -55),
            "decimalLongitude":str(25+j%5),
            "lifeStage":"nests" if j%2 else "unknown",
            "basisOfRecord":"HumanObservation",
            "dynamicProperties":"N3",
            "associatedReferences":"field2020" if j<1500 else "Woehler",
        })
    return original


def test_original_penguin_and_flying_birds_are_in_same_first_party_sample():
    source=source_group_audit(build())
    assert source["original_record_n"]==2787
    assert source["original_all_12_source_species_guild_metrics"]["FLIGHTLESS_PENGUIN"]["original_guild_record_count"]==1400
    assert source["original_all_12_source_species_guild_metrics"]["FLYING_PETREL"]["original_guild_record_count"]==1387
    assert len(source["original_zero_quantity_rows_UNVERIFIED_SURVEYED_ABSENCE"])==1
    assert len(source["million_count_outliers_NOT_ACCEPTED_DIRECT_NEST_CENSUS"])==1
    assert source["original_occurrenceStatus_field_present"] is False
    assert source["biological_island_effect_models_fitted"]==0
    assert source["same_locality_names_not_independent_islands"] is True


def test_source_year_and_species_quantity_not_inferred_absence():
    assert source_species_guild("Macronectes halli")=="FLYING_PETREL"
    assert source_species_guild("Pygoscelis antarctica")=="FLIGHTLESS_PENGUIN"
    assert source_species_guild("FakeTaxon species")=="UNKNOWN_GUILD_HOLD"
    assert original_year_value({"year":"","eventDate":"1974-10-15"})==1974
    assert original_year_value({"year":"","eventDate":"unknown"}) is None
    assert finite_nonnegative_original_quantity({"individualCount":""}) is None
    assert finite_nonnegative_original_quantity({"individualCount":"0"})==0
    assert finite_nonnegative_original_quantity({"individualCount":"-3"}) is None


def test_historical_source_record_number_is_not_real_independent_islands():
    source=source_group_audit(build())
    penguin=source["original_all_12_source_species_guild_metrics"]["FLIGHTLESS_PENGUIN"]
    assert penguin["original_duplicate_species_year_literal_locality_group_n"]>0
    assert penguin["original_source_unique_nonempty_literal_locality_strings"]==10
    assert "original_source_valid_coordinates_rows" in penguin
