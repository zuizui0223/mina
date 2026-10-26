"""Synthetic schema QA for actual BAS Hart root count CSV, not ecology effects."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_bas_hart_ssi_count_source_v17 import parse_original_counts, choose_source


def test_first_party_csv_schema_counts_blank_not_zero():
    raw=b"island,site,species,direct_nests,estimated_nests\nZavodovski,Point A,Macaroni,5,0\nCandlemas,Point B,Adelie,3,\n"
    values,result=parse_original_counts(raw)
    assert result["status"]=="BAS_HART_ORIGINAL_SSI_COUNTS_CSV_SOURCE_SCHEMA_V17"
    assert result["first_party_source_nest_count_rows"]==2
    assert result["source_column_shape_and_literal_values"]["estimated_nests"]["nonempty_source_rows"]==1
    assert result["source_column_shape_and_literal_values"]["direct_nests"]["numeric_source_cell_count"]==2
    assert values[1]["estimated_nests"]==""
    assert result["original_nest_point_coordinate_csv_records_opened"]==0


def test_unknown_header_or_extra_values_stop():
    with pytest.raises(ValueError,match="SCHEMA_STOP"):
        parse_original_counts(b"island,island\nA,B\n")
    with pytest.raises(ValueError,match="SCHEMA_STOP"):
        parse_original_counts(b"island,species\nA,macaroni,extra\n")


def test_verified_live_source_file_only():
    files=[{
        "original_archive_relative_path":f"source{i}.csv",
        "source_file_url_https":"https://ramadda.data.bas.ac.uk/repository/entry/get/source.csv"
    } for i in range(163)]
    files.append({
        "original_archive_relative_path":"SSI_count_results.csv",
        "source_file_url_https":"https://ramadda.data.bas.ac.uk/repository/entry/get/SSI_count_results.csv?entryid=official",
        "original_publisher_archive_id":"official"
    })
    m={"status":"VERIFIED_ORIGINAL_SOURCE_FILES_PUBLISHER_SUMMARY_COUNT_DISCREPANCY",
       "original_all_file_metadata_only":files}
    x=choose_source(m)
    assert x["original_publisher_archive_id"]=="official"
    m["status"]="HOLD_INCOMPLETE_ORIGINAL_SOURCE_FILE_MANIFEST"
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        choose_source(m)
