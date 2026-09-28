"""Fail-closed structural audit for the Ecosphere v0.6 submission shell."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .ecosphere_submission_metadata import load_metadata, validate_metadata

TITLE_LIMIT = 120
ABSTRACT_LIMIT = 350
KEYWORDS_MIN = 6
KEYWORDS_MAX = 12

EXPECTED_TITLE = (
    "Common decline, divergent endpoints: hierarchical demography across "
    "Antarctic penguin breeding islands"
)

REQUIRED_HUMAN_BLOCKER_ALIASES = (
    ("author list",),
    ("affiliations",),
    ("corresponding author",),
    ("author contribution",),
    ("funding",),
    ("conflict of interest", "conflict-of-interest"),
    ("ai tool", "ai tools"),
    ("dual-publication", "overlap"),
)

PLACEHOLDER_PATTERNS = (
    "[AUTHOR",
    "[Department",
    "[PRESENT ADDRESS",
    "[ONE AUTHOR NAME]",
    "[EMAIL ADDRESS]",
)


def _abstract(text: str) -> str:
    if "## Abstract" not in text or "**Keywords:**" not in text:
        raise ValueError("manuscript missing Abstract or Keywords boundary")
    return text.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0].strip()


def _keywords(text: str) -> list[str]:
    match = re.search(r"\*\*Keywords:\*\*\s*(.+)", text)
    if not match:
        raise ValueError("manuscript missing Keywords line")
    return [part.strip() for part in match.group(1).split(";") if part.strip()]


def inspect(
    manuscript: str | Path,
    title_page: str | Path,
    contract: str | Path,
    metadata: str | Path | None = None,
    word_qa_confirmed: bool = False,
) -> dict[str, object]:
    manuscript_text = Path(manuscript).read_text(encoding="utf-8")
    title_page_text = Path(title_page).read_text(encoding="utf-8")
    contract_data = json.loads(Path(contract).read_text(encoding="utf-8"))

    first_line = manuscript_text.splitlines()[0]
    title = re.sub(r"^#\s*", "", first_line).strip()
    abstract_words = len(re.findall(r"\b[\w’'-]+\b", _abstract(manuscript_text)))
    keywords = _keywords(manuscript_text)

    structural = {
        "title_matches_frozen_v0_6": title == EXPECTED_TITLE,
        "title_characters": len(title),
        "title_within_limit": len(title) <= TITLE_LIMIT,
        "abstract_words": abstract_words,
        "abstract_within_limit": abstract_words <= ABSTRACT_LIMIT,
        "keyword_count": len(keywords),
        "keywords_within_range": KEYWORDS_MIN <= len(keywords) <= KEYWORDS_MAX,
        "open_research_template_present": "## Open Research Statement" in title_page_text,
        "public_review_code_link_present": (
            "https://github.com/zuizui0223/mina" in title_page_text
        ),
        "preview_word_qa_recorded": bool(
            contract_data.get("word_preview",{}).get(
                "preview_generated_and_visually_checked"
            )
        ),
    }
    failed = [
        name
        for name, value in structural.items()
        if isinstance(value, bool) and not value
    ]
    if failed:
        raise ValueError(f"submission structural checks failed: {failed}")

    unresolved_placeholders = [
        pattern for pattern in PLACEHOLDER_PATTERNS if pattern in title_page_text
    ]
    contract_blockers = list(contract_data.get("human_only_blockers", []))
    blocker_text = " ".join(contract_blockers).lower()
    missing_expected_blockers = [
        "/".join(aliases)
        for aliases in REQUIRED_HUMAN_BLOCKER_ALIASES
        if not any(alias in blocker_text for alias in aliases)
    ]
    if missing_expected_blockers:
        raise ValueError(
            "submission contract no longer fails closed for: "
            + ", ".join(missing_expected_blockers)
        )

    metadata_result=None
    blockers: list[str]=[]
    if metadata is None:
        blockers.extend(contract_blockers)
        blockers.append(
            "author-complete Word Main Document not yet generated and visually checked"
        )
    else:
        metadata_result=validate_metadata(load_metadata(metadata))
        blockers.extend(
            f"metadata unresolved: {field}"
            for field in metadata_result["unresolved_fields"]
        )
        if not word_qa_confirmed:
            blockers.append(
                "author-complete Word Main Document not yet visually checked"
            )

    return {
        "schema_version": 2,
        "audit_id": "mina-ecosphere-v0.6-submission-readiness-v2",
        "structural_checks": structural,
        "unresolved_title_page_template_placeholders": unresolved_placeholders,
        "metadata_validation": metadata_result,
        "word_qa_confirmed_for_author_complete_document": bool(word_qa_confirmed),
        "blocking_items": blockers,
        "ready_for_scholarone": len(blockers) == 0,
        "post_acceptance_tasks": contract_data.get("post_acceptance_tasks", []),
        "boundary": {
            "scientific_endpoints_changed": False,
            "author_metadata_invented": False,
            "coi_assumed": False,
            "funding_assumed": False,
            "permanent_archive_doi_required_before_initial_submission": False,
            "ai_disclosure_already_present_in_docx_builder": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manuscript", required=True, type=Path)
    parser.add_argument("--title-page", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--word-qa-confirmed", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--expect-blocked", action="store_true")
    args = parser.parse_args()
    result = inspect(
        args.manuscript,
        args.title_page,
        args.contract,
        metadata=args.metadata,
        word_qa_confirmed=args.word_qa_confirmed,
    )
    if args.expect_blocked and result["ready_for_scholarone"]:
        raise ValueError("expected unresolved human submission metadata")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
