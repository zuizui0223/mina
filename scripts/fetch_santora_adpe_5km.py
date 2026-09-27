#!/usr/bin/env python3
"""Fetch the published Santora et al. (2020) Adélie 5-km colony shapefile.

Dryad's legacy file-stream URLs currently return HTTP 403 to automated clients.
Zenodo record 4534745 is a mirror of the same Dryad dataset and exposes the
individual files with the same published MD5 checksums.
"""
from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

ZENODO_RECORD = "4534745"
BASE = f"https://zenodo.org/records/{ZENODO_RECORD}/files"
FILES = {
    "ADPE-5km.dbf": "6b87ddabb5dc8c5ce19b0a6eca272174",
    "ADPE-5km.prj": "c742bee3d4edfc2948a2ad08de1790a5",
    "ADPE-5km.shp": "3ec07dd2e924a66fc3fd9db2d11765d6",
    "ADPE-5km.shx": "de836894e96ec4cac99137043eb2f246",
}
DOI = "10.7291/D1NT0S"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for name, expected_md5 in FILES.items():
        url = f"{BASE}/{name}?download=1"
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "mina-island-reassembly/0.15 "
                    "(+https://github.com/zuizui0223/mina)"
                )
            },
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        observed_md5 = hashlib.md5(data).hexdigest()
        if observed_md5 != expected_md5:
            raise RuntimeError(
                f"checksum mismatch for {name}: {observed_md5} != {expected_md5}"
            )
        target = args.out_dir / name
        target.write_bytes(data)
        print(
            f"{name} bytes={len(data)} md5={observed_md5} "
            f"sha256={hashlib.sha256(data).hexdigest()}"
        )
    print(f"doi={DOI}")
    print(f"zenodo_record={ZENODO_RECORD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
