"""Author-controlled publication disclosure insertion, not scientific analysis.

The frozen manuscript and source metrics are NEVER altered by this module.
Only an author-reviewed PRODUCTION markdown derivative can be assembled.
"""
from __future__ import annotations

import re
from typing import Any

AI_SECTION_HEADER = "### Evidence design and transparency"
PLACEHOLDER_RE = re.compile(r"\[[^\]]+\]|\b(?:TBD|TODO|TBC)\b", re.I)
AI_TERM_RE = re.compile(r"\b(?:AI|OpenAI|ChatGPT|LLM)\b", re.I)


def _verified_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"author-reviewed {label} is missing")
    text = value.strip()
    if PLACEHOLDER_RE.search(text):
        raise ValueError(f"author-reviewed {label} has unresolved placeholders")
    if not AI_TERM_RE.search(text):
        raise ValueError(f"author-reviewed {label} must identify AI use")
    return text


def approved_ai_disclosure(metadata: dict[str, Any]) -> tuple[str, str]:
    """Fail closed unless methods and acknowledgment texts are supplied."""
    if metadata.get("ai_tool_inventory_confirmed") is not True:
        raise ValueError("AI tool inventory must be author-confirmed")
    tools = metadata.get("additional_ai_tools")
    if not isinstance(tools, list) or any(not isinstance(t, str) or not t.strip() for t in tools):
        raise ValueError("AI tool inventory list has not been confirmed")
    methods = _verified_text(metadata.get("ai_methods_disclosure_final_text"),
                             "AI Methods disclosure")
    ack = _verified_text(metadata.get("ai_acknowledgments_disclosure_final_text"),
                         "AI Acknowledgments disclosure")
    return methods, ack


def methods_disclosure_derivative(body: str, metadata: dict[str, Any] | None) -> str:
    """Insert approved transparency note in Methods in PRODUCTION only.

    A metadata-free mock rendering stays unchanged to preserve earlier QA.
    Incomplete metadata produces an unapproved preview, NOT final output.
    """
    if metadata is None:
        return body
    methods = str(metadata.get("ai_methods_disclosure_final_text") or "").strip()
    if not methods:
        return body
    if body.count(AI_SECTION_HEADER) != 1:
        raise ValueError("Cannot safely locate frozen Methods transparency subsection")
    if PLACEHOLDER_RE.search(methods):
        raise ValueError("AI Methods text has placeholders")
    return body.replace(AI_SECTION_HEADER,
                        AI_SECTION_HEADER + "\n\n" + methods, 1)


def review_acknowledgment(metadata: dict[str, Any] | None,
                          historical_preview_ack: str) -> str:
    """Use real author text if supplied; leave old AI preview text as a preview only."""
    if metadata is None:
        return historical_preview_ack
    approved = str(metadata.get("ai_acknowledgments_disclosure_final_text") or "").strip()
    if approved:
        if PLACEHOLDER_RE.search(approved):
            raise ValueError("AI Acknowledgments text has placeholders")
        return approved
    return historical_preview_ack


SUBMISSION_SIGNOFF_KEYS = (
    "all_authors_approved_final_version",
    "corresponding_author_authorized_submission",
    "methods_acknowledgments_and_form_AI_consistent",
    "publisher_open_research_and_public_code_checked",
    "data_rights_and_attribution_checked",
    "dual_publication_and_conflicts_confirmed",
    "final_author_complete_docx_render_checked",
    "journal_article_length_or_cover_justification_confirmed",
)


def require_author_publication_signoff(metadata: dict[str, Any]) -> None:
    """Author-controlled FINAL production gate, stricter than generic metadata."""
    approved_ai_disclosure(metadata)
    repo = str(metadata.get("intended_permanent_repository") or "").strip()
    if not repo or PLACEHOLDER_RE.search(repo):
        raise ValueError("named intended permanent archive not author-confirmed")
    signoff = metadata.get("initial_submission_human_signoff") or {}
    missing = [key for key in SUBMISSION_SIGNOFF_KEYS if signoff.get(key) is not True]
    if missing:
        raise ValueError("unconfirmed final publication signoffs: " + ", ".join(missing))
