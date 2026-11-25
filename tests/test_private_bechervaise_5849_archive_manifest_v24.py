"""Offline-only ZIP original AADC source intake tests; NEVER read real tags."""
import importlib.util
import hashlib
from pathlib import Path
from zipfile import ZipFile
import pytest

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/"scripts/intake_private_bechervaise_5849_archive_manifest_v24.py"
spec=importlib.util.spec_from_file_location("priv_aadc5849",F)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_offline_zip_member_type_year_counts_without_raw_tags(tmp_path):
    p=tmp_path/"publisher_sample.zip"
    with ZipFile(p,"w") as z:
        z.writestr("season2007/observations.csv","SYNTHETIC_PRIVATE_TAG_NEVER_READ,year\nA,2007\n")
        z.writestr("season2009/observations.tsv","NOT_ORIGINAL_BIRDS\t2009\n")
        z.writestr("bad/../../sensitive.tag","MUST_NOT_UNZIP")
    r=m.archive_summary(p)
    assert r["source_container"]=="ZIP_FILE_CENTRAL_DIRECTORY_ONLY"
    assert r["zip_source_member_count"]==3
    assert r["zip_source_member_file_suffix_groups"]=={".csv":1,".tsv":1}
    assert r["zip_member_path_traversal_count"]==1
    assert r["year_tokens_from_member_names_only"]=={"2007":1,"2009":1}
    assert r["source_binary_sha256_computed_locally"]==hashlib.sha256(p.read_bytes()).hexdigest()
    assert r["zip_manifest_not_proof_of_valid_RFID_data"]
    assert r["publisher_MD5_not_independently_verified"]
    assert r["no_original_penguin_tag_records_read"]
    assert r["no_original_penguin_individual_identifiers_output"]
    assert r["no_original_member_filenames_output"]
    assert "SYNTHETIC_PRIVATE_TAG_NEVER_READ" not in str(r)
    assert "sensitive.tag" not in str(r)

def test_browser_html_not_original_wildlife_file(tmp_path):
    file=tmp_path/"not_a_download.html"
    file.write_text("<!doctype html><html>Use email to request download</html>")
    r=m.archive_summary(file)
    assert r["source_container"]=="HOLD_HTML_NOT_ORIGINAL_DATA"
    assert r["source_rows_schema_opened"]==0
    assert r["no_same_tag_to_egg_join_performed"]

def test_unverified_file_and_empty_archive_cannot_be_used(tmp_path):
    with pytest.raises(ValueError,match="local file"):
        m.archive_summary(tmp_path/"missing.zip")
    empty=tmp_path/"empty.zip"
    empty.write_bytes(b"")
    with pytest.raises(ValueError,match="Empty or oversized"):
        m.archive_summary(empty)

def test_archive_receipt_does_not_certify_causes_or_first_breeding(tmp_path):
    p=tmp_path/"safe.zip"
    with ZipFile(p,"w") as zipfile:
        zipfile.writestr("readme.txt","Only dummy contents")
    r=m.archive_summary(p)
    assert r["no_private_source_bytes_committed"]
    assert r["no_causal_antarctic_island_ecology_result"]
    assert m.SOURCE_URL=="https://data.aad.gov.au/eds/5849/download"
    assert m.EXPECTED_DOI=="10.26179/1205-2s58"
