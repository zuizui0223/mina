from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "EVIDENCE_LEDGER_66_ENDPOINTS_V1.csv"
CONTRACT = ROOT / "contracts" / "EVIDENCE_LEDGER_66_ENDPOINTS_V1.json"
DOC = ROOT / "docs" / "EVIDENCE_LEDGER_66_ENDPOINTS_V1.md"


def rows():
    with CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_ledger_has_exactly_66_unique_frozen_source_files():
    data = rows()
    assert len(data) == 66
    assert [int(r["source_order"]) for r in data] == list(range(1, 67))
    files = [r["source_file"] for r in data]
    assert len(files) == len(set(files)) == 66


def test_evidence_class_counts_are_frozen():
    data = rows()
    counts = Counter(r["evidence_class"][0] for r in data)
    assert counts == {"A": 2, "B": 21, "C": 14, "D": 21, "E": 8}

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["source_snapshot"]["sha"] == "7764523c5f1e536b86084de8583cdd6262ee8fa7"
    assert contract["source_snapshot"]["expected_endpoint_files"] == 66
    assert contract["expected_class_counts"] == {
        "A": 2,
        "B": 21,
        "C": 14,
        "D": 21,
        "E": 8,
    }


def test_only_two_positive_confirmatory_replication_units_exist():
    data = rows()
    confirmatory = [r for r in data if r["evidence_class"].startswith("A_")]
    assert [r["source_file"] for r in confirmatory] == [
        "SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
        "SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
    ]
    assert all(r["core_claim_unit"] == "replication" for r in confirmatory)


def test_palmer_is_discovery_and_strict_signy_is_not_third_vote():
    data = {r["source_file"]: r for r in rows()}
    palmer = data["PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json"]
    strict_signy = data["SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json"]

    assert palmer["evidence_class"].startswith("B_")
    assert palmer["core_claim_unit"] == "discovery"
    assert strict_signy["evidence_class"].startswith("B_")
    assert strict_signy["core_claim_unit"] == "none"
    assert strict_signy["outcome"] == "nested_robustness"


def test_static_place_has_no_class_a_evidence():
    data = rows()
    static_place = [r for r in data if r["story_layer"] == "static_place"]
    assert len(static_place) == 28
    assert not any(r["evidence_class"].startswith("A_") for r in static_place)


def test_only_within_configuration_contains_class_a_evidence():
    data = rows()
    class_a_layers = {
        r["story_layer"]
        for r in data
        if r["evidence_class"].startswith("A_")
    }
    assert class_a_layers == {"within_configuration"}


def test_ledger_doc_states_anti_double_counting_rule():
    text = DOC.read_text(encoding="utf-8")
    assert "only positive **class-A replication units**" in text
    assert "must not be counted as another independent replication" in text
    assert "No manuscript sentence should convert the number of files into an apparent replication count." in text
