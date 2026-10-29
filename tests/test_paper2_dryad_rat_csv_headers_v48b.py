"""V48b original public Dryad rat source field availability tests without biological rows."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_paper2_dryad_rat_csv_headers_v48b as m


def test_frozen_original_public_file_catalog_exact():
    assert set(m.SOURCE)=={"DetectedS.csv","Relative_Abunance.csv"}
    assert m.SOURCE["DetectedS.csv"]["id"]==55543
    assert m.SOURCE["Relative_Abunance.csv"]["size"]==12000


def test_source_storage_redirect_only_HTTPS_official_or_S3():
    assert m.safe_download_host("https://datadryad.org/api/v2/files/55543/download")
    assert m.safe_download_host("https://dryad-csv.s3.us-west-2.amazonaws.com/obj")
    assert m.safe_download_host("https://s3.amazonaws.com/bucket/obj")
    assert not m.safe_download_host("https://example.org/whatever")
    assert not m.safe_download_host("http://datadryad.org/api/v2/files/55543/download")
    assert not m.safe_download_host("https://s3.evilamazonaws.com/key")


def test_original_headers_without_bird_rows_published():
    raw=b"Island_ID,Rat_Status,Survey_Year,Passerine_Count\nIsland A,present,2011,77\nIsland B,absent,2012,12\n"
    obj=m.inspect_csv_schema(raw,"synthetic.csv")
    assert obj["original_csv_rows_including_header"]==3
    assert obj["original_csv_columns"]==4
    assert obj["original_headers_support_all_three_mammal_predictor_requirements"]
    assert len(obj["candidate_original_source_field_names_without_row_values"])==3
    assert "Island A" not in str(obj)
    assert "Island B" not in str(obj)
    assert "Passerine_Count" not in str(obj)
    assert obj["original_candidate_columns_completeness"]["Rat_Status"]["original_distinct_nonempty_values_n"]==2


def test_detected_passserine_only_source_lacks_field_mammal_exposure():
    obj=m.inspect_csv_schema(b"Passerine_Species,Detected,Relative_Abundance\nBird A,1,20\n",
                             "sample.csv")
    assert not obj["original_headers_support_all_three_mammal_predictor_requirements"]
    assert obj["original_header_keyword_support_by_source_role"]["rat_observed_status_or_eradication"]==[]


def test_missing_or_malformed_source_file_is_not_silent_zero():
    with pytest.raises(ValueError,match="UNKNOWN_DRYAD"):
        m.original_download("unregistered.csv")
    with pytest.raises(ValueError,match="RAGGED_ROWS"):
        m.inspect_csv_schema(b"Island,Year\nA,2001,extra\n","synthetic.csv")
