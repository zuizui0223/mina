#!/usr/bin/env python3
"""Fetch pinned Palmer LTER HUMPOP colony-level arrival files."""
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
BASE_PATH = "station/formatted/Adelie_Humble_Population_Arrival"
FILES = {
    "Adelie_Humble_Population_Arrival_1992_2020.csv": "98cbe512be3899f108c22f44a3ff985ef890a3ff",
    "Adelie_Humble_Population_Arrival_2021.csv": "2c4b0032eb57294f392eb070efa8d207818121c7",
    "Adelie_Humble_Population_Arrival_2022.csv": "4a4d1b5a20b3d5f0ce2601d9feb02137e2af7335",
    "Adelie_Humble_Population_Arrival_2023.csv": "1d6ae2f77bd9c1062c9a2c9004d9915f3e45552e",
    "Adelie_Humble_Population_Arrival_2024.csv": "5600c4373ed2318d548e7ee72eed8afb96e1645c",
    "Adelie_Humble_Population_Arrival_2025.csv": "9bd055adf5cb92f999e9fd9beda933f6640a8840",
    "Adelie_Humble_Population_Arrival_2026.csv": "02db0c7bb2f39fe9cf22265ef0c986866f2b524a",
}
HEADER = ["studyName", "Date", "Island", "Colony", "Adults"]


def git_blob_sha(data: bytes) -> str:
    payload = b"blob " + str(len(data)).encode() + b"\0" + data
    return hashlib.sha1(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    combined: list[dict[str, str]] = []
    file_receipts = []
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
        if reader.fieldnames != HEADER:
            raise RuntimeError(
                f"unexpected HUMPOP header in {name}: {reader.fieldnames!r}"
            )
        rows = list(reader)
        combined.extend(rows)
        file_receipts.append(
            {
                "file": name,
                "git_blob_sha": observed_blob,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "rows": len(rows),
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(combined)

    combined_bytes = args.out.read_bytes()
    print(f"repo={REPO}")
    print(f"commit={COMMIT}")
    print(f"files={len(FILES)}")
    print(f"rows={len(combined)}")
    print(f"combined_sha256={hashlib.sha256(combined_bytes).hexdigest()}")
    for receipt in file_receipts:
        print(
            "file={file} rows={rows} bytes={bytes} git_blob={git_blob_sha} sha256={sha256}".format(
                **receipt
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
