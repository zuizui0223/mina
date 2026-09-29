"""Outcome-blind row-key audit for Palmer LTER chick-census metadata."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from .lter import ISLANDS


def _finite(value: str | None) -> bool:
    if value in {None, "", "NA", "NaN", "nan"}:
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def load_metadata(path: str | Path) -> list[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError("empty chick metadata")
    if "num_chicks" in rows[0]:
        raise ValueError("outcome column num_chicks is forbidden in key audit")

    out: list[dict[str, object]] = []
    for row in rows:
        island = str(row.get("island_name", "")).strip()
        if island not in ISLANDS:
            continue
        if not _finite(row.get("num_breeding_pairs")):
            continue
        adult = float(row["num_breeding_pairs"])
        if adult <= 0:
            continue
        time = str(row.get("time", "")).strip()
        try:
            census_year = int(time[:4])
        except (TypeError, ValueError):
            continue
        code = str(row.get("colony_code", "")).strip()
        if not code:
            continue
        out.append(
            {
                "study_name": str(row.get("study_name", "")).strip(),
                "time": time,
                "island": island,
                "colony_code": code,
                "season": census_year - 1,
                "adult_pairs": adult,
                "census_time": str(row.get("census_time", "")).strip(),
            }
        )
    if not out:
        raise ValueError("no usable chick metadata rows")
    return out


def _key(row: dict[str, object], kind: str) -> tuple[object, ...]:
    if kind == "coarse":
        return (row["island"], row["colony_code"], row["season"])
    if kind == "plus_study":
        return (
            row["study_name"],
            row["island"],
            row["colony_code"],
            row["season"],
        )
    if kind == "plus_time":
        return (row["time"], row["island"], row["colony_code"])
    if kind == "plus_census_time":
        return (
            row["island"],
            row["colony_code"],
            row["season"],
            row["census_time"],
        )
    if kind == "full_nonoutcome":
        return (
            row["study_name"],
            row["time"],
            row["island"],
            row["colony_code"],
            row["census_time"],
        )
    raise ValueError(kind)


def _collision_summary(
    rows: list[dict[str, object]], kind: str
) -> dict[str, int]:
    groups: dict[tuple[object, ...], int] = defaultdict(int)
    for row in rows:
        groups[_key(row, kind)] += 1
    duplicated = [n for n in groups.values() if n > 1]
    return {
        "n_unique_keys": len(groups),
        "n_duplicate_keys": len(duplicated),
        "n_rows_in_duplicate_keys": int(sum(duplicated)),
        "n_extra_rows_beyond_unique": int(sum(n - 1 for n in duplicated)),
        "max_rows_per_key": max(groups.values()),
    }


def audit_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    coarse: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        coarse[_key(row, "coarse")].append(row)

    duplicates: list[dict[str, object]] = []
    for key, local in sorted(coarse.items()):
        if len(local) <= 1:
            continue
        studies = sorted({str(r["study_name"]) for r in local})
        times = sorted({str(r["time"]) for r in local})
        census_times = sorted({str(r["census_time"]) for r in local})
        adults = sorted({float(r["adult_pairs"]) for r in local})
        duplicates.append(
            {
                "key": {
                    "island": str(key[0]),
                    "colony_code": str(key[1]),
                    "season_start_year": int(key[2]),
                },
                "n_rows": len(local),
                "n_distinct_study_names": len(studies),
                "n_distinct_times": len(times),
                "n_distinct_census_times": len(census_times),
                "n_distinct_adult_pair_counts": len(adults),
                "same_adult_pair_count": len(adults) == 1,
                "rows": [
                    {
                        "study_name": str(r["study_name"]),
                        "time": str(r["time"]),
                        "adult_pairs": float(r["adult_pairs"]),
                        "census_time": str(r["census_time"]),
                    }
                    for r in local
                ],
            }
        )

    key_kinds = (
        "coarse",
        "plus_study",
        "plus_time",
        "plus_census_time",
        "full_nonoutcome",
    )
    collisions = {
        kind: _collision_summary(rows, kind)
        for kind in key_kinds
    }
    return {
        "n_usable_metadata_rows": len(rows),
        "season_range": [
            min(int(r["season"]) for r in rows),
            max(int(r["season"]) for r in rows),
        ],
        "coarse_duplicate_key_count": len(duplicates),
        "coarse_duplicate_groups": duplicates,
        "candidate_key_collisions": collisions,
        "outcome_column_accessed": False,
    }


def analyze(path: str | Path) -> dict[str, object]:
    rows = load_metadata(path)
    audit = audit_rows(rows)
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-chick-key-audit-v1",
        "status": "outcome_blind",
        **audit,
        "decision_boundary": {
            "deduplication_rule_selected": False,
            "num_chicks_accessed": False,
            "next_step": (
                "Interpret duplicate groups using only non-outcome fields, then freeze "
                "the reproductive-success unit and duplicate rule before num_chicks access."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = analyze(args.metadata)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
