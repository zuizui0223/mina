#!/usr/bin/env python3
"""Fetch pinned Palmer LTER Adelie reproductive-success files."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import urllib.parse
import urllib.request
from pathlib import Path

REPO = "PAL-LTER/pal-seabirds"
COMMIT = "523e74a064e2f1153704a32731631cbff4395e73"
BASE_PATH = "station/formatted/Adelie_Reproductive_Success"
FILES = {
    "Adelie_Reproductive_Success_1992_2020.csv": "9ddba35ac53edb191ed19580f78e7e773754eb23",
    "Adelie_Reproductive_Success_2021.csv": "2fcd3194262442a990c186d256b689ce72eb957b",
    "Adelie_Reproductive_Success_2022.csv": "ba4888ad54b3f4f8c4997e712ff1f0042616bf14",
    "Adelie_Reproductive_Success_2023.csv": "93643aab6f76a2345b585bb2d65874b4fb5f6ecc",
    "Adelie_Reproductive_Success_2024.csv": "fee1c8cc9d0d0e254e4d03f7db331adbbd558f49",
    "Adelie_Reproductive_Success_2025.csv": "39c0a7b434668debeff1594b613a84e63e1567f6",
    "Adelie_Reproductive_Success_2026.csv": "dd4b1bf437be6cfe95875afc3475804bb8b6fa7d",
}


def git_blob_sha(data: bytes) -> str:
    payload = b"blob " + str(len(data)).encode() + b"\0" + data
    return hashlib.sha1(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    combined_rows: list[dict[str, str]] = []
    fieldnames: list[str] | None = None
    receipts = []
    for name, expected_blob in FILES.items():
        path = f"{BASE_PATH}/{name}"
        url = (
            f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/"
            + urllib.parse.quote(path, safe="/")
        )
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "mina-island-reassembly/0.15"},
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read()
        observed_blob = git_blob_sha(data)
        if observed_blob != expected_blob:
            raise RuntimeError(
                f"git blob mismatch for {name}: {observed_blob} != {expected_blob}"
            )
        text = data.decode("utf-8-sig", "strict")
        reader = csv.DictReader(io.StringIO(text))
        if fieldnames is None:
            fieldnames = list(reader.fieldnames or [])
        elif list(reader.fieldnames or []) != fieldnames:
            raise RuntimeError(
                f"REPRO header mismatch in {name}: {reader.fieldnames!r}"
            )
        rows = list(reader)
        combined_rows.extend(rows)
        receipts.append(
            {
                "file": name,
                "git_blob_sha": observed_blob,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "rows": len(rows),
            }
        )

    if not fieldnames:
        raise RuntimeError("no REPRO header")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_rows)

    print(f"repo={REPO}")
    print(f"commit={COMMIT}")
    print(f"files={len(FILES)}")
    print(f"rows={len(combined_rows)}")
    print(f"combined_sha256={hashlib.sha256(args.out.read_bytes()).hexdigest()}")
    for receipt in receipts:
        print(
            "file={file} rows={rows} bytes={bytes} git_blob={git_blob_sha} sha256={sha256}".format(
                **receipt
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
