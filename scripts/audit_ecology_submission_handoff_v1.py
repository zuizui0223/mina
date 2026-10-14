#!/usr/bin/env python3
"""Author-safe ESA Ecology Article submission preflight, NOT a submission action.

Never guess people, institution, funding, original source rights, AI-tool
inventories, approvals or permanent archive identifiers. The public default
template is intentionally blocked. No animal-data outcomes are computed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from mina.ecosphere_submission_metadata import load_metadata, validate_metadata
from mina.ecology_ai_submission_disclosure import (
    require_author_publication_signoff,
)

FROZEN_BLOBS = {
    "docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_8.md":
        "b95ccc5f662b21c77635e5b7273fd400cd51d59f",
    "docs/REFERENCES_SPATIAL_RECOVERY_PATH_STATE_V0_8.bib":
        "09e1e8c6cc7a52cde9d71ebccdb77a26d76b818e",
    "results/SPATIAL_RECOVERY_CLAIM_EVIDENCE_LEDGER_V4.json":
        "e4f5549cbb0b218a0b03fb0bf665459f6ddfcad8",
    "results/ROSS_PATH_VERSUS_STATE_RECOVERY_AUDIT_V1.json":
        "ee274203b373d38dd8fc2035cbde54103706864f",
    "results/ROSS_PATH_STATE_SPATIAL_GRAIN_AUDIT_V1.json":
        "6682dafcf49d0b9d335ce99ce0e6bb8fa6c4e5d0",
    "docs/ROSS_LOCAL_RECOVERY_RATIO_DECOMPOSITION_V1.md":
        "c48cf9054f3ee7451c756351cd87da0a5ba4579f",
    "scripts/build_spatial_recovery_path_state_figures.py":
        "a458fa5fe7d1fb03261c0e08ba354a5d78302776",
    "docs/FIGURE_CAPTIONS_SPATIAL_RECOVERY_PATH_STATE_V0_1.md":
        "afdd6a6d15dce8e57b8f61858414a87246d830c6",
}
MANUSCRIPT = "docs/MANUSCRIPT_SPATIAL_RECOVERY_PATH_STATE_V0_9.md"
BIBLIOGRAPHY = "docs/REFERENCES_SPATIAL_RECOVERY_PATH_STATE_V0_8.bib"
CAPTIONS = "docs/FIGURE_CAPTIONS_SPATIAL_RECOVERY_PATH_STATE_V0_3.md"
SUPPLEMENT = "submission/SUPPLEMENT_SPATIAL_RECOVERY_PATH_STATE_V1.md"
BUILDER = "scripts/build_spatial_recovery_ecology_docx.py"
RECORDED_QA = "submission/SPATIAL_RECOVERY_ECOLOGY_PRODUCTION_QA_V2.json"
HANDOFF = "submission/ECOLOGY_INITIAL_SUBMISSION_HANDOFF_20261014.md"
AI_REVIEW = "submission/ECOLOGY_AI_DISCLOSURE_AUTHOR_REVIEW_20261014.md"
PUBLIC_BLANK = "submission/ECOLOGY_INITIAL_SUBMISSION_METADATA_TEMPLATE_20261014.json"
TITLE = "Population recovery can retrace local losses while spatial structure remains altered"

AUTHOR_SIGNOFF = (
    "all_authors_approved_final_version",
    "corresponding_author_authorized_submission",
    "methods_acknowledgments_and_form_AI_consistent",
    "publisher_open_research_and_public_code_checked",
    "data_rights_and_attribution_checked",
    "dual_publication_and_conflicts_confirmed",
    "final_author_complete_docx_render_checked",
    "journal_article_length_or_cover_justification_confirmed",
)
MANUSCRIPT_REQUIRED = (
    MANUSCRIPT, BIBLIOGRAPHY, CAPTIONS, SUPPLEMENT, BUILDER, RECORDED_QA,
    HANDOFF, AI_REVIEW, PUBLIC_BLANK,
)
EXPECTED_DATASET_DOIS = (
    "10.7931/kf06-x745",
    "10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e",
    "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
)


def git_blob_sha(path: Path) -> str:
    """Compute the 40-character Git blob SHA-1, not the raw-file SHA."""
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                        b"\0" + raw).hexdigest()


def freeze_integrity(root: Path) -> dict[str, Any]:
    actual = {}
    wrong = []
    for rel, expected in FROZEN_BLOBS.items():
        file = root / rel
        observed = git_blob_sha(file) if file.is_file() else None
        actual[rel] = {"expected": expected, "current": observed, "match": observed == expected}
        if observed != expected:
            wrong.append(rel)
    return {"all_frozen_blobs_unchanged": not wrong, "files_checked": len(actual),
            "blobs": actual, "drift_paths": wrong,
            "archived_freeze_head": "3e8882742ca2affc6717d373fd9b6d903b01f4c1",
            "legacy_typographical_Sha_addendum": "submission/ECOLOGY_SPATIAL_RECOVERY_FREEZE_BLOB_VERIFICATION_20261014.md"}


def abstract_body(manuscript: str) -> str:
    match = re.search(r"(?ms)^## Abstract\s*\n(.*?)(?=^## Introduction\b)", manuscript)
    if not match:
        raise ValueError("STRUCTURE_STOP abstract or introduction absent")
    return re.sub(r"^\*\*Keywords:\*\*.*$", "", match.group(1), flags=re.M).strip()


def word_count(text: str) -> int:
    # Journal site may count hyphenation differently; only enforce <=350 here.
    return len(re.findall(r"\b[\w]+(?:[-’'][\w]+)*\b", text))


def source_and_production_checks(root: Path) -> dict[str, Any]:
    missing = [name for name in MANUSCRIPT_REQUIRED if not (root/name).is_file()]
    if missing:
        return {"pass": False, "missing_submission_files": missing}
    manuscript = (root/MANUSCRIPT).read_text(encoding="utf-8")
    biblio = (root/BIBLIOGRAPHY).read_text(encoding="utf-8")
    qa = json.loads((root/RECORDED_QA).read_text(encoding="utf-8"))
    builder = (root/BUILDER).read_text(encoding="utf-8")
    caps = (root/CAPTIONS).read_text(encoding="utf-8")
    supp = (root/SUPPLEMENT).read_text(encoding="utf-8")
    title = manuscript.splitlines()[0].removeprefix("# ").strip()
    abstract = abstract_body(manuscript)
    cited = set(re.findall(r"@([A-Za-z][\w.-]*)", manuscript))
    available = set(re.findall(r"(?m)^\s*@[A-Za-z]+\s*\{\s*([^,\s]+)", biblio))
    absent = sorted(cited - available)
    methods_match = re.search(
        r"(?ms)^## Materials and Methods\s*\n(.*?)(?=^## Results\b)", manuscript
    )
    methods = methods_match.group(1) if methods_match else ""
    ai_in_frozen_methods = bool(re.search(
        r"OpenAI|ChatGPT|AI-assisted|artificial intelligence|large language model",
        methods, flags=re.I
    ))
    ai_ack_builder = "AI_ACK" in builder and "OpenAI ChatGPT" in builder
    verified_author_insertion = all(
        marker in builder for marker in (
            "methods_disclosure_derivative",
            "review_acknowledgment",
            "require_author_publication_input",
        )
    )
    mock_pages = 30
    ok = (
        title == TITLE and word_count(abstract) <= 350 and not absent
        and qa.get("decision", {}).get("qa_pass") is True
        and qa.get("production_manuscript") == MANUSCRIPT
        and qa.get("checks", {}).get("missing_bibliography_keys") == 0
        and "Figure 1" in caps and "Figure 2" in caps
        and "Figure S1" in supp and "Figure S2" in supp
        and ai_ack_builder and verified_author_insertion
    )
    return {
        "pass": bool(ok),
        "journal": "Ecology",
        "article_type": "Article",
        "canonical_title_matches": title == TITLE,
        "abstract_words_simple_tokenizer": word_count(abstract),
        "journal_abstract_maximum_words": 350,
        "missing_bibliography_keys_recomputed": absent,
        "frozen_production_qa_receipt_pass": qa.get("decision",{}).get("qa_pass") is True,
        "previous_mock_author_complete_pages": mock_pages,
        "previous_mock_render_source": RECORDED_QA,
        "real_author_complete_docx_rechecked": False,
        "main_figure_count": 2,
        "supporting_figure_count": 2,
        "AI_acknowledgment_template_present": ai_ack_builder,
        "author_approved_AI_Methods_and_ack_insertion_wired": verified_author_insertion,
        "AI_disclosure_in_frozen_methods": ai_in_frozen_methods,
        "production_Methods_AI_disclosure_requires_author_review": not ai_in_frozen_methods,
        "source_dataset_DOIs_in_open_research_document": {
            doi: doi in (root/"submission/OPEN_RESEARCH_STATEMENT_SPATIAL_RECOVERY_V1.md").read_text(encoding="utf-8")
            for doi in EXPECTED_DATASET_DOIS
        },
        "note": "Historical placeholder Word QA is not a final author-complete Word/PDF verification.",
    }


def metadata_checks(data: dict[str, Any]) -> dict[str, Any]:
    basic = validate_metadata(data)
    votes = data.get("initial_submission_human_signoff") or {}
    confirmations = {key: votes.get(key) is True for key in AUTHOR_SIGNOFF}
    repo_plan = str(data.get("intended_permanent_repository") or "").strip()
    methods = str(data.get("ai_methods_disclosure_final_text") or "").strip()
    ack = str(data.get("ai_acknowledgments_disclosure_final_text") or "").strip()
    has_ai = bool(re.search(r"\b(?:AI|OpenAI|ChatGPT)\b", methods, re.I)
                  and re.search(r"\b(?:AI|OpenAI|ChatGPT)\b", ack, re.I))
    strict_publisher_input_and_signoff_valid = True
    try:
        require_author_publication_signoff(data)
    except ValueError:
        strict_publisher_input_and_signoff_valid = False
    pending = sorted(
        set(basic["unresolved_fields"]) |
        {key for key, verified in confirmations.items() if not verified} |
        ({"intended_permanent_repository"} if not repo_plan else set()) |
        ({"ai_methods_and_ack_final_text"} if not has_ai else set()) |
        ({"author_approved_production_metadata_or_signoffs"}
         if not strict_publisher_input_and_signoff_valid else set())
    )
    return {
        "ready_for_submission_metadata": not pending,
        "author_count": basic["author_count"],
        "corresponding_author_count": basic["corresponding_author_count"],
        "post_acceptance_archive_doi_still_pending": basic["post_acceptance_archive_pending"],
        "intended_permanent_repository_specified": bool(repo_plan),
        "AI_Methods_and_Acknowledgments_final_text_supplied": has_ai,
        "human_signoff": confirmations,
        "unresolved_fields": pending,
        "privacy_safeguard": "Author names, email addresses and contributions are NOT printed in this public QA receipt."
    }


def audit(root: Path, author_metadata: Path | None = None) -> dict[str, Any]:
    frozen = freeze_integrity(root)
    package = source_and_production_checks(root)
    if author_metadata is None:
        author_metadata = root/PUBLIC_BLANK
        origin = "PUBLIC_PLACEHOLDER_TEMPLATE_NOT_AUTHOR_CONFIRMED"
    else:
        origin = "LOCAL_PRIVATELY_FILLED_AUTHOR_METADATA_NOT_EMITTED"
    human = metadata_checks(load_metadata(author_metadata))
    science_ok = frozen["all_frozen_blobs_unchanged"]
    package_ok = package["pass"]
    ready = science_ok and package_ok and human["ready_for_submission_metadata"]
    return {
        "result": "ELIGIBLE_FOR_MANUAL_SCHOLARONE_FINAL_PROOF_CHECK" if ready
                  else "BLOCKED_BEFORE_REAL_SUBMISSION",
        "journal": "Ecology / Article",
        "not_submitted": True,
        "no_new_scientific_endpoints": True,
        "science_freeze": frozen,
        "production_static_audit": package,
        "author_metadata": human,
        "author_metadata_origin": origin,
        "scholarone_submission_not_performed": True,
        "open_research_requirement": (
            "External public GitHub code can be used for peer review; "
            "authors must select intended permanent data/code archive; "
            "accepted paper needs actual permanent identifier. "
            "Do not upload .csv/.xlsx or novel code as ScholarOne SI files."
        ),
        "policy_sources": [
            "https://esajournals.onlinelibrary.wiley.com/hub/journal/19399170/author-guidelines",
            "https://esa.org/publications/data-policy/",
            "https://esa.org/publications/artificial-intelligence-ai-policy/",
            "https://esa.org/about/code-of-ethics/",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--metadata", type=Path,
                        help="Path to private author-filled JSON; NEVER commit or print it")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--require-ready", action="store_true",
                        help="Exit nonzero if genuine author-controlled metadata remains incomplete")
    args = parser.parse_args()
    result = audit(args.root, args.metadata)
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded, encoding="utf-8")
    # No author name, email, funding, signed consent, or other personal data is printed.
    print(encoded)
    if not result["science_freeze"]["all_frozen_blobs_unchanged"]:
        return 2
    if not result["production_static_audit"]["pass"]:
        return 2
    if args.require_ready and result["result"] != "ELIGIBLE_FOR_MANUAL_SCHOLARONE_FINAL_PROOF_CHECK":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
