#!/usr/bin/env python3
"""Guarded Stage-C launcher for the frozen guillemot same-site test."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.freeze_guillemot_same_site_stageb_v1 import sha256_file
from scripts.gate_guillemot_same_site_support_v1 import run as run_stageb
from scripts.prepare_guillemot_same_site_input_v1 import prepare
from scripts.run_guillemot_same_site_recovery_v1 import (
    _with_offsets,
    analyse,
    extract_spells,
)


FREEZE_ID = "mina-guillemot-same-site-stageb-freeze-v1"


def _canonical_spell_view(spells: list[dict]) -> list[dict]:
    keys = [
        "spell_id",
        "subcolony",
        "site_id",
        "block_start",
        "block_end",
        "vacancy_pre_year",
        "vacancy_first_year",
        "vacancy_last_year",
        "reoccupation_year",
        "vacancy_duration_years",
        "shift_group_id",
        "common_offset_values",
    ]
    return [
        {k: s[k] for k in keys}
        for s in sorted(spells, key=lambda z: z["spell_id"])
    ]


def _eligible_from_standardized(df) -> list[dict]:
    s = _with_offsets(extract_spells(df))
    if len(s) == 0:
        return []
    s = s.loc[
        s["common_offsets"].map(lambda v: 0 in v and len(v) >= 3)
    ].copy()
    rows = []
    for r in s.itertuples(index=False):
        rows.append({
            "spell_id": str(r.spell_id),
            "subcolony": str(r.subcolony),
            "site_id": str(r.site_id),
            "block_start": int(r.block_start),
            "block_end": int(r.block_end),
            "vacancy_pre_year": int(r.vacancy_pre_year),
            "vacancy_first_year": int(r.vacancy_first_year),
            "vacancy_last_year": int(r.vacancy_last_year),
            "reoccupation_year": int(r.reoccupation_year),
            "vacancy_duration_years": int(r.vacancy_duration_years),
            "shift_group_id": str(r.group_id),
            "common_offset_values": [int(v) for v in r.common_offsets],
        })
    return rows


def run_guarded(
    raw: Path,
    stageb_json: Path,
    freeze_json: Path,
    *,
    B: int = 9999,
    seed: int = 20261005,
) -> dict:
    stageb = json.loads(stageb_json.read_text(encoding="utf-8"))
    freeze = json.loads(freeze_json.read_text(encoding="utf-8"))

    if freeze.get("receipt_id") != FREEZE_ID:
        raise ValueError("not a valid guillemot Stage-B freeze receipt")
    if freeze.get("status") != "STAGE_B_FROZEN_STAGE_C_AUTHORIZED":
        raise ValueError("freeze receipt does not authorize Stage C")
    if not freeze.get("decision", {}).get("stage_C_authorized"):
        raise ValueError("Stage C not authorized")

    raw_sha = sha256_file(raw)
    if raw_sha != freeze["input_hashes"]["raw_extract"]["sha256"]:
        raise ValueError("raw input changed after Stage-B freeze")
    if sha256_file(stageb_json) != freeze["input_hashes"]["stageb_support"]["sha256"]:
        raise ValueError("Stage-B support changed after freeze")

    # Re-run the state-only gate from the exact raw bytes. This still reads no
    # population-size magnitude and must reproduce the frozen spell roster.
    fresh_stageb = run_stageb(raw)
    if fresh_stageb["completed_spells"] != stageb["completed_spells"]:
        raise ValueError("fresh state-only spell roster differs from frozen Stage B")

    # Only after all pre-magnitude checks pass is Subcolony.size read.
    standardized, adapter_audit = prepare(raw)
    magnitude_spell_view = _eligible_from_standardized(standardized)
    frozen_spell_view = _canonical_spell_view(stageb["completed_spells"])
    if magnitude_spell_view != frozen_spell_view:
        raise ValueError(
            "Stage-C magnitude-complete site-year support does not reproduce "
            "the frozen state-only spell roster"
        )

    primary = analyse(
        standardized, B=B, seed=seed, min_vacancy=1
    )
    secondary = analyse(
        standardized, B=B, seed=seed, min_vacancy=2
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-guillemot-same-site-recovery-v1",
        "primary": primary,
        "secondary_two_year_vacancy": secondary,
        "operational_provenance": {
            "stageb_freeze_receipt_id": freeze["receipt_id"],
            "stageb_freeze_receipt_sha256": sha256_file(freeze_json),
            "raw_extract_sha256": raw_sha,
            "stageb_support_sha256": sha256_file(stageb_json),
            "adapter_audit": adapter_audit,
            "guarded_launcher": (
                "scripts/guarded_run_guillemot_same_site_recovery_v1.py"
            ),
        },
        "claim_boundary": {
            "event": "annual breeding-site vacancy and later reoccupation",
            "not_identified": [
                "individual return",
                "causal Allee effect",
                "causal social attraction",
                "permanent abandonment",
                "multi-species seabird-wide hysteresis",
            ],
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True, type=Path)
    p.add_argument("--stageb-json", required=True, type=Path)
    p.add_argument("--freeze-receipt", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--B", type=int, default=9999)
    p.add_argument("--seed", type=int, default=20261005)
    a = p.parse_args()

    result = run_guarded(
        a.raw,
        a.stageb_json,
        a.freeze_receipt,
        B=a.B,
        seed=a.seed,
    )
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "primary_support": result["primary"]["support"],
        "primary_decision": result["primary"]["decision"],
        "secondary_decision": result["secondary_two_year_vacancy"]["decision"],
        "operational_provenance": result["operational_provenance"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
