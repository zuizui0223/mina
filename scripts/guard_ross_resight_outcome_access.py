#!/usr/bin/env python3
"""Fail-closed gate for opening Ross Island behavioral resight rows.

Future full-data workflows must call this script with --require-unlocked before
fetching USAP-DC 601444. The current branch is intentionally locked.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def is_unlocked(receipt: dict[str, object]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    raw = receipt.get("raw_access", {})
    decision = receipt.get("decision", {})
    if not isinstance(raw, dict) or not bool(raw.get("exact_csv_header_verified")):
        reasons.append("exact_csv_header_not_verified")
    if not isinstance(decision, dict) or not bool(decision.get("movement_analysis_unlocked")):
        reasons.append("movement_analysis_not_unlocked")
    if receipt.get("outcome_blind_status", {}).get("behavioral_rows_read") not in {0, 0.0}:
        reasons.append("receipt_already_records_behavioral_row_access")
    return (not reasons), reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("results/ROSS_ISLAND_RESIGHT_SCHEMA_GATE_RESULT_V1.json"),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--require-unlocked", action="store_true")
    mode.add_argument("--assert-locked", action="store_true")
    args = parser.parse_args()

    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    unlocked, reasons = is_unlocked(receipt)

    print(f"unlocked={unlocked}")
    print("reasons=" + ",".join(reasons))

    if args.require_unlocked:
        if not unlocked:
            print(
                "STOP: Ross behavioral rows must not be fetched. "
                "Complete exact-header audit and update the frozen receipt first."
            )
            return 2
        print("GO: exact-header gate is recorded as unlocked.")
        return 0

    if unlocked:
        print("Expected a locked pre-outcome state, but receipt is unlocked.")
        return 3
    print("LOCKED as intended; no full resight download is authorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
