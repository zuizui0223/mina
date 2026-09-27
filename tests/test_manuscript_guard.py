from pathlib import Path

from mina.manuscript_guard import validate


def _validate_version(root: Path, version: str, caption_version: str, reference_version: str):
    return validate(
        root/f"docs/MANUSCRIPT_{version}.md",
        root/f"docs/FIGURE_CAPTIONS_{caption_version}.md",
        root/f"docs/REFERENCES_{reference_version}.bib",
        root/"results",
    )


def test_manuscript_v01_matches_frozen_synthesis():
    root=Path(__file__).resolve().parents[1]
    out=_validate_version(root,"V0_1","V1","V1")
    assert out["prohibited_claim_check"]=="pass"
    assert out["unknown_citations"]==[]
    assert out["citation_count"]>=6
    assert out["manuscript_words"]>2500


def test_manuscript_v02_matches_frozen_synthesis():
    root=Path(__file__).resolve().parents[1]
    out=_validate_version(root,"V0_2","V2","V2")
    assert out["prohibited_claim_check"]=="pass"
    assert out["unknown_citations"]==[]
    assert out["citation_count"]>=8
    assert out["manuscript_words"]>2800
