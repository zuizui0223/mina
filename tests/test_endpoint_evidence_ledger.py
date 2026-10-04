from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "contracts" / "ENDPOINT_EVIDENCE_LEDGER_V1.json"
RESULTS = ROOT / "results"


def load():
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_ledger_is_exactly_the_frozen_66_main_results_snapshot():
    ledger = load()
    rows = ledger["rows"]
    files = [row["file"] for row in rows]

    assert ledger["source"]["commit"] == "7764523c5f1e536b86084de8583cdd6262ee8fa7"
    assert ledger["source"]["result_file_count"] == 66
    assert len(rows) == 66
    assert len(set(files)) == 66
    assert all((RESULTS / name).exists() for name in files)


def test_evidence_tier_counts_are_locked():
    ledger = load()
    counts = Counter(row["tier"] for row in ledger["rows"])
    assert counts == {
        "A0": 31,
        "E1": 3,
        "E2": 17,
        "E3": 14,
        "E4": 1,
    }
    assert ledger["counts"] == dict(counts)


def test_confirmatory_evidence_occurs_only_at_within_system_spatial_layer():
    ledger = load()
    e1 = [row for row in ledger["rows"] if row["tier"] == "E1"]
    assert len(e1) == 3
    assert {row["layer"] for row in e1} == {"within_system_spatial"}
    assert {row["file"] for row in e1} == {
        "SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
        "SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
        "SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json",
    }


def test_static_place_has_only_scope_limiting_ecological_outcomes():
    ledger = load()
    rows = [row for row in ledger["rows"] if row["layer"] == "static_place"]
    ecological = [row for row in rows if row["tier"] != "A0"]
    assert ecological
    assert {row["tier"] for row in ecological} == {"E3"}


def test_regional_direction_has_context_plus_falsification_but_no_confirmation():
    ledger = load()
    tiers = Counter(
        row["tier"] for row in ledger["rows"]
        if row["layer"] == "regional_direction"
    )
    assert tiers == {"E2": 2, "E3": 3}


def test_individual_process_boundary_is_data_stopped():
    ledger = load()
    e4 = [row for row in ledger["rows"] if row["tier"] == "E4"]
    assert len(e4) == 1
    assert e4[0]["file"] == "PALMER_MARK_RESIGHT_DATA_AUDIT_RESULT_V1.json"
    assert e4[0]["layer"] == "individual_process_boundary"


def test_ecological_and_auxiliary_counts_are_separate():
    ledger = load()
    assert ledger["ecological_outcome_file_count"] == 35
    assert ledger["auxiliary_file_count"] == 31


def test_non_independent_families_are_explicit():
    ledger = load()
    families = {
        item["family_id"]: item
        for item in ledger["non_independent_evidence_families"]
    }
    assert "signy_adelie_concentration" in families
    assert set(families["signy_adelie_concentration"]["files"]) == {
        "SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
        "SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json",
        "SIGNY_CONCENTRATION_QUALITY_AUDIT_V1.json",
    }
    assert len(families["palmer_neff_growth_association"]["files"]) == 6
    assert len(families["paper2_static_place_architecture"]["files"]) == 7
