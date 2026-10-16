"""No real author metadata: author-approved production disclosure tests are fictional."""
import copy

import pytest

from mina.ecology_ai_submission_disclosure import (
    AI_SECTION_HEADER,
    approved_ai_disclosure,
    methods_disclosure_derivative,
    require_author_publication_input,
    require_author_publication_signoff,
    review_acknowledgment,
    SUBMISSION_SIGNOFF_KEYS,
)


def fake_metadata():
    return {
        "ai_tool_inventory_confirmed": True,
        "additional_ai_tools": [],
        "intended_permanent_repository": "Zenodo (FAKE EXAMPLE)",
        "ai_methods_disclosure_final_text":
            "OpenAI ChatGPT was used to assist coding and manuscript drafting (FICTIONAL FIXTURE).",
        "ai_acknowledgments_disclosure_final_text":
            "OpenAI ChatGPT assisted, with authors responsible (FICTIONAL FIXTURE).",
        "initial_submission_human_signoff": {},
    }


def test_no_author_metadata_keeps_existing_frozen_methods_unchanged():
    body = "## Materials and Methods\n\n### Evidence design and transparency\n\nFrozen calculation."
    assert methods_disclosure_derivative(body, None) == body


def test_author_approved_methods_are_injected_only_under_evidence_transparency():
    body = "## Introduction\n\nSome text\n\n" + AI_SECTION_HEADER + "\n\nFrozen text\n\n## Results\n\nFrozen results"
    meta = fake_metadata()
    result = methods_disclosure_derivative(body, meta)
    assert result.count(meta["ai_methods_disclosure_final_text"]) == 1
    assert result.index(meta["ai_methods_disclosure_final_text"]) < result.index("Frozen text")
    assert result.endswith("Frozen results")


def test_approved_methods_cannot_be_inserted_without_frozen_anchor():
    with pytest.raises(ValueError, match="Cannot safely locate"):
        methods_disclosure_derivative("## Methods\n\nNo required subsection", fake_metadata())


def test_final_ai_acknowledgments_supersede_unverified_historical_preview_only():
    meta=fake_metadata()
    assert review_acknowledgment(meta, "Old fixed model not confirmed") == meta[
        "ai_acknowledgments_disclosure_final_text"]
    assert review_acknowledgment(None, "Old fixed model not confirmed") == "Old fixed model not confirmed"


def test_final_input_rejects_missing_inventory_and_placeholders():
    d=fake_metadata()
    assert approved_ai_disclosure(d) == (
        d["ai_methods_disclosure_final_text"],
        d["ai_acknowledgments_disclosure_final_text"],
    )
    d["ai_tool_inventory_confirmed"] = False
    with pytest.raises(ValueError, match="inventory"):
        require_author_publication_input(d)
    d=fake_metadata()
    d["ai_methods_disclosure_final_text"] = "OpenAI [MODEL TO VERIFY] assisted."
    with pytest.raises(ValueError, match="placeholder"):
        require_author_publication_input(d)


def test_post_render_author_signoffs_are_not_required_while_building_preview():
    d=fake_metadata()
    require_author_publication_input(d)
    with pytest.raises(ValueError, match="signoffs"):
        require_author_publication_signoff(d)
    d["initial_submission_human_signoff"] = {k: True for k in SUBMISSION_SIGNOFF_KEYS}
    require_author_publication_signoff(d)


def test_real_production_docx_builder_routes_methods_and_acknowledgment_when_library_available():
    pytest.importorskip("docx")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from build_spatial_recovery_ecology_docx import _combined_markdown
    manuscript = (
        "# Population recovery can retrace local losses while spatial structure remains altered\n"
        "\n## Abstract\n\nA brief abstract.\n\n"
        "## Introduction\n\nExisting science.\n\n"
        "## Materials and Methods\n\n"
        "### Evidence design and transparency\n\nThe original analysis methods.\n\n"
        "## Results\n\nOriginal results.\n\n## Discussion\n\nOriginal discussion.\n"
        "## References\n"
    )
    captions = "# Captions\n\n## Figure 1. A figure.\n"
    d=fake_metadata()
    d.update({
        "authors": [{"name":"FICTIONAL TEST AUTHOR","affiliation_ids":["1"],
                     "corresponding":True,"email":"fake@example.invalid"}],
        "affiliations":{"1":"FICTIONAL INSTITUTE"},
        "present_addresses":[],
        "funding_acknowledgments":"Test funding only",
        "author_contributions":"Fake author: code and writing.",
        "conflict_of_interest":"Fixture only.",
        "dual_publication_statement":"No overlap in mock example.",
    })
    assembled = _combined_markdown(manuscript, captions, d)
    assert d["ai_methods_disclosure_final_text"] in assembled
    assert d["ai_acknowledgments_disclosure_final_text"] in assembled
    assert "GPT-5.6 Sol" not in assembled
    assert "The original analysis methods." in assembled
    assert "Original results." in assembled
    assert "archived in Zenodo (FAKE EXAMPLE)" in assembled
    assert "[@rossSeaAerialData2026]" in assembled
    assert "[@palmerLterPenguinCensus2020]" in assembled
    assert "[@signyAdelieMonitoring2021]" in assembled
