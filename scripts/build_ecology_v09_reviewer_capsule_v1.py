#!/usr/bin/env python3
"""Build a verified, review-only Ecology v0.9 scientific capsule.

Includes ONLY allowlisted, frozen manuscript science and figure inputs.
Not a deposit, final submission, or complete rerun of all historical models.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from audit_ecology_submission_handoff_v1 import FROZEN_BLOBS, git_blob_sha

SOURCES = (
    "docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_8.md",
    "docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_9.md",
    "docs/REFERENCES_SPATIAL_RECOVERY_PATH_STATE_V0_8.bib",
    "docs/FIGURE_CAPTIONS_SPATIAL_RECOVERY_PATH_STATE_V0_1.md",
    "docs/FIGURE_CAPTIONS_SPATIAL_RECOVERY_PATH_STATE_V0_3.md",
    "docs/ROSS_LOCAL_RECOVERY_RATIO_DECOMPOSITION_V1.md",
    "docs/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.md",
    "docs/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.md",
    "results/SPATIAL_RECOVERY_CLAIM_EVIDENCE_LEDGER_V4.json",
    "results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json",
    "results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json",
    "results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
    "results/SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json",
    "results/BEAUFORT_ISLAND_INTENSIFICATION_EXPANSION_RESULT_V1.json",
    "external/ross_island_v2_frozen_counts.csv",
    "scripts/analyze_ross_aggregate_vs_spatial_restoration.py",
    "scripts/analyze_ross_inverse_path_mismatch.py",
    "scripts/build_spatial_recovery_path_state_figures.py",
    "submission/SUPPLEMENT_SPATIAL_RECOVERY_PATH_STATE_V1.md",
    "submission/OPEN_RESEARCH_STATEMENT_SPATIAL_RECOVERY_V1.md",
    "submission/SPATIAL_RECOVERY_PUBLICATION_ARCHIVE_MANIFEST_V1.md",
    "submission/ECOLOGY_SOURCE_DATASET_BIB_ADDENDUM_20261014.bib",
    "submission/ECOLOGY_SPATIAL_RECOVERY_FREEZE_BLOB_VERIFICATION_20261014.md",
)

FIGURES = (
    "figure1_three_recovery_dimensions.png",
    "figure2_local_recovery_state_reweighting.png",
    "figure3_ross_path_state_calibration.png",
    "figure4_process_contrasts.png",
)

DOIS = {
    "Ross Sea Adélie": "10.7931/kf06-x745",
    "Palmer LTER": "10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e",
    "Signy": "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
    "Beaufort natural-history article": "10.1371/journal.pone.0060568",
}

README = """# Ecology Article reviewer reproduction capsule

REVIEW ONLY. NOT SUBMITTED. NOT AN IMMUTABLE DOI ARCHIVE.
Contains no approved author list, email, private IDs, or confidential files.

The central 1999-2001-2002 Ross result is observational, and its
path/state reinterpretation was developed after earlier exploration.
The Palmer/Signy attrition and Beaufort capacity contrasts are different
systems, NOT independent replications of the Ross iceberg experiment.

This deliberately compact archive includes frozen results and executable
Ross numerical scripts, one frozen public aerial census extract, and
the original code needed to regenerate FOUR figure PNG/PDF pairs.
It is not a complete independent rerun of the original 100,000-draw
Palmer/Signy count-error inference. Those source-backed result receipts
are provided without re-claiming new independent validation.

To reproduce figures with Python 3.12 or later:
  python -m pip install "matplotlib>=3.8,<4"
  mkdir -p build
  python scripts/analyze_ross_aggregate_vs_spatial_restoration.py --out build/ross.json
  python scripts/analyze_ross_inverse_path_mismatch.py --out build/inverse.json
  python scripts/build_spatial_recovery_path_state_figures.py --repo-root . --outdir build/figures

The source file paths and raw SHA256 checksums are listed in MANIFEST.json.
Eight historical scientific source Git blob SHA1 values were checked
against the immutable scientific freeze before this ZIP was created.

Public original sources: https://doi.org/10.7931/kf06-x745 ;
https://doi.org/10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e ;
https://doi.org/10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d .
Beaufort source: https://doi.org/10.1371/journal.pone.0060568

