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
