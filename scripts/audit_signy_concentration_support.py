#!/usr/bin/env python3
"""Outcome-blind roster/support audit for a Signy concentration replication.

This audit deliberately does not read breeding-pair magnitudes.  It freezes the
season/label support structure needed to define a later concentration test
before any Signy N_eff trajectory or effect is computed.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

from scripts.audit_signy_replication_support import read_official_zip, season_start

EXPECTED_CSV_SHA256 = "585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62"
WINDOW_START = 1996
WINDOW_END = 2019


def canonical_label(label: str) -> str:
    """Outcome-blind harmonization forced by the source's later pooled label."""
    x = re.sub(r"\s+", " ", str(label).strip())
    if x in {"A1", "A60", "A1 + A60", "A1+A60"}:
        return "A1+A60"
    return x


def audit_frame(frame: pd.DataFrame) -> dict[str, object]:
    required = {"SEASON", "COLONY", "TOTAL_NUMBER_OF_PAIRS"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"missing Signy columns: {missing}")

    rows: list[dict[str, object]] = []
    for idx, row in frame.iterrows():
        season = season_start(row["SEASON"])
        if season is None or not WINDOW_START <= season <= WINDOW_END:
            continue
        literal = str(row["COLONY"]).strip()
        if not literal or literal.lower() in {"nan", "none", "na"}:
            continue
        rows.append(
            {
                "source_row": int(idx),
                "season": int(season),
                "literal": literal,
                "canonical": canonical_label(literal),
                # Presence only: never inspect the numerical count magnitude.
                "pairs_present": bool(pd.notna(row["TOTAL_NUMBER_OF_PAIRS"])),
            }
        )

    if not rows:
        raise ValueError("no Signy rows in frozen window")

    seasons = list(range(WINDOW_START, WINDOW_END + 1))
    raw_labels = sorted({str(r["literal"]) for r in rows})
    canonical_labels = sorted({str(r["canonical"]) for r in rows})

    def spans(key: str) -> dict[str, object]:
        out: dict[str, object] = {}
        for label in sorted({str(r[key]) for r in rows}):
            local = [r for r in rows if str(r[key]) == label]
            ss = sorted({int(r["season"]) for r in local})
            pp = sorted({int(r["season"]) for r in local if bool(r["pairs_present"])})
            out[label] = {
                "first_season": min(ss),
                "last_season": max(ss),
                "row_seasons": ss,
                "n_row_seasons": len(ss),
                "pair_present_seasons": pp,
                "n_pair_present_seasons": len(pp),
            }
        return out

    by_season: dict[int, list[dict[str, object]]] = defaultdict(list)
    for r in rows:
        by_season[int(r["season"])].append(r)

    season_support: dict[str, object] = {}
    duplicate_canonical: dict[str, object] = {}
    for season in seasons:
        local = by_season.get(season, [])
        canon_to_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
        for r in local:
            canon_to_rows[str(r["canonical"])].append(r)
        dups = {
            lab: sorted(str(x["literal"]) for x in xs)
            for lab, xs in canon_to_rows.items()
            if len(xs) > 1
        }
        if dups:
            duplicate_canonical[str(season)] = dups
        season_support[str(season)] = {
            "literal_labels": sorted({str(r["literal"]) for r in local}),
            "canonical_labels": sorted(canon_to_rows),
            "canonical_units_with_any_pair_field": sorted(
                lab
                for lab, xs in canon_to_rows.items()
                if any(bool(x["pairs_present"]) for x in xs)
            ),
            "n_literal_rows": len(local),
            "n_canonical_labels": len(canon_to_rows),
            "n_canonical_units_with_any_pair_field": sum(
                any(bool(x["pairs_present"]) for x in xs)
                for xs in canon_to_rows.values()
            ),
        }

    # Structural candidates only.  These rules inspect label/date support, not counts.
    first_third_end = WINDOW_START + 7
    last_third_start = WINDOW_END - 7
    candidates = []
    for lab, info in spans("canonical").items():
        row_seasons = set(info["row_seasons"])
        pair_seasons = set(info["pair_present_seasons"])
        spans_window = (
            any(s <= first_third_end for s in row_seasons)
            and any(s >= last_third_start for s in row_seasons)
        )
        if spans_window and len(pair_seasons) >= 12:
            candidates.append(lab)

    complete_candidate_seasons = []
    for season in seasons:
        supported = set(
            season_support[str(season)]["canonical_units_with_any_pair_field"]
        )
        if candidates and set(candidates).issubset(supported):
            complete_candidate_seasons.append(season)

    return {
        "schema_version": 1,
        "audit_id": "mina-signy-concentration-support-v1",
        "window": [WINDOW_START, WINDOW_END],
        "effect_computed": False,
        "numeric_pair_magnitudes_read": False,
        "literal_labels": raw_labels,
        "canonical_labels": canonical_labels,
        "canonicalization": {
            "A1": "A1+A60",
            "A60": "A1+A60",
            "A1 + A60": "A1+A60",
            "A1+A60": "A1+A60",
            "reason": (
                "The official source later publishes A1 and A60 as one pooled label; "
                "harmonizing all seasons to the pooled observational unit prevents "
                "a label-definition change from manufacturing a concentration trend."
            ),
        },
        "literal_spans": spans("literal"),
        "canonical_spans": spans("canonical"),
        "duplicate_canonical_rows": duplicate_canonical,
        "season_support": season_support,
        "structural_candidate_rule": (
            "canonical unit has a row in both the first and last thirds of the "
            "1996-2019 window and a nonmissing pair field in >=12 seasons"
        ),
        "structural_candidates": sorted(candidates),
        "complete_candidate_seasons": complete_candidate_seasons,
        "n_complete_candidate_seasons": len(complete_candidate_seasons),
        "support_gate": {
            "required_complete_seasons": 12,
            "required_candidate_units": 4,
            "passes": bool(
                len(complete_candidate_seasons) >= 12 and len(candidates) >= 4
            ),
        },
        "boundary": [
            "No breeding-pair magnitude is summarized, transformed or modeled.",
            "No N_eff value, trend, abundance trajectory or concentration statistic is computed.",
            "The next effect contract may use only source-label/date support exposed here.",
            "Missing pair fields are support failures, never converted to zero.",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--official-zip", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    frame, source = read_official_zip(a.official_zip)
    if str(source["selected_csv_sha256"]) != EXPECTED_CSV_SHA256:
        raise ValueError("official Signy CSV hash drift")

    result = audit_frame(frame)
    result["source"] = {
        "doi": "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
        "selected_csv": source["selected_csv"],
        "selected_csv_sha256": source["selected_csv_sha256"],
        "rows": int(len(frame)),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
