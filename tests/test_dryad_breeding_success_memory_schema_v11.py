"""No penguin record parsing from official Kappes Dryad source probe."""
import importlib.util
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/"scripts/probe_dryad_breeding_success_memory_schema_v11.py"
spec=importlib.util.spec_from_file_location("dryad_source",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FIELDS="ID,colony,season,success,breeder,age,afr,afrc,expt,expl,alr"

def test_schema_first_line_only_not_animal_identifier_records():
    source=(FIELDS+"\r\nsecret_animal_123,Crozier,2007,1,1,10,5,5,1,2,15\n").encode()
    z=m.header_only(source,"text/csv")
    assert z["status"]=="OFFICIAL_CSV_FIRST_HEADER_VERIFIED_NO_ANIMAL_RECORDS"
    assert z["source_header"]==FIELDS.split(",")
    assert z["individual_identifiers_read"]==0
    assert z["individual_outcome_rows_read"]==0
    assert "secret_animal_123" not in str(z)

def test_html_cloudflare_is_not_source_data():
    z=m.header_only(b"<!DOCTYPE html>\n<p>Challenge</p>","text/html")
    assert z["status"]=="HOLD_HTML_INSTEAD_OF_OFFICIAL_CSV"

def test_missing_or_unexpected_columns_do_not_unlock_fit():
    z=m.header_only(b"ID,colony,season,success\n1,here,2004,1\n","text/csv")
    assert z["status"]=="HOLD_DRYAD_SCHEMA_UNLIKE_METADATA"
    assert not z["header_matches_original_metadata"]
    assert not z["fit_performed"]

def test_partial_first_row_does_not_expose_a_fake_header():
    z=m.header_only(b"ID,colony,season,success","text/plain")
    assert z["status"]=="HOLD_NO_COMPLETE_VERIFIED_CSV_HEADER"

def test_unverified_hosts_and_protocol_rejected():
    assert m.validate_url(m.URL)
    for url in ["http://datadryad.org/downloads/file_stream/532106",
                "https://example.com/download.csv",
                "https://datadryad.org.evil.example/data.csv"]:
        assert not m.validate_url(url)

def test_contract_frozen_no_outcome_or_pvalues():
    import json
    c=json.loads((Path(__file__).resolve().parents[1]/
                  "contracts/ADELIE_MULTIGENERATION_REPRODUCTIVE_STATE_MEMORY_SOURCE_GATE_V11.json").read_text())
    assert c["original_animal_rows_read"]==0
    assert c["models_fitted"]==0
    assert c["p_values_computed"]==0
    assert c["PR189_frozen"]
    assert c["PR142_frozen"]
    assert c["source_metadata"]["ID_cross_link_to_other_data_forbidden"]
