"""Synthetic no-network tests for bounded Fraser independent ice archive gate."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fraser_gate",
    ROOT / "scripts/audit_fraser_fastice_http_range_readiness_v1.py",
)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class FakeResponse:
    def __init__(self, status=200, headers=None, body=b""):
        self.status = status
        self.headers = headers or {}
        self.body = body
        self.read_calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self, maxbytes):
        self.read_calls += 1
        return self.body[:maxbytes]


def test_signature():
    assert M.classify_magic(b"\x89HDF\r\n\x1a\nAAAA") == "HDF5_NETCDF4"
    assert M.classify_magic(b"CDF\x02" + b"z"*28) == "NETCDF_CLASSIC_OR_64_BIT"
    assert M.classify_magic(b"<html>") == "UNKNOWN_OR_NON_NC"


def test_synthetic_range_ok_reads_only_32_bytes():
    magic = b"\x89HDF\r\n\x1a\n" + b"\0" * 24
    replies = [
        FakeResponse(
            status=200,
            headers={"Content-Length": "500000000", "Accept-Ranges": "bytes"},
        ),
        FakeResponse(
            status=206,
            headers={
                "Content-Range": "bytes 0-31/500000000",
                "Content-Type": "application/octet-stream",
            },
            body=magic,
        ),
    ]
    requests = []

    def opener(req, *, timeout):
        requests.append(req)
        return replies[len(requests)-1]

    result = M.check_year(2011, opener=opener)
    assert result["head_status"] == "SUCCESS"
    assert result["byte_range_status"] == "NETCDF_SIGNATURE_VERIFIED"
    assert result["read_payload_bytes"] == 32
    assert result["physical_fastice_values_read"] == 0
    assert len(requests) == 2
    assert requests[1].get_header("Range") == "bytes=0-31"
    assert replies[1].read_calls == 1


def test_server_ignoring_range_never_reads_body():
    huge = FakeResponse(
        status=200,
        headers={"Content-Length": "800000000"},
    )
    rejected = FakeResponse(status=200, body=b"should never be read")

    class Opener:
        count = 0
        def __call__(self, req, *, timeout):
            self.count += 1
            return huge if self.count == 1 else rejected

    result = M.check_year(2011, opener=Opener())
    assert result["byte_range_status"] == "HOLD_FULL_BODY_NOT_READ"
    assert rejected.read_calls == 0
    assert result["read_payload_bytes"] == 0


@pytest.mark.parametrize("bad_year", [1999, 2015, 2022])
def test_outside_frozen_six_years_rejected(bad_year):
    with pytest.raises(ValueError, match="frozen contract"):
        M.check_year(bad_year)


def test_range_malformed_fails_without_read():
    heads = [
        FakeResponse(200, {"Content-Length": "500000000"}),
        FakeResponse(206, {"Content-Range": "bytes 12-43/500000000"},
                     body=b"@"*32),
    ]
    class O:
        n=0
        def __call__(self, request, *, timeout):
            self.n+=1
            return heads[self.n-1]

    result = M.check_year(2014, opener=O())
    assert result["byte_range_status"] == "HOLD_UNEXPECTED_CONTENT_RANGE"
    assert heads[1].read_calls == 0


def test_offline_does_not_call_network():
    def deny(*args, **kwargs):
        raise AssertionError("Network should not be accessed")
    result = M.run(offline=True, opener=deny)
    assert len(result["checks"]) == 6
    assert result["all_six_files_remote_random_read_capable"] is False
    assert result["total_downloaded_body_bytes"] == 0
    assert result["biological_response_rows_read"] == 0
    assert result["effect_fitted"] is False
    assert result["decision"] == "HOLD_RANGE_ACCESS_OR_SOURCE_IDENTITY"
