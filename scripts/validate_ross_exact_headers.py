#!/usr/bin/env python3
"""Validate Ross Island exact CSV headers without opening behavioral rows.

Consumes the schema-only audit JSON. It never downloads source data. When exact
headers are absent, it emits a BLOCKED receipt. When present, it verifies the
minimum frozen parser columns and emits a PROPOSED header receipt for review.
It does not modify the committed schema-gate result and therefore cannot unlock
behavioral-row access by itself.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

RESIGHT_REQUIRED = {"Band", "Date", "Colony", "Eggs", "Chicks"}
BANDING_REQUIRED = {"Low", "High", "Colony", "Season"}


def parse_header(value: object) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) != 1:
        raise ValueError("expected exactly one CSV header line")
    return [field.strip() for field in rows[0]]


def validate(audit: dict[str, object]) -> dict[str, object]:
    if int(audit.get("behavioral_rows_read", -1)) != 0:
        raise ValueError("schema audit is not outcome-blind")

    resight = parse_header(audit.get("resight_header"))
    banding = parse_header(audit.get("banding_header"))

    if not resight or not banding:
        return {
            "schema_version": 1,
            "receipt_id": "mina-ross-island-exact-header-proposed-receipt-v1",
            "status": "BLOCKED_NO_EXACT_HEADERS",
            "behavioral_rows_read": 0,
            "resight_header": resight or None,
            "banding_header": banding or None,
            "resight_required": sorted(RESIGHT_REQUIRED),
            "banding_required": sorted(BANDING_REQUIRED),
            "missing_resight_required": sorted(RESIGHT_REQUIRED - set(resight)),
            "missing_banding_required": sorted(BANDING_REQUIRED - set(banding)),
            "header_parser_ready": False,
            "movement_analysis_unlock_candidate": False,
            "note": (
                "Add the USAP_DC_API_KEY secret and rerun the schema-only "
                "workflow. This proposed receipt cannot unlock full-data access."
            ),
        }

    missing_resight = sorted(RESIGHT_REQUIRED - set(resight))
    missing_banding = sorted(BANDING_REQUIRED - set(banding))
    duplicate_resight = sorted(
        {x for x in resight if resight.count(x) > 1}
    )
    duplicate_banding = sorted(
        {x for x in banding if banding.count(x) > 1}
    )
    ready = not (
        missing_resight
        or missing_banding
        or duplicate_resight
        or duplicate_banding
    )
    return {
        "schema_version": 1,
        "receipt_id": "mina-ross-island-exact-header-proposed-receipt-v1",
        "status": "HEADER_VALIDATED_PROPOSED" if ready else "HEADER_INCOMPATIBLE",
        "behavioral_rows_read": 0,
        "resight_header": resight,
        "banding_header": banding,
        "resight_required": sorted(RESIGHT_REQUIRED),
        "banding_required": sorted(BANDING_REQUIRED),
        "missing_resight_required": missing_resight,
        "missing_banding_required": missing_banding,
        "duplicate_resight_columns": duplicate_resight,
        "duplicate_banding_columns": duplicate_banding,
        "header_parser_ready": ready,
        "movement_analysis_unlock_candidate": ready,
        "manual_freeze_required_before_full_download": True,
        "next_step": (
            "Review this artifact, freeze an exact-header/parser receipt in "
            "the repository, then explicitly update the schema-gate result. "
            "Do not let this artifact itself unlock behavioral data."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    result = validate(audit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("status=", result["status"])
    print("header_parser_ready=", result["header_parser_ready"])
    print(
        "movement_analysis_unlock_candidate=",
        result["movement_analysis_unlock_candidate"],
    )
    print("behavioral_rows_read=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
