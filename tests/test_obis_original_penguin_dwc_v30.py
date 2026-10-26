"""Offline tests for the original OBIS IPT historical penguin archive source."""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_obis_original_penguin_dwc_v30 import (
    safe_source_zip,parse_dwc_core,summarize_original_rows
)


def source_zip(core_rows=None,malicious=False):
    if core_rows is None:
        core_rows=(
            "id\tscientificName\tyear\tindividualCount\tdecimalLatitude\tdecimalLongitude\tlocality\n"
            "1001\tPygoscelis adeliae\t1986\t321\t-69.1\t74.0\tBeaufort\n"
            "1002\tPygoscelis adeliae\t1987\t295\t-69.1\t74.0\tBeaufort\n"
            "1003\tPygoscelis papua\t1991\t\t-58.3\t-26.3\tSaunders\n"
        )
    xml=(
        '<archive xmlns="http://rs.tdwg.org/dwc/text/">'
        '<core fieldsTerminatedBy="\\t" fieldsEnclosedBy=\'"\' '
        'ignoreHeaderLines="1" '
        'rowType="http://rs.tdwg.org/dwc/terms/Occurrence">'
        '<files><location>occurrence.txt</location></files>'
        '<id index="0"/>'
        '<field index="1" term="http://rs.tdwg.org/dwc/terms/scientificName"/>'
        '<field index="2" term="http://rs.tdwg.org/dwc/terms/year"/>'
        '<field index="3" term="http://rs.tdwg.org/dwc/terms/individualCount"/>'
        '<field index="4" term="http://rs.tdwg.org/dwc/terms/decimalLatitude"/>'
        '<field index="5" term="http://rs.tdwg.org/dwc/terms/decimalLongitude"/>'
        '<field index="6" term="http://rs.tdwg.org/dwc/terms/locality"/>'
        '</core></archive>'
    )
    out=io.BytesIO()
    with zipfile.ZipFile(out,mode="w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("meta.xml",xml)
        z.writestr("../occurrence.txt" if malicious else "occurrence.txt",core_rows)
    return out.getvalue()


def test_original_dwc_count_source_values_are_not_inferred_bird_zero():
    z,receipt=safe_source_zip(source_zip())
    assert len(receipt["original_zip_SHA256"])==64
    with z:
        rows,meta=parse_dwc_core(z)
    assert len(rows)==3
    assert list(rows[0])==[
        "core_id","scientificName","year","individualCount",
        "decimalLatitude","decimalLongitude","locality"
    ]
    report=summarize_original_rows(rows,{**receipt,**meta})
    assert report["original_archive_row_count"]==3
    assert report["original_source_numeric_breeding_or_count_fields"]["individualCount"]["count_nonmissing_numeric_nonnegative"]==2
    assert report["original_source_numeric_breeding_or_count_fields"]["individualCount"]["strictly_positive_original_rows"]==2
    assert report["original_source_year_min"]==1986
    assert report["original_source_year_max"]==1991
    assert report["original_source_decimal_coordinate_rows_valid"]==3
    assert report["original_source_coordinate_pairs_used_by_multiple_rows"]==1
    assert report["row_count_matches_publisher_listing"] is False
    assert report["source_presence_record_missingness_is_surveyed_breeding_absence"] is False
    assert report["new_ecological_island_effect_fitted"] is False


def test_zip_slip_is_rejected_before_unsafe_file_interpretation():
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        safe_source_zip(source_zip(malicious=True))


def test_obis_core_malformed_width_is_hard_stop():
    broken=source_zip("a\tb\tc\n")
    z,_=safe_source_zip(broken)
    with z,pytest.raises(ValueError,match="SCHEMA_STOP"):
        parse_dwc_core(z)