Original data and imagery rights remain with their data stewards;
do not assume third-party data can be republished under a new licence.
The version, rights, actual author agreement, and permanent archive are
pending final corresponding-author review.
"""
REQUIREMENTS = "matplotlib>=3.8,<4\n"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def audited_inputs(root: Path) -> dict[str, bytes]:
    if not set(FROZEN_BLOBS).issubset(SOURCES):
        raise ValueError("STOP: a frozen scientific blob was omitted")
    if len(set(SOURCES)) != len(SOURCES):
        raise ValueError("STOP: duplicate file")
    data = {}
    for name in SOURCES:
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts or len(rel.parts)<2:
            raise ValueError("STOP: unsafe path")
        path = root/rel
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 1_000_000:
            raise ValueError("STOP: missing or non-regular source: " + name)
        if name in FROZEN_BLOBS and git_blob_sha(path) != FROZEN_BLOBS[name]:
            raise ValueError("STOP: frozen scientific content changed: " + name)
        data[name] = path.read_bytes()
    return data


def receipt_numbers(data: dict[str, bytes]) -> dict[str, float]:
    import math
    ross = json.loads(data["results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json"])
    grain = json.loads(data["results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json"])
    f = ross["focal_episode"]
    checks = {
        "aggregate_restoration": (f["aggregate"]["aggregate_loss_restored_fraction"], 0.9696749043183291),
        "six_component_path": (grain["six_component"]["inverse_path_fidelity"], 0.9059455495961382),
        "three_colony_path": (grain["three_colony"]["inverse_path_fidelity"], 0.9327199232407497),
        "six_component_state": (grain["six_component"]["state_restoration_fraction"], 0.0239611381095024),
        "three_colony_state": (grain["three_colony"]["state_restoration_fraction"], 0.2830106852134694),
    }
    for key,(value,expected) in checks.items():
        if not math.isclose(value, expected, abs_tol=1e-10, rel_tol=0):
            raise ValueError("STOP: original claim drift: " + key)
    return {k:float(v[0]) for k,v in checks.items()}


def add_zip(zf, name: str, data: bytes):
    zi=zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
    zi.external_attr=(0o100644 << 16)
    zi.compress_type=zipfile.ZIP_DEFLATED
    zf.writestr(zi, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def make(root: Path, target: Path) -> dict:
    data=audited_inputs(root)
    numbers=receipt_numbers(data)
    included={**data,"README_REVIEW_ONLY.md": README.encode("utf-8"),
              "requirements.txt": REQUIREMENTS.encode("utf-8")}
    manifest={
        "status":"REVIEW_ONLY_NOT_AUTHOR_APPROVED_NOT_PERMANENT_ARCHIVE",
        "version":1,
        "scientific_freeze_commit":"3e8882742ca2affc6717d373fd9b6d903b01f4c1",
        "scientific_source_blob_sha1": dict(FROZEN_BLOBS),
        "origin_dois":DOIS,
        "four_figure_pngs_expected":list(FIGURES),
        "frozen_focal_results":numbers,
        "files":{name:{"sha256":sha(raw),"bytes":len(raw)}
                 for name,raw in sorted(included.items())},
        "scope":"Ross numeric and four figure regenerations from frozen receipts; NOT fresh Palmer/Signy model fitting.",
        "excluded":"author personal data, email, tokens, raw images and unrelated island projects",
    }
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,"w") as archive:
        for name,raw in sorted(included.items()):
            add_zip(archive,name,raw)
        add_zip(archive,"MANIFEST.json",
                (json.dumps(manifest,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
    with zipfile.ZipFile(target) as archive:
        assert set(archive.namelist())==set(included)|{"MANIFEST.json"}
        assert archive.testzip() is None
        for name,x in manifest["files"].items():
            assert sha(archive.read(name))==x["sha256"]
    return {"status":"REVIEW_ONLY_CAPSULE_VERIFIED_NOT_SUBMITTED",
            "member_count":len(included)+1,
            "source_file_count":len(data),
            "science_frozen":True,
            "zip_bytes":target.stat().st_size,
            "zip_sha256":sha(target.read_bytes()),
            "expected_figures": list(FIGURES),
            "original_focal_numbers":numbers,
            "artifact_path":str(target)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(make(args.root,args.out),indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
