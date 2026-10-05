#!/usr/bin/env python3
"""Create an immutable Stage-B freeze receipt before any SMP magnitude opening.

This is an operational guard only. It does not alter the frozen V3 scientific
design. It verifies that all pre-magnitude gates passed on one raw extract,
checks the preregistered canonical file blob SHAs, and hashes the exact inputs
that Stage C is allowed to use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


CANDIDATE_ID = "mina-smp-spatial-recovery-hysteresis-structure-v1"
RESOLVED_ID = "mina-smp-spatial-recovery-structure-v1"
STAGEB_ID = "mina-smp-spatial-recovery-hysteresis-support-v1"
PREREG_ID = "mina-smp-spatial-recovery-hysteresis-preregistration-receipt-v3"
CUSTODY_ID = "mina-smp-raw-custody-v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    payload = f"blob {len(data)}\0".encode("utf-8") + data
    return hashlib.sha1(payload).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_zero_semantics(z: dict) -> None:
    for key in (
        "row_with_direct_count_zero_is_surveyed_nil",
        "absent_site_year_row_is_not_zero",
        "estimated_or_imputed_zero_excluded_from_primary",
    ):
        if z.get(key) is not True:
            raise ValueError(f"zero semantics not confirmed: {key}")
    if not str(z.get("confirmation_source", "")).strip():
        raise ValueError("zero semantics confirmation_source missing")
    if not str(z.get("compatible_record_family_or_era", "")).strip():
        raise ValueError("zero semantics record family/era missing")
    start = int(z["compatible_start_year"])
    end = int(z["compatible_end_year"])
    if not (1986 <= start <= end <= 2024):
        raise ValueError("zero semantics year scope invalid")


def verify_canonical_blobs(repo_root: Path, prereg: dict) -> list[dict]:
    failures = []
    checked = []
    for item in prereg.get("canonical_files", []):
        rel = str(item["path"])
        want = str(item["git_blob_sha"])
        path = repo_root / rel
        if not path.exists():
            failures.append({"path": rel, "reason": "missing"})
            continue
        got = git_blob_sha(path)
        checked.append({"path": rel, "git_blob_sha": got})
        if got != want:
            failures.append({"path": rel, "expected": want, "observed": got})
    if failures:
        raise ValueError(
            "canonical frozen design drift detected: "
            + json.dumps(failures, sort_keys=True)
        )
    return checked


def run(
    raw_path: Path,
    custody_json: Path,
    candidate_json: Path,
    identity_csv: Path,
    resolved_json: Path,
    zero_json: Path,
    stageb_json: Path,
    prereg_json: Path,
    repo_root: Path,
) -> dict:
    custody = load_json(custody_json)
    candidate = load_json(candidate_json)
    resolved = load_json(resolved_json)
    zero = load_json(zero_json)
    stageb = load_json(stageb_json)
    prereg = load_json(prereg_json)

    if custody.get("receipt_id") != CUSTODY_ID:
        raise ValueError("not a valid raw-custody receipt")
    if custody.get("status") != "RAW_EXTRACT_CUSTODY_RECORDED_CONTENT_NOT_PARSED":
        raise ValueError("raw-custody receipt status invalid")
    if custody.get("content_parsed") is not False or custody.get("content_inspected") is not False:
        raise ValueError("raw-custody receipt does not preserve content blind")

    if prereg.get("receipt_id") != PREREG_ID:
        raise ValueError("not the canonical V3 preregistration receipt")
    if not str(prereg.get("frozen_design_head_sha", "")).strip():
        raise ValueError("canonical preregistration missing frozen design SHA")

    checked_blobs = verify_canonical_blobs(repo_root, prereg)

    if candidate.get("analysis_id") != CANDIDATE_ID:
        raise ValueError("candidate A0 analysis_id mismatch")
    if not candidate.get("decision", {}).get("structural_gate_passed"):
        raise ValueError("candidate A0 gate did not pass")

    raw_sha = sha256_file(raw_path)
    if str(custody.get("sha256", "")).strip() != raw_sha:
        raise ValueError("raw extract SHA does not match custody receipt")
    if int(custody.get("byte_size", -1)) != int(raw_path.stat().st_size):
        raise ValueError("raw extract byte size does not match custody receipt")
    if str(custody.get("local_filename", "")).strip() != raw_path.name:
        raise ValueError("raw extract filename does not match custody receipt")
    frozen_raw_sha = str(candidate.get("source", {}).get("sha256", "")).strip()
    if not frozen_raw_sha or raw_sha != frozen_raw_sha:
        raise ValueError("raw extract SHA does not match A0 structural receipt")

    if resolved.get("analysis_id") != RESOLVED_ID:
        raise ValueError("resolved A1 analysis_id mismatch")
    if not resolved.get("decision", {}).get("structural_gate_passed"):
        raise ValueError("resolved physical-identity gate did not pass")

    identity_header = identity_csv.read_text(encoding="utf-8-sig").splitlines()[0]
    forbidden_identity_fields = {"Count", "count", "H", "E", "kappa", "gamma"}
    present = {x.strip() for x in identity_header.split(",")}
    bad = sorted(forbidden_identity_fields & present)
    if bad:
        raise ValueError(f"identity-resolution CSV contains forbidden fields: {bad}")

    validate_zero_semantics(zero)

    if stageb.get("analysis_id") != STAGEB_ID:
        raise ValueError("Stage-B analysis_id mismatch")
    if not stageb.get("decision", {}).get("hysteresis_magnitude_execution_authorized"):
        raise ValueError("Stage-B magnitude opening was not authorized")

    embedded_zero = stageb.get("zero_semantics_confirmation", {})
    for key in (
        "row_with_direct_count_zero_is_surveyed_nil",
        "absent_site_year_row_is_not_zero",
        "estimated_or_imputed_zero_excluded_from_primary",
        "confirmation_source",
        "compatible_start_year",
        "compatible_end_year",
        "compatible_record_family_or_era",
    ):
        if embedded_zero.get(key) != zero.get(key):
            raise ValueError(f"Stage-B zero semantics drift: {key}")

    spells = stageb.get("completed_spells", [])
    if len(spells) < int(stageb["thresholds"]["minimum_linear_shift_eligible_completed_spells"]):
        raise ValueError("Stage-B spell roster is below its own frozen threshold")
    for spell in spells:
        offsets = [int(v) for v in spell.get("common_offset_values", [])]
        if 0 not in offsets or len(offsets) < 3:
            raise ValueError(
                f"invalid common-offset support for spell {spell.get('spell_id')}"
            )
        forbidden = {"H", "abandon_state", "recolonize_state"}
        if forbidden & set(spell):
            raise ValueError("Stage-B output contains forbidden magnitude endpoint")

    files = {
        "raw_extract": raw_path,
        "raw_custody": custody_json,
        "candidate_structure": candidate_json,
        "identity_resolution": identity_csv,
        "resolved_structure": resolved_json,
        "zero_semantics": zero_json,
        "stageb_support": stageb_json,
        "canonical_preregistration": prereg_json,
    }

    return {
        "schema_version": 1,
        "receipt_id": "mina-smp-spatial-recovery-stageb-freeze-v1",
        "status": "STAGE_B_FROZEN_STAGE_C_AUTHORIZED",
        "canonical_design": {
            "receipt_id": prereg["receipt_id"],
            "frozen_design_head_sha": prereg["frozen_design_head_sha"],
            "canonical_file_blobs_verified": checked_blobs,
        },
        "input_hashes": {
            name: {
                "path": path.name,
                "sha256": sha256_file(path),
            }
            for name, path in files.items()
        },
        "raw_extract_sha256": raw_sha,
        "custody": {
            "receipt_id": custody["receipt_id"],
            "received_at": custody["received_at"],
            "provider_filename": custody["provider_filename"],
            "local_filename": custody["local_filename"],
            "byte_size": int(custody["byte_size"]),
            "sha256": custody["sha256"],
        },
        "gate_summary": {
            "raw_custody_verified": True,
            "candidate_A0_passed": True,
            "identity_A1_passed": True,
            "zero_semantics_A2_passed": True,
            "stage_B_passed": True,
            "stage_B_spell_count": int(len(spells)),
            "stage_B_physical_master_count": int(
                stageb.get("support", {}).get("mastersites_with_spells", 0)
            ),
            "stage_B_species_count": int(
                stageb.get("support", {}).get("species_with_spells", 0)
            ),
        },
        "decision": {
            "stage_C_authorized": True,
            "required_execution": (
                "Use only the guarded Stage-C wrapper with this receipt and the "
                "exact hashed raw/resolved/stage-B files."
            ),
        },
        "boundary": (
            "Operational provenance receipt only. It changes no ecological "
            "definition, threshold, weighting, null, or inferential rule."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True, type=Path)
    p.add_argument("--custody-json", required=True, type=Path)
    p.add_argument("--candidate-json", required=True, type=Path)
    p.add_argument("--identity-csv", required=True, type=Path)
    p.add_argument("--resolved-json", required=True, type=Path)
    p.add_argument("--zero-json", required=True, type=Path)
    p.add_argument("--stageb-json", required=True, type=Path)
    p.add_argument("--prereg-json", required=True, type=Path)
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    result = run(
        a.raw,
        a.custody_json,
        a.candidate_json,
        a.identity_csv,
        a.resolved_json,
        a.zero_json,
        a.stageb_json,
        a.prereg_json,
        a.repo_root,
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
