#!/usr/bin/env python3
"""Guard the integrated v0.3 manuscript against claim drift."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: Path) -> dict[str, object]:
    manuscript = (root / "docs/MANUSCRIPT_INTEGRATED_V0_3.md").read_text(
        encoding="utf-8"
    )
    lower = manuscript.lower()
    contract = _load_json(
        root / "contracts/INTEGRATED_PALMER_ANTARCTIC_MANUSCRIPT_V0_3.json"
    )
    lag = _load_json(
        root / "results/PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json"
    )
    repro = _load_json(
        root / "results/PALMER_REPRO_REDISTRIBUTION_RESULT_V1.json"
    )
    paper2 = _load_json(
        root / "results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json"
    )

    checks: dict[str, bool] = {}
    checks["title_matches_contract"] = manuscript.startswith(
        "# " + str(contract["title"])
    )
    checks["late_season_state_central"] = (
        lower.count("late-season colony-wide state") >= 4
    )
    checks["fixed_specification_boundary_present"] = (
        "fixed-specification validation" in lower
        and "not as a fully outcome-blind preregistered test" in lower
    )
    checks["lag2_numbers_present"] = (
        "0.0409" in manuscript and "0.00327" in manuscript
    )
    checks["recruitment_echo_negative_present"] = (
        "−0.0422" in manuscript and "0.988" in manuscript
    )
    checks["repro_failure_present"] = (
        "0.0296" in manuscript and "0.232" in manuscript
        and "−0.0164" in manuscript and "0.629" in manuscript
    )
    checks["paper2_nonconfirmation_present"] = (
        "0.0947" in manuscript and "0.081" in manuscript
    )
    checks["state_not_place_dichotomy_rejected"] = (
        "not evidence that state matters while place does not" in lower
        and "the resulting lesson is not that state replaces place" in lower
    )
    checks["repro_not_rescued"] = (
        "failed primary endpoint prevents using that result as a rescue" in lower
    )
    checks["ross_not_current_evidence"] = (
        "ross island" not in lower
        and "no ross" not in lower
    )
    checks["no_near_significance_language"] = (
        "marginally significant" not in lower
        and "near significant" not in lower
        and "nearly significant" not in lower
    )
    checks["no_generic_repro_claim"] = (
        "generic reproductive success predicts redistribution" not in lower
    )
    checks["no_public_information_claim"] = (
        "penguins were shown to use public information" not in lower
        and "proves public-information" not in lower
    )
    checks["no_control_characters"] = (
        "\x0c" not in manuscript and "\t" not in manuscript
    )

    # Verify key source receipts, not only rendered text.
    primary_lag2 = lag["primary_lag_profile"]["lag_2"]
    checks["lag_receipt_exact"] = (
        abs(float(primary_lag2["beta"]) - 0.040890746633273245) < 1e-15
        and abs(
            float(primary_lag2["one_sided_upper_p"])
            - 0.0032699673003269967
        ) < 1e-15
        and lag["decision"][
            "confirmatory_preregistration_claim_allowed"
        ] is False
    )
    checks["repro_receipt_exact"] = (
        abs(float(repro["primary_lag1"]["beta"]) - 0.02960239689099827) < 1e-15
        and abs(
            float(repro["primary_lag1"]["one_sided_upper_p"])
            - 0.23194768052319475
        ) < 1e-15
        and repro["decision"]["independent_nest_validation_supported"] is False
    )
    checks["paper2_receipt_nonconfirmatory"] = (
        paper2["decision"]["cross_species_primary_supported"] is False
    )

    failed = [name for name, ok in checks.items() if not ok]
    return {
        "schema_version": 1,
        "audit_id": "mina-integrated-manuscript-v0.3-guard-v1",
        "checks": checks,
        "failed_checks": failed,
        "all_checks_pass": not failed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = check(args.repo_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_checks_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
