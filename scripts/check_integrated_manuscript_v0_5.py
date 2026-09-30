#!/usr/bin/env python3
"""Guard integrated v0.5 against Antarctic macroecology novelty drift."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_KEYS = {
    "ainley1995",
    "santora2020",
    "lyver2014",
    "iles2020",
    "danchin1998",
    "boulinier2008",
    "meheust2024",
    "cimino2025",
    "dugger2026",
}


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: Path) -> dict[str, object]:
    manuscript = (root / "docs/MANUSCRIPT_INTEGRATED_V0_5.md").read_text(
        encoding="utf-8"
    )
    refs = (root / "docs/REFERENCES_V8.bib").read_text(encoding="utf-8")
    contract = _load(
        root / "contracts/INTEGRATED_PALMER_ANTARCTIC_MANUSCRIPT_V0_5.json"
    )
    lower = manuscript.lower()

    checks: dict[str, bool] = {}
    checks["version_label"] = "draft v0.5" in lower
    checks["title_matches_contract"] = manuscript.startswith(
        "# " + str(contract["title"])
    )
    checks["required_reference_keys_present"] = all(
        f"{{{key}," in refs for key in REQUIRED_KEYS
    )
    checks["required_citations_used"] = all(
        f"@{key}" in manuscript for key in REQUIRED_KEYS
    )

    checks["ainley_spatial_precedent"] = (
        "@ainley1995" in manuscript
        and "colony size" in lower
        and "neighbouring colony" in lower
    )
    checks["santora_macro_precedent"] = (
        "@santora2020" in manuscript
        and "colony size, clustering and distribution" in lower
        and "polynyas" in lower
        and "submarine canyons" in lower
    )
    checks["lyver_synchrony_precedent"] = (
        "@lyver2014" in manuscript
        and "strong synchrony" in lower
    )
    checks["iles_multiscale_precedent"] = (
        "@iles2020" in manuscript
        and "multidecadal" in lower
        and "annual sea-ice anomalies" in lower
    )
    checks["part2_response_is_temporal_coupling"] = (
        "site-specific coupling to demographic variation shared through time"
        in lower
        and "this response differs from the colony-size and spatial-clustering responses"
        in lower
    )
    checks["not_claiming_first_geographic_test"] = (
        "neither geographic structuring nor temporal synchrony is novel here"
        in lower
    )
    checks["prior_geography_not_refuted"] = (
        "does not overturn earlier evidence that antarctic penguin geography is structured"
        in lower
        and "specific to that latter response" in lower
    )
    checks["title_scoped_to_temporal_coupling"] = (
        "temporal demographic coupling in antarctic penguins" in lower.splitlines()[0]
    )

    # Retain the v0.4 novelty/public-information ceiling.
    checks["public_information_precedent_retained"] = (
        "performance-based breeding-habitat selection is not itself a new hypothesis"
        in lower
        and "@meheust2024" in manuscript
    )
    checks["lag1_novelty_ceiling_retained"] = (
        "our lag-1 coefficient therefore has little standalone mechanistic novelty"
        in lower
    )
    checks["repro_nonreplication_retained"] = (
        "mean chicks reaching crèche per monitored nest" in lower
        and "0.232" in manuscript
        and "not generic nest reproductive success" in lower
    )
    checks["part2_nonconfirmatory_retained"] = (
        "0.0947" in manuscript
        and "directionally concordant but non-confirmatory" in lower
    )
    checks["cross_scale_not_head_to_head"] = (
        "not a head-to-head predictive model comparison" in lower
        and "different response definitions, spatial grains and species panels" in lower
    )
    checks["ross_unpublished_absent"] = (
        "no ross movement result is part of the present evidentiary chain" in lower
        and "ross island confirms the mechanism" not in lower
        and "our ross" not in lower
        and "ross coefficient" not in lower
        and "ross p =" not in lower
    )

    prohibited = [
        "first antarctic-wide test of penguin geography",
        "static geography does not predict penguin demography",
        "geography is unimportant",
        "habitat does not explain penguin populations",
        "synchrony is newly discovered here",
        "dynamic state outperforms static architecture",
        "state replaces place",
        "marginally significant",
        "near significant",
        "nearly significant",
    ]
    checks["prohibited_language_absent"] = not any(x in lower for x in prohibited)

    # Frozen numerical decisions must stay unchanged.
    lag = _load(
        root / "results/PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json"
    )
    repro = _load(root / "results/PALMER_REPRO_REDISTRIBUTION_RESULT_V1.json")
    paper2 = _load(root / "results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json")
    lag2 = lag["primary_lag_profile"]["lag_2"]
    checks["frozen_lag2_unchanged"] = (
        abs(float(lag2["beta"]) - 0.040890746633273245) < 1e-15
        and abs(
            float(lag2["one_sided_upper_p"]) - 0.0032699673003269967
        ) < 1e-15
    )
    checks["frozen_repro_unchanged"] = (
        abs(float(repro["primary_lag1"]["beta"]) - 0.02960239689099827)
        < 1e-15
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
        "audit_id": "mina-integrated-manuscript-v0.5-prior-macroecology-guard-v1",
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
