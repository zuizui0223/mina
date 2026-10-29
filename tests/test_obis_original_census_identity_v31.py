"""Unit-test actual source semantics, no island hypotheses fitted."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_obis_original_census_identity_v31 import (
    source_count_class,source_taxon_group,source_audit
)


def test_negative_unknown_blank_and_zero_never_relabelled_surveyed_absence():
    assert source_count_class("-1.0")=="SOURCE_NEGATIVE_MINUS_ONE_UNKNOWN"
    assert source_count_class("-2")=="SOURCE_OTHER_NEGATIVE_COUNT_CODE"
    assert source_count_class("")=="ORIGINAL_BLANK_UNOBSERVED_COUNT"
    assert source_count_class("0")=="ORIGINAL_REPORTED_ZERO_ABSENCE_UNVERIFIED"
    assert source_count_class("2000.0")=="ORIGINAL_POSITIVE_NUMERIC_COUNT"
    assert source_count_class("NaN")=="ORIGINAL_NONFINITE_COUNT"
    assert source_taxon_group("Pygoscelis adeliae")=="PENGUIN"
    assert source_taxon_group("Macronectes giganteus")=="FLYING_SEABIRD"


def test_locality_time_species_multiple_observations_not_independent_islands():
    rows=[]
    for i in range(2787):
        if i<7:
            stage=["10.0","-1.0","0.0","","22.0","31.0","1.0"][i]
            year=["1978","1978","1978","1978","1980","1981","1981"][i]
            species="Pygoscelis adeliae" if i<5 else "Macronectes giganteus"
        else:
            stage="1.0";year="1983";species="Pygoscelis adeliae"
        rows.append({
            "core_id":str(i+1),
            "scientificName":species,
            "individualCount":stage,"year":year,
            "locality":"Cape Bird",
            "decimalLatitude":"-69.5",
            "decimalLongitude":"169.1",
            "eventDate":year+"-01-01T12:00:00Z",
            "lifeStage":"nest" if i%2==0 else "unknown",
            "basisOfRecord":"HumanObservation",
            "catalogNumber":str(i+1),
        })
    report=source_audit(rows,{
        "original_archive_row_count":2787,
        "original_zip_SHA256":"a"*64,
        "source_original_DwC_core_SHA256":"b"*64,
    })
    assert report["source_penguin_flying_seabird_count_semantics_by_original_group"]["FLYING_SEABIRD"]["original_source_row_total"]==2
    assert report["first_party_original_count_value_classes"]["SOURCE_NEGATIVE_MINUS_ONE_UNKNOWN"]==1
    assert report["first_party_original_count_value_classes"]["ORIGINAL_REPORTED_ZERO_ABSENCE_UNVERIFIED"]==1
    assert report["first_party_original_count_value_classes"]["ORIGINAL_BLANK_UNOBSERVED_COUNT"]==1
    assert report["source_locality_taxon_year_cells_with_multiple_source_records"]>0
    assert report["original_source_fields_and_observation_semantics"]["lifeStage"]["source_field_is_verified_nest_count_stage"] is False
    assert report["source_original_23_zero_count_rows_as_true_searched_absence_verified"] is False
    assert report["ecological_island_breeding_model_fitted"] is False
