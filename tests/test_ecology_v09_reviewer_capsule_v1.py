"""Reviewer-only capsule tests; preserve the frozen scientific results."""
import copy
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_ecology_v09_reviewer_capsule_v1 import (
    SOURCES, FIGURES, audited_inputs, make, receipt_numbers
)


def test_capsule_only_allowlisted_science_with_8_frozen_sha(tmp_path):
    dest=tmp_path/"ecology_capsule.zip"
    summary=make(ROOT,dest)
    assert summary["science_frozen"] is True
    assert summary["member_count"] == len(SOURCES)+3
    assert summary["status"] == "REVIEW_ONLY_CAPSULE_VERIFIED_NOT_SUBMITTED"
    assert "figure1_three_recovery_dimensions.png" in summary["expected_figures"]
    with zipfile.ZipFile(dest) as archive:
        names=set(archive.namelist())
        assert names==set(SOURCES)|{"README_REVIEW_ONLY.md","requirements.txt","MANIFEST.json"}
        assert all(not n.endswith((".env",".key",".secret")) for n in names)
        assert not any("author_metadata" in n or "Béchervaise" in n or "ZAVODOVSKI" in n for n in names)
        metadata=json.loads(archive.read("MANIFEST.json"))
        assert len(metadata["scientific_source_blob_sha1"])==8
        for path,details in metadata["files"].items():
            assert hashlib.sha256(archive.read(path)).hexdigest()==details["sha256"]


def test_capsule_is_content_deterministic(tmp_path):
    a=make(ROOT,tmp_path/"first.zip")
    b=make(ROOT,tmp_path/"second.zip")
    assert a["zip_sha256"]==b["zip_sha256"]
    assert a["zip_bytes"] == b["zip_bytes"]


def test_source_edition_detects_mutation_before_public_packaging(tmp_path):
    for rel in SOURCES:
        source=ROOT/rel
        dest=tmp_path/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,dest)
    damaged=tmp_path/"results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json"
    damaged.write_bytes(damaged.read_bytes()+b"\n")
    with pytest.raises(ValueError, match="frozen scientific content changed"):
        audited_inputs(tmp_path)


def test_receipts_keep_original_claims_not_changed():
    vals=receipt_numbers(audited_inputs(ROOT))
    assert 0.96<vals["aggregate_restoration"]<0.98
    assert vals["six_component_state"]<vals["three_colony_state"]
    assert vals["six_component_path"]>0.90
