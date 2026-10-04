from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER_CSV = ROOT / "data" / "EVIDENCE_LEDGER_66_V1.csv"
CONTRACT = ROOT / "contracts" / "EVIDENCE_LEDGER_66_V1.json"
RESULTS = ROOT / "results"


def _rows():
    with LEDGER_CSV.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_ledger_covers_every_main_result_exactly_once():
    rows = _rows()
    result_files = sorted(p.name for p in RESULTS.glob("*.json"))
    ledger_files = sorted(r["result_file"] for r in rows)
    assert len(result_files) == 66
    assert len(rows) == 66
    assert ledger_files == result_files


def test_tiers_and_counts_are_frozen():
    rows = _rows()
    counts = {}
    for row in rows:
        tier = row["evidence_tier"]
        assert tier in {"A", "B", "C", "D", "N"}
        counts[tier] = counts.get(tier, 0) + 1
    assert counts == {"A": 3, "B": 18, "C": 15, "D": 4, "N": 26}


def test_a_tier_is_only_replicated_concentration():
    rows = [r for r in _rows() if r["evidence_tier"] == "A"]
    assert {r["result_file"] for r in rows} == {
        "SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
        "SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
        "SIGNY_CONCENTRATION_REPLICATION_RESULT_V2.json",
    }
    assert {r["independence_group"] for r in rows} == {
        "Signy Adelie concentration",
        "Signy chinstrap concentration",
    }


def test_non_evidence_records_cannot_be_counted_as_ecological_support():
    rows = _rows()
    assert all(
        r["manuscript_use"] not in {"main confirmatory evidence", "discovery supporting main claim"}
        for r in rows
        if r["evidence_tier"] == "N"
    )


def test_contract_matches_csv():
    rows = _rows()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["source_main_sha"] == "7764523c5f1e536b86084de8583cdd6262ee8fa7"
    assert len(contract["rows"]) == len(rows) == 66
    assert contract["tier_counts"] == {"A": 3, "B": 18, "C": 15, "D": 4, "N": 26}
