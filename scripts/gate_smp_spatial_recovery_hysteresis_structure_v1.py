#!/usr/bin/env python3
"""Outcome-blind structural gate dedicated to SMP spatial-recovery hysteresis.

Reuses the legacy count-blind MasterSite panel builder, then applies only the
panel support and minimum program size needed for the hysteresis design.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.gate_smp_master_site_support_v1 import analyze as legacy_analyze


MIN_SPAN = 12
MIN_PANELS = 10
MIN_MASTERS = 10
MIN_SPECIES = 5


def run(path: Path, *, assume_whole_colony_extract: bool = False) -> dict:
    legacy = legacy_analyze(
        path,
        assume_whole_colony_extract=assume_whole_colony_extract,
    )

    panels = [
        p for p in legacy["eligible_panels"]
        if int(p["calendar_span_years"]) >= MIN_SPAN
    ]
    species = sorted({str(p["species"]) for p in panels})
    masters = sorted({str(p["master_site"]) for p in panels})

    passed = bool(
        len(panels) >= MIN_PANELS
        and len(masters) >= MIN_MASTERS
        and len(species) >= MIN_SPECIES
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-smp-spatial-recovery-hysteresis-structure-v1",
        "status": "outcome_blind_structure_only",
        "source": legacy["source"],
        "thresholds": {
            "minimum_retained_components": 3,
            "minimum_complete_years": 10,
            "minimum_calendar_span_years": MIN_SPAN,
            "minimum_structurally_eligible_panels": MIN_PANELS,
            "minimum_distinct_master_sites": MIN_MASTERS,
            "minimum_species": MIN_SPECIES,
        },
        "eligible_panel_count": int(len(panels)),
        "distinct_master_site_count": int(len(masters)),
        "eligible_species_count": int(len(species)),
        "eligible_species": species,
        "eligible_panels": panels,
        "decision": {
            "structural_gate_passed": passed,
            "identity_resolution_authorized": passed,
            "state_only_hysteresis_gate_authorized": False,
            "if_passed": "Proceed only to provider/site-history identity resolution; positive/zero states remain locked.",
            "if_failed": "Stop before SiteID identity resolution or positive/zero states; do not lower thresholds.",
        },
        "forbidden_outputs_confirmed_absent": [
            "count magnitudes",
            "positive/zero occupancy states",
            "vacancy spells",
            "panel abundance totals",
            "hysteresis H",
            "E",
            "kappa",
            "gamma",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()
    result = run(
        a.input,
        assume_whole_colony_extract=a.assume_whole_colony_extract,
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
