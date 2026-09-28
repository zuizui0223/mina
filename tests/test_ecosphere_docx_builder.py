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
