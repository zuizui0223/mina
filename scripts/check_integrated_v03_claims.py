#!/usr/bin/env python3
"""Fail-closed claim guard for integrated manuscript v0.3."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_SNIPPETS = [
    "Integrated manuscript draft v0.3",
    "late-season colony-wide state",
    "fixed-specification validation",
    "provenance repair",
    "β₂ = 0.0409",
    "p = 0.00327",
    "C_recruit = −0.0422",
    "β = 0.0296, p = 0.232",
    "69 matched colony-seasons",
    "median γ_AH = −0.318",
    "p = 0.0947",
    "p = 0.0810",
    "not a contest between “state” and “place”",
    "not generic nest reproductive success",
]

PROHIBITED_SNIPPETS = [
    "Integrated manuscript draft v0.2",
    "state replaces habitat",
    "place is irrelevant",
    "generic reproductive success predicts redistribution",
    "Palmer proves public-information use",
    "fully preregistered",
    "marginally significant",
    "near significant",
    "Ross Island confirms the mechanism",
    "island architecture buffers Antarctic penguins",
]


def audit(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    missing = [x for x in REQUIRED_SNIPPETS if x not in text]
    prohibited = [x for x in PROHIBITED_SNIPPETS if x in text]
    return {
        "schema_version": 1,
        "audit_id": "mina-integrated-manuscript-v0.3-claim-guard-v1",
        "manuscript": str(path),
        "required_snippets": REQUIRED_SNIPPETS,
        "missing_required_snippets": missing,
        "prohibited_snippets_found": prohibited,
        "pass": not missing and not prohibited,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manuscript",
        type=Path,
        default=Path("docs/MANUSCRIPT_INTEGRATED_V0_3.md"),
    )
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    if not args.manuscript.exists():
        raise FileNotFoundError(args.manuscript)

    result = audit(args.manuscript)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
