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


def test_manuscript_v04_ecosphere_after_neff_diagnostics():
    root=Path(__file__).resolve().parents[1]
    out=validate(
        root/"docs/MANUSCRIPT_ECOSPHERE_V0_4.md",
        root/"docs/FIGURE_CAPTIONS_V3.md",
        root/"docs/REFERENCES_V3.bib",
        root/"results",
    )
    assert out["prohibited_claim_check"]=="pass"
    assert out["unknown_citations"]==[]
    assert out["citation_count"]>=12
    assert out["manuscript_words"]>3000

    text=(root/"docs/MANUSCRIPT_ECOSPHERE_V0_4.md").read_text()
    assert "0.262" in text
    assert "5,244/20,000" in text
    assert "Palmer Penguins data set" not in text
    assert "withdraw the claim that effective colony number provides robust held-out-year predictive information" in text
    assert "timescale-dependent" in text.lower()
