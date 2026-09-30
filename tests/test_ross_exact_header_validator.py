from __future__ import annotations

import pytest

from mina_ross_header_loader import load_header_module


def test_missing_headers_stays_blocked():
    mod = load_header_module()
    result = mod.validate({
        "behavioral_rows_read": 0,
        "resight_header": None,
        "banding_header": None,
    })
    assert result["status"] == "BLOCKED_NO_EXACT_HEADERS"
    assert result["header_parser_ready"] is False
    assert result["movement_analysis_unlock_candidate"] is False


def test_required_header_subset_creates_proposed_receipt_only():
    mod = load_header_module()
    result = mod.validate({
        "behavioral_rows_read": 0,
        "resight_header": "Band,Date,Colony,Eggs,Chicks,Sex,Notes",
        "banding_header": "Low,High,Colony,Season,Notes",
    })
    assert result["status"] == "HEADER_VALIDATED_PROPOSED"
    assert result["header_parser_ready"] is True
    assert result["movement_analysis_unlock_candidate"] is True
    assert result["manual_freeze_required_before_full_download"] is True


def test_missing_required_column_is_incompatible():
    mod = load_header_module()
    result = mod.validate({
        "behavioral_rows_read": 0,
        "resight_header": "Band,Date,Colony,Eggs",
        "banding_header": "Low,High,Colony,Season",
    })
    assert result["status"] == "HEADER_INCOMPATIBLE"
    assert result["header_parser_ready"] is False
    assert "Chicks" in result["missing_resight_required"]


def test_behavioral_row_access_is_rejected():
    mod = load_header_module()
    with pytest.raises(ValueError, match="not outcome-blind"):
        mod.validate({
            "behavioral_rows_read": 1,
            "resight_header": "Band,Date,Colony,Eggs,Chicks",
            "banding_header": "Low,High,Colony,Season",
        })
