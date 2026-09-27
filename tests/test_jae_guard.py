from pathlib import Path

from mina.jae_guard import validate


def test_jae_submission_v03_format():
    root = Path(__file__).resolve().parents[1]
    out = validate(
        root / "docs/MANUSCRIPT_JAE_V0_3.md",
        root / "docs/FIGURE_CAPTIONS_V2.md",
        root / "docs/REFERENCES_V2.bib",
    )
    assert out["abstract_words"] <= 350
    assert out["abstract_statement_count"] >= 3
    assert out["keyword_count"] <= 8
    assert out["total_submission_words_approx"] <= 8500
    assert out["anonymization_surface_check"] == "pass"
    assert out["data_availability_check"] == "pass"
