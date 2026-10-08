"""Synthetic byte identity test only: never parse any behavioral source content."""
import importlib.util
import hashlib
from pathlib import Path

F=Path(__file__).resolve().parents[1]/"scripts/verify_ross_public_resight_mirror_md5_v1.py"
spec=importlib.util.spec_from_file_location("ross_digest",F)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_same_exact_synthetic_author_copy_passes_only_both_author_and_official(tmp_path):
    payload=b"opaque binary regression fixture\nnever an animal data row\n"
    f=tmp_path/"private_fixture.bin"
    f.write_bytes(payload)
    md5=hashlib.md5(payload,usedforsecurity=False).hexdigest()
    blob=hashlib.sha1(f"blob {len(payload)}\0".encode()+payload,
                       usedforsecurity=False).hexdigest()
    r=m.checksum_candidate(f,expected_official_md5=md5,
                             expected_source_blob=blob,expected_length=len(payload))
    assert r["identity_eligible_exact_digest_and_size"]
    assert r["headers_read"]==0
    assert r["behavioral_rows_read"]==0
    assert r["PR142_original_frozen_gate_modified"] is False


def test_different_official_bytes_never_pass_author_match(tmp_path):
    b=b"no animal rows here"
    f=tmp_path/"f"
    f.write_bytes(b)
    blob=hashlib.sha1(f"blob {len(b)}\0".encode()+b,usedforsecurity=False).hexdigest()
    z=m.checksum_candidate(f,expected_source_blob=blob,expected_length=len(b),
                            expected_official_md5="0"*32)
    assert not z["identity_eligible_exact_digest_and_size"]
    assert z["status"].startswith("HOLD_")
    assert z["source_blob_matches_pin"] is True


def test_author_blob_discrepancy_blocks_matching_md5(tmp_path):
    b=b"another synthetic payload"
    f=tmp_path/"f"
    f.write_bytes(b)
    md5=hashlib.md5(b,usedforsecurity=False).hexdigest()
    z=m.checksum_candidate(f,expected_source_blob="0"*40,
                            expected_official_md5=md5,expected_length=len(b))
    assert not z["identity_eligible_exact_digest_and_size"]
    assert z["official_md5_matches"] is True
    assert not z["source_blob_matches_pin"]
