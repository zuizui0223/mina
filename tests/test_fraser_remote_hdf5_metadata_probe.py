"""File-object HDF5 test with synthetic local file, never actual penguin data."""
import io
import importlib.util
from pathlib import Path
import re

import h5py
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fraser_hdf5_probe",
    ROOT / "scripts/probe_fraser_remote_hdf5_schema_v1.py",
)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class Response:
    def __init__(self, status, headers, body=b""):
        self.status = status
        self.headers = headers
        self.body = body
        self.n_reads = 0
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, n):
        self.n_reads += 1
        return self.body[:n]


def synthetic_hdf5_bytes(tmp_path):
    file = tmp_path / "dummy.h5"
    with h5py.File(file, "w") as h:
        h.attrs["Conventions"]="CF-1.7"
        h.create_dataset("fast_ice_status", data=np.zeros((2, 4, 5), dtype=np.uint8))
        h.create_dataset("time", data=np.arange(2))
    return file.read_bytes()


def make_opener(data, *, ignore_range=False):
    replies=[]
    def opener(request, timeout):
        if request.get_method()=="HEAD":
            r=Response(200,{"Content-Length":str(len(data))})
            replies.append(r)
            return r
        m=re.fullmatch(r"bytes=(\d+)-(\d+)",request.get_header("Range"))
        assert m
        a,b=map(int,m.groups())
        if ignore_range:
            r=Response(200,{"Content-Length":str(len(data))},data)
        else:
            r=Response(206,{"Content-Range":f"bytes {a}-{b}/{len(data)}"},
                       data[a:b+1])
        replies.append(r)
        return r
    return opener,replies


def test_remote_like_bounded_hdf5_metadata_schema(tmp_path):
    source=synthetic_hdf5_bytes(tmp_path)
    opener,replies=make_opener(source)
    r=M.probe_one(2011,opener=opener)
    assert r["status"]=="SCHEMA_ONLY_VERIFIED",r
    names={v["name"] for v in r["dataset_entries"]}
    assert {"fast_ice_status","time"}.issubset(names)
    assert r["ice_class_values_opened"]==0
    assert r["remote_range_requests"]<=5
    assert r["bytes_network_read"]<=M.MAX_NETWORK_BYTES


def test_full_body_when_server_ignores_range_is_not_decoded(tmp_path):
    source=synthetic_hdf5_bytes(tmp_path)
    opener,replies=make_opener(source,ignore_range=True)
    r=M.probe_one(2014,opener=opener)
    assert r["status"]=="HOLD_SCHEMA_NOT_READABLE"
    assert "HTTP 206" in r["error_message"]
    assert r["bytes_network_read"]==0
    assert all(x.n_reads==0 for x in replies if x.status==200)


def test_frozen_sites_and_no_unbounded_download():
    with pytest.raises(ValueError,match="Unfrozen"):
        M.probe_one(2018)
    f=M.LimitedHTTPRangeFile.__new__(M.LimitedHTTPRangeFile)
    with pytest.raises(M.RangeGateError,match="unbounded"):
        f.read(-1)


def test_file_offsets_never_outside_dataset(tmp_path):
    source=synthetic_hdf5_bytes(tmp_path)
    opener,replies=make_opener(source)
    h=M.LimitedHTTPRangeFile("https://example.invalid/test.nc",opener=opener)
    assert h.seek(-8,io.SEEK_END)==len(source)-8
    assert len(h.read(8))==8
    with pytest.raises(M.RangeGateError,match="outside"):
        h.seek(len(source)+1)
    h.close()
