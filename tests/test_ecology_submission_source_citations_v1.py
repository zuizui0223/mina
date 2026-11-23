"""ESA Open Research dataset references, production-only, never new ecology."""
from pathlib import Path

from mina.ecology_submission_source_citations import (
    cite_public_sources_in_production_methods,
    OPEN_RESEARCH_METHODS_CITATION,
    REQUIRED_DATA_CITATION_KEYS,
)
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_no_scientific_source_manuscript_edit_when_unnamed_preview():
    original = "### Evidence design and transparency\n\nOriginal methodology."
    assert cite_public_sources_in_production_methods(original, production=False) == original


def test_three_source_citations_added_only_once_at_methods_anchor():
    body = (
        "## Materials and Methods\n\n"
        "### Evidence design and transparency\n\nExisting source notes.\n\n"
        "## Results\n\nFrozen effects."
    )
    out = cite_public_sources_in_production_methods(body, production=True)
    assert out.count(OPEN_RESEARCH_METHODS_CITATION) == 1
    assert out.endswith("Frozen effects.")
    for key in REQUIRED_DATA_CITATION_KEYS:
        assert f"[@{key}]" in out


def test_missing_method_anchor_is_a_hard_stop():
    with pytest.raises(ValueError, match="anchor"):
        cite_public_sources_in_production_methods("## Materials\nNo anchor", production=True)


def test_original_source_identifiers_in_addendum_but_not_frozen_bibliography():
    addendum = (ROOT/"submission/ECOLOGY_SOURCE_DATASET_BIB_ADDENDUM_20261014.bib").read_text(encoding="utf-8")
    oldbib = (ROOT/"docs/REFERENCES_SPATIAL_RECOVERY_PATH_STATE_V0_8.bib").read_text(encoding="utf-8")
    expected = (
        "10.7931/kf06-x745",
        "10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e",
        "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
    )
    for key, doi in zip(REQUIRED_DATA_CITATION_KEYS, expected):
        assert f"{{{key}," in addendum
        assert doi in addendum
        assert f"{{{key}," not in oldbib
