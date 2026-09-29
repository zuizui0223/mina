from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "docs" / "PALMER_PHENOTYPE_REASSEMBLY_MANUSCRIPT_SPINE_V1.md"


def test_spine_centers_species_sorting_and_temporal_reassembly():
    text = SPINE.read_text(encoding="utf-8")

    assert "Species sorting creates transient island phenotypes" in text
    assert "morphology versus pooled site marginal: **+0.38946**" in text
    assert "morphology beyond species identity: **−0.08375**" in text
    assert "**0.4482**" in text
    assert "**0.3424**" in text
    assert "**0.1059**" in text
    assert "temporally unstable" in text
    assert "species sorting plus temporal reassembly" in text
    assert "ODSP methodological novelty" in text


def test_spine_does_not_merge_with_frozen_paper1_or_paper2():
    text = SPINE.read_text(encoding="utf-8")

    assert "long-term LTER colony-network concentration" in text
    assert "Paper 2 Antarctic-wide demographic filtering" in text
    assert "Those remain separate mina/ODSP products." in text
