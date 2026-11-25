"""Synthetic original IPT/OBIS Darwin Core Archive science/method gates."""
from __future__ import annotations
import hashlib,io,zipfile
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_obis_historical_penguin_dwca_v30 import (
    safe_archive_files,original_dwc_core,describe_original_census
)


def synthetic_zip():
    meta='''<?xml version="1.0" encoding="utf-8"?>
<archive xmlns="http://rs.tdwg.org/dwc/text/" metadata="eml.xml">
  <core rowType="http://rs.tdwg.org/dwc/terms/Occurrence"
        fieldsTerminatedBy="\\t" ignoreHeaderLines="1"
        encoding="utf-8">
    <files><location>occurrence.txt</location></files>
    <id index="0"/>
    <field index="0" term="http://rs.tdwg.org/dwc/terms/occurrenceID"/>
    <field index="1" term="http://rs.tdwg.org/dwc/terms/scientificName"/>
    <field index="2" term="http://rs.tdwg.org/dwc/terms/eventDate"/>
    <field index="3" term="http://rs.tdwg.org/dwc/terms/individualCount"/>
    <field index="4" term="http://rs.tdwg.org/dwc/terms/locality"/>
    <field index="5" term="http://rs.tdwg.org/dwc/terms/decimalLatitude"/>
    <field index="6" term="http://rs.tdwg.org/dwc/terms/decimalLongitude"/>
  </core>
</archive>
'''
    data=("occurrenceID\tscientificName\teventDate\tindividualCount\tlocality\tdecimalLatitude\tdecimalLongitude\n"
         "occ-1\tPygoscelis adeliae\t1950-01-01\t10\tIsland A\t-65\t50\n"
         "occ-2\tPygoscelis antarcticus\t1974-01-01\t\tIsland B\t-63\t-42\n")
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w") as archive:
        archive.writestr("meta.xml",meta)
        archive.writestr("occurrence.txt",data)
    return out.getvalue()


def test_original_dwca_source_core_species_count_must_be_declared():
    raw=synthetic_zip()
    files,source_sha=safe_archive_files(raw)
    assert len(source_sha)==64
    rows,source=original_dwc_core(files)
    assert len(rows)==2
    assert rows[0]["individualCount"]=="10"
    assert rows[1]["individualCount"]==""
    receipt=describe_original_census(rows)
    assert receipt["original_dwca_occurrence_core_rows"]==2
    assert receipt["source_quantity_field_observational_numeric_support"]["individualCount"]["original_rows_with_finite_nonnegative_numeric_value"]==1
    assert receipt["original_field_unvisited_site_recoded_to_zero"] is False
    assert receipt["original_1900_1996_penguin_census_is_independent_of_2026_MAPPPD"] is False


def test_archive_zip_slip_and_wrong_source_scope_stop():
    raw=io.BytesIO()
    with zipfile.ZipFile(raw,"w") as archive:
        archive.writestr("meta.xml",b"<archive/>")
        archive.writestr("../leak.txt",b"bad")
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        safe_archive_files(raw.getvalue())


def test_metadata_only_appearance_is_not_zero_colony_observation():
    rows=[{"scientificName":"Pygoscelis adeliae","locality":"Island A",
           "eventDate":"1922","occurrenceStatus":"present"}]
    data=describe_original_census(rows)
    assert data["source_quantity_field_observational_numeric_support"]=={}
    assert data["original_field_unvisited_site_recoded_to_zero"] is False
    assert data["new_species_island_biological_effects_fitted"]==0
