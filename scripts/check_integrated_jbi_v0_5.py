#!/usr/bin/env python3
"""Validate current Journal of Biogeography v0.5 submission package."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _words(text: str) -> int:
    cleaned = re.sub(r"[#*_\\$\\{}\\[\\]()|<>]", " ", text)
    return len(cleaned.split())


def check(root: Path) -> dict[str, object]:
    manuscript_path = root / "docs/MANUSCRIPT_INTEGRATED_JBI_V0_5.md"
    manuscript = manuscript_path.read_text(encoding="utf-8")
    lower = manuscript.lower()
    package = _load(
        root / "contracts/INTEGRATED_JBI_SUBMISSION_PACKAGE_V0_5.json"
    )
    freeze = _load(
        root / "contracts/INTEGRATED_JBI_ANALYSIS_FREEZE_V0_5.json"
    )

    lines = manuscript.splitlines()
    title = lines[0].removeprefix("# ").strip()
    running = ""
    for line in lines[:12]:
        if line.startswith("**Running title:**"):
            running = line.split(":", 1)[1].strip()
            break

    abstract_start = manuscript.index("## Abstract")
    keyword_start = manuscript.index("**Keywords:**")
    intro_start = manuscript.index("## Introduction")
    data_start = manuscript.index("## Data Accessibility Statement")
    abstract = manuscript[abstract_start:keyword_start]
    main = manuscript[intro_start:data_start]

    counts = {
        "title_characters": len(title),
        "running_title_characters": len(running),
        "abstract_words": _words(abstract),
        "main_text_words": _words(main),
    }
    checks: dict[str, bool] = {
        "title_limit_115": counts["title_characters"] <= 115,
        "running_title_limit_40": counts["running_title_characters"] < 40,
        "abstract_limit_300": counts["abstract_words"] <= 300,
        "main_text_limit_6000": counts["main_text_words"] <= 6000,
    }

    for heading in (
        "**Aim:**",
        "**Location:**",
        "**Taxon:**",
        "**Methods:**",
        "**Results:**",
        "**Main conclusions:**",
    ):
        name = heading.strip("*:").lower().replace(" ", "_")
        checks[f"abstract_{name}"] = heading in abstract

    keyword_line = next(
        (line for line in lines if line.startswith("**Keywords:**")), ""
    )
    keyword_text = keyword_line.split(":", 1)[1].strip().strip("*").strip()
    keywords = [x.strip() for x in keyword_text.split(",") if x.strip()]
    checks["keywords_6_to_10"] = 6 <= len(keywords) <= 10
    checks["keywords_alphabetized"] = keywords == sorted(
        keywords, key=lambda x: x.casefold()
    )
    checks["required_main_headers"] = all(
        h in manuscript
        for h in (
            "## Introduction",
            "## Materials and Methods",
            "## Results",
            "## Discussion",
            "## Data Accessibility Statement",
        )
    )
    checks["double_anonymous_main"] = (
        "## Acknowledgements" not in manuscript
        and "## Author contributions" not in manuscript
        and "## Conflict of interest statement" not in manuscript
    )
    checks["current_scientific_story"] = (
        "late-season colony-wide state" in lower
        and "mean chicks reaching crèche per monitored nest" in lower
        and "0.232" in manuscript
        and "signy" not in lower
    )
    checks["macro_precedent_boundary"] = all(
        key in manuscript
        for key in ("@ainley1995", "@santora2020", "@lyver2014", "@iles2020")
    )
    checks["part2_scoped_to_temporal_coupling"] = (
        "site-specific coupling to demographic variation shared through time"
        in lower
        and "colony-size and spatial-clustering responses" in lower
    )
    checks["prior_geography_not_refuted"] = (
        "does not overturn earlier geographic evidence" in lower
        and "not a general failure of geographic or environmental explanation"
        in lower
    )
    checks["public_information_not_claimed"] = (
        "not as the demonstrated mechanism" in lower
        and "our lag-1 coefficient therefore has little standalone mechanistic novelty"
        in lower
    )
    checks["part2_nonconfirmatory"] = (
        "0.0947" in manuscript
        and "directionally concordant but non-confirmatory" in lower
    )
    checks["radius_not_scale_discovery"] = (
        "0.081" in manuscript
        and "rather than biological scale dependence" in lower
    )
    checks["ross_unpublished_absent"] = (
        "no ross movement result is part of the present evidentiary chain" in lower
        and "our ross" not in lower
        and "ross coefficient" not in lower
    )
    prohibited = (
        "marginally significant",
        "near significant",
        "nearly significant",
        "dynamic state outperforms static architecture",
        "state replaces place",
        "static geography does not predict penguin demography",
        "first antarctic-wide test of penguin geography",
    )
    checks["prohibited_language_absent"] = not any(x in lower for x in prohibited)
    checks["package_points_to_current_main"] = (
        package["anonymous_review_files"]["main_manuscript"]
        == "docs/MANUSCRIPT_INTEGRATED_JBI_V0_5.md"
        and package["anonymous_review_files"]["supporting_information"]
        == "docs/SUPPORTING_INFORMATION_JBI_INTEGRATED_V0_5.md"
        and package["anonymous_review_files"]["figure_captions_source"]
        == "docs/INTEGRATED_FIGURE_CAPTIONS_JBI_V0_5.md"
        and package["scientific_source_of_truth"]["integrated_manuscript"]
        == "docs/MANUSCRIPT_INTEGRATED_V0_5.md"
    )
    checks["analysis_freeze_closed"] = (
        freeze["status"] == "all_preplanned_validation_routes_closed"
        and freeze["new_analysis_after_freeze_allowed"] is False
    )

    lag = _load(
        root / "results/PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json"
    )
    repro = _load(root / "results/PALMER_REPRO_REDISTRIBUTION_RESULT_V1.json")
    paper2 = _load(root / "results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json")
    humpop = _load(root / "results/PALMER_HUMPOP_ARRIVAL_RESULT_V1.json")
    lag2 = lag["primary_lag_profile"]["lag_2"]
    checks["frozen_lag2"] = (
        abs(float(lag2["beta"]) - 0.040890746633273245) < 1e-15
        and abs(float(lag2["one_sided_upper_p"]) - 0.0032699673003269967)
        < 1e-15
    )
    checks["frozen_repro"] = (
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
    hgate = humpop["primary_information_gate"]
    hdecision = humpop["decision"]
    checks["humpop_information_gate_closed"] = (
        humpop["status"] == "STOP_insufficient_information"
        and hgate["n_panel_rows_after_minimum_three_colonies_per_predictor_season"] == 69
        and hgate["n_predictor_seasons"] == 18
        and hgate["required_minimum_panel_rows"] == 100
        and hdecision["primary_model_fit"] is False
        and hdecision["permutation_test_run"] is False
        and hdecision["performance_arrival_association_estimated"] is False
        and hdecision["posthoc_threshold_rescue_allowed"] is False
    )
    checks["humpop_boundary_in_main_text"] = (
        "69 matched colony-seasons across 18 predictor seasons" in lower
        and "required 100" in lower
        and "no arrival coefficient" in lower
    )

    failed = [name for name, ok in checks.items() if not ok]
    return {
        "schema_version": 1,
        "audit_id": "mina-integrated-jbi-v0.5-validation-v1",
        "counts": counts,
        "keywords": keywords,
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
