#!/usr/bin/env python3
"""Preflight audit for Ross Island mechanism execution readiness.

This audit is intentionally file-only. It opens no USAP-DC behavioral source.
It requires both:
1) the parser-independent scientific machinery is validated; and
2) the real-data access gate remains locked until exact headers are frozen.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read(root: Path, relative: str) -> dict[str, object]:
    path = root / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return json.loads(path.read_text(encoding="utf-8"))


def audit(root: Path) -> dict[str, object]:
    schema = _read(
        root, "results/ROSS_ISLAND_RESIGHT_SCHEMA_GATE_RESULT_V1.json"
    )
    header = _read(
        root, "results/ROSS_ISLAND_EXACT_HEADER_PROPOSED_RECEIPT_V1.json"
    )
    choice = _read(
        root, "results/ROSS_ISLAND_CHOICE_ENGINE_SYNTHETIC_RESULT_V2.json"
    )
    state = _read(
        root, "results/ROSS_ISLAND_STATE_ENGINE_SYNTHETIC_RESULT_V2.json"
    )
    end_to_end = _read(
        root, "results/ROSS_ISLAND_END_TO_END_SYNTHETIC_RESULT_V1.json"
    )
    performance = _read(
        root, "results/ROSS_INDEPENDENT_PERFORMANCE_SOURCE_AUDIT_V1.json"
    )
    size = _read(
        root, "results/ROSS_ISLAND_COLONY_SIZE_CONTROL_RESULT_V1.json"
    )

    checks: dict[str, bool] = {
        "behavioral_rows_still_zero": (
            schema["outcome_blind_status"]["behavioral_rows_read"] == 0
        ),
        "settlement_outcomes_unopened": (
            schema["outcome_blind_status"]["settlement_outcomes_opened"] is False
        ),
        "exact_header_not_verified": (
            schema["raw_access"]["exact_csv_header_verified"] is False
        ),
        "movement_analysis_locked": (
            schema["decision"]["movement_analysis_unlocked"] is False
        ),
        "official_api_key_block_recorded": (
            schema["public_schema_audit"]["swagger_documents_api_key_required"]
            is True
        ),
        "anonymous_html_not_accepted": (
            schema["public_schema_audit"]["anonymous_response_rejected_as_html"]
            is True
        ),
        "header_receipt_blocked": (
            header["status"] == "BLOCKED_NO_EXACT_HEADERS"
            and header["header_parser_ready"] is False
            and header["movement_analysis_unlock_candidate"] is False
        ),
        "choice_v2_synthetic_ready": (
            choice["decision"]["choice_engine_v2_ready_before_real_data"] is True
            and choice["execution"]["real_behavioral_rows_used"] == 0
        ),
        "detection_builder_ready": (
            choice["decision"]["detection_proxy_builder_ready_before_real_data"]
            is True
        ),
        "state_engine_ready": (
            state["decision"]["canonical_state_and_event_builder_ready"] is True
            and state["execution"]["real_behavioral_rows_used"] == 0
        ),
        "end_to_end_synthetic_ready": (
            end_to_end["decision"]["full_parser_independent_pipeline_ready"]
            is True
            and end_to_end["execution"]["real_behavioral_rows_used"] == 0
        ),
        "external_three_colony_performance_unavailable": (
            performance["decision"][
                "independent_three_colony_chick_state_available"
            ]
            is False
        ),
        "two_colony_rescue_forbidden": (
            performance["decision"]["use_two_colony_rescue"] is False
        ),
        "predeclared_performance_fallback_retained": (
            "banded-breeder chick-presence"
            in performance["decision"]["frozen_fallback_retained"]
        ),
        "colony_size_control_viable": (
            size["decision"]["colony_size_control_viable"] is True
        ),
        "no_imputation_needed_for_size_control": (
            size["decision"]["imputation_required"] is False
        ),
    }

    failed = [name for name, ok in checks.items() if not ok]
    return {
        "schema_version": 1,
        "audit_id": "mina-ross-island-execution-readiness-v1",
        "behavioral_rows_read": 0,
        "checks": checks,
        "failed_checks": failed,
        "all_checks_pass": not failed,
        "scientific_pipeline_status": (
            "READY_PARSER_INDEPENDENT" if not failed else "NOT_READY"
        ),
        "real_data_status": "LOCKED_PENDING_EXACT_HEADERS",
        "next_external_dependency": (
            "USAP_DC_API_KEY -> schema-only exact-header audit -> manual parser "
            "receipt freeze"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = audit(args.repo_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
