#!/usr/bin/env python3
"""Run the frozen Palmer within-year versus cross-year persistence extension."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from mina.palmer_persistence import analyze_persistence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = analyze_persistence(args.raw)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
