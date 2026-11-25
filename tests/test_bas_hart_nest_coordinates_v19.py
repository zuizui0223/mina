"""Zero-biology classification of Hart nest coordinate CSV sources."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_bas_hart_nest_coordinates_v19 as v19


def original(path,loc):
    return {
      "original_archive_relative_path":path,
      "top_level_source_locality_folder":loc,
      "original_publisher_archive_id":"publisher-original",
      "source_file_url_https":
         "https://ramadda.data.bas.ac.uk/repository/entry/get/"+path.split("/")[-1]+"?entryid=synth"
    }


def test_source_label_mixed_2022_chinstrap_and_outlines_never_rescued():
    b=v19.classify_filename(original(
        "Zavodovski/coordinates/ZAVO_2022_Chinstrap_coordinates.csv","Zavodovski"))
    assert b["species_source_filename_label"]=="CHINSTRAP"
    assert b["2022_Zavodovski_chinstrap_not_2020"] is True
    outline=v19.classify_filename(original(
        "Zavodovski/coordinates/ZAVO_Macaroni_colony_outline_coordinates.csv","Zavodovski"))
    assert outline["file_source_type"]=="SOURCE_COLONY_OUTLINE_VERTEX_NOT_NEST"
    mixed=v19.classify_filename(original(
        "Zavodovski/coordinates/ZAVO_2020_Mixed_species_coordinates.csv","Zavodovski"))
    assert mixed["species_source_filename_label"]=="MIXED_UNASSIGNED"


def test_source_root_count_not_species_individual_nests():
    x=v19.classify_filename(original("SSI_count_results.csv","ROOT_COUNT_RESULTS"))
    assert x["file_source_type"]=="ROOT_COUNTS_NOT_NEST_POINT"


def test_publisher_real_filename_identity_cannot_sneak_unverified_locality():
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        v19.classify_filename(original("UNKNOWN_SITE/coordinate.csv","UNKNOWN_SITE"))
