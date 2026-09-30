#!/usr/bin/env python3
"""Guard integrated v0.4 literature-gap revision against novelty drift."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_KEYS = {
    "danchin1998",
    "boulinier2008",
    "meheust2024",
    "cimino2025",
    "dugger2026",
}


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: Path) -> dict[str, object]:
    manuscript_path = root / "docs/MANUSCRIPT_INTEGRATED_V0_4.md"
    refs_path = root / "docs/REFERENCES_V7.bib"
    contract = _load_json(
        root / "contracts/INTEGRATED_PALMER_ANTARCTIC_MANUSCRIPT_V0_4.json"
    )
    manuscript = manuscript_path.read_text(encoding="utf-8")
    refs = refs_path.read_text(encoding="utf-8")
    lower = manuscript.lower()

    checks: dict[str, bool] = {}

    checks["version_label"] = "draft v0.4" in lower
    checks["title_matches_contract"] = manuscript.startswith(
        "# " + str(contract["title"])
    )
    checks["required_reference_keys_present"] = all(
        f"{{{key}," in refs for key in REQUIRED_KEYS
    )
    checks["required_citations_used"] = all(
        f"@{key}" in manuscript for key in REQUIRED_KEYS
    )

    checks["prior_public_information_precedent_explicit"] = (
        "performance-based breeding-habitat selection is not itself a new hypothesis"
        in lower
        and "black-legged kittiwakes" in lower
    )
    checks["adelie_one_year_precedent_explicit"] = (
        "one-year-lagged growth" in lower
        and "@meheust2024" in manuscript
        and "neither mechanistically diagnostic nor novel on its own" in lower
    )
    checks["lag1_novelty_ceiling"] = (
        "our lag-1 coefficient therefore has little standalone mechanistic novelty"
        in lower
    )
    checks["novel_inference_explicit"] = (
        "specific late-season colony-wide state carries short-lived demographic history"
        in lower
        and "not interchangeable with generic nest productivity" in lower
    )
    checks["public_information_not_claimed"] = (
        "public information as a motivated hypothesis with strong precedent" in lower
        and "not as the demonstrated mechanism" in lower
    )
    checks["physical_place_retained"] = (
        "snow, topography and geomorphology structure subcolony persistence" in lower
        and "not evidence that state matters while place does not" in lower
    )
    checks["ross_only_published_context"] = (
        "@dugger2026" in manuscript
        and "no ross movement result is part of the present evidentiary chain" in lower
    )
    checks["ross_unpublished_results_absent"] = (
        "ross island confirms the mechanism" not in lower
        and "our ross" not in lower
        and "ross coefficient" not in lower
        and "ross p =" not in lower
    )
    checks["part2_nonconfirmatory_retained"] = (
        "0.0947" in manuscript
        and "directionally concordant but non-confirmatory" in lower
    )
    checks["cross_scale_not_head_to_head"] = (
        "not a head-to-head predictive model comparison" in lower
        and "evidentiary rather than a comparison of effect sizes" in lower
        and "different response definitions, spatial grains and species panels" in lower
    )
    checks["no_dynamic_outperformance_claim"] = (
        "dynamic state outperforms static architecture" not in lower
    )
    checks["repro_nonreplication_retained"] = (
        "mean chicks reaching crèche per monitored nest" in lower
        and "0.232" in manuscript
        and "not generic nest reproductive success" in lower
    )
    checks["no_near_significance_language"] = not any(
        phrase in lower
        for phrase in (
            "marginally significant",
            "near significant",
            "nearly significant",
        )
    )

    # Frozen numerical receipts must still agree with v0.3.
    lag = _load_json(
        root / "results/PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json"
    )
    repro = _load_json(
        root / "results/PALMER_REPRO_REDISTRIBUTION_RESULT_V1.json"
    )
    paper2 = _load_json(
        root / "results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json"
    )
    lag2 = lag["primary_lag_profile"]["lag_2"]
    checks["frozen_lag2_unchanged"] = (
        abs(float(lag2["beta"]) - 0.040890746633273245) < 1e-15
        and abs(float(lag2["one_sided_upper_p"]) - 0.0032699673003269967) < 1e-15
    )
    checks["frozen_repro_unchanged"] = (
        abs(float(repro["primary_lag1"]["beta"]) - 0.02960239689099827) < 1e-15
        and abs(
            float(repro["primary_lag1"]["one_sided_upper_p"])
            - 0.23194768052319475
        )
        < 1e-15
    )
    checks["frozen_paper2_nonconfirmatory"] = (
        paper2["decision"]["frozen_primary_permutation_test_rejects_at_0_05"]
        is False
    )

    failed = [name for name, ok in checks.items() if not ok]
    return {
        "schema_version": 1,
        "audit_id": "mina-integrated-manuscript-v0.4-literature-gap-guard-v1",
        "checks": checks,
        "failed_checks": failed,
        "all_checks_pass": not failed,
        "scientific_results_changed": False,
        "figure_data_changed": False,
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
