#!/usr/bin/env python3
"""Stricter outcome-blind structural gate for the SMP trend-symmetry program.

This wrapper reuses the legacy MasterSite support audit, which drops Count
magnitudes before analysis, then applies the intersection of all previously
frozen SMP macro support criteria. It never reopens abundance magnitudes.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from scripts.gate_smp_master_site_support_v1 import analyze as legacy_analyze


MIN_PANELS = 20
MIN_SPECIES = 8
MIN_MASTER_SITES = 15
MIN_REGIONS = 3
MIN_MULTI_PANEL_SPECIES = 4
MIN_SPAN = 12


def apply_composite_gate(result: dict) -> dict:
    panels = [
        p for p in result["eligible_panels"]
        if int(p["calendar_span_years"]) >= MIN_SPAN
    ]
    species = sorted({str(p["species"]) for p in panels})
    masters = sorted({str(p["master_site"]) for p in panels})
    regions = sorted({r for p in panels for r in p.get("countries", []) if str(r).strip()})
    species_panel_n = Counter(str(p["species"]) for p in panels)
    multi_species = sorted([sp for sp, n in species_panel_n.items() if n >= 2])

    passed = bool(
        len(panels) >= MIN_PANELS
        and len(species) >= MIN_SPECIES
        and len(masters) >= MIN_MASTER_SITES
        and len(regions) >= MIN_REGIONS
        and len(multi_species) >= MIN_MULTI_PANEL_SPECIES
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-smp-trend-symmetry-support-v1",
        "status": "outcome_blind_structural_gate_only",
        "source": result["source"],
        "legacy_gate_provenance": {
            "analysis_id": result["analysis_id"],
            "legacy_eligible_panels_before_stricter_span": int(result["eligible_panel_count"]),
        },
        "frozen_thresholds": {
            "minimum_retained_components": 3,
            "minimum_complete_years": 10,
            "minimum_calendar_span_years": MIN_SPAN,
            "minimum_eligible_panels": MIN_PANELS,
            "minimum_species": MIN_SPECIES,
            "minimum_distinct_master_sites": MIN_MASTER_SITES,
            "minimum_broad_regions": MIN_REGIONS,
            "minimum_species_with_two_or_more_panels": MIN_MULTI_PANEL_SPECIES,
        },
        "eligible_panel_count": int(len(panels)),
        "eligible_species_count": int(len(species)),
        "distinct_master_site_count": int(len(masters)),
        "broad_regions": regions,
        "broad_region_count": int(len(regions)),
        "species_with_two_or_more_panels": multi_species,
        "species_with_two_or_more_panels_count": int(len(multi_species)),
        "eligible_panels": panels,
        "decision": {
            "structural_gate_passed": passed,
            "next_stage_authorized": "total_abundance_trend_balance_gate" if passed else None,
            "if_failed": "Stop without relaxing structural thresholds.",
        },
        "forbidden_outputs_confirmed_absent": [
            "count magnitudes",
            "annual panel totals",
            "abundance trend slopes",
            "increase/decline labels",
            "component proportions",
            "effective component number E",
            "kappa",
            "gamma",
            "delta_gamma",
        ],
    }


def run(path: Path, assume_whole_colony_extract: bool = False) -> dict:
    legacy = legacy_analyze(
        path,
        assume_whole_colony_extract=assume_whole_colony_extract,
    )
    return apply_composite_gate(legacy)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--assume-whole-colony-extract", action="store_true")
    a = p.parse_args()
    result = run(a.input, a.assume_whole_colony_extract)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
