#!/usr/bin/env python3
"""Freeze the exact guillemot Stage-B state-only support before Stage C."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("utf-8") + data
    ).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_preregistration(repo_root: Path, prereg: dict) -> list[dict]:
    receipt_id = str(prereg.get("receipt_id", ""))
    if not receipt_id.startswith(
        "mina-guillemot-same-site-recovery-preregistration-"
    ):
        raise ValueError("not a guillemot same-site preregistration receipt")

    failures = []
    checked = []
    for item in prereg.get("canonical_files", []):
        rel = str(item["path"])
        expected = str(item["git_blob_sha"])
        path = repo_root / rel
        if not path.exists():
            failures.append({"path": rel, "reason": "missing"})
            continue
        got = git_blob_sha(path)
        checked.append({"path": rel, "git_blob_sha": got})
        if got != expected:
            failures.append({
                "path": rel,
                "expected": expected,
                "observed": got,
            })
    if failures:
        raise ValueError(
            "frozen preregistration drift detected: "
            + json.dumps(failures, sort_keys=True)
        )
    return checked


def run(
    raw: Path,
    stageb_json: Path,
    prereg_json: Path,
    repo_root: Path,
) -> dict:
    stageb = load_json(stageb_json)
    prereg = load_json(prereg_json)

    checked = verify_preregistration(repo_root, prereg)

    if stageb.get("analysis_id") != "mina-guillemot-same-site-support-v1":
        raise ValueError("Stage-B analysis_id mismatch")
    if stageb.get("status") != "STAGE_B_SUPPORT_PASSED":
        raise ValueError("Stage-B support did not pass")
    if not stageb.get("decision", {}).get(
        "stage_C_magnitude_opening_authorized"
    ):
        raise ValueError("Stage C not authorized by Stage B")

    raw_sha = sha256_file(raw)
    if raw_sha != stageb.get("source", {}).get("raw_file_sha256"):
        raise ValueError("raw-file SHA differs from Stage-B source")

    boundary = stageb.get("magnitude_boundary", {})
    required_false = [
        "Subcolony.size_read",
        "H_computed",
        "A_vacancy_computed",
        "A_reoccupation_computed",
        "population_state_magnitudes_exposed",
    ]
    for key in required_false:
        if boundary.get(key) is not False:
            raise ValueError(f"Stage-B magnitude boundary failed: {key}")
    if stageb.get("source", {}).get("magnitude_fields_read") != []:
        raise ValueError("Stage B reports reading magnitude fields")

    spells = stageb.get("completed_spells", [])
    if len(spells) < 30:
        raise ValueError("frozen Stage-B roster below minimum spell count")
    for s in spells:
        offsets = [int(v) for v in s.get("common_offset_values", [])]
        if 0 not in offsets or len(offsets) < 3:
            raise ValueError(
                f"invalid offset support for spell {s.get('spell_id')}"
            )
        forbidden = {
            "H", "A_v", "A_r", "T_obs",
            "subcolony_size", "N_minus_j",
            "vacancy_state", "reoccupation_state",
        }
        bad = forbidden.intersection(s)
        if bad:
            raise ValueError(
                f"magnitude field(s) leaked into Stage B: {sorted(bad)}"
            )

    return {
        "schema_version": 1,
        "receipt_id": "mina-guillemot-same-site-stageb-freeze-v1",
        "status": "STAGE_B_FROZEN_STAGE_C_AUTHORIZED",
        "canonical_design": {
            "receipt_id": prereg["receipt_id"],
            "frozen_design_head_sha": prereg["frozen_design_head_sha"],
            "canonical_file_blobs_verified": checked,
        },
        "input_hashes": {
            "raw_extract": {
                "path": raw.name,
                "sha256": raw_sha,
            },
            "stageb_support": {
                "path": stageb_json.name,
                "sha256": sha256_file(stageb_json),
            },
            "preregistration": {
                "path": prereg_json.name,
                "sha256": sha256_file(prereg_json),
            },
        },
        "support_snapshot": stageb["support"],
        "frozen_spell_ids": [str(s["spell_id"]) for s in spells],
        "decision": {
            "stage_C_authorized": True,
            "required_execution": (
                "Use only guarded_run_guillemot_same_site_recovery_v1.py "
                "with this receipt and the exact hashed raw/Stage-B files."
            ),
        },
        "boundary": (
            "Operational provenance only; no abundance magnitude was opened "
            "by the Stage-B gate or this freeze."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True, type=Path)
    p.add_argument("--stageb-json", required=True, type=Path)
    p.add_argument("--prereg-json", required=True, type=Path)
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    result = run(
        a.raw, a.stageb_json, a.prereg_json, a.repo_root
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "support_snapshot": result["support_snapshot"],
        "decision": result["decision"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
