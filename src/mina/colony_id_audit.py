"""Descriptive continuity audit for Palmer LTER colony identifiers."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from .lter import ISLANDS, load_colony_rows

YEARS = tuple(range(1991, 2018))


def audit(path: str | Path) -> dict[str, object]:
    rows = load_colony_rows(path)
    seen: dict[tuple[str, str], set[int]] = defaultdict(set)
    counts: dict[tuple[str, str, int], float] = defaultdict(float)
    for row in rows:
        year = int(row["year"])
        if year not in YEARS:
            continue
        island = str(row["island"])
        code = str(row["colony_code"])
        seen[(island, code)].add(year)
        counts[(island, code, year)] += float(row["breeding_pairs"])

    islands: dict[str, object] = {}
    for island in ISLANDS:
        records = []
        codes = sorted(code for ii, code in seen if ii == island)
        for code in codes:
            years = sorted(seen[(island, code)])
            missing = [year for year in YEARS if year not in seen[(island, code)]]
            positive_years = [
                year
                for year in years
                if counts[(island, code, year)] > 0
            ]
            records.append(
                {
                    "colony_code": code,
                    "n_reported_years": len(years),
                    "first_year": years[0],
                    "last_year": years[-1],
                    "missing_years": missing,
                    "n_positive_years": len(positive_years),
                    "first_positive_year": (
                        positive_years[0] if positive_years else None
                    ),
                    "last_positive_year": (
                        positive_years[-1] if positive_years else None
                    ),
                }
            )
        islands[island] = {
            "n_unique_codes": len(codes),
            "n_complete_codes": sum(
                int(record["n_reported_years"]) == len(YEARS)
                for record in records
            ),
            "records": records,
        }
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-colony-id-continuity-audit-v1",
        "years": list(YEARS),
        "islands": islands,
        "interpretation_boundary": {
            "descriptive_only": True,
            "does_not_change_island_partition_validity_gate": True,
            "does_not_merge_or_relabel_colony_codes": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.census)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
