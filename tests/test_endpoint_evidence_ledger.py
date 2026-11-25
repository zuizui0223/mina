from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "ENDPOINT_EVIDENCE_LEDGER_V1.csv"
CONTRACT = ROOT / "contracts" / "ENDPOINT_EVIDENCE_LEDGER_V1.json"


def load_rows():
    with LEDGER.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_ledger_covers_every_main_result_receipt_once():
    rows = load_rows()
    ledger_paths = [row["result_path"] for row in rows]
    repo_paths = sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ROOT / "results").glob("*.json")
    )

    assert len(rows) == 66
    assert len(set(ledger_paths)) == 66
    assert sorted(ledger_paths) == repo_paths


def test_tier_counts_match_frozen_contract():
    rows = load_rows()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    observed = Counter(row["tier"] for row in rows)
    expected = {
        tier: spec["count"]
        for tier, spec in contract["tiers"].items()
    }
    assert dict(observed) == expected


def test_confirmatory_tier_is_only_the_two_prospective_signy_replications():
    rows = load_rows()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    observed = sorted(
        row["result_path"] for row in rows if row["tier"] == "C1"
    )
    assert observed == sorted(contract["c1_receipts"])


def test_design_audits_never_receive_claim_weight():
    rows = load_rows()
    for row in rows:
        if row["tier"] == "D0":
            assert row["claim_weight"] == "none", row["result_path"]


def test_primary_palmer_concentration_is_discovery_not_c1():
    rows = {row["result_path"]: row for row in load_rows()}
    path = "results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json"
    assert rows[path]["tier"] == "C2"
    assert rows[path]["claim_weight"] == "primary_discovery"


def test_negative_primary_families_are_scope_limiting_not_failures_of_audit():
    rows = {row["result_path"]: row for row in load_rows()}
    for path in (
        "results/PALMER_SEAICE_HABITAT_MECHANISM_RESULT_V1.json",
        "results/PALMER_SEAICE_TIMESCALE_SEPARATION_RESULT_V1.json",
        "results/PALMER_WEATHER_X_HABITAT_MECHANISM_RESULT_V2.json",
        "results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json",
        "results/SIGNY_PERFORMANCE_REDISTRIBUTION_REPLICATION_RESULT_V1.json",
    ):
        assert rows[path]["tier"] == "C3"


def test_mark_resight_is_the_only_result_receipt_data_stop():
    rows = load_rows()
    stopped = [row for row in rows if row["tier"] == "C4"]
    assert len(stopped) == 1
    assert stopped[0]["result_path"] == (
        "results/PALMER_MARK_RESIGHT_DATA_AUDIT_RESULT_V1.json"
    )
