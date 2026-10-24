"""APBP original-source-only test fixtures: invented colonies, no effect test."""
import importlib.util
import io
from pathlib import Path
import zipfile

import pytest
pytest.importorskip("requests")

SOURCE=Path(__file__).resolve().parents[1]/"scripts"/"audit_apbp_darwincore_source_v1.py"
spec=importlib.util.spec_from_file_location("apbp_v1",SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def synthetic():
    meta=r'''<?xml version="1.0" encoding="UTF-8"?>
    <archive xmlns="http://rs.tdwg.org/dwc/text/" metadata="eml.xml">
     <core rowType="http://rs.tdwg.org/dwc/terms/Event" fieldsTerminatedBy="\t" ignoreHeaderLines="1">
      <files><location>event.txt</location></files>
      <id index="0"/>
      <field index="1" term="http://rs.tdwg.org/dwc/terms/eventDate"/>
      <field index="2" term="http://rs.tdwg.org/dwc/terms/locationID"/>
      <field index="3" term="http://rs.tdwg.org/dwc/terms/samplingProtocol"/>
     </core>
     <extension rowType="http://rs.tdwg.org/dwc/terms/Occurrence" fieldsTerminatedBy="\t" ignoreHeaderLines="1">
      <files><location>occurrence.txt</location></files>
      <coreid index="0"/>
      <field index="1" term="http://rs.tdwg.org/dwc/terms/scientificName"/>
     </extension>
     <extension rowType="http://rs.iobis.org/obis/terms/ExtendedMeasurementOrFact" fieldsTerminatedBy="\t" ignoreHeaderLines="1">
      <files><location>measure.txt</location></files>
      <coreid index="0"/>
      <field index="1" term="http://rs.tdwg.org/dwc/terms/measurementType"/>
      <field index="2" term="http://rs.tdwg.org/dwc/terms/measurementValue"/>
      <field index="3" term="http://rs.tdwg.org/dwc/terms/measurementUnit"/>
     </extension>
    </archive>'''.encode()
    sources={
        "meta.xml":meta,
        "event.txt":b"eventID\tdate\tsite\tmethod\nE1\t2001-12-01\tISL1\tground\nE2\t2002-12-01\tISL1\tground\nE3\t2003-12-01\tISL2\tsatellite\n",
        "occurrence.txt":b"event\tspecies\nE1\tPygoscelis adeliae\nE2\tPygoscelis adeliae\nE3\tPygoscelis papua\n",
        "measure.txt":b"event\ttype\tvalue\tunit\nE1\tnests\t10\tpairs\nE2\tnests\t9\tpairs\nE3\tnests\t12\tpairs\n",
    }
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for name,value in sources.items():
            z.writestr(name,value)
    return buf.getvalue()


def test_successfully_join_source_events_species_and_measurements():
    r=m.audited_schema(synthetic(),{"Event":3,"Occurrence":3,"ExtendedMeasurementOrFact":3})
    assert r["status"]=="SOURCE_LOCKED_SCHEMA_ONLY_NO_ECOLOGICAL_EFFECT"
    assert r["coverage_metadata"]["distinct_original_site_identifiers"]==2
    assert r["coverage_metadata"]["surveyed_site_ids_with_at_least_2_distinct_years"]==1
    assert r["tables"]["Event"]["rows"]==3
    assert r["tables"]["Occurrence"]["rows"]==3
    assert r["tables"]["ExtendedMeasurementOrFact"]["rows"]==3
    assert r["coverage_metadata"]["known_six_species_occurrence_rows"]["Pygoscelis adeliae"]==2
    assert r["eco_models_fitted"]==0
    assert r["marine_or_island_environment_joined"] is False
    assert r["no_missing_year_as_zero"] is True


def test_original_v23_count_locked_not_compatible_with_toy_data():
    with pytest.raises(ValueError,match="SOURCE_VERSION_STOP"):
        m.audited_schema(synthetic())


def test_prevent_zip_path_traversal():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w") as z:
        z.writestr("meta.xml",b"<archive/>")
        z.writestr("../outside",b"secret")
    with pytest.raises(ValueError,match="unsafe ZIP"):
        m.safe_zip(buf.getvalue())


def test_no_zip_html_fails_closed():
    with pytest.raises(ValueError,match="not ZIP"):
        m.safe_zip(b"<html>source blocked</html>")


def test_date_intervals_only_parse_declared_year_not_absence():
    assert m.event_year("1998-12-17")==1998
    assert m.event_year("1982")==1982
    assert m.event_year("unknown") is None
    assert m.event_year("") is None


def test_broken_core_link_rejected():
    orig=synthetic()
    with zipfile.ZipFile(io.BytesIO(orig)) as source:
        parts={name:source.read(name) for name in source.namelist()}
    parts["measure.txt"]=parts["measure.txt"].replace(b"E2\tnests",b"NOEVENT\tnests")
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as archive:
        for name,value in parts.items():archive.writestr(name,value)
    with pytest.raises(ValueError,match="foreign event keys unlinked"):
        m.audited_schema(b.getvalue(),{"Event":3,"Occurrence":3,"ExtendedMeasurementOrFact":3})
