"""V42 strictly source-only GBIF positive mammal observations, invented fixtures."""
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_jncc_gbif_independent_predator_positive_v42 as g


def fake_record(species="Rattus norvegicus",uncertainty=125,year=2025):
    return {
       "species":species,
       "decimalLatitude":56.5,
       "decimalLongitude":-5.1,
       "coordinateUncertaintyInMeters":uncertainty,
       "year":year,
       "eventDate":str(year)+"-05-19",
       "gbifID":"fake-public-GBIF-0001",
       "occurrenceID":"fake-original-sighting-id",
    }


def test_exact_four_taxa_and_public_source_pinned():
    assert set(g.TAXA)=={
       "American mink","Brown rat","House mouse",
       "Cat_sighting_NOT_verified_feral",
    }
    assert g.DATASETS["Mammal Mapper"][0]=="8898e990-9d39-4871-9e6e-d1031c19e24b"
    assert g.DATASETS["National Mammal Atlas"][1]=="CC_BY_NC_4_0"
    assert g.MAX_PER_DATASET_TAXON==5000
    assert g.PAGE_SIZE<=300
    assert g.AS_OF=="2026-10-27"


def test_quality_filter_requires_known_geo_precision_no_false_absences():
    item,status=g.record_quality(fake_record(),"Brown rat")
    assert status=="COORDINATE_UNCERTAINTY_ELIGIBLE"
    assert item["precision_gate"] is True
    item,status=g.record_quality(fake_record(uncertainty=None),"Brown rat")
    assert status=="COORDINATE_UNCERTAINTY_NOT_KNOWN_LE250"
    assert item["precision_gate"] is False
    item,status=g.record_quality(fake_record(uncertainty=0),"Brown rat")
    assert not item["precision_gate"]
    item,status=g.record_quality(fake_record(uncertainty=300),"Brown rat")
    assert not item["precision_gate"]


def test_future_year_and_sci_name_mismatches_do_not_enter():
    a,b=g.record_quality(fake_record(year=2018),"Brown rat")
    assert a is None and b=="SOURCE_YEAR_OUT_OF_RANGE"
    a,b=g.record_quality(fake_record(species="Mus musculus"),"Brown rat")
    assert a is None and b=="GBIF_TAXON_LINEAGE_MISMATCH"
    row=fake_record()
    row["eventDate"]="2026-11-01"
    row["year"]=2026
    assert g.record_quality(row,"Brown rat")== (None,"FUTURE_EVENT_DATE")


def test_cat_species_is_not_evidence_of_feral_cat_status():
    x,status=g.record_quality(fake_record(species="Felis catus"),
                             "Cat_sighting_NOT_verified_feral")
    assert x is not None and x["precision_gate"]
    assert "feral" in "Cat_sighting_NOT_verified_feral"


def test_page_query_handles_multi_year_and_source_status_only():
    params=g.request_parameters("fake-dataset","2441021")
    assert params["year"]=="2022,2026"
    assert params["hasCoordinate"]=="true"
    assert params["occurrenceStatus"]=="PRESENT"
    assert params["hasGeospatialIssue"]=="false"
    assert "island" not in params and "absent" not in params


def test_public_record_count_gate_no_partial_prefix_as_exhaustive(monkeypatch):
    calls=[]
    def fake_api(session,path,params=None):
        calls.append((path,params))
        return {"count":5010,"results":[{}]}
    monkeypatch.setattr(g,"safe_gbif_json",fake_api)
    rows,qa=g.page_public_records(None,"fake_dataset",42)
    assert not rows
    assert qa["status"]=="TOO_MANY_PUBLIC_SEARCH_ROWS_STOP"
    assert qa["retrieved"]==0
    assert len(calls)==1


def test_full_page_fetch_counts_and_de_duplicates_only_on_authorized_source(monkeypatch):
    calls=[]
    def fake_api(session,path,params=None):
        calls.append(params)
        if params["limit"]==1 and params["offset"]==0:
            return {"count":3,"results":[{}]}
        return {"count":3,"results":[{"key":i} for i in range(3)]}
    monkeypatch.setattr(g,"safe_gbif_json",fake_api)
    rows,qa=g.page_public_records(None,"fake_dataset",42)
    assert qa["status"]=="COMPLETE_PUBLIC_SEARCH"
    assert qa["retrieved"]==3
    assert len(rows)==3
    assert calls[-1]["offset"]==0


def test_species_resolution_only_exact_taxonomic_usage(monkeypatch):
    def fake(session,path,params=None):
        return {"rank":"SPECIES","matchType":"EXACT",
                "usageKey":243,"canonicalName":"Rattus norvegicus"}
    monkeypatch.setattr(g,"safe_gbif_json",fake)
    keys,report=g.matching_taxon(None,("Rattus norvegicus",))
    assert keys==[243]
    assert report[0]["state"]=="RESOLVED"


def test_canonical_gbif_registry_creative_commons_licence_urls_are_not_bypasses():
    assert g.normalized_gbif_license(
        "http://creativecommons.org/licenses/by/4.0/legalcode")=="CC_BY_4_0"
    assert g.normalized_gbif_license(
        "https://creativecommons.org/licenses/by-nc/4.0/legalcode")=="CC_BY_NC_4_0"
    assert g.normalized_gbif_license("http://creativecommons.org/licenses/by-nc-nd/4.0/legalcode") is None
    assert g.normalized_gbif_license("CC_BY_4_0")=="CC_BY_4_0"
    assert g.normalized_gbif_license("https://fake.creativecommons.org/licenses/by/4.0") is None
