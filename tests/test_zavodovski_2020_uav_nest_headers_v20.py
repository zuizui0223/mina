import importlib.util
import io
from pathlib import Path
import pytest
pytest.importorskip("requests")
path=Path(__file__).resolve().parents[1]/"scripts"/"audit_zavodovski_2020_uav_nest_headers_v20.py"
spec=importlib.util.spec_from_file_location("uav",path)
uav=importlib.util.module_from_spec(spec);spec.loader.exec_module(uav)

def test_latlon_candidate_does_not_claim_crs():
    x=uav.validate_headers(["longitude","latitude","species","id"])
    assert x["status"]=="PASS_POTENTIAL_COORDINATE_HEADER_CRS_UNVERIFIED"
    assert x["latitude_longitude_columns"] is True
    assert x["verified_crs"] is False
    assert x["nest_location_rows_read"]==0

def test_projected_candidate_and_no_temp_reassignment():
    x=uav.validate_headers(["Easting","Northing","NestIndex"])
    assert x["projected_xy_columns"]
    assert all("2022" not in filename for filename in uav.FILES)

def test_only_headers_no_nest_data():
    raw=io.BytesIO(b"# citation: example\r\n\nx,y,species\r\n111,222,macaroni\r\n")
    head, meta=uav.first_csv_header(raw.readline)
    assert head==["x","y","species"]
    assert raw.readline()==b"111,222,macaroni\r\n"
    assert meta["publisher_comment_bytes_read"]>0

def test_missing_coordinate_not_pass():
    assert uav.validate_headers(["Name","Abundance"])["status"]=="HOLD_NO_PAIR_OF_COORDINATE_COLUMNS"

def test_source_bytes_header_length_gate():
    with pytest.raises(ValueError):
        uav.first_csv_header(io.BytesIO(b"A"*1600+b"\nX,Y\n").readline)
