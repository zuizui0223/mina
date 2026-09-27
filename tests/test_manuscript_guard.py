from pathlib import Path

from mina.manuscript_guard import validate


def test_manuscript_v01_matches_frozen_synthesis():
    root=Path(__file__).resolve().parents[1]
    out=validate(
        root/"docs/MANUSCRIPT_V0_1.md",
        root/"docs/FIGURE_CAPTIONS_V1.md",
        root/"docs/REFERENCES_V1.bib",
        root/"results",
    )
    assert out["prohibited_claim_check"]=="pass"
    assert out["unknown_citations"]==[]
    assert out["citation_count"]>=6
    assert out["manuscript_words"]>2500
