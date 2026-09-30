from __future__ import annotations

from mina_ross_guard_loader import load_guard_module


def test_locked_receipt_is_not_unlocked():
    mod = load_guard_module()
    receipt = {
        "outcome_blind_status": {"behavioral_rows_read": 0},
        "raw_access": {"exact_csv_header_verified": False},
        "decision": {"movement_analysis_unlocked": False},
    }
    unlocked, reasons = mod.is_unlocked(receipt)
    assert not unlocked
    assert "exact_csv_header_not_verified" in reasons
    assert "movement_analysis_not_unlocked" in reasons


def test_only_fully_unlocked_receipt_passes():
    mod = load_guard_module()
    receipt = {
        "outcome_blind_status": {"behavioral_rows_read": 0},
        "raw_access": {"exact_csv_header_verified": True},
        "decision": {"movement_analysis_unlocked": True},
    }
    unlocked, reasons = mod.is_unlocked(receipt)
    assert unlocked
    assert reasons == []


def test_behavioral_access_record_prevents_unlock():
    mod = load_guard_module()
    receipt = {
        "outcome_blind_status": {"behavioral_rows_read": 1},
        "raw_access": {"exact_csv_header_verified": True},
        "decision": {"movement_analysis_unlocked": True},
    }
    unlocked, reasons = mod.is_unlocked(receipt)
    assert not unlocked
    assert "receipt_already_records_behavioral_row_access" in reasons
