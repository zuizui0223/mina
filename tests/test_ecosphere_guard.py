from pathlib import Path

from mina.ecosphere_guard import validate


def test_ecosphere_v051_package():
    root=Path(__file__).resolve().parents[1]
    out=validate(
        root/"docs/MANUSCRIPT_ECOSPHERE_V0_5.md",
        root/"docs/TITLE_PAGE_ECOSPHERE_TEMPLATE.md",
        root/"docs/AI_DISCLOSURE_ECOSPHERE_V1.md",
    )
    assert out["target"]=="Ecosphere"
    assert out["article_type"]=="Article"
    assert out["subject_track"]=="Animal Ecology"
    assert out["abstract_words"]<=350
    assert 6<=out["keyword_count"]<=12
    assert out["abstract_citation_url_check"]=="pass"
    assert out["open_research_check"]=="pass"
    assert out["structured_null_claim_check"]=="pass"
    assert out["predictive_withdrawal_check"]=="pass"
    assert out["ai_disclosure_template_check"]=="pass"
    assert out["human_metadata_complete"] is False
    assert len(out["unresolved_human_placeholders"])>=3
