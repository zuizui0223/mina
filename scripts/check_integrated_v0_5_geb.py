#!/usr/bin/env python3
"""Guard the GEB-oriented v0.5 manuscript against format and claim drift."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ABSTRACT_HEADINGS = [
    "Aim",
    "Location",
    "Time period",
    "Major taxa studied",
    "Methods",
    "Results",
    "Main conclusions",
]


def words(text: str) -> int:
    text = re.sub(r"\$[\s\S]*?\$", " ", text)
    text = re.sub(r"[@#*\x60>|_\[\]\(\){}\\]", " ", text)
    return len([x for x in re.split(r"\s+", text) if x])


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: Path) -> dict[str, object]:
    manuscript = (
        root / "docs/MANUSCRIPT_INTEGRATED_V0_5_GEB.md"
    ).read_text(encoding="utf-8")
    lower = manuscript.lower()
    contract = read_json(
        root / "contracts/INTEGRATED_V0_5_GEB_SUBMISSION_V1.json"
    )

    abstract = manuscript.split("## Abstract", 1)[1].split(
        "## Introduction", 1
    )[0]
    main = manuscript.split("## Introduction", 1)[1].split(
        "## Data and code availability", 1
    )[0]

    running_match = re.search(
        r"\*\*Running title:\*\*\s*(.+)", manuscript
    )
    running = running_match.group(1).strip() if running_match else ""

    keyword_match = re.search(
        r"\*\*Keywords:\*\*\s*(.+?)\n\n## Introduction",
        manuscript,
        flags=re.S,
    )
    keywords = (
        [x.strip() for x in keyword_match.group(1).split(";")]
        if keyword_match
        else []
    )

    checks: dict[str, bool] = {}
    checks["title_matches_contract"] = manuscript.startswith(
        "# " + str(contract["title"])
    )
    checks["geb_version_label"] = "v0.5 — geb submission revision" in lower
    checks["running_title_present"] = bool(running)
    checks["running_title_lt_40_chars"] = 0 < len(running) < 40
    checks["abstract_le_300"] = words(abstract) <= 300
    positions = [
        abstract.find(f"**{heading}.**") for heading in ABSTRACT_HEADINGS
    ]
    checks["abstract_headings_in_order"] = (
        all(pos >= 0 for pos in positions)
        and positions == sorted(positions)
    )
    checks["main_body_le_5200"] = words(main) <= 5200
    checks["main_body_not_overcompressed"] = words(main) >= 3000
    checks["keyword_count_6_10"] = 6 <= len(keywords) <= 10
    checks["keywords_alphabetical"] = (
        [x.casefold() for x in keywords]
        == sorted(x.casefold() for x in keywords)
    )

    checks["lag2_boundary_retained"] = (
        "0.0409" in manuscript
        and "0.00327" in manuscript
        and "fixed-specification validation" in lower
    )
    checks["repro_failure_retained"] = (
        "0.0296" in manuscript
        and "0.232" in manuscript
        and "did not replicate" in lower
    )
    checks["paper2_nonconfirmatory_retained"] = (
        "−0.318" in manuscript
        and "0.0947" in manuscript
        and "non-confirmatory" in lower
    )
    checks["radius_boundary_retained"] = (
        "0.0810" in manuscript
        and "not as evidence for biological scale dependence" in lower
    )
    checks["cross_scale_not_head_to_head"] = (
        "not a head-to-head predictive model comparison" in lower
        and "evidentiary asymmetry" in lower
    )
    checks["public_information_not_claimed"] = (
        "public information is thus a motivated hypothesis with strong precedent, not the demonstrated mechanism"
        in lower
    )
    checks["state_not_place"] = (
        "does not imply that state matters while place does not" in lower
    )
    checks["ross_current_evidence_absent"] = (
        "no ross movement result is part of the present evidentiary chain" in lower
        and "ross island confirms" not in lower
    )
    checks["no_near_significance_language"] = not any(
        phrase in lower
        for phrase in (
            "marginally significant",
            "near significant",
            "nearly significant",
        )
    )

    cover = (
        root / "docs/GEB_COVER_LETTER_INTEREST_PARAGRAPH_V0_5.md"
    ).read_text(encoding="utf-8")
    cover_body = cover.split("\n\n", 1)[1] if "\n\n" in cover else cover
    checks["cover_interest_paragraph_lt_250"] = words(cover_body) < 250
    checks["cover_emphasizes_generality"] = (
        "macroecological generalization" in cover.lower()
        and "broadly relevant to geb readers" in cover.lower()
    )

    failed = [name for name, ok in checks.items() if not ok]
    return {
        "schema_version": 1,
        "audit_id": "mina-integrated-v0.5-geb-guard-v1",
        "checks": checks,
        "failed_checks": failed,
        "all_checks_pass": not failed,
        "counts": {
            "abstract_words": words(abstract),
            "main_words_intro_through_conclusion": words(main),
            "running_title_chars": len(running),
            "keyword_count": len(keywords),
            "cover_interest_words": words(cover_body),
        },
        "scientific_results_changed_from_v0_4": False,
        "figure_data_changed_from_v0_4": False,
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
