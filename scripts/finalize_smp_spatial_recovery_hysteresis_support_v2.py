#!/usr/bin/env python3
"""Finalize V2 non-circular common-shift support from the frozen V1 state scan.

No abundance magnitude is read. V2 retains the provider-confirmed completed
vacancy spells but replaces the failed circular phase support with one common,
non-circular integer-year shift per physical MasterSite phase block.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


MIN_COMMON_SHIFTS = 3
MIN_SPELLS = 30
MIN_SITES = 20
MIN_MASTERS = 10
MIN_SPECIES = 5
MIN_SPECIES_3SPELLS = 4
MIN_SPECIES_2MASTERS = 3


def event_years(spell: dict) -> list[int]:
    return [
        int(spell["abandon_from"]),
        int(spell["abandon_to"]),
        int(spell["recolonize_from"]),
        int(spell["recolonize_to"]),
    ]


def shift_group_id(spell: dict) -> str:
    return (
        f"{spell['master_site_key']}|"
        f"{int(spell['phase_block_start'])}|{int(spell['phase_block_end'])}"
    )


def common_noncircular_shifts(spells: list[dict]) -> list[int]:
    if not spells:
        return []
    blocks = {
        tuple(int(v) for v in sp["phase_block_years"])
        for sp in spells
    }
    if len(blocks) != 1:
        raise ValueError("shift group has inconsistent phase_block_years")
    block = list(next(iter(blocks)))
    if not block:
        return []
    expected = list(range(block[0], block[-1] + 1))
    if block != expected:
        raise ValueError("V2 common-shift null requires a consecutive phase block")
    yset = set(block)

    # One shift is applied to every event in every spell in this physical block.
    lo = max(block[0] - min(event_years(sp)) for sp in spells)
    hi = min(block[-1] - max(event_years(sp)) for sp in spells)
    out = []
    for k in range(int(lo), int(hi) + 1):
        ok = all(
            all((y + k) in yset for y in event_years(sp))
            for sp in spells
        )
        if ok:
            out.append(int(k))
    if 0 not in out:
        raise ValueError("observed alignment k=0 is not valid for its own phase block")
    return out


def run(v1_support_json: Path) -> dict:
    v1 = json.loads(v1_support_json.read_text(encoding="utf-8"))
    if v1.get("analysis_id") != "mina-smp-spatial-recovery-hysteresis-support-v1":
        raise ValueError("V2 finalizer requires V1 provider-confirmed state-only support output")

    spells = list(v1.get("completed_spells", []))
    groups: dict[str, list[dict]] = defaultdict(list)
    for sp in spells:
        gid = shift_group_id(sp)
        groups[gid].append(dict(sp))

    eligible_groups = {}
    excluded_groups = []
    retained_spells = []

    for gid, local in sorted(groups.items()):
        shifts = common_noncircular_shifts(local)
        meta = {
            "shift_group_id": gid,
            "master_site_key": str(local[0]["master_site_key"]),
            "phase_block_start": int(local[0]["phase_block_start"]),
            "phase_block_end": int(local[0]["phase_block_end"]),
            "eligible_common_shifts": shifts,
            "n_common_shifts": int(len(shifts)),
            "n_spells": int(len(local)),
        }
        if len(shifts) < MIN_COMMON_SHIFTS:
            excluded_groups.append({**meta, "reason": "fewer than 3 common non-circular shifts"})
            continue
        eligible_groups[gid] = meta
        for sp in local:
            q = dict(sp)
            q["shift_group_id"] = gid
            q["eligible_common_shifts"] = shifts
            q["n_common_shifts"] = int(len(shifts))
            retained_spells.append(q)

    frame = pd.DataFrame(retained_spells)
    n_spells = int(len(frame))
    n_sites = (
        int(frame[["species", "master_site_key", "site_id"]].drop_duplicates().shape[0])
        if n_spells else 0
    )
    n_masters = int(frame["master_site_key"].nunique()) if n_spells else 0
    n_species = int(frame["species"].nunique()) if n_spells else 0
    sp_counts = Counter(frame["species"]) if n_spells else Counter()
    sp_masters = (
        frame.groupby("species")["master_site_key"].nunique().to_dict()
        if n_spells else {}
    )
    species_3 = sorted([sp for sp, n in sp_counts.items() if n >= 3])
    species_2masters = sorted(
        [sp for sp, n in sp_masters.items() if int(n) >= 2]
    )

    passed = bool(
        n_spells >= MIN_SPELLS
        and n_sites >= MIN_SITES
        and n_masters >= MIN_MASTERS
        and n_species >= MIN_SPECIES
        and len(species_3) >= MIN_SPECIES_3SPELLS
        and len(species_2masters) >= MIN_SPECIES_2MASTERS
    )

    return {
        "schema_version": 2,
        "analysis_id": "mina-smp-spatial-recovery-hysteresis-support-v2",
        "status": "state_only_noncircular_common_shift_support",
        "source_v1_support_analysis_id": v1.get("analysis_id"),
        "zero_semantics_confirmation": v1.get("zero_semantics_confirmation"),
        "completed_spells": retained_spells,
        "shift_groups": list(eligible_groups.values()),
        "excluded_shift_groups": excluded_groups,
        "support": {
            "shift_eligible_completed_spells": n_spells,
            "distinct_siteids_with_spells": n_sites,
            "physical_mastersites_with_spells": n_masters,
            "species_with_spells": n_species,
            "species_with_at_least_3_spells": species_3,
            "species_with_spells_in_at_least_2_mastersites": species_2masters,
            "eligible_shift_groups": int(len(eligible_groups)),
        },
        "thresholds": {
            "minimum_common_noncircular_shifts_per_group": MIN_COMMON_SHIFTS,
            "minimum_shift_eligible_completed_spells": MIN_SPELLS,
            "minimum_distinct_siteids_with_spells": MIN_SITES,
            "minimum_physical_mastersites_with_spells": MIN_MASTERS,
            "minimum_species_with_spells": MIN_SPECIES,
            "minimum_species_with_at_least_3_spells": MIN_SPECIES_3SPELLS,
            "minimum_species_with_spells_in_at_least_2_mastersites": MIN_SPECIES_2MASTERS,
        },
        "decision": {
            "v2_magnitude_execution_support_passed": passed,
            "if_failed": "Stop V2; do not lower common-shift or replication thresholds.",
        },
        "forbidden_outputs_confirmed_absent": [
            "count magnitudes",
            "abandonment abundance",
            "recolonization abundance",
            "H",
            "shift-null H values",
            "E",
            "kappa",
            "gamma",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--v1-support-json", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    result = run(a.v1_support_json)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "completed_spells"}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
