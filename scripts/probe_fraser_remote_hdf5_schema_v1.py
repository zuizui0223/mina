"""Inspect AADC Fraser fast-ice v2.2 2011/2014 HDF5 metadata by bounded HTTP ranges.

No ice-class values, coordinates or penguin outcomes read. This probes only
dataset schema to design later independently frozen cell extraction.
Remote annual NetCDF4s are ~431 MB each; this script NEVER fetches whole files.
"""
from __future__ import annotations

from collections import OrderedDict
import argparse
import io
import json
import math
from pathlib import Path
import re
import urllib.error
import urllib.request

import h5py

UUID = "f88a75e3-257f-4904-99ef-764e5cf9a064"
URL = ("https://data.aad.gov.au/eds/api/dataset/" + UUID
       + "/object/download?prefix=fastice_v2_2/FastIce_70_{year}.nc")
YEARS = (2011, 2014)
BLOCK_SIZE = 128 * 1024
MAX_NETWORK_BYTES = 20 * 1024 * 1024
MAX_REQUESTS = 160
CACHE_BLOCKS = 20
TIMEOUT_SECONDS = 20

class RangeGateError(RuntimeError):
    pass

class LimitedHTTPRangeFile(io.RawIOBase):
    """Read-only seekable stream with strict HTTP 206 and total-body caps."""
    def __init__(self, url, *, opener=urllib.request.urlopen):
        super().__init__()
        self.url = url
        self.opener = opener
        self.offset = 0
        self.bytes_network = 0
        self.request_count = 0
        self._cache = OrderedDict()
        req = urllib.request.Request(
            url, method="HEAD",
            headers={"User-Agent":"mina-frser-nc-metadata-probe/1.0",
                     "Accept-Encoding":"identity"})
        with opener(req, timeout=TIMEOUT_SECONDS) as res:
            if res.status != 200:
                raise RangeGateError("NetCDF remote HEAD did not return 200")
            n = res.headers.get("Content-Length", "")
        if not n.isdigit() or int(n) <= 0 or int(n) > 2_000_000_000:
            raise RangeGateError("Unverifiable or unsafe remote file size")
        self.size = int(n)

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.offset

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            pos = offset
        elif whence == io.SEEK_CUR:
            pos = self.offset + offset
        elif whence == io.SEEK_END:
            pos = self.size + offset
        else:
            raise ValueError("invalid seek whence")
        if not isinstance(pos, int) or not 0 <= pos <= self.size:
            raise RangeGateError("seek outside remote file")
        self.offset = pos
        return self.offset

    def _get_block(self, start):
        if start in self._cache:
            self._cache.move_to_end(start)
            return self._cache[start]
        if self.request_count >= MAX_REQUESTS:
            raise RangeGateError("maximum bounded range requests reached")
        end = min(self.size - 1, start + BLOCK_SIZE - 1)
        expected = end - start + 1
        if self.bytes_network + expected > MAX_NETWORK_BYTES:
            raise RangeGateError("maximum network-body budget reached")
        req = urllib.request.Request(self.url, headers={
            "Range": f"bytes={start}-{end}",
            "Accept-Encoding": "identity",
            "User-Agent": "mina-fraser-nc-metadata-probe/1.0",
        })
        with self.opener(req, timeout=TIMEOUT_SECONDS) as res:
            cr = res.headers.get("Content-Range", "")
            if res.status != 206:
                raise RangeGateError(
                    "Server omitted HTTP 206; refused entire potential 431MB body"
                )
            if cr != f"bytes {start}-{end}/{self.size}":
                raise RangeGateError("Unmatched Content-Range")
            data = res.read(expected + 1)
        if len(data) != expected:
            raise RangeGateError("Short or oversized response for byte block")
        self.bytes_network += len(data)
        self.request_count += 1
        self._cache[start] = data
        if len(self._cache) > CACHE_BLOCKS:
            self._cache.popitem(last=False)
        return data

    def read(self, n=-1):
        if n is None or n < 0:
            raise RangeGateError("unbounded remote read forbidden")
        if n == 0 or self.offset == self.size:
            return b""
        todo = min(n, self.size - self.offset)
        pieces = []
        while todo:
            base = (self.offset // BLOCK_SIZE) * BLOCK_SIZE
            block = self._get_block(base)
            start = self.offset - base
            slice_ = block[start:start + todo]
            if not slice_:
                raise RangeGateError("unexpected range shortfall")
            pieces.append(slice_)
            self.offset += len(slice_)
            todo -= len(slice_)
        return b"".join(pieces)

    def readinto(self, buffer):
        b = self.read(len(buffer))
        buffer[:len(b)] = b
        return len(b)

    def flush(self):
        return None


def probe_one(year: int, *, opener=urllib.request.urlopen) -> dict:
    if year not in YEARS:
        raise ValueError("Unfrozen year")
    url = URL.format(year=year)
    report = {
        "year": year,
        "url": url,
        "status": "NOT_TESTED",
        "dataset_entries": [],
        "attribute_value_cells_opened": 0,
        "ice_class_values_opened": 0,
        "penguin_outcome_rows_opened": 0,
    }
    remote = None
    try:
        remote = LimitedHTTPRangeFile(url, opener=opener)
        if remote.read(8) != b"\x89HDF\r\n\x1a\n":
            raise RangeGateError("file is not HDF5")
        remote.seek(0)
        with h5py.File(remote, "r") as f:
            def visit(name, obj):
                if len(report["dataset_entries"]) >= 100:
                    raise RangeGateError("unexpectedly many HDF5 objects")
                if isinstance(obj, h5py.Dataset):
                    record = {
                        "name": name,
                        "kind": "dataset",
                        "shape": list(obj.shape),
                        "dtype": str(obj.dtype),
                        "chunks": list(obj.chunks) if obj.chunks else None,
                        "compression": obj.compression,
                        "attrs_names": list(obj.attrs.keys())[:20],
                    }
                elif isinstance(obj, h5py.Group):
                    record = {"name":name, "kind":"group",
                              "attrs_names":list(obj.attrs.keys())[:15]}
                else:
                    return
                report["dataset_entries"].append(record)
            f.visititems(visit)
        report["status"] = "SCHEMA_ONLY_VERIFIED"
    except Exception as e:
        report["status"] = "HOLD_SCHEMA_NOT_READABLE"
        report["error_type"] = type(e).__name__
        report["error_message"] = str(e)[:260]
    finally:
        report["bytes_network_read"] = remote.bytes_network if remote else 0
        report["remote_range_requests"] = remote.request_count if remote else 0
        report["bound_max_network_bytes"] = MAX_NETWORK_BYTES
        report["bound_max_http_requests"] = MAX_REQUESTS
        if remote:
            remote.close()
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    records=[probe_one(y) for y in YEARS]
    d={
        "schema_version":1,
        "source":"https://doi.org/10.26179/5d267d1ceb60c",
        "official_dataset_uuid": UUID,
        "years":list(YEARS),
        "results":records,
        "all_years_schema_verified":all(x["status"]=="SCHEMA_ONLY_VERIFIED" for x in records),
        "total_bytes_network_read":sum(x["bytes_network_read"] for x in records),
        "total_physical_ice_class_values_read":0,
        "total_penguin_response_values_read":0,
        "causal_fit_done":False,
        "decision":"READY_FOR_FROZEN_PIXEL_LEVEL_EXTRACTION_CONTRACT" if all(
            x["status"]=="SCHEMA_ONLY_VERIFIED" for x in records
        ) else "HOLD_HDF5_METADATA_REMOTE_ACCESS"
    }
    txt=json.dumps(d,ensure_ascii=False,indent=2)+"\n"
    args.out.write_text(txt,encoding="utf8")
    print(txt,end="")


if __name__=="__main__":
    main()
