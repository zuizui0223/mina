"""Invented Event/Occurrence/eMoF rows only; no actual ecology effects."""
import hashlib
import io
import sys
from pathlib import Path
import zipfile

import pytest
pytest.importorskip("requests")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import join_apbp_nest_records_v2 as v


def synthetic(mixed=False,broken=False):
    metadata=r'''<?xml version="1.0" encoding="UTF-8"?>
    <archive xmlns="http://rs.tdwg.org/dwc/text/" metadata="eml.xml">
     <core rowType="http://rs.tdwg.org/dwc/terms/Event" fieldsTerminatedBy="\t" ignoreHeaderLines="1">
      <files><location>event.txt</location></files><id index="0"/>
      <field index="1" term="http://rs.tdwg.org/dwc/terms/eventDate"/>
      <field index="2" term="http://rs.tdwg.org/dwc/terms/locationID"/>
     </core>
     <extension rowType="http://rs.tdwg.org/dwc/terms/Occurrence" fieldsTerminatedBy="\t" ignoreHeaderLines="1">
      <files><location>occurrence.txt</location></files><coreid index="0"/>
      <field index="1" term="http://rs.tdwg.org/dwc/terms/occurrenceID"/>
      <field index="2" term="http://rs.tdwg.org/dwc/terms/scientificName"/>
      <field index="3" term="http://rs.tdwg.org/dwc/terms/organismQuantity"/>
      <field index="4" term="http://rs.tdwg.org/dwc/terms/organismQuantityType"/>
     </extension>
     <extension rowType="http://rs.iobis.org/obis/terms/ExtendedMeasurementOrFact" fieldsTerminatedBy="\t" ignoreHeaderLines="1">
      <files><location>measure.txt</location></files><coreid index="0"/>
      <field index="1" term="http://rs.tdwg.org/dwc/terms/occurrenceID"/>
      <field index="2" term="http://rs.tdwg.org/dwc/terms/measurementID"/>
      <field index="3" term="http://rs.tdwg.org/dwc/terms/measurementType"/>
      <field index="4" term="http://rs.tdwg.org/dwc/terms/measurementValue"/>
      <field index="5" term="http://rs.tdwg.org/dwc/terms/measurementAccuracy"/>
      <field index="6" term="http://rs.tdwg.org/dwc/terms/measurementUnit"/>
     </extension>
    </archive>'''.encode()
    event=b"eventID\tdate\tsite\nE1\t2001-12-01\tISL1\nE2\t2002-12-01\tISL1\n"
    if mixed:
        event+=b"E3\t2002-12-01\tISL1\n"
    occ=b"event\toccID\ttaxon\tcount\ttype\nE1\tO1\tPygoscelis antarctica\t10\tnumber of nests\nE1\tO2\tPygoscelis papua\t5\tnumber of nests\nE2\tO3\tPygoscelis antarctica\t0\tnumber of nests\n"
    emof=(b"event\toccID\tmeasurementID\tmt\tmv\tprecision\tunit\n"
          b"E1\tO1\tM1\tthe number of nests (equivalently, breeding pairs)\tN1\tN1\tnests\n"
          b"E1\tO2\tM2\tthe number of nests (equivalently, breeding pairs)\tN2\tN2\tnests\n"
          b"E2\tO3\tM3\tthe number of nests (equivalently, breeding pairs)\tN3\tN3\tnests\n")
    if mixed:
        occ+=b"E3\tO4\tPygoscelis antarctica\t10\tnumber of nests\n"
        emof+=b"E3\tO4\tM4\tthe number of nests (equivalently, breeding pairs)\tN1\tN1\tnests\n"
    if broken:
        emof=emof.replace(b"E1\tO2\tM2",b"E1\tO99\tM2")
    files={"meta.xml":metadata,"event.txt":event,"occurrence.txt":occ,"measure.txt":emof}
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for k,b in files.items(): z.writestr(k,b)
    return out.getvalue(),dict(Event=3 if mixed else 2,
                              Occurrence=4 if mixed else 3,
                              ExtendedMeasurementOrFact=4 if mixed else 3)


def test_join_by_unique_occurrenceID_not_eventID_even_with_two_species_in_one_event():
    raw,n=synthetic()
    rows,ev,occ,by=v.raw_join(raw,expected_sha=hashlib.sha256(raw).hexdigest(),expected_rows=n)
    assert len(rows)==3
    assert by["E1"]==2
    assert [(x["scientificName_accepted"],x["nest_numeric_candidate"]) for x in rows]==[
        ("Pygoscelis antarcticus",10),("Pygoscelis papua",5),("Pygoscelis antarcticus",0)]
    assert rows[0]["measurementValue_original"]=="N1"  # not used as abundance!
    assert sum(r["eligibility"]=="ELIGIBLE_NEST_RECORD_ONLY" for r in rows)==3
    assert rows[0]["scientificName_original"]=="Pygoscelis antarctica"
    result=v.summarize(rows,ev,occ,by,hashlib.sha256(raw).hexdigest())
    assert result["explicit_measured_nest_zeros"]==1
    assert result["site_species_histories_with_2plus_distinct_years"]==1
    assert result["site_species_histories_with_5plus_distinct_years"]==0
    assert result["penguin_ecological_slopes_or_pvalues_fitted"]==0
    assert not result["environmental_covariates_joined"]


def test_unknown_organism_quantity_type_is_not_assumed_to_be_nests():
    raw,n=synthetic()
    with zipfile.ZipFile(io.BytesIO(raw)) as zz:
        members={k:zz.read(k) for k in zz.namelist()}
    members["occurrence.txt"]=members["occurrence.txt"].replace(
        b"O1\tPygoscelis antarctica\t10\tnumber of nests",
        b"O1\tPygoscelis antarctica\t10\tunknown")
    z=io.BytesIO()
    with zipfile.ZipFile(z,"w") as out:
        for k,vv in members.items():out.writestr(k,vv)
    rr,n2,occ,by=v.raw_join(z.getvalue(),expected_sha=hashlib.sha256(z.getvalue()).hexdigest(),expected_rows=n)
    assert rr[0]["eligibility"]=="HOLD_ORGANISM_QUANTITY_UNIT"
    assert rr[0]["nest_numeric_candidate"]==""


def test_no_cross_species_assignment_with_missing_occurrence_id():
    raw,n=synthetic(broken=True)
    with pytest.raises(ValueError,match="eMoF orphan"):
        v.raw_join(raw,expected_sha=hashlib.sha256(raw).hexdigest(),expected_rows=n)


def test_original_source_sha_is_mandatory():
    raw,n=synthetic()
    with pytest.raises(ValueError,match="original zip SHA changed"):
        v.raw_join(raw,expected_rows=n)


def test_no_negative_or_estimated_count_coercion():
    assert v.numeric("10")==10
    assert v.numeric("0")==0
    assert v.numeric("-10") is None
    assert v.numeric("~100") is None
    assert v.numeric("10-20") is None
    assert v.numeric("1.5") is None


def test_exact_same_site_species_year_is_not_silently_deduplicated():
    raw,n=synthetic(mixed=True)
    rows,ev,occ,by=v.raw_join(raw,expected_sha=hashlib.sha256(raw).hexdigest(),expected_rows=n)
    qa=v.summarize(rows,ev,occ,by,hashlib.sha256(raw).hexdigest())
    assert qa["same_site_species_year_duplicate_groups"]==1
    assert qa["same_site_species_year_duplicate_record_rows"]==2
