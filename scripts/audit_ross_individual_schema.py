#!/usr/bin/env python3
"""Schema-only audit of Ross Sea Adélie individual and chick-count sources.

This script intentionally does not compute dispersal, recruitment, survival,
breeding success, or any association among scientific variables.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tarfile
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://www.usap-dc.org/api/v2.0/datafiles"
SOURCES = {
    "banding": {
        "dataset": "601443",
        "readme": "README_601443.txt",
        "data": "band_inv_1994-2021.csv",
        "expected_md5": "3da33defa4decc82b6e317c7fa9f9044",
    },
    "resight": {
        "dataset": "601444",
        "readme": "README_601444.txt",
        "data": "band_resighting_1997-2021.csv",
        "expected_md5": "aaae6ddad6d12081b5a68466794438a2",
    },
    "chick_counts_crozier": {
        "dataset": "600007",
        "readme": "README_600007.txt",
        "data": "chickcount_CapeCrozier.zip",
        "expected_md5": "d590d91fe51e66e3f7dc1206b346955c",
    },
    "chick_counts_royds": {
        "dataset": "600007",
        "readme": "README_600007.txt",
        "data": "chickcount_CapeRoyds.zip",
        "expected_md5": "95251b2696761cb9f74243716d34a881",
    },
    "chick_counts_legacy": {
        "dataset": "600007",
        "readme": "README_600007.txt",
        "data": "B031_chickcount.tar.gz",
        "expected_md5": "4228279d1e4ed05953db145f267d0f37",
    },
}

USER_AGENT = "mina-ross-schema-audit/1.0 (+https://github.com/zuizui0223/mina)"


def fetch(dataset: str, filename: str) -> bytes:
    url = f"{BASE}/{dataset}/{filename}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read()


def text_summary(data: bytes) -> dict[str, object]:
    text = data.decode("utf-8", errors="replace")
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "text": text,
    }


def csv_schema(data: bytes) -> dict[str, object]:
    text = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8-sig", newline="")
    reader = csv.reader(text)
    header = next(reader)
    n_rows = sum(1 for _ in reader)
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "md5": hashlib.md5(data).hexdigest(),
        "bytes": len(data),
        "header": header,
        "rows": n_rows,
    }


def archive_inventory(data: bytes, filename: str) -> dict[str, object]:
    names: list[str] = []
    if filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = sorted(
                name for name in archive.namelist()
                if not name.endswith("/")
            )
    elif filename.endswith(".tar.gz"):
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            names = sorted(
                member.name for member in archive.getmembers()
                if member.isfile()
            )
    else:
        raise ValueError(filename)
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "md5": hashlib.md5(data).hexdigest(),
        "bytes": len(data),
        "members": names,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    readmes: dict[str, object] = {}
    for dataset, filename in {
        ("601443", "README_601443.txt"),
        ("601444", "README_601444.txt"),
        ("600007", "README_600007.txt"),
    }:
        readmes[dataset] = text_summary(fetch(dataset, filename))

    output: dict[str, object] = {
        "schema_version": 1,
        "analysis_id": "mina-ross-individual-schema-audit-v1",
        "scope": (
            "schema/provenance only; no movement, survival, recruitment, "
            "breeding-success or cross-dataset scientific outcome computed"
        ),
        "readmes": readmes,
        "sources": {},
    }

    for key, spec in SOURCES.items():
        data = fetch(str(spec["dataset"]), str(spec["data"]))
        observed_md5 = hashlib.md5(data).hexdigest()
        if observed_md5 != spec["expected_md5"]:
            raise RuntimeError(
                f"{key} md5 mismatch: {observed_md5} != {spec['expected_md5']}"
            )
        if str(spec["data"]).endswith(".csv"):
            summary = csv_schema(data)
        else:
            summary = archive_inventory(data, str(spec["data"]))
        summary["dataset"] = spec["dataset"]
        summary["filename"] = spec["data"]
        output["sources"][key] = summary

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # User-visible CI log contains metadata only, never scientific data rows.
    print("banding_header=", output["sources"]["banding"]["header"])
    print("banding_rows=", output["sources"]["banding"]["rows"])
    print("resight_header=", output["sources"]["resight"]["header"])
    print("resight_rows=", output["sources"]["resight"]["rows"])
    for key in (
        "chick_counts_crozier",
        "chick_counts_royds",
        "chick_counts_legacy",
    ):
        print(key, "members=", output["sources"][key]["members"])
    for dataset in ("601443", "601444", "600007"):
        text = str(output["readmes"][dataset]["text"])
        print(f"README_{dataset}_BEGIN")
        print(text)
        print(f"README_{dataset}_END")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
