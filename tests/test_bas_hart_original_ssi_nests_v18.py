"""Original SSI nest ledger: additive source receipts, imputation, missingness."""
from __future__ import annotations
import pytest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyze_bas_hart_original_ssi_nests_v18 import (
    SITE_IDS,ROW_CLASSES,source_matrix_counts,ledger
)


def synthetic():
    rows=[]
    for c in ROW_CLASSES:
        x={"":c}
        for site in SITE_IDS:x[site]=""
        rows.append(x)
    t={r[""]:r for r in rows}
    t["Adelie"]["Candlemas"]="10"
    t["Total"]["Candlemas"]="10"
    t["Chinstrap"]["Zavodovski"]="40"
    t["Mixed"]["Zavodovski"]="20"
    t["Unknown_estimate"]["Zavodovski"]="12.5"
    t["Total"]["Zavodovski"]="72.5"
    t["Adelie"]["Beach_Point"]="10"
    t["Chinstrap"]["Beach_Point"]="7"
    t["Total"]["Beach_Point"]="100"  # original total inconsistency must be surfaced
    return rows


def test_four_taxa_and_counted_mixed_estimates_are_separate():
    rows=synthetic()
    header={
        "original_wide_site_by_count_category_matrix":True,
        "source_column_names":["",*SITE_IDS]
    }
    data=source_matrix_counts(rows,header)
    result=ledger(data)
    assert result["original_survey_locality_n"]==7
    assert result["original_named_physical_island_group_n"]==5
    d={r["original_survey_locality"]:r for r in result["reported_source_count_data_by_original_survey_locality"]}
    assert d["Zavodovski"]["original_source_four_species_labelled_sum"]==40
    assert d["Zavodovski"]["original_source_counted_mixed_or_unknown_species_nests"]==20
    assert d["Zavodovski"]["original_source_spatially_extrapolated_nests"]==pytest.approx(12.5)
    assert d["Zavodovski"]["publisher_reported_total_equals_source_cell_arithmetic"] is True
    assert d["Zavodovski"]["fraction_species_identified_source_labeled_nests_of_total_if_reconciled"]==pytest.approx(40/72.5)
    assert d["Zavodovski"]["original_zavo_chinstrap_2022_supplement_may_create_mixed_year_label"] is True
    assert d["Candlemas"]["original_Candlemas_only_Adelie_countable_due_image_resolution"] is True
    assert d["Candlemas"]["source_original_nonreported_species_taxon_are_true_absence"] is False
    assert d["Beach_Point"]["publisher_reported_total_equals_source_cell_arithmetic"] is False
    assert d["Beach_Point"]["fraction_species_identified_source_labeled_nests_of_total_if_reconciled"] is None
    assert result["source_species_nest_temporal_replicates_n"]==0


def test_original_source_count_matrix_cannot_silently_create_zero_for_blank():
    rows=synthetic()
    schema={
        "original_wide_site_by_count_category_matrix":True,
        "source_column_names":["",*SITE_IDS]
    }
    x=source_matrix_counts(rows,schema)
    assert x["Gentoo","Candlemas"] is None
    rows[0]["Zavodovski"]="17.5"
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        source_matrix_counts(rows,schema)


def test_species_labels_or_locality_order_not_selected_from_outcomes():
    rows=synthetic()
    wrong={"original_wide_site_by_count_category_matrix":True,
           "source_column_names":["",*SITE_IDS[::-1]]}
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        source_matrix_counts(rows,wrong)
    rows[1][""]="CHPE"
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        source_matrix_counts(rows,{"original_wide_site_by_count_category_matrix":True,
           "source_column_names":["",*SITE_IDS]})
