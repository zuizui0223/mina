#!/usr/bin/env python3
"""Audit JBI v0.4 submission readiness without inventing author-controlled fields."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_FILES = {
    "main_manuscript": "docs/MANUSCRIPT_INTEGRATED_JBI_V0_4.md",
    "supporting_information": "docs/SUPPLEMENT_INTEGRATED_V0_2.md",
    "figure_captions": "docs/INTEGRATED_FIGURE_CAPTIONS_V0_1.md",
    "title_page": "docs/TITLE_PAGE_JBI_INTEGRATED_V0_4_TEMPLATE.md",
    "cover_letter": "docs/COVER_LETTER_JBI_INTEGRATED_V0_2.md",
    "submission_manifest": "contracts/INTEGRATED_JBI_SUBMISSION_PACKAGE_V0_4.json",
    "format_contract": "contracts/INTEGRATED_JBI_FORMAT_V0_4.json",
    "positioning_contract": "contracts/INTEGRATED_JBI_POSITIONING_V0_2.json",
    "checklist": "submission/JBI_SUBMISSION_CHECKLIST_INTEGRATED_V0_4.md",
    "scientific_source": "docs/MANUSCRIPT_INTEGRATED_V0_3.md",
    "signy_result": "results/SIGNY_PERFORMANCE_REDISTRIBUTION_REPLICATION_RESULT_V1.json",
    "paper2_primary": "results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json",
    "detectable_effect": "results/PAPER2_DETECTABLE_EFFECT_RESULT_V1.json",
    "radius_null": "results/PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json",
}


AUTHOR_TOKENS = (
    "[author-controlled]",
    "[one corresponding author",
    "[complete]",
    "[confirm]",
    "[Corresponding author]",
)

ARCHIVE_TOKENS = (
    "permanent repository/archive URL",
    "permanent archive URL",
    "archive DOI/URL",
)

SCIENTIFIC_GUARDS = {
    "primary_paper2_p": "0.0947",
    "radius_null_p": "0.0810",
    "mde80": "0.498",
    "mde90": "0.539",
    "palmer_lag2_beta": "0.0409",
    "palmer_lag2_p": "0.00327",
    "signy_beta": "0.0213",
    "signy_p": "0.279",
}


def audit(root: Path) -> dict:
    files = {}
    missing = []
    for key, rel in REQUIRED_FILES.items():
        path = root / rel
        exists = path.is_file()
        files[key] = {"path": rel, "exists": exists}
        if not exists:
            missing.append(rel)

    if missing:
        return {
            "schema_version": 1,
            "audit_id": "mina-jbi-submission-readiness-v0.4",
            "status": "INCOMPLETE_SCIENTIFIC_PACKAGE",
            "missing_files": missing,
            "files": files,
        }

    main = (root / REQUIRED_FILES["main_manuscript"]).read_text(encoding="utf-8")
    supplement = (root / REQUIRED_FILES["supporting_information"]).read_text(encoding="utf-8")
    title = (root / REQUIRED_FILES["title_page"]).read_text(encoding="utf-8")
    cover = (root / REQUIRED_FILES["cover_letter"]).read_text(encoding="utf-8")
    checklist = (root / REQUIRED_FILES["checklist"]).read_text(encoding="utf-8")
    manifest = json.loads(
        (root / REQUIRED_FILES["submission_manifest"]).read_text(encoding="utf-8")
    )

    scientific = {
        key: (value in main or value in supplement)
        for key, value in SCIENTIFIC_GUARDS.items()
    }
    scientific.update(
        {
            "no_marginal_significance_language": "marginally significant"
            not in (main + supplement).lower(),
            "signy_nonreplication_explicit": "did not replicate" in main.lower(),
            "signy_sensitivity_not_promoted": (
                "cannot replace the null primary replication" in main.lower()
                and "cannot replace the null frozen signy primary result"
                in supplement.lower()
            ),
            "anonymous_main": all(
                marker not in main
                for marker in (
                    "## Acknowledgements",
                    "## Author contributions",
                    "## Conflict of interest statement",
                )
            ),
            "structured_abstract": all(
                f"**{heading}:**" in main
                for heading in (
                    "Aim",
                    "Location",
                    "Taxon",
                    "Methods",
                    "Results",
                    "Main conclusions",
                )
            ),
        }
    )

    author_unresolved = sorted(
        token
        for token in AUTHOR_TOKENS
        if token in title or token in cover or token in checklist
    )

    archive_unresolved = []
    for token in ARCHIVE_TOKENS:
        if token.lower() in (title + checklist).lower():
            archive_unresolved.append(token)

    taxon_image_unresolved = (
        "taxon image" in checklist.lower()
        and "- [ ]" in "\n".join(
            line for line in checklist.splitlines() if "taxon image" in line.lower()
        )
    )

    checklist_open = [
        line.strip()[6:]
        for line in checklist.splitlines()
        if line.startswith("- [ ] ")
    ]

    scientific_ready = bool(all(scientific.values()))
    upload_blockers = {
        "author_controlled_fields": author_unresolved,
        "archive_or_doi": sorted(set(archive_unresolved)),
        "taxon_image": bool(taxon_image_unresolved),
        "open_checklist_items": checklist_open,
    }
    upload_ready = (
        scientific_ready
        and not author_unresolved
        and not archive_unresolved
        and not taxon_image_unresolved
        and not checklist_open
    )

    return {
        "schema_version": 1,
        "audit_id": "mina-jbi-submission-readiness-v0.4",
        "status": (
            "UPLOAD_READY"
            if upload_ready
            else "SCIENTIFIC_PACKAGE_READY_UPLOAD_BLOCKED"
            if scientific_ready
            else "SCIENTIFIC_PACKAGE_NOT_READY"
        ),
        "scientific_package_ready": scientific_ready,
        "upload_ready": upload_ready,
        "files": files,
        "scientific_guards": scientific,
        "upload_blockers": upload_blockers,
        "manifest_status": manifest.get("status"),
        "boundary": (
            "This audit never fills author identity, funding, declarations, "
            "archive identifiers, taxon-image permissions or approval fields."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result.get("scientific_package_ready", False):
        raise SystemExit("scientific JBI package is not ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
