#!/usr/bin/env python3
"""Record raw SMP extract custody without parsing biological contents.

Operational only. This script hashes the received file and records provenance
metadata. It never opens the file as CSV/Excel and never inspects rows, columns,
counts, species, zeros, or any biological value.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


RECEIPT_ID = "mina-smp-raw-custody-v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(
    raw: Path,
    *,
    received_at: str,
    provider_filename: str | None = None,
    source_channel: str | None = None,
) -> dict:
    if not raw.is_file():
        raise FileNotFoundError(raw)
    if not str(received_at).strip():
        raise ValueError("received_at is required and must be supplied explicitly")

    return {
        "schema_version": 1,
        "receipt_id": RECEIPT_ID,
        "status": "RAW_EXTRACT_CUSTODY_RECORDED_CONTENT_NOT_PARSED",
        "received_at": str(received_at).strip(),
        "provider_filename": (
            str(provider_filename).strip()
            if provider_filename is not None and str(provider_filename).strip()
            else raw.name
        ),
        "local_filename": raw.name,
        "file_suffix": raw.suffix.casefold(),
        "byte_size": int(raw.stat().st_size),
        "sha256": sha256_file(raw),
        "source_channel": (
            str(source_channel).strip()
            if source_channel is not None and str(source_channel).strip()
            else None
        ),
        "content_parsed": False,
        "content_inspected": False,
        "boundary": (
            "Operational chain-of-custody receipt only. No row, column, count, "
            "species, zero frequency, abundance value, or ecological outcome was parsed."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True, type=Path)
    p.add_argument("--received-at", required=True)
    p.add_argument("--provider-filename")
    p.add_argument("--source-channel")
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    result = run(
        a.raw,
        received_at=a.received_at,
        provider_filename=a.provider_filename,
        source_channel=a.source_channel,
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
