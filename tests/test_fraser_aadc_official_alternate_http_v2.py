"""Strict bounded AADC official EDS metadata and no-full-download tests."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "aadc_official_gate",
    ROOT / "scripts/audit_fraser_aadc_official_alternate_http_v2.py"
)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class Response:
    def __init__(self, code, head=None, data=b""):
        self.status=code
        self.headers=head or {}
        self.data=data
        self.n_reads=0
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, n):
        self.n_reads += 1
        return self.data[:n]


def test_offline_gate_zero_response_rows():
    d=M.run(offline=True)
    assert d["physical_ice_class_values_read"]==0
    assert d["penguin_response_values_read"]==0
    assert d["total_payload_bytes_read"]==0
    assert d["source_readiness"].startswith("HOLD")


def test_bounded_manifest_2011_2014_names():
    listing = json.dumps([
        {"name":"fastice_v2_2/FastIce_70_2011.nc","size":500000000},
        {"name":"fastice_v2_2/FastIce_70_2014.nc","size":500000000},
    ]).encode()
    r=Response(200,{"Content-Type":"application/json"},listing)
    d=M.manifest(opener=lambda req,timeout: r)
    assert d["status"]=="PUBLIC_MANIFEST_READ"
    assert d["exact_frozen_prefix_verified"]
    assert d["objects_count"]==2


def test_range_works_only_with_206_and_netCDF_magic():
    head=Response(200,{"Content-Length":"500000000"})
    data=Response(206,{"Content-Range":"bytes 0-31/500000000"},
                  b"\x89HDF\r\n\x1a\n"+b"\x00"*24)
    queue=[head,data]
    d=M.range_check(2011,opener=lambda req,timeout: queue.pop(0))
    assert d["head"]=="OK"
    assert d["range_status"]=="NETCDF_HEADER_CONFIRMED"
    assert d["bytes_read"]==32
    assert d["physical_ice_values_read"]==0
    assert data.n_reads==1


def test_server_ignores_range_does_not_read_large_body():
    head=Response(200,{"Content-Length":"500000000"})
    returned200=Response(200,{"Content-Type":"application/octet-stream"},
                         b"this-is-the-start-of-500megabytes")
    queue=[head,returned200]
    d=M.range_check(2014,opener=lambda req,timeout: queue.pop(0))
    assert d["range_status"]=="HOLD_NO_VALID_PARTIAL_RESPONSE"
    assert d["bytes_read"]==0
    assert returned200.n_reads==0


@pytest.mark.parametrize("badyear",[2009,2012,2015,2022])
def test_outside_source_selection_rejected(badyear):
    with pytest.raises(ValueError,match="frozen"):
        M.range_check(badyear)


def test_manifest_auth_required_stops_without_pretending_ice_absent():
    class Block(Exception):
        pass
    d=M.manifest(opener=lambda req,timeout: (_ for _ in ()).throw(OSError("Authorization required")))
    assert d["status"]=="HOLD_METADATA_ROUTE_UNAVAILABLE"
