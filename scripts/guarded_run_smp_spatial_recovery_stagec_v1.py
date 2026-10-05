#!/usr/bin/env python3
"""Guarded one-time Stage-C launcher for the frozen SMP hysteresis analysis.

This operational wrapper verifies the Stage-B freeze receipt and exact input
hashes before delegating to the frozen scientific Stage-C implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.run_smp_spatial_recovery_hysteresis_v1 import run as frozen_run


RECEIPT_ID = "mina-smp-spatial-recovery-stageb-freeze-v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_hash(receipt: dict, key: str, path: Path) -> None:
    entry = receipt.get("input_hashes", {}).get(key)
    if not entry:
        raise ValueError(f"freeze receipt missing hash entry: {key}")
    got = sha256_file(path)
    if got != str(entry.get("sha256", "")):
        raise ValueError(
            f"Stage-C input hash mismatch for {key}: "
            f"{got} != {entry.get('sha256')}"
        )


def run_guarded(
    raw: Path,
    resolved: Path,
    stageb: Path,
    freeze_receipt: Path,
    *,
    assume_whole_colony_extract: bool = False,
):
    receipt = json.loads(freeze_receipt.read_text(encoding="utf-8"))
    if receipt.get("receipt_id") != RECEIPT_ID:
        raise ValueError("not a valid Stage-B freeze receipt")
    if receipt.get("status") != "STAGE_B_FROZEN_STAGE_C_AUTHORIZED":
        raise ValueError("Stage-B freeze receipt does not authorize Stage C")
    if not receipt.get("decision", {}).get("stage_C_authorized"):
        raise ValueError("Stage C is not authorized by the freeze receipt")

    require_hash(receipt, "raw_extract", raw)
    require_hash(receipt, "resolved_structure", resolved)
    require_hash(receipt, "stageb_support", stageb)

    result, frame = frozen_run(
        raw,
        resolved,
        stageb,
        assume_whole_colony_extract=assume_whole_colony_extract,
    )

    result["operational_provenance"] = {
        "stageb_freeze_receipt_id": receipt["receipt_id"],
        "stageb_freeze_receipt_sha256": sha256_file(freeze_receipt),
        "raw_extract_sha256": sha256_file(raw),
        "resolved_structure_sha256": sha256_file(resolved),
        "stageb_support_sha256": sha256_file(stageb),
        "guarded_launcher": "scripts/guarded_run_smp_spatial_recovery_stagec_v1.py",
    }
    return result, frame


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True, type=Path)
    p.add_argument("--resolved-json", required=True, type=Path)
    p.add_argument("--stageb-json", required=True, type=Path)
    p.add_argument("--freeze-receipt", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-spells-csv", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()

    result, frame = run_guarded(
        a.raw,
        a.resolved_json,
        a.stageb_json,
        a.freeze_receipt,
        assume_whole_colony_extract=a.assume_whole_colony_extract,
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    frame.to_csv(a.out_spells_csv, index=False)
    print(json.dumps({
        "decision": result["decision"],
        "operational_provenance": result["operational_provenance"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
