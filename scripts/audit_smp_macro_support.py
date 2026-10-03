#!/usr/bin/env python3
"""Outcome-blind structural audit for SMP macroecology panels.

This script intentionally does NOT summarize positive count magnitudes and
does NOT compute abundance trends, N_eff, kappa, concentration, or trait
associations. It only evaluates support structure needed by
contracts/SMP_MACRO_ELIGIBILITY_V1.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


MIN_COMPONENTS = 3
MIN_COMPLETE_SEASONS = 10
MIN_SPAN = 12
OUTER_START = 1986
OUTER_END = 2024

ALIASES = {
    "species": ["Species", "species"],
    "site_id": ["SiteID", "site_id", "Site Id", "Site ID"],
    "site": ["Site", "site"],
    "master_site": ["MasterSite", "master_site", "Master Site"],
    "year": ["Year", "year"],
    "start_date": ["Start date", "StartDate", "start_date", "Date", "date"],
    "method": ["Method", "method"],
    "unit": ["Unit", "unit"],
    "count": ["Count", "count"],
    "accuracy": ["Accuracy", "accuracy"],
    "estimate": ["Estimate", "estimate"],
    "comments": ["Comments", "comments", "Comment", "comment"],
}

MERGED_PATTERNS = (
    re.compile(r"\bmerg(?:e|ed|ing)\b", re.I),
    re.compile(r"\btotal\s+count\b", re.I),
    re.compile(r"\bcombined\b", re.I),
    re.compile(r"\baggregate(?:d)?\b", re.I),
)


def _pick(fieldnames: list[str], key: str, required: bool = False) -> str | None:
    for name in ALIASES[key]:
        if name in fieldnames:
            return name
    if required:
        raise ValueError(f"required SMP column not found for {key}: {ALIASES[key]}")
    return None


def _parse_year(row: dict[str, str], year_col: str | None, date_col: str | None) -> int | None:
    if year_col:
        raw = str(row.get(year_col, "")).strip()
        if raw:
            m = re.search(r"(19|20)\d{2}", raw)
            if m:
                return int(m.group(0))
    if date_col:
        raw = str(row.get(date_col, "")).strip()
        m = re.search(r"(19|20)\d{2}", raw)
        if m:
            return int(m.group(0))
    return None


def _count_state(raw: str) -> str:
    """Return observed_positive / explicit_zero / missing_or_unparseable without retaining magnitude."""
    text = str(raw).strip()
    if not text:
        return "missing_or_unparseable"
    # Handle plain numeric and common estimate strings by taking the first signed number.
    m = re.search(r"[-+]?\d+(?:\.\d+)?", text.replace(",", ""))
    if not m:
        return "missing_or_unparseable"
    value = float(m.group(0))
    if value < 0:
        return "missing_or_unparseable"
    if value == 0:
        return "explicit_zero"
    return "observed_positive"


def _merged_flag(comment: str) -> bool:
    text = str(comment or "")
    return any(p.search(text) for p in MERGED_PATTERNS)


def audit(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("SMP CSV has no header")
        fields = list(reader.fieldnames)
        col = {
            "species": _pick(fields, "species", True),
            "site_id": _pick(fields, "site_id", True),
            "site": _pick(fields, "site", False),
            "master_site": _pick(fields, "master_site", True),
            "year": _pick(fields, "year", False),
            "start_date": _pick(fields, "start_date", False),
            "method": _pick(fields, "method", False),
            "unit": _pick(fields, "unit", True),
            "count": _pick(fields, "count", True),
            "accuracy": _pick(fields, "accuracy", False),
            "estimate": _pick(fields, "estimate", False),
            "comments": _pick(fields, "comments", False),
        }
        if col["year"] is None and col["start_date"] is None:
            raise ValueError("SMP CSV requires Year or a date field")

        records: list[dict[str, Any]] = []
        for raw in reader:
            year = _parse_year(raw, col["year"], col["start_date"])
            if year is None or not (OUTER_START <= year <= OUTER_END):
                continue
            species = str(raw.get(col["species"], "")).strip()
            master = str(raw.get(col["master_site"], "")).strip()
            site_id = str(raw.get(col["site_id"], "")).strip()
            if not species or not master or not site_id:
                continue
            records.append(
                {
                    "species": species,
                    "master_site": master,
                    "site_id": site_id,
                    "site": "" if col["site"] is None else str(raw.get(col["site"], "")).strip(),
                    "year": year,
                    "unit": str(raw.get(col["unit"], "")).strip(),
                    "method": "" if col["method"] is None else str(raw.get(col["method"], "")).strip(),
                    "count_state": _count_state(str(raw.get(col["count"], ""))),
                    "accuracy": "" if col["accuracy"] is None else str(raw.get(col["accuracy"], "")).strip(),
                    "estimate": "" if col["estimate"] is None else str(raw.get(col["estimate"], "")).strip(),
                    "merged_flag": False if col["comments"] is None else _merged_flag(str(raw.get(col["comments"], ""))),
                }
            )

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        grouped[(rec["species"], rec["master_site"])].append(rec)

    panels: list[dict[str, Any]] = []
    for (species, master), recs in sorted(grouped.items()):
        site_ids = sorted({r["site_id"] for r in recs})
        years = sorted({r["year"] for r in recs})
        unit_set = sorted({r["unit"] for r in recs if r["unit"]})
        method_set = sorted({r["method"] for r in recs if r["method"]})

        key_counts = Counter((r["site_id"], r["year"]) for r in recs if r["count_state"] != "missing_or_unparseable")
        duplicate_keys = sorted([f"{s}|{y}" for (s, y), n in key_counts.items() if n > 1])

        observed_by_year: dict[int, set[str]] = defaultdict(set)
        state_counts = Counter()
        for r in recs:
            state_counts[r["count_state"]] += 1
            if r["count_state"] in {"observed_positive", "explicit_zero"}:
                observed_by_year[r["year"]].add(r["site_id"])

        complete_years = [
            y for y in years
            if observed_by_year.get(y, set()) == set(site_ids)
        ]
        span = 0 if not complete_years else complete_years[-1] - complete_years[0] + 1

        merged_rows = sum(bool(r["merged_flag"]) for r in recs)
        basic_support = (
            len(site_ids) >= MIN_COMPONENTS
            and len(complete_years) >= MIN_COMPLETE_SEASONS
            and span >= MIN_SPAN
            and len(unit_set) == 1
            and len(method_set) <= 1
            and not duplicate_keys
            and merged_rows == 0
        )

        panels.append(
            {
                "species": species,
                "master_site": master,
                "component_site_ids": site_ids,
                "n_components": len(site_ids),
                "n_record_years": len(years),
                "complete_years": complete_years,
                "n_complete_years": len(complete_years),
                "complete_year_span": span,
                "units": unit_set,
                "methods_nonblank": method_set,
                "duplicate_site_year_keys": duplicate_keys,
                "merged_or_aggregate_comment_rows": merged_rows,
                "explicit_zero_records": int(state_counts["explicit_zero"]),
                "positive_records": int(state_counts["observed_positive"]),
                "unparseable_count_records": int(state_counts["missing_or_unparseable"]),
                "basic_support_gate_pass": bool(basic_support),
                "identity_continuity_status": "UNRESOLVED_REQUIRES_SITE_HISTORY_OR_PROVIDER_CONFIRMATION",
                "mutual_exclusivity_status": "UNRESOLVED_REQUIRES_SITE_HISTORY_OR_PROVIDER_CONFIRMATION",
                "final_eligible": False,
            }
        )

    basic = [p for p in panels if p["basic_support_gate_pass"]]
    basic_species = sorted({p["species"] for p in basic})

    return {
        "schema_version": 1,
        "analysis_id": "mina-smp-macro-support-audit-v1",
        "status": "OUTCOME_BLIND_SUPPORT_ONLY",
        "source_file": str(path),
        "outer_year_window": [OUTER_START, OUTER_END],
        "record_count_retained_for_structure_audit": len(records),
        "candidate_panel_count": len(panels),
        "basic_support_panel_count": len(basic),
        "basic_support_species_count": len(basic_species),
        "basic_support_species": basic_species,
        "macro_gate_cannot_open_until_identity_and_exclusivity_confirmed": True,
        "panels": panels,
        "prohibited_outputs_confirmed_absent": [
            "abundance totals",
            "abundance trends",
            "N_eff",
            "kappa",
            "concentration effects",
            "trait associations",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--records", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = audit(args.records)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_panel_count": result["candidate_panel_count"],
        "basic_support_panel_count": result["basic_support_panel_count"],
        "basic_support_species_count": result["basic_support_species_count"],
        "macro_gate_cannot_open_until_identity_and_exclusivity_confirmed": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
