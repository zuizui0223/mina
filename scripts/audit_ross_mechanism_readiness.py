#!/usr/bin/env python3
"""Fail-closed readiness audit for the Ross Island mechanism analysis.

This script never touches external or behavioral data. It checks committed
contracts/results only and reports whether the pre-outcome design is complete,
whether raw behavioral access is still locked, and what exact dependency
remains.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read(root: Path, rel: str) -> dict[str, object]:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(rel)
    return value


def audit(root: Path) -> dict[str, object]:
    gate = _read(root, "results/ROSS_ISLAND_RESIGHT_SCHEMA_GATE_RESULT_V1.json")
    state = _read(root, "results/ROSS_ISLAND_STATE_ENGINE_SYNTHETIC_RESULT_V2.json")
    choice = _read(root, "results/ROSS_ISLAND_CHOICE_ENGINE_SYNTHETIC_RESULT_V2.json")
    e2e = _read(root, "results/ROSS_ISLAND_END_TO_END_SYNTHETIC_RESULT_V1.json")
    size = _read(root, "results/ROSS_ISLAND_COLONY_SIZE_CONTROL_RESULT_V1.json")
    perf = _read(root, "results/ROSS_INDEPENDENT_PERFORMANCE_SOURCE_AUDIT_V1.json")
    chick = _read(root, "results/ROSS_MAPPPD_CHICK_COVERAGE_RESULT_V1.json")
    readme = _read(root, "results/ROSS_ISLAND_PUBLIC_README_SCHEMA_RECEIPT_V1.json")
    header = _read(root, "results/ROSS_ISLAND_EXACT_HEADER_PROPOSED_RECEIPT_V1.json")

    errors: list[str] = []
    checks: dict[str, bool] = {}

    checks["behavioral_rows_unopened"] = (
        gate.get("outcome_blind_status", {}).get("behavioral_rows_read") == 0
        and not bool(gate.get("outcome_blind_status", {}).get("settlement_outcomes_opened"))
        and not bool(gate.get("outcome_blind_status", {}).get("transition_frequencies_opened"))
        and int(state.get("execution", {}).get("real_behavioral_rows_used", -1)) == 0
        and int(choice.get("execution", {}).get("real_behavioral_rows_used", -1)) == 0
        and not bool(e2e.get("decision", {}).get("behavioral_outcomes_opened"))
    )
    checks["public_schema_scientifically_sufficient"] = bool(
        gate.get("scientific_gate_decision", {}).get(
            "schema_scientifically_sufficient_in_principle"
        )
    )
    checks["state_engine_ready"] = bool(
        state.get("decision", {}).get("canonical_state_and_event_builder_ready")
    )
    checks["choice_engine_v2_ready"] = bool(
        choice.get("decision", {}).get("choice_engine_v2_ready_before_real_data")
    )
    checks["detection_builder_ready"] = bool(
        choice.get("decision", {}).get("detection_proxy_builder_ready_before_real_data")
    )
    checks["end_to_end_ready"] = bool(
        e2e.get("decision", {}).get("full_parser_independent_pipeline_ready")
    )
    checks["size_control_viable"] = bool(
        size.get("decision", {}).get("colony_size_control_viable")
    )
    checks["external_three_colony_performance_unavailable"] = (
        perf.get("decision", {}).get("independent_three_colony_chick_state_available")
        is False
        and chick.get("decision", {}).get(
            "three_colony_independent_mapppd_chick_state_viable"
        )
        is False
    )
    checks["predeclared_fallback_retained"] = bool(
        perf.get("decision", {}).get("frozen_fallback_retained")
    )
    checks["readme_schema_verified"] = bool(
        readme.get("decision", {}).get(
            "scientific_state_reconstruction_schema_sufficient"
        )
    )
    checks["exact_header_still_blocked"] = (
        header.get("status") == "BLOCKED_NO_EXACT_HEADERS"
        and not bool(header.get("header_parser_ready"))
        and not bool(header.get("movement_analysis_unlock_candidate"))
        and gate.get("raw_access", {}).get("exact_csv_header_verified") is False
    )
    checks["movement_analysis_still_locked"] = (
        gate.get("decision", {}).get("movement_analysis_unlocked") is False
        and gate.get("raw_access", {}).get("full_behavioral_download_allowed") is False
    )
    checks["usap_auth_requirement_documented"] = bool(
        gate.get("public_schema_audit", {}).get(
            "swagger_documents_api_key_required"
        )
    )
    public_audit = gate.get("public_schema_audit", {})
    checks["anonymous_header_rejected_as_non_csv"] = bool(
        public_audit.get("anonymous_response_rejected_as_html")
        or public_audit.get("anonymous_header_non_csv")
    )

    required_preoutcome = [
        "behavioral_rows_unopened",
        "public_schema_scientifically_sufficient",
        "state_engine_ready",
        "choice_engine_v2_ready",
        "detection_builder_ready",
        "end_to_end_ready",
        "size_control_viable",
        "external_three_colony_performance_unavailable",
        "predeclared_fallback_retained",
        "readme_schema_verified",
        "usap_auth_requirement_documented",
        "anonymous_header_rejected_as_non_csv",
    ]
    for name in required_preoutcome:
        if not checks[name]:
            errors.append(f"failed_preoutcome_check:{name}")

    if not checks["exact_header_still_blocked"]:
        errors.append("exact_header_gate_not_in_expected_blocked_state")
    if not checks["movement_analysis_still_locked"]:
        errors.append("movement_gate_not_in_expected_locked_state")

    preoutcome_ready = all(checks[name] for name in required_preoutcome)
    locked_as_intended = (
        checks["exact_header_still_blocked"]
        and checks["movement_analysis_still_locked"]
    )

    return {
        "schema_version": 1,
        "audit_id": "mina-ross-island-mechanism-readiness-v1",
        "checks": checks,
        "preoutcome_design_and_engine_ready": preoutcome_ready,
        "behavioral_access_locked_as_intended": locked_as_intended,
        "movement_analysis_allowed_now": False,
        "only_external_dependency": (
            "USAP_DC_API_KEY -> exact first-line CSV header audit -> reviewed "
            "exact-header/parser receipt -> explicit movement gate unlock"
            if preoutcome_ready and locked_as_intended
            else None
        ),
        "errors": errors,
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

    if (
        not result["preoutcome_design_and_engine_ready"]
        or not result["behavioral_access_locked_as_intended"]
        or result["movement_analysis_allowed_now"]
    ):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
