import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("docx")

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_ecosphere_submission_docx.py"
spec = importlib.util.spec_from_file_location("ecosphere_docx_builder", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

METHODS_AI_DISCLOSURE = module.METHODS_AI_DISCLOSURE
_strip_submission_source = module._strip_submission_source
_normalize_submission_markdown = module._normalize_submission_markdown
_strip_caption_heading = module._strip_caption_heading
_combined_markdown = module._combined_markdown


def test_strip_source_removes_submission_duplicates_and_adds_ai_disclosure():
    text = """# A title

**Ecosphere-oriented manuscript v0.6 — provenance**

## Abstract

Text.

**Keywords:** a; b; c; d; e; f

### Reproducibility and frozen result family

Frozen.

## References

See docs/REFERENCES_V4.bib.
"""
    out = _strip_submission_source(text)
    assert "# A title" not in out
    assert "**Keywords:**" not in out
    assert "See docs/REFERENCES_V4.bib." not in out
    assert METHODS_AI_DISCLOSURE in out


def test_normalize_submission_markdown_fixes_word_math_boundaries():
    raw = (
        r"Following Wang and Loreau [@wang2014]. "
        r"Yielded \(\beta=\)**1.0111** and "
        r"\(\beta_{within}=\)**1.1030**."
    )
    out = _normalize_submission_markdown(raw)
    assert "Following @wang2014" in out
    assert r"\(\beta=1.0111\)" in out
    assert r"\(\beta_{within}=1.1030\)" in out
    assert r"\)**" not in out


def test_normalize_submission_markdown_replaces_underbrace_and_old_repo_text():
    raw = module.UNDERBRACE_SOURCE + "\n\n" + module.OLD_DATA_AVAILABILITY
    out = _normalize_submission_markdown(raw)
    assert r"\underbrace" not in out
    assert r"\beta_{within}=\frac{\alpha_{sub}}{\alpha_{island}}" in out
    assert "https://github.com/zuizui0223/mina" in out
    assert "anonymized repository snapshot" not in out


def test_strip_caption_heading_preserves_figure_1():
    raw = """# Figure captions v5

## Figure 1. First figure

Caption body.

## Figure 2. Second figure
"""
    out = _strip_caption_heading(raw)
    assert "Figure captions v5" not in out
    assert "## Figure 1. First figure" in out
    assert "## Figure 2. Second figure" in out


def test_combined_markdown_uses_complete_metadata():
    manuscript = """# Frozen title

## Abstract

Text.

**Keywords:** a; b; c; d; e; f

### Reproducibility and frozen result family

Frozen.

## References

See docs/REFERENCES_V4.bib.
"""
    captions = """# Figure captions v5

## Figure 1. First figure

Caption body.
"""
    metadata = {
        "authors": [
            {
                "name": "A. Author",
                "affiliation_ids": ["1"],
                "corresponding": True,
                "email": "a@example.org",
            }
        ],
        "affiliations": {
            "1": "Department A, University A, City, Country"
        },
        "present_addresses": [],
        "funding_acknowledgments": "Supported by grant X.",
        "additional_acknowledgments": "We thank C. Colleague.",
        "author_contributions": "A. Author: Conceptualization, analysis, writing.",
        "conflict_of_interest": "The author declares no conflict of interest.",
        "ai_tool_inventory_confirmed": True,
        "additional_ai_tools": [],
        "dual_publication_statement": "No overlapping manuscript is under review elsewhere.",
        "review_code_url": "https://example.org/review-code",
        "permanent_archive_doi": None,
    }
    out = _combined_markdown(manuscript, captions, metadata=metadata)
    assert "**Authors:** A. Author^1^*" in out
    assert "^1^ Department A, University A" in out
    assert "**Corresponding author:** A. Author, a@example.org" in out
    assert "Present address(es)" not in out
    assert "Supported by grant X." in out
    assert "Supported by grant X.." not in out
    assert "A. Author: Conceptualization, analysis, writing." in out
    assert "The author declares no conflict of interest." in out
    assert "https://example.org/review-code" in out
    assert "[AUTHOR" not in out
    assert "[FUNDING" not in out
